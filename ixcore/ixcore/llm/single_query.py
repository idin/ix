"""
Single query function that routes to the appropriate provider.
"""

from typing import List, Dict, Optional, Any, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

from .query_openai import query_openai
from .query_anthropic import query_anthropic
from .caching import get_cached_result, set_cached_result


# Type aliases
Message = Dict[str, str]
Messages = List[Message]
Query = Messages
Queries = List[Query]

def _detect_provider(model_name: str) -> str:
    """
    Detect the provider from the model name.
    
    Args:
        model_name: The model name.
    
    Returns:
        The detected provider name.
    """
    model_lower = model_name.lower()
    if model_lower.startswith("gpt") or model_lower.startswith("o1"):
        return "openai"
    elif model_lower.startswith("claude"):
        return "anthropic"
    elif model_lower.startswith("gemini"):
        return "google"
    else:
        # Default to OpenAI for unknown models
        return "openai"


def single_query(
    client: Any,
    messages: Query,
    model_name: str,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    use_cache: bool = False,
    **kwargs: Any,
) -> Union[str, Dict[str, Any]]:
    """
    Execute a single query using the appropriate provider.
    
    Routes to query_openai or query_anthropic based on the model_name.
    Provider is auto-detected from the model name.
    
    Args:
        client: The client instance (OpenAI or Anthropic).
        messages: List of message dictionaries with 'role' and 'content' keys.
        model_name: The model name to use. Provider is auto-detected from this.
        max_tokens: Maximum number of tokens to generate.
        temperature: Sampling temperature.
        use_cache: If True, cache LLM responses based on query parameters to avoid
            duplicate API calls. When True, results will include 'from_cache' flag.
            Default: False.
        **kwargs: Additional provider-specific parameters.
    
    Returns:
        The query result (string or dict depending on provider and response type).
        When use_cache=True, dict results will include 'from_cache' boolean flag.
    
    Raises:
        ValueError: If provider is not supported.
    """
    provider = _detect_provider(model_name)
    provider = provider.lower()
    
    # Check cache if enabled
    from_cache = False
    if use_cache:
        cached_result = get_cached_result(
            model_name=model_name,
            provider=provider,
            query_messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            merged_kwargs=kwargs,
        )
        if cached_result is not None:
            from_cache = True
            # Add from_cache flag to cached result
            if isinstance(cached_result, dict):
                cached_result["from_cache"] = True
                return cached_result
            else:
                # Wrap string result in dict with from_cache flag
                return {"content": cached_result, "from_cache": True}
    
    # Execute query
    if provider == "openai":
        result = query_openai(
            client=client,
            model_name=model_name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )
    elif provider == "anthropic":
        result = query_anthropic(
            client=client,
            model_name=model_name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )
    else:
        raise ValueError(
            f"Unsupported provider: {provider}. "
            "Supported providers: openai, anthropic"
        )
    
    # Cache the result if enabled
    if use_cache:
        set_cached_result(
            model_name=model_name,
            provider=provider,
            query_messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            merged_kwargs=kwargs,
            result=result,
        )
        # Add from_cache flag to result
        if isinstance(result, dict):
            result["from_cache"] = False
        else:
            # Wrap string result in dict with from_cache flag
            result = {"content": result, "from_cache": False}
    
    return result


def batch_query(
    client: Any,
    model_name: str,
    queries: Queries,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    max_workers: Optional[int] = None,
    use_cache: bool = False,
    **kwargs: Any,
) -> List[Union[str, Dict[str, Any], Exception]]:
    """
    Execute multiple queries in parallel.
    
    Args:
        client: The client instance (OpenAI or Anthropic).
        model_name: The model name to use. Provider is auto-detected from this.
        queries: List of queries, where each query is a list of message dictionaries.
        max_tokens: Maximum number of tokens to generate.
        temperature: Sampling temperature.
        max_workers: Maximum number of parallel workers.
            If None, uses default ThreadPoolExecutor value.
        use_cache: If True, cache LLM responses based on query parameters to avoid
            duplicate API calls. Default: False.
        **kwargs: Additional provider-specific parameters.
    
    Returns:
        List of query results in the same order as input.
        Each result is either a string/dict or an Exception if the query failed.
    
    Example:
        results = batch_query(
            client=client,
            model_name="gpt-4o-mini",
            queries=[
                [{"role": "user", "content": "What is 2+2?"}],
                [{"role": "user", "content": "What is 3+3?"}],
            ],
        )
    """
    if not queries:
        return []
    
    def execute_single_query(
        query: Query,
        index: int,
    ) -> tuple[int, Union[str, Dict[str, Any], Exception]]:
        """Execute a single query with the given messages."""
        try:
            result = single_query(
                client=client,
                model_name=model_name,
                messages=query,
                max_tokens=max_tokens,
                temperature=temperature,
                use_cache=use_cache,
                **kwargs,
            )
            return (index, result)
        except Exception as exc:
            return (index, exc)
    
    results: List[Union[str, Dict[str, Any], Exception, None]] = [None] * len(queries)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(execute_single_query, query, idx): idx
            for idx, query in enumerate(queries)
        }
        
        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                result_idx, result = future.result()
                results[result_idx] = result
            except Exception as exc:
                results[idx] = exc
    
    return results
