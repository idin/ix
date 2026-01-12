"""
Pricing and cost calculation for LLM.
"""

from typing import Dict, Optional, Union

from ..utils.normalize_keys import normalize_key, normalize_keys


def fetch_pricing_from_web(
    provider: str,
    model_name: str,
    llm_instance,
) -> Optional[Dict[str, Union[float, Dict[str, float]]]]:
    """
    Fetch pricing from the web using get_model_prices.
    
    This is called lazily on the first query if fetch_pricing=True.
    
    Args:
        provider: The provider name (e.g., "openai", "anthropic").
        model_name: The model name.
        llm_instance: The LLM instance (used to call get_model_prices).
    
    Returns:
        Pricing dictionary if found, None otherwise.
    """
    try:
        # Lazy import to avoid circular dependencies
        from ..tools.pricing import get_model_prices
        
        # Use provider name directly as company name
        company = provider
        # Only support known providers
        if company not in ["openai", "anthropic", "google"]:
            return None
        
        # Fetch pricing using llm_instance (the _pricing_fetched flag prevents recursion)
        result = get_model_prices(company=company, llm=llm_instance, max_search_results=5)
        
        if result.get("success") and result.get("prices"):
            prices = result["prices"]
            # Normalize model name for lookup
            normalized_model = normalize_key(model_name)
            
            # Normalize all keys in prices dictionary
            normalized_prices = normalize_keys(prices)
            
            # Try exact match first
            price_data = normalized_prices.get(normalized_model)
            if price_data:
                return price_data
            
            # Try partial match (check if normalized_model is contained in any key)
            for key, value in normalized_prices.items():
                if normalized_model in key or key in normalized_model:
                    return value
    except Exception:
        # Silently fail - pricing fetch is optional
        pass
    
    return None


def calculate_cost(
    pricing: Optional[Union[float, Dict[str, float]]],
    usage: Dict[str, int],
) -> Optional[Dict[str, float]]:
    """
    Calculate cost from usage based on pricing.
    
    Args:
        pricing: Pricing information. Can be:
            - A float: single price per million tokens (same for input/output)
            - A dict with "input" and "output" keys: different prices per million tokens
        usage: Dictionary with input_tokens, output_tokens, and total_tokens.
    
    Returns:
        Dictionary with "input_cost", "output_cost", and "total_cost" in dollars.
        Returns None if pricing is not available or tokens are missing.
    """
    if pricing is None:
        return None
    
    # If input_tokens or output_tokens are None, return None, do not return 0
    input_tokens = usage.get("input_tokens", None)
    output_tokens = usage.get("output_tokens", None)
    
    if input_tokens is None or output_tokens is None:
        return None
    
    # Handle different pricing formats
    if isinstance(pricing, (int, float)):
        # Single price per million tokens (same for input/output)
        price_per_million = float(pricing)
        input_cost = (input_tokens / 1_000_000) * price_per_million
        output_cost = (output_tokens / 1_000_000) * price_per_million
    elif isinstance(pricing, dict):
        # Different prices for input/output
        input_price = pricing.get("input", None)
        output_price = pricing.get("output", None)
        
        # If input_price or output_price are None, return None, do not return 0
        if input_price is None or output_price is None:
            return None
        
        input_cost = (input_tokens / 1_000_000) * float(input_price)
        output_cost = (output_tokens / 1_000_000) * float(output_price)
    else:
        return None
    
    total_cost = input_cost + output_cost
    
    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost,
    }


def calculate_cost_from_usage(
    pricing: Optional[Union[float, Dict[str, float]]],
    input_tokens: int,
    output_tokens: int,
) -> Optional[Dict[str, float]]:
    """
    Calculate cost from input and output tokens.
    
    This is a pure calculator method that does NOT update tracking.
    It only calculates the cost based on the provided tokens and current pricing.
    
    Args:
        pricing: Pricing information. Can be:
            - A float: single price per million tokens (same for input/output)
            - A dict with "input" and "output" keys: different prices per million tokens
        input_tokens: Number of input tokens.
        output_tokens: Number of output tokens.
    
    Returns:
        Dictionary with "input_cost", "output_cost", and "total_cost" in dollars.
        Returns None if pricing is not set.
    """
    if pricing is None:
        return None
    
    # Calculate cost without updating tracking
    if isinstance(pricing, (int, float)):
        # Single price per million tokens (same for input/output)
        price_per_million = float(pricing)
        input_cost = (input_tokens / 1_000_000) * price_per_million
        output_cost = (output_tokens / 1_000_000) * price_per_million
    elif isinstance(pricing, dict):
        # Different prices for input/output
        input_price = pricing.get("input")
        output_price = pricing.get("output")
        
        if input_price is None or output_price is None:
            return None
        
        input_cost = (input_tokens / 1_000_000) * float(input_price)
        output_cost = (output_tokens / 1_000_000) * float(output_price)
    else:
        return None
    
    total_cost = input_cost + output_cost
    
    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost,
    }

