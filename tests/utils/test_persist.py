"""
Tests for persist decorator.
"""

import os
import time
import pytest
from pathlib import Path
from ixmachina.utils.persist import persist, set_cache_path, get_cache_path
from ixmachina.tools.file_system.delete import delete
from ixmachina.tools.file_system.path_utils import path_exists


def test_disk_cache_basic():
    """Test basic disk caching functionality."""
    cache_dir = Path(".cache/ix_test/persist")
    
    # Clean up any existing cache
    if path_exists(str(cache_dir)):
        delete(paths=str(cache_dir))
    
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
    
    if path_exists(str(cache_dir)):
        delete(paths=str(cache_dir))
    
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
    cache_dir = Path(".cache/ix_test/persist_none")
    
    if path_exists(str(cache_dir)):
        delete(paths=str(cache_dir))
    
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
    
    if path_exists(str(cache_dir)):
        delete(paths=str(cache_dir))
    
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
        time.sleep(1.1)
        
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
    
    if path_exists(str(cache_dir)):
        delete(paths=str(cache_dir))
    
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


def test_default_cache_path():
    """Test that default cache path is used when path is not specified."""
    default_cache = Path(".cache/ix") / "test_function"
    
    # Clean up if exists (only the test-specific directory, not the entire parent)
    if path_exists(str(default_cache)):
        delete(paths=str(default_cache))
    
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
    if path_exists(str(default_cache.parent)):
        delete(paths=str(default_cache.parent))


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


def test_global_cache_path_set_and_use():
    """Test that setting a global cache path works and functions use it."""
    global_cache = Path(".cache/ix_test/global")
    function_cache = global_cache / "test_function"
    
    # Clean up
    if path_exists(str(global_cache)):
        delete(paths=str(global_cache))
    
    # Save original global cache path
    original_cache_path = get_cache_path()
    
    try:
        # Set global cache path
        set_cache_path(global_cache)
        assert get_cache_path() == global_cache
        
        call_count = {"count": 0}
        
        @persist()  # No path specified, should use global cache path
        def test_function(x: int) -> int:
            call_count["count"] += 1
            return x * 3
        
        # First call - should execute function
        result1 = test_function(5)
        assert result1 == 15
        assert call_count["count"] == 1
        
        # Verify cache file was created in global cache location
        assert function_cache.exists()
        
        # Second call - should use cache
        result2 = test_function(5)
        assert result2 == 15
        assert call_count["count"] == 1
        
        # Clean up
        if path_exists(str(global_cache)):
            delete(paths=str(global_cache))
    finally:
        # Reset global cache path
        set_cache_path(original_cache_path)




def test_global_cache_path_reset_to_default():
    """Test that resetting global cache path to None uses default path."""
    global_cache = Path(".cache/ix_test/global_reset")
    default_cache = Path(".cache/ix") / "test_function2"
    
    # Clean up
    for cache in [global_cache, default_cache.parent]:
        if path_exists(str(cache)):
            delete(paths=str(cache))
    
    # Save original global cache path
    original_cache_path = get_cache_path()
    
    try:
        # Set global cache path
        set_cache_path(global_cache)
        assert get_cache_path() == global_cache
        
        call_count = {"count": 0}
        
        @persist()  # No path specified
        def test_function(x: int) -> int:
            call_count["count"] += 1
            return x * 5
        
        # First call with global cache set
        result1 = test_function(5)
        assert result1 == 25
        assert call_count["count"] == 1
        
        # Verify cache was created in global location
        assert (global_cache / "test_function").exists()
        
        # Reset global cache path to None
        set_cache_path(None)
        assert get_cache_path() is None
        
        # Create a new function - should use default path
        call_count2 = {"count": 0}
        
        @persist()  # No path specified, should use default now
        def test_function2(x: int) -> int:
            call_count2["count"] += 1
            return x * 6
        
        # First call - should execute function
        result2 = test_function2(5)
        assert result2 == 30
        assert call_count2["count"] == 1
        
        # Verify cache was created in default location
        assert default_cache.exists()
        
        # Second call - should use cache
        result3 = test_function2(5)
        assert result3 == 30
        assert call_count2["count"] == 1
        
        # Clean up
        for cache in [global_cache, default_cache.parent]:
            if path_exists(str(cache)):
                delete(paths=str(cache))
    finally:
        # Reset global cache path
        set_cache_path(original_cache_path)


def test_global_cache_path_with_cache_path_parameter():
    """Test that cache_path parameter still overrides global cache path."""
    global_cache = Path(".cache/ix_test/global_param")
    override_cache = Path(".cache/ix_test/override_param")
    override_function_cache = override_cache / "test_function"
    
    # Clean up
    for cache in [global_cache, override_cache]:
        if path_exists(str(cache)):
            delete(paths=str(cache))
    
    # Save original global cache path
    original_cache_path = get_cache_path()
    
    try:
        # Set global cache path
        set_cache_path(global_cache)
        
        call_count = {"count": 0}
        
        @persist()  # No path specified, should use global
        def test_function(x: int) -> int:
            call_count["count"] += 1
            return x * 7
        
        # Call with cache_path parameter - should override global
        result1 = test_function(5, cache_path=override_cache)
        assert result1 == 35
        assert call_count["count"] == 1
        
        # Verify cache was created in override location, not global
        assert override_function_cache.exists()
        assert not (global_cache / "test_function").exists()
        
        # Call again with same override - should use cache
        result2 = test_function(5, cache_path=override_cache)
        assert result2 == 35
        assert call_count["count"] == 1
        
        # Clean up
        for cache in [global_cache, override_cache]:
            if path_exists(str(cache)):
                delete(paths=str(cache))
    finally:
        # Reset global cache path
        set_cache_path(original_cache_path)

