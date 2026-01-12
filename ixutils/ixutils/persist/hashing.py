"""
Hashing utilities for cache key generation.
"""

import hashlib
import json
import pickle
from typing import Any, Optional


def hash_data(data: Any, exclude_keys: Optional[set] = None) -> str:
    """
    Create a hash of data for cache key generation.
    
    **Hashing Limitations:**
    
    This function uses `json.dumps(default=str)` to serialize data, which
    converts non-serializable types to their string representation. This can
    cause false cache hits for complex objects that have similar string
    representations but are semantically different. For example, two different
    class instances with the same `__str__` output will hash to the same value.
    
    This limitation is acceptable for most use cases, but users should be aware
    that caching may be unsafe when:
    - Data contains custom objects with identical string representations
    - Data contains objects where identity matters more than value
    - Data contains complex nested structures that serialize identically
    
    Args:
        data: The data to hash. Can be any serializable type.
        exclude_keys: Optional set of keys to exclude if data is a dict.
    
    Returns:
        Hexadecimal hash string.
    """
    # If data is a dict and we have keys to exclude, filter them
    if isinstance(data, dict) and exclude_keys:
        data = {k: v for k, v in data.items() if k not in exclude_keys}
    
    # Serialize to JSON string for hashing
    # Handle non-serializable types by converting to string
    try:
        data_str = json.dumps(data, sort_keys=True, default=str)
    except (TypeError, ValueError):
        # Fallback: use pickle for complex objects
        data_bytes = pickle.dumps(data)
        data_str = data_bytes.hex()
    
    # Create hash
    hash_obj = hashlib.sha256(
        data_str.encode() if isinstance(data_str, str) else data_str
    )
    return hash_obj.hexdigest()


def hash_arguments(args: tuple, kwargs: dict) -> str:
    """
    Create a hash of function arguments for cache key generation.
    
    Excludes cache-related parameters (use_cache, cache_path) from the hash.
    
    Args:
        args: Positional arguments.
        kwargs: Keyword arguments (cache-related params will be filtered out).
    
    Returns:
        Hexadecimal hash string.
    """
    # Filter out cache-related parameters
    cache_params = {"use_cache", "cache_path"}
    filtered_kwargs = {k: v for k, v in kwargs.items() if k not in cache_params}
    
    # Convert args and filtered kwargs to a serializable format
    # Sort kwargs for consistent hashing
    sorted_kwargs = sorted(filtered_kwargs.items()) if filtered_kwargs else []
    
    # Create a dictionary representation
    arg_dict = {
        "args": args,
        "kwargs": sorted_kwargs,
    }
    
    return hash_data(arg_dict)

