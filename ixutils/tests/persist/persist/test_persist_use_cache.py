"""
Tests for persist decorator use_cache flag.
"""

from pathlib import Path
import shutil
from ixutils import persist, set_cache_path, get_cache_path


def test_use_cache_flag_disables_caching():
    """Test that use_cache=False disables caching for a specific call."""
    cache_dir = Path(".cache/ix_test/use_cache")
    
    # Clean up
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    
    # Save original
    original_cache_path = get_cache_path()
    
    try:
        # Set cache path
        set_cache_path(cache_dir)
        
        call_count = {"count": 0}
        
        @persist()
        def test_function(x: int) -> int:
            call_count["count"] += 1
            return x * 10
        
        # First call - should execute and cache
        result1 = test_function(5)
        assert result1 == 50
        assert call_count["count"] == 1
        
        # Second call - should use cache
        result2 = test_function(5)
        assert result2 == 50
        assert call_count["count"] == 1  # Still 1, used cache
        
        # Third call with use_cache=False - should execute again
        result3 = test_function(5, use_cache=False)
        assert result3 == 50
        assert call_count["count"] == 2  # Now 2, cache was bypassed
        
        # Fourth call - should use cache again
        result4 = test_function(5)
        assert result4 == 50
        assert call_count["count"] == 2  # Still 2, used cache
        
        # Clean up
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
    finally:
        set_cache_path(original_cache_path)


def test_use_cache_flag_does_not_affect_cache_key():
    """Test that use_cache parameter is not included in cache key."""
    cache_dir = Path(".cache/ix_test/use_cache_key")
    
    # Clean up
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    
    # Save original
    original_cache_path = get_cache_path()
    
    try:
        # Set cache path
        set_cache_path(cache_dir)
        
        call_count = {"count": 0}
        
        @persist()
        def test_function(x: int) -> int:
            call_count["count"] += 1
            return x * 15
        
        # Call with use_cache=True
        result1 = test_function(5, use_cache=True)
        assert result1 == 75
        assert call_count["count"] == 1
        
        # Call with use_cache=False - should bypass cache but same key
        result2 = test_function(5, use_cache=False)
        assert result2 == 75
        assert call_count["count"] == 2  # Executed again
        
        # Call again with use_cache=True - should use cache from first call
        result3 = test_function(5, use_cache=True)
        assert result3 == 75
        assert call_count["count"] == 2  # Used cache, didn't increment
        
        # Clean up
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
    finally:
        set_cache_path(original_cache_path)


def test_cache_path_parameter_not_in_cache_key():
    """Test that cache_path parameter is not included in cache key."""
    cache_dir1 = Path(".cache/ix_test/cache_path_key1")
    cache_dir2 = Path(".cache/ix_test/cache_path_key2")
    
    # Clean up
    for cache in [cache_dir1, cache_dir2]:
        if cache.exists():
            shutil.rmtree(cache)
    
    # Save original
    original_cache_path = get_cache_path()
    
    try:
        call_count = {"count": 0}
        
        @persist()
        def test_function(x: int) -> int:
            call_count["count"] += 1
            return x * 35
        
        # Call with first cache path
        result1 = test_function(5, cache_path=cache_dir1)
        assert result1 == 175
        assert call_count["count"] == 1
        
        # Call with second cache path - should use cache (same key, different location)
        # But since cache_path affects where cache is stored, it won't find it
        # So it will execute again, but the result should be the same
        result2 = test_function(5, cache_path=cache_dir2)
        assert result2 == 175
        # This will execute again because cache is in different location
        # But the key is the same, so if we use the same cache_path, it should work
        
        # Call again with first cache path - should use cache
        result3 = test_function(5, cache_path=cache_dir1)
        assert result3 == 175
        assert call_count["count"] == 2  # Only executed twice (once per cache location)
        
        # Clean up
        for cache in [cache_dir1, cache_dir2]:
            if cache.exists():
                shutil.rmtree(cache)
    finally:
        set_cache_path(original_cache_path)

