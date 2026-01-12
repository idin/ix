"""
Main persist decorator implementation.
"""

import inspect
import os
import pickle
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union

from .cache_path import (
    DEFAULT_CACHE_PATH,
    _CACHE_MISS,
    get_cache_path,
    resolve_cache_file_path_for_function,
)
from .hashing import hash_arguments
from .disk_cache import get_from_disk_cache, set_to_disk_cache
from .memory_cache import get_from_memory_cache, set_to_memory_cache
from ..time import current_timestamp
from ..file_system import move_to_trash


def persist(
    memory: bool = False,
    expire_seconds: Optional[int] = None,
    max_entries: Optional[int] = None,
    raise_on_cache_write_error: bool = False,
) -> Callable:
    """
    Decorator to cache/persist function results.
    
    Caches function results based on argument hashing. By default, caches to disk.
    Can also cache in memory for faster access.
    
    The cache path is controlled globally via set_cache_path(). If not set,
    defaults to ".cache/ix" in current working directory.
    
    **Thread Safety:**
    
    This decorator is NOT thread-safe for concurrent writers. Multiple threads
    writing to the same cache simultaneously may result in race conditions or
    corrupted cache files. Reading from cache is generally safe, but concurrent
    writes should be avoided.
    
    Args:
        memory: If True, cache in memory instead of on disk. Default: False.
        expire_seconds: Optional expiration time in seconds. Cached results older
                       than this will be ignored. Default: None (no expiration).
        max_entries: Optional maximum number of entries in memory cache. When
                    exceeded, oldest entries are evicted. Recently written entries
                    are moved to the end, so eviction favours least recently
                    written entries. Only applies when memory=True.
                    Default: None (unbounded).
        raise_on_cache_write_error: If True, raise exceptions when disk cache
                                   writes fail instead of silently continuing.
                                   Default: False.
    
    Returns:
        Decorator function.
    
    Example:
        ```python
        # Set global cache path (e.g., in tests)
        set_cache_path(".cache/test")
        
        @persist()
        def expensive_function(x, y):
            # ... expensive computation ...
            return result
        
        @persist(memory=True, max_entries=100)
        def fast_function(x):
            # ... cached in memory only, max 100 entries ...
            return result
        ```
    """
    # In-memory cache storage
    # Use dict to track access order for eviction (dicts are ordered in Python 3.7+)
    # Recently written entries are moved to the end, so oldest entries are evicted
    _memory_cache: Dict[str, Dict[str, Any]] = {}
    
    def decorator(func: Callable) -> Callable:
        # Determine default cache base path
        # Global cache path takes precedence, otherwise use default
        if memory:
            default_cache_path = None  # Memory-only caching
        else:
            global_cache_path = get_cache_path()
            default_cache_path = global_cache_path if global_cache_path is not None else DEFAULT_CACHE_PATH
        
        # Get function signature to add cache_path parameter
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        
        # Add cache_path and use_cache parameters if not already present
        has_cache_path = any(p.name == "cache_path" for p in params)
        has_use_cache = any(p.name == "use_cache" for p in params)
        
        if not has_cache_path and not memory:
            # Add cache_path parameter with default from decorator
            cache_path_param = inspect.Parameter(
                "cache_path",
                inspect.Parameter.KEYWORD_ONLY,
                default=default_cache_path,
                annotation=Optional[Union[str, Path]]
            )
            params.append(cache_path_param)
        
        if not has_use_cache:
            # Add use_cache parameter
            use_cache_param = inspect.Parameter(
                "use_cache",
                inspect.Parameter.KEYWORD_ONLY,
                default=True,
                annotation=bool
            )
            params.append(use_cache_param)
        
        sig = sig.replace(parameters=params)
        
        def _get_cache_info(*args, **kwargs):
            """Helper to get cache path and hash for given arguments."""
            # Extract cache_path from kwargs if present (only for disk caching)
            kwargs_copy = kwargs.copy()
            cache_path_override = kwargs_copy.pop("cache_path", None)
            use_cache_flag = kwargs_copy.pop("use_cache", True)
            
            # Generate cache key from arguments (excluding cache-related params)
            arg_hash = hash_arguments(args, kwargs_copy)
            cache_key = f"{func.__name__}:{arg_hash}"
            
            # Determine runtime default cache path (check global at runtime, not decoration time)
            # The cache_path_override (if provided) is passed through to resolve_cache_file_path_for_function
            # Here we determine what the default should be if no override is provided
            if memory:
                runtime_default_cache_path = None
            else:
                # Check global cache path at runtime (may have changed since decoration)
                global_cache_path = get_cache_path()
                runtime_default_cache_path = global_cache_path if global_cache_path is not None else default_cache_path
            
            # Resolve final cache file path using centralized helper
            cache_file_path = resolve_cache_file_path_for_function(
                function_name=func.__name__,
                arg_hash=arg_hash,
                cache_path_override=cache_path_override,  # Pass through if provided
                default_cache_path=runtime_default_cache_path,
                memory=memory,
            )
            
            return cache_file_path, arg_hash, cache_key, use_cache_flag
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get cache info
            cache_file_path, arg_hash, cache_key, use_cache_flag = _get_cache_info(*args, **kwargs)
            
            # If use_cache is False, skip cache entirely
            if not use_cache_flag:
                return func(*args, **{k: v for k, v in kwargs.items() if k not in ["cache_path", "use_cache"]})
            
            # Try to load from cache
            cached_result = _CACHE_MISS
            
            if memory:
                cached_result = get_from_memory_cache(
                    memory_cache=_memory_cache,
                    cache_key=cache_key,
                    expire_seconds=expire_seconds,
                )
            else:
                if cache_file_path is not None:
                    cached_result = get_from_disk_cache(
                        cache_file_path=cache_file_path,
                        expire_seconds=expire_seconds,
                    )
            
            # Return cached result if found
            if cached_result is not _CACHE_MISS:
                return cached_result
            
            # Execute function (remove cache-related kwargs)
            func_kwargs = {k: v for k, v in kwargs.items() if k not in ["cache_path", "use_cache"]}
            result = func(*args, **func_kwargs)
            
            # Store result in cache
            if memory:
                set_to_memory_cache(
                    memory_cache=_memory_cache,
                    cache_key=cache_key,
                    value=result,
                    expire_seconds=expire_seconds,
                    max_entries=max_entries,
                )
            else:
                if cache_file_path is not None:
                    set_to_disk_cache(
                        cache_file_path=cache_file_path,
                        value=result,
                        expire_seconds=expire_seconds,
                        raise_on_error=raise_on_cache_write_error,
                    )
            
            return result
        
        def delete(*args, **kwargs):
            """
            Delete cached value for the given arguments.
            
            Has the same signature as the original function.
            Cache-related parameters (cache_path, use_cache) are ignored.
            Files are moved to Trash instead of being permanently deleted.
            """
            # Remove cache-related parameters before getting cache info
            kwargs_for_delete = {k: v for k, v in kwargs.items() if k not in ["cache_path", "use_cache"]}
            cache_file_path, arg_hash, cache_key, _ = _get_cache_info(*args, **kwargs_for_delete)
            
            if memory:
                # Delete from memory cache
                if cache_key in _memory_cache:
                    del _memory_cache[cache_key]
            else:
                # Delete from disk cache - move to Trash
                if cache_file_path is not None and cache_file_path.exists():
                    move_to_trash(cache_file_path)
        
        def exists(*args, **kwargs) -> bool:
            """
            Check if a cached value exists for the given arguments.
            
            Has the same signature as the original function.
            Cache-related parameters (cache_path, use_cache) are ignored.
            
            Returns:
                True if cached value exists, False otherwise.
            """
            # Remove cache-related parameters before getting cache info
            kwargs_for_exists = {k: v for k, v in kwargs.items() if k not in ["cache_path", "use_cache"]}
            cache_file_path, arg_hash, cache_key, _ = _get_cache_info(*args, **kwargs_for_exists)
            
            if memory:
                # Check in-memory cache
                if cache_key not in _memory_cache:
                    return False
                
                cached_data = _memory_cache[cache_key]
                
                # Check expiration if set
                if expire_seconds is not None:
                    cache_time = cached_data.get("timestamp", 0)
                    if (current_timestamp() - cache_time) >= expire_seconds:
                        return False
                
                return True
            else:
                # Check disk cache
                if cache_file_path is None or not cache_file_path.exists():
                    return False
                
                # Check expiration if set
                # Expiration checking precedence: file mtime first, then stored timestamp
                if expire_seconds is not None:
                    file_age = os.path.getmtime(cache_file_path)
                    current_time = current_timestamp()
                    if (current_time - file_age) >= expire_seconds:
                        return False
                    
                    # Also check timestamp in file if available (takes precedence)
                    try:
                        with open(cache_file_path, "rb") as f:
                            cached_data = pickle.load(f)
                            if "timestamp" in cached_data:
                                cache_time = cached_data.get("timestamp", 0)
                                if (current_timestamp() - cache_time) >= expire_seconds:
                                    return False
                    except (pickle.UnpicklingError, EOFError, FileNotFoundError, KeyError):
                        # Cache file corrupted or missing timestamp
                        return False
                
                return True
        
        def clear_all(cache_path_override: Optional[Union[str, Path]] = None) -> None:
            """
            Clear all cached values for this function.
            
            Deletes all cache entries regardless of arguments. Works for both
            disk and memory caches. Files are moved to Trash instead of
            being permanently deleted.
            
            Args:
                cache_path_override: Optional cache path override. If provided,
                                   clears cache from this path instead of the
                                   default cache path. Only applies to disk cache.
            """
            if memory:
                # Clear all entries for this function from memory cache
                # Find all cache keys that start with function name
                keys_to_delete = [
                    key for key in _memory_cache.keys()
                    if key.startswith(f"{func.__name__}:")
                ]
                for key in keys_to_delete:
                    del _memory_cache[key]
            else:
                # Clear all cache files for this function from disk
                # Determine cache path
                if cache_path_override is not None:
                    cache_path_str = str(cache_path_override)
                else:
                    global_cache_path = get_cache_path()
                    cache_path_str = str(global_cache_path) if global_cache_path is not None else str(default_cache_path)
                
                if cache_path_str is None:
                    return
                
                # Get function's cache directory
                cache_path_obj = Path(cache_path_str)
                if cache_path_obj.name != func.__name__:
                    function_cache_dir = cache_path_obj / func.__name__
                else:
                    function_cache_dir = cache_path_obj
                
                # Move entire cache directory to Trash
                if function_cache_dir.exists() and function_cache_dir.is_dir():
                    move_to_trash(function_cache_dir)
        
        # Attach delete, exists, and clear_all methods to wrapper
        wrapper.delete = delete
        wrapper.exists = exists
        wrapper.clear_all = clear_all
        
        # Update function signature to include cache_path and use_cache parameters
        wrapper.__signature__ = sig
        
        return wrapper
    
    return decorator

