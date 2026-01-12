"""
Caching utilities for LLM queries.
"""

from typing import List, Dict, Optional, Any

from ixutils import get_cache_path
from ixutils.persist import (
    hash_data,
    resolve_cache_file_path,
    get_from_disk_cache,
    set_to_disk_cache,
    DEFAULT_CACHE_PATH,
    _CACHE_MISS,
)


def get_cached_result(
    model_name: str,
    provider: str,
    query_messages: List[Dict[str, str]],
    max_tokens: Optional[int],
    temperature: Optional[float],
    merged_kwargs: Dict[str, Any],
) -> Optional[str]:
    """
    Get cached LLM query result if available.
    
    Args:
        model_name: The model name.
        provider: The provider name.
        query_messages: List of message dictionaries.
        max_tokens: Maximum tokens parameter.
        temperature: Temperature parameter.
        merged_kwargs: Additional merged kwargs.
    
    Returns:
        Cached result if found, None otherwise.
    """
    cache_data = {
        "model_name": model_name,
        "provider": provider,
        "messages": query_messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "kwargs": sorted(merged_kwargs.items()) if merged_kwargs else [],
    }
    arg_hash = hash_data(cache_data)
    cache_key = f"llm_query:{model_name}"
    
    # Resolve cache file path
    default_cache_path = get_cache_path() or DEFAULT_CACHE_PATH
    cache_file_path = resolve_cache_file_path(
        cache_key=cache_key,
        arg_hash=arg_hash,
        cache_path_override=None,
        default_cache_path=default_cache_path,
        memory=False,
    )
    
    # Try to get from cache
    if cache_file_path is not None:
        cached_result = get_from_disk_cache(
            cache_file_path=cache_file_path,
            expire_seconds=None,
        )
        if cached_result is not _CACHE_MISS:
            return cached_result
    
    return None


def set_cached_result(
    model_name: str,
    provider: str,
    query_messages: List[Dict[str, str]],
    max_tokens: Optional[int],
    temperature: Optional[float],
    merged_kwargs: Dict[str, Any],
    result: Any,
) -> None:
    """
    Cache an LLM query result.
    
    Args:
        model_name: The model name.
        provider: The provider name.
        query_messages: List of message dictionaries.
        max_tokens: Maximum tokens parameter.
        temperature: Temperature parameter.
        merged_kwargs: Additional merged kwargs.
        result: The result to cache.
    """
    cache_data = {
        "model_name": model_name,
        "provider": provider,
        "messages": query_messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "kwargs": sorted(merged_kwargs.items()) if merged_kwargs else [],
    }
    arg_hash = hash_data(cache_data)
    cache_key = f"llm_query:{model_name}"
    
    # Resolve cache file path
    default_cache_path = get_cache_path() or DEFAULT_CACHE_PATH
    cache_file_path = resolve_cache_file_path(
        cache_key=cache_key,
        arg_hash=arg_hash,
        cache_path_override=None,
        default_cache_path=default_cache_path,
        memory=False,
    )
    
    # Cache the result if enabled
    if cache_file_path is not None:
        set_to_disk_cache(
            cache_file_path=cache_file_path,
            value=result,
            expire_seconds=None,
            raise_on_error=False,
        )

