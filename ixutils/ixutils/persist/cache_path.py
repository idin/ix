"""
Cache path management utilities.
"""

from pathlib import Path
from typing import Optional, Union

DEFAULT_CACHE_PATH = ".cache/ix"

# Global cache path override (can be set via set_cache_path)
_global_cache_path: Optional[Union[str, Path]] = None

# Sentinel object to distinguish cache miss from cached None
_CACHE_MISS = object()


def set_cache_path(path: Optional[Union[str, Path]]) -> None:
    """
    Set the global cache path for all persist decorators.
    
    This affects all @persist() decorators that don't have an explicit
    cache_path parameter. Setting to None resets to default.
    
    Args:
        path: Path to use as base cache directory, or None to reset to default.
    """
    global _global_cache_path
    _global_cache_path = path


def get_cache_path() -> Optional[Union[str, Path]]:
    """
    Get the current global cache path.
    
    Returns:
        Current cache path, or None if using default.
    """
    return _global_cache_path


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


def resolve_cache_file_path_for_function(
    function_name: str,
    arg_hash: str,
    cache_path_override: Optional[Union[str, Path]],
    default_cache_path: Optional[Union[str, Path]],
    memory: bool,
) -> Optional[Path]:
    """
    Resolve cache file path for a function (wrapper around resolve_cache_file_path).
    
    Args:
        function_name: Name of the function being cached.
        arg_hash: Hash of function arguments.
        cache_path_override: Optional cache path override.
        default_cache_path: Default cache path from global setting.
        memory: Whether this is memory-only caching.
    
    Returns:
        Path to cache file, or None if memory-only or no path available.
    """
    return resolve_cache_file_path(
        cache_key=function_name,
        arg_hash=arg_hash,
        cache_path_override=cache_path_override,
        default_cache_path=default_cache_path,
        memory=memory,
    )

