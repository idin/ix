"""
Disk-based caching utilities.
"""

import os
import pickle
from pathlib import Path
from typing import Any, Optional

from .cache_path import _CACHE_MISS
from ..time import current_timestamp


def get_from_disk_cache(
    cache_file_path: Path,
    expire_seconds: Optional[int] = None,
) -> Any:
    """
    Get a value from disk cache.
    
    Args:
        cache_file_path: Path to the cache file.
        expire_seconds: Optional expiration time in seconds.
    
    Returns:
        Cached value if found and not expired, _CACHE_MISS sentinel otherwise.
        This allows distinguishing between "cache miss" and "cached None value".
    """
    if not cache_file_path.exists():
        return _CACHE_MISS
    
    # Check expiration using file mtime first (fast check)
    if expire_seconds is not None:
        file_age = os.path.getmtime(cache_file_path)
        current_time = current_timestamp()
        if (current_time - file_age) >= expire_seconds:
            return _CACHE_MISS
    
    try:
        with open(cache_file_path, "rb") as f:
            cached_data = pickle.load(f)
            
            # Check expiration from stored timestamp if available (more accurate)
            if expire_seconds is not None and "timestamp" in cached_data:
                cache_time = cached_data.get("timestamp", 0)
                if (current_timestamp() - cache_time) >= expire_seconds:
                    return _CACHE_MISS
            
            return cached_data.get("result")
    except (pickle.UnpicklingError, EOFError, FileNotFoundError, KeyError):
        # Cache file corrupted or missing data
        return _CACHE_MISS


def set_to_disk_cache(
    cache_file_path: Path,
    value: Any,
    expire_seconds: Optional[int] = None,
    raise_on_error: bool = False,
) -> None:
    """
    Store a value to disk cache.
    
    Args:
        cache_file_path: Path to the cache file.
        value: The value to cache.
        expire_seconds: Optional expiration time in seconds (stored for later checks).
        raise_on_error: If True, raise exceptions on write errors. Default: False.
    """
    try:
        # Ensure parent directory exists
        cache_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Store with timestamp for expiration checking
        cache_data = {
            "result": value,
            "timestamp": current_timestamp(),
        }
        
        with open(cache_file_path, "wb") as f:
            pickle.dump(cache_data, f)
    except Exception as e:
        if raise_on_error:
            raise
        # Silently fail - caching is optional

