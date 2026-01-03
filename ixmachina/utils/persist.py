"""
Flexible caching/persistence decorator for function results.

Supports both in-memory and disk-based caching with automatic argument hashing.
"""

import hashlib
import json
import os
import pickle
import time
import inspect
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union

# Import delete as _delete to avoid naming conflict with the local delete() method
# defined in the persist decorator (line 527). The local delete() method is attached
# to the decorated function and would shadow the imported delete function.
from ..tools.file_system import delete as _delete

DEFAULT_CACHE_PATH = ".cache/ix"

# Global cache path override (can be set via set_cache_path)
_global_cache_path: Optional[Union[str, Path]] = None


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


def _hash_arguments(args: tuple, kwargs: dict) -> str:
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


def set_cache_path(path: Optional[Union[str, Path]]) -> None:
    """
    Set the global cache path for all cached functions.
    
    This allows you to override the default cache path globally, which is useful
    for tests or when you want to isolate cache directories.
    
    Args:
        path: The global cache path to use. If None, resets to default behavior.
              Individual functions can still override via their cache_path parameter.
    
    Example:
        ```python
        # Set global cache path for tests
        set_cache_path(".cache/test")
        
        # All cached functions will now use .cache/test as base
        # (unless they have their own path specified in @persist decorator)
        
        # Reset to default
        set_cache_path(None)
        ```
    """
    global _global_cache_path
    _global_cache_path = path


def get_cache_path() -> Optional[Union[str, Path]]:
    """
    Get the current global cache path.
    
    Returns:
        The current global cache path, or None if not set.
    """
    return _global_cache_path


