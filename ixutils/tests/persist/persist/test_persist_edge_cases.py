"""
Tests for persist decorator edge cases.
"""

from pathlib import Path
import shutil
from ixutils import delay
from ixutils import persist, set_cache_path, get_cache_path


def test_cache_with_none_result():
    """Test that caching works correctly when function returns None."""
    cache_dir = Path(".cache/ix_test/persist_none")
    
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    
    # Save original global cache path
    original_cache_path = get_cache_path()
    
    try:
        # Set global cache path
        set_cache_path(cache_dir)
        
        call_count = {"count": 0}
        
        @persist()
        def test_function(x: int) -> None:
            call_count["count"] += 1
            return None
        
        # First call
        result1 = test_function(1)
        assert result1 is None
        assert call_count["count"] == 1
        
        # Second call - should use cache (None is a valid cached result)
        result2 = test_function(1)
        assert result2 is None
        assert call_count["count"] == 1
    finally:
        # Reset global cache path
        set_cache_path(original_cache_path)


def test_cache_expiration():
    """Test cache expiration functionality."""
    cache_dir = Path(".cache/ix_test/persist_expire")
    
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    
    # Save original global cache path
    original_cache_path = get_cache_path()
    
    try:
        # Set global cache path
        set_cache_path(cache_dir)
        
        call_count = {"count": 0}
        
        @persist(expire_seconds=1)
        def test_function(x: int) -> int:
            call_count["count"] += 1
            return x * 2
        
        # First call
        result1 = test_function(5)
        assert result1 == 10
        assert call_count["count"] == 1
        
        # Immediate second call - should use cache
        result2 = test_function(5)
        assert result2 == 10
        assert call_count["count"] == 1
        
        # Wait for expiration
        delay(1.1)
        
        # Call after expiration - should execute function again
        result3 = test_function(5)
        assert result3 == 10
        assert call_count["count"] == 2
    finally:
        # Reset global cache path
        set_cache_path(original_cache_path)


def test_cache_with_complex_objects():
    """Test caching with complex objects (lists, dicts, etc.)."""
    cache_dir = Path(".cache/ix_test/persist_complex")
    
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    
    # Save original global cache path
    original_cache_path = get_cache_path()
    
    try:
        # Set global cache path
        set_cache_path(cache_dir)
        
        call_count = {"count": 0}
        
        @persist()
        def test_function(data: dict) -> dict:
            call_count["count"] += 1
            return {"processed": data}
        
        # First call
        input_data = {"key": "value", "list": [1, 2, 3]}
        result1 = test_function(input_data)
        assert result1 == {"processed": input_data}
        assert call_count["count"] == 1
        
        # Second call with same data - should use cache
        result2 = test_function(input_data)
        assert result2 == {"processed": input_data}
        assert call_count["count"] == 1
    finally:
        # Reset global cache path
        set_cache_path(original_cache_path)

