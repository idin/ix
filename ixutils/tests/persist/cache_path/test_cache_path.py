"""
Tests for persist decorator cache path management.
"""

from pathlib import Path
import shutil
from ixutils import persist, set_cache_path, get_cache_path


def test_default_cache_path():
    """Test that default cache path is used when path is not specified."""
    default_cache = Path(".cache/ix") / "test_function"
    
    # Clean up if exists (only the test-specific directory, not the entire parent)
    if default_cache.exists():
        shutil.rmtree(default_cache)
    
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
        shutil.rmtree(default_cache.parent)


def test_global_cache_path_set_and_use():
    """Test that setting a global cache path works and functions use it."""
    global_cache = Path(".cache/ix_test/global")
    function_cache = global_cache / "test_function"
    
    # Clean up
    if global_cache.exists():
        shutil.rmtree(global_cache)
    
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
        if global_cache.exists():
            shutil.rmtree(global_cache)
    finally:
        # Reset global cache path
        set_cache_path(original_cache_path)


def test_global_cache_path_reset_to_default():
    """Test that resetting global cache path to None uses default path."""
    global_cache = Path(".cache/ix_test/global_reset")
    default_cache = Path(".cache/ix") / "test_function2"
    
    # Clean up
    for cache in [global_cache, default_cache.parent]:
        if cache.exists():
            shutil.rmtree(cache)
    
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
            if cache.exists():
                shutil.rmtree(cache)
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
        if cache.exists():
            shutil.rmtree(cache)
    
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
            if cache.exists():
                shutil.rmtree(cache)
    finally:
        # Reset global cache path
        set_cache_path(original_cache_path)

