"""
Tests for persist decorator delete method.
"""

from pathlib import Path
import shutil
from ixutils import persist, set_cache_path, get_cache_path


def test_delete_method_removes_cached_value():
    """Test that delete method removes cached values."""
    cache_dir = Path(".cache/ix_test/delete")
    
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
            return x * 20
        
        # First call - should execute and cache
        result1 = test_function(5)
        assert result1 == 100
        assert call_count["count"] == 1
        
        # Second call - should use cache
        result2 = test_function(5)
        assert result2 == 100
        assert call_count["count"] == 1  # Used cache
        
        # Delete the cached value
        test_function.delete(5)
        
        # Third call - should execute again (cache was deleted)
        result3 = test_function(5)
        assert result3 == 100
        assert call_count["count"] == 2  # Executed again
        
        # Fourth call - should use cache again
        result4 = test_function(5)
        assert result4 == 100
        assert call_count["count"] == 2  # Used cache
        
        # Clean up
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
    finally:
        set_cache_path(original_cache_path)


def test_delete_method_with_different_arguments():
    """Test that delete method only deletes the specific cached value."""
    cache_dir = Path(".cache/ix_test/delete_specific")
    
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
        def test_function(x: int, y: int) -> int:
            call_count["count"] += 1
            return x + y
        
        # Cache multiple values
        result1 = test_function(1, 2)
        assert result1 == 3
        assert call_count["count"] == 1
        
        result2 = test_function(3, 4)
        assert result2 == 7
        assert call_count["count"] == 2
        
        # Both should be cached
        result3 = test_function(1, 2)
        assert result3 == 3
        assert call_count["count"] == 2  # Used cache
        
        result4 = test_function(3, 4)
        assert result4 == 7
        assert call_count["count"] == 2  # Used cache
        
        # Delete only one cached value
        test_function.delete(1, 2)
        
        # Deleted value should execute again
        result5 = test_function(1, 2)
        assert result5 == 3
        assert call_count["count"] == 3  # Executed again
        
        # Other value should still be cached
        result6 = test_function(3, 4)
        assert result6 == 7
        assert call_count["count"] == 3  # Still cached
        
        # Clean up
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
    finally:
        set_cache_path(original_cache_path)


def test_delete_method_with_kwargs():
    """Test that delete method works with keyword arguments."""
    cache_dir = Path(".cache/ix_test/delete_kwargs")
    
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
        def test_function(x: int, y: int = 10) -> int:
            call_count["count"] += 1
            return x + y
        
        # Cache with kwargs
        result1 = test_function(5, y=20)
        assert result1 == 25
        assert call_count["count"] == 1
        
        # Should use cache
        result2 = test_function(5, y=20)
        assert result2 == 25
        assert call_count["count"] == 1
        
        # Delete with same kwargs
        test_function.delete(5, y=20)
        
        # Should execute again
        result3 = test_function(5, y=20)
        assert result3 == 25
        assert call_count["count"] == 2
        
        # Clean up
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
    finally:
        set_cache_path(original_cache_path)


def test_delete_method_ignores_cache_params():
    """Test that delete method ignores cache_path and use_cache parameters."""
    cache_dir = Path(".cache/ix_test/delete_ignore")
    override_cache = Path(".cache/ix_test/delete_override")
    
    # Clean up
    for cache in [cache_dir, override_cache]:
        if cache.exists():
            shutil.rmtree(cache)
    
    # Save original
    original_cache_path = get_cache_path()
    
    try:
        # Set cache path
        set_cache_path(cache_dir)
        
        call_count = {"count": 0}
        
        @persist()
        def test_function(x: int) -> int:
            call_count["count"] += 1
            return x * 25
        
        # Cache a value
        result1 = test_function(5)
        assert result1 == 125
        assert call_count["count"] == 1
        
        # Delete with cache_path parameter - should still delete from default cache
        test_function.delete(5, cache_path=override_cache)
        
        # Should execute again (cache was deleted)
        result2 = test_function(5)
        assert result2 == 125
        assert call_count["count"] == 2
        
        # Clean up
        for cache in [cache_dir, override_cache]:
            if cache.exists():
                shutil.rmtree(cache)
    finally:
        set_cache_path(original_cache_path)


def test_delete_method_with_memory_cache():
    """Test that delete method works with memory cache."""
    # Save original
    original_cache_path = get_cache_path()
    
    try:
        call_count = {"count": 0}
        
        @persist(memory=True)
        def test_function(x: int) -> int:
            call_count["count"] += 1
            return x * 30
        
        # Cache a value
        result1 = test_function(5)
        assert result1 == 150
        assert call_count["count"] == 1
        
        # Should use cache
        result2 = test_function(5)
        assert result2 == 150
        assert call_count["count"] == 1
        
        # Delete the cached value
        test_function.delete(5)
        
        # Should execute again
        result3 = test_function(5)
        assert result3 == 150
        assert call_count["count"] == 2
    finally:
        set_cache_path(original_cache_path)