# Sentinel object to distinguish cache miss from cached None
_CACHE_MISS = object()


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
        current_time = time.time()
        if (current_time - file_age) >= expire_seconds:
            return _CACHE_MISS
    
    try:
        with open(cache_file_path, "rb") as f:
            cached_data = pickle.load(f)
            
            # Check expiration from stored timestamp if available (more accurate)
            if expire_seconds is not None and "timestamp" in cached_data:
                cache_time = cached_data.get("timestamp", 0)
                if (time.time() - cache_time) >= expire_seconds:
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
        value: Value to cache.
        expire_seconds: Optional expiration time (used for timestamp).
        raise_on_error: If True, raise exceptions on write errors.
    """
    cache_data = {
        "result": value,
        "timestamp": time.time() if expire_seconds else None,
    }
    
    try:
        cache_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file_path, "wb") as f:
            pickle.dump(cache_data, f)
    except (IOError, OSError) as e:
        if raise_on_error:
            raise
        # Otherwise, silently continue without caching


def get_from_memory_cache(
    memory_cache: Dict[str, Dict[str, Any]],
    cache_key: str,
    expire_seconds: Optional[int] = None,
) -> Any:
    """
    Get a value from memory cache.
    
    Args:
        memory_cache: The memory cache dictionary.
        cache_key: The cache key.
        expire_seconds: Optional expiration time in seconds.
    
    Returns:
        Cached value if found and not expired, _CACHE_MISS sentinel otherwise.
        This allows distinguishing between "cache miss" and "cached None value".
    """
    if cache_key not in memory_cache:
        return _CACHE_MISS
    
    cached_data = memory_cache[cache_key]
    
    # Check expiration if set
    if expire_seconds is not None:
        cache_time = cached_data.get("timestamp", 0)
        if (time.time() - cache_time) >= expire_seconds:
            return _CACHE_MISS
    
    return cached_data.get("result")


def set_to_memory_cache(
    memory_cache: Dict[str, Dict[str, Any]],
    cache_key: str,
    value: Any,
    expire_seconds: Optional[int] = None,
    max_entries: Optional[int] = None,
) -> None:
    """
    Store a value to memory cache.
    
    Args:
        memory_cache: The memory cache dictionary.
        cache_key: The cache key.
        value: Value to cache.
        expire_seconds: Optional expiration time (used for timestamp).
        max_entries: Optional maximum number of entries. When exceeded, oldest entries are evicted.
    """
    cache_data = {
        "result": value,
        "timestamp": time.time() if expire_seconds else None,
    }
    
    # Move to end (most recently written) if key exists
    if cache_key in memory_cache:
        # Move to end by removing and re-adding (dicts are ordered in Python 3.7+)
        memory_cache[cache_key] = memory_cache.pop(cache_key)
    else:
        # New entry - evict oldest if over limit before adding
        if max_entries is not None and len(memory_cache) >= max_entries:
            # Remove oldest entry (first item in ordered dict)
            oldest_key = next(iter(memory_cache))
            memory_cache.pop(oldest_key)
    
    # Update or add the entry
    memory_cache[cache_key] = cache_data


def resolve_cache_file_path(
    cache_key: str,
    arg_hash: str,
    cache_path_override: Optional[Union[str, Path]],
    default_cache_path: Optional[Union[str, Path]],
    memory: bool,
) -> Optional[Path]:
    """
    Resolve the final cache file path for a cache entry.
    
    This centralizes all cache path resolution logic to ensure consistency
    across the codebase. Returns None for memory-only caching or when no
    cache path is available.
    
    Args:
        cache_key: Key identifying the cache entry (e.g., function name).
        arg_hash: Hash of arguments/data being cached.
        cache_path_override: Optional cache path override.
        default_cache_path: Default cache path from global setting.
        memory: Whether this is memory-only caching.
    
    Returns:
        Path to cache file, or None if memory-only or no path available.
    """
    if memory:
        return None
    
    # Use override if provided, otherwise use default
    if cache_path_override is not None:
        cache_path_str = str(cache_path_override)
    else:
        cache_path_str = str(default_cache_path) if default_cache_path is not None else None
    
    if cache_path_str is None:
        return None
    
    # Ensure cache key is in the cache path
    cache_path_obj = Path(cache_path_str)
    # Check if cache key is already at the end of the path
    if cache_path_obj.name != cache_key:
        # Append cache key if not present
        cache_dir = cache_path_obj / cache_key
    else:
        cache_dir = cache_path_obj
    
    # Lazy creation: create directory (and all parent directories) only when needed
    cache_dir.mkdir(parents=True, exist_ok=True)
    # Use first 16 chars of hash for filename (sufficient uniqueness)
    return cache_dir / f"{arg_hash[:16]}.cache"


def _resolve_cache_file_path(
    function_name: str,
    arg_hash: str,
    cache_path_override: Optional[Union[str, Path]],
    default_cache_path: Optional[Union[str, Path]],
    memory: bool,
) -> Optional[Path]:
    """
    Resolve the final cache file path for a function call.
    
    This is a wrapper around resolve_cache_file_path for backward compatibility.
    """
    return resolve_cache_file_path(
        cache_key=function_name,
        arg_hash=arg_hash,
        cache_path_override=cache_path_override,
        default_cache_path=default_cache_path,
        memory=memory,
    )


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
        elif _global_cache_path is not None:
            # Use global cache path if set
            default_cache_path = _global_cache_path
        else:
            default_cache_path = DEFAULT_CACHE_PATH
        
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
            arg_hash = _hash_arguments(args, kwargs_copy)
            cache_key = f"{func.__name__}:{arg_hash}"
            
            # Resolve final cache file path using centralized helper
            cache_file_path = _resolve_cache_file_path(
                function_name=func.__name__,
                arg_hash=arg_hash,
                cache_path_override=cache_path_override,
                default_cache_path=default_cache_path,
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
            """
            # Remove cache-related parameters before getting cache info
            kwargs_for_delete = {k: v for k, v in kwargs.items() if k not in ["cache_path", "use_cache"]}
            cache_file_path, arg_hash, cache_key, _ = _get_cache_info(*args, **kwargs_for_delete)
            
            if memory:
                # Delete from memory cache
                if cache_key in _memory_cache:
                    del _memory_cache[cache_key]
            else:
                # Delete from disk cache using recycle bin
                if cache_file_path is not None and cache_file_path.exists():
                    try:
                        _delete(paths=str(cache_file_path))
                    except (IOError, OSError):
                        pass
        
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
                    if (time.time() - cache_time) >= expire_seconds:
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
                    current_time = time.time()
                    if (current_time - file_age) >= expire_seconds:
                        return False
                    
                    # Also check timestamp in file if available (takes precedence)
                    try:
                        with open(cache_file_path, "rb") as f:
                            cached_data = pickle.load(f)
                            if "timestamp" in cached_data:
                                cache_time = cached_data.get("timestamp", 0)
                                if (time.time() - cache_time) >= expire_seconds:
                                    return False
                    except (pickle.UnpicklingError, EOFError, FileNotFoundError, KeyError):
                        # Cache file corrupted or missing timestamp
                        return False
                
                return True
        
        # Attach delete and exists methods to wrapper
        wrapper.delete = delete
        wrapper.exists = exists
        
        # Update function signature to include cache_path and use_cache parameters
        wrapper.__signature__ = sig
        
        return wrapper
    
    return decorator

