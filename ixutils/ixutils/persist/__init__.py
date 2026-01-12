"""
Flexible caching/persistence decorator for function results.

Supports both in-memory and disk-based caching with automatic argument hashing.
"""

from .persist import persist
from .cache_path import (
    set_cache_path,
    get_cache_path,
    resolve_cache_file_path,
    DEFAULT_CACHE_PATH,
    _CACHE_MISS,
)
from .hashing import hash_data, hash_arguments
from .disk_cache import get_from_disk_cache, set_to_disk_cache
from .memory_cache import get_from_memory_cache, set_to_memory_cache

__all__ = [
    "persist",
    "set_cache_path",
    "get_cache_path",
    "resolve_cache_file_path",
    "hash_data",
    "hash_arguments",
    "get_from_disk_cache",
    "set_to_disk_cache",
    "get_from_memory_cache",
    "set_to_memory_cache",
    "DEFAULT_CACHE_PATH",
    "_CACHE_MISS",
]

