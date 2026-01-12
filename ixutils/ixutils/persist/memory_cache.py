"""
In-memory caching utilities.
"""

from typing import Any, Dict, Optional

from .cache_path import _CACHE_MISS
from ..time import current_timestamp


def get_from_memory_cache(
    memory_cache: Dict[str, Dict[str, Any]],
    cache_key: str,
    expire_seconds: Optional[int] = None,
) -> Any:
    """
    Get a value from memory cache.
    
    Args:
        memory_cache: Dictionary storing cache entries.
        cache_key: Key to look up in cache.
        expire_seconds: Optional expiration time in seconds.
    
    Returns:
        Cached value if found and not expired, _CACHE_MISS sentinel otherwise.
    """
    if cache_key not in memory_cache:
        return _CACHE_MISS
    
    cache_data = memory_cache[cache_key]
    
    # Check expiration
    if expire_seconds is not None:
        cache_time = cache_data.get("timestamp", 0)
        if (current_timestamp() - cache_time) >= expire_seconds:
            # Remove expired entry
            del memory_cache[cache_key]
            return _CACHE_MISS
    
    return cache_data.get("result")


def set_to_memory_cache(
    memory_cache: Dict[str, Dict[str, Any]],
    cache_key: str,
    value: Any,
    expire_seconds: Optional[int] = None,
    max_entries: Optional[int] = None,
) -> None:
    """
    Store a value in memory cache.
    
    Args:
        memory_cache: Dictionary storing cache entries.
        cache_key: Key to store value under.
        value: The value to cache.
        expire_seconds: Optional expiration time in seconds (stored for later checks).
        max_entries: Optional maximum number of entries. When exceeded, oldest
                    entries are evicted. Default: None (unbounded).
    """
    # Evict oldest entries if max_entries exceeded
    if max_entries is not None and len(memory_cache) >= max_entries:
        # Remove oldest entry (first in dict, since dicts are ordered)
        if memory_cache:
            oldest_key = next(iter(memory_cache))
            del memory_cache[oldest_key]
    
    # Store with timestamp for expiration checking
    cache_data = {
        "result": value,
        "timestamp": current_timestamp(),
    }
    
    # Update or add the entry
    memory_cache[cache_key] = cache_data

