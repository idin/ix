"""
Tests for persist decorator.
"""

import os
import time
import pytest
from pathlib import Path
from ixmachina.utils.persist import persist


def test_disk_cache_basic():
    """Test basic disk caching functionality."""
    cache_dir = Path(".cache/test_persist")
    
    # Clean up any existing cache
    if cache_dir.exists():
        import shutil
        shutil.rmtree(cache_dir)
    
    call_count = {"count": 0}
    
    @persist(path=cache_dir)
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


def test_disk_cache_with_kwargs():
    """Test disk caching with keyword arguments."""
    cache_dir = Path(".cache/test_persist_kwargs")
    
    if cache_dir.exists():
        import shutil
        shutil.rmtree(cache_dir)
    
    call_count = {"count": 0}
    
    @persist(path=cache_dir)
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


def test_memory_cache():
    """Test in-memory caching."""
    call_count = {"count": 0}
    
    @persist(memory=True)
    def test_function(x: int) -> int:
        call_count["count"] += 1
        return x * 2
    
    # First call
    result1 = test_function(5)
    assert result1 == 10
    assert call_count["count"] == 1
    
    # Second call - should use memory cache
    result2 = test_function(5)
    assert result2 == 10
    assert call_count["count"] == 1


def test_cache_with_none_result():
    """Test that caching works correctly when function returns None."""
    cache_dir = Path(".cache/test_persist_none")
    
    if cache_dir.exists():
        import shutil
        shutil.rmtree(cache_dir)
    
    call_count = {"count": 0}
    
    @persist(path=cache_dir)
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


def test_cache_expiration():
    """Test cache expiration functionality."""
    cache_dir = Path(".cache/test_persist_expire")
    
    if cache_dir.exists():
        import shutil
        shutil.rmtree(cache_dir)
    
    call_count = {"count": 0}
    
    @persist(path=cache_dir, expire_seconds=1)
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
    time.sleep(1.1)
    
    # Call after expiration - should execute function again
    result3 = test_function(5)
    assert result3 == 10
    assert call_count["count"] == 2


def test_cache_with_complex_objects():
    """Test caching with complex objects (lists, dicts, etc.)."""
    cache_dir = Path(".cache/test_persist_complex")
    
    if cache_dir.exists():
        import shutil
        shutil.rmtree(cache_dir)
    
    call_count = {"count": 0}
    
    @persist(path=cache_dir)
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


def test_default_cache_path():
    """Test that default cache path is used when path is not specified."""
    default_cache = Path(".cache/ix") / "test_function"
    
    # Clean up if exists
    if default_cache.parent.exists():
        import shutil
        shutil.rmtree(default_cache.parent)
    
    call_count = {"count": 0}
    
    @persist()  # No path specified, should use default
    def test_function(x: int) -> int:
        call_count["count"] += 1
        return x * 2
    
    # First call
    result1 = test_function(5)
    assert result1 == 10
    assert call_count["count"] == 1
    
    # Verify cache file was created in default location (with function name appended)
    assert default_cache.exists()
    
    # Second call - should use cache
    result2 = test_function(5)
    assert result2 == 10
    assert call_count["count"] == 1
    
    # Clean up
    if default_cache.parent.exists():
        import shutil
        shutil.rmtree(default_cache.parent)


def test_persist_preserves_docstring():
    """Test that persist decorator preserves function docstring."""
    @persist()
    def documented_function(x: int) -> int:
        """This is a test function with a docstring.
        
        Args:
            x: An integer input.
        
        Returns:
            The input multiplied by 2.
        """
        return x * 2
    
    # Check that docstring is preserved
    assert documented_function.__doc__ is not None
    assert "This is a test function with a docstring" in documented_function.__doc__
    assert "Args:" in documented_function.__doc__
    assert "Returns:" in documented_function.__doc__
    
    # Also test with memory cache
    @persist(memory=True)
    def memory_documented_function(x: int) -> int:
        """Memory cached function with docstring."""
        return x * 3
    
    assert memory_documented_function.__doc__ is not None
    assert "Memory cached function with docstring" in memory_documented_function.__doc__

