"""
Tests for persist decorator disk caching functionality.
"""

from pathlib import Path
import shutil
from ixutils import persist, set_cache_path, get_cache_path


def test_disk_cache_basic():
    """Test basic disk caching functionality."""
    cache_dir = Path(".cache/ix_test/persist")
    
    # Clean up any existing cache
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    
    # Save original global cache path
    original_cache_path = get_cache_path()
    
    try:
        # Set global cache path
        set_cache_path(cache_dir)
        
        call_count = {"count": 0}
        
        @persist()
        def test_function(x: int, y: int) -> int:
            call_count["count"] += 1
            return x + y
        
        # First call - should execute function
        result1 = test_function(1, 2)
        assert result1 == 3
        assert call_count["count"] == 1
        
        # Second call with same args - should use cache
        result2 = test_function(1, 2)
        assert result2 == 3
        assert call_count["count"] == 1  # Should not increment
        
        # Different args - should execute function
        result3 = test_function(2, 3)
        assert result3 == 5
        assert call_count["count"] == 2
    finally:
        # Reset global cache path
        set_cache_path(original_cache_path)


def test_disk_cache_with_kwargs():
    """Test disk caching with keyword arguments."""
    cache_dir = Path(".cache/ix_test/persist_kwargs")
    
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    
    # Save original global cache path
    original_cache_path = get_cache_path()
    
    try:
        # Set global cache path
        set_cache_path(cache_dir)
        
        call_count = {"count": 0}
        
        @persist()
        def test_function(x: int, y: int = 10) -> int:
            call_count["count"] += 1
            return x + y
        
        # First call
        result1 = test_function(5, y=10)
        assert result1 == 15
        assert call_count["count"] == 1
        
        # Same call - should use cache
        result2 = test_function(5, y=10)
        assert result2 == 15
        assert call_count["count"] == 1
        
        # Different kwargs - should execute
        result3 = test_function(5, y=20)
        assert result3 == 25
        assert call_count["count"] == 2
    finally:
        # Reset global cache path
        set_cache_path(original_cache_path)

