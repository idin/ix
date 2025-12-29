"""
Tests for persist decorator with cache_path parameter injection.
"""

import pytest
from pathlib import Path
from ixmachina.utils.persist import persist


def test_cache_path_parameter_injection():
    """Test that cache_path parameter is added to function signature."""
    cache_dir = ".cache/test_cache_path_param"
    
    import shutil
    cache_path = Path(cache_dir)
    if cache_path.exists():
        shutil.rmtree(cache_path)
    
    @persist(path=cache_dir)
    def test_function(x: int) -> int:
        return x * 2
    
    # Check that cache_path parameter exists in signature
    import inspect
    sig = inspect.signature(test_function)
    assert "cache_path" in sig.parameters
    assert sig.parameters["cache_path"].default == cache_dir  # Should be string, not Path
    
    # Verify that function name is appended to cache path
    result = test_function(5)
    assert result == 10
    # Cache should be at cache_dir/test_function, not just cache_dir
    assert (Path(cache_dir) / "test_function").exists()


def test_cache_path_parameter_override():
    """Test that cache_path parameter can override decorator default."""
    default_cache = ".cache/test_default"
    override_cache = ".cache/test_override"
    
    # Clean up
    import shutil
    for cache in [Path(default_cache), Path(override_cache), Path(".cache/test_override_path")]:
        if cache.exists():
            shutil.rmtree(cache)
    
    call_count = {"count": 0}
    
    @persist(path=default_cache)
    def test_function(x: int) -> int:
        call_count["count"] += 1
        return x * 2
    
    # Call with default cache path
    result1 = test_function(5)
    assert result1 == 10
    assert call_count["count"] == 1
    # Verify function name is appended
    assert (Path(default_cache) / "test_function").exists()
    
    # Call again - should use cache from default location
    result2 = test_function(5)
    assert result2 == 10
    assert call_count["count"] == 1  # Cached
    
    # Call with override cache path (as string) - should execute again (different cache)
    result3 = test_function(5, cache_path=override_cache)
    assert result3 == 10
    assert call_count["count"] == 2  # Not cached (different location)
    # Verify function name is appended to override path too
    assert (Path(override_cache) / "test_function").exists()
    
    # Call again with same override - should use cache
    result4 = test_function(5, cache_path=override_cache)
    assert result4 == 10
    assert call_count["count"] == 2  # Cached in override location
    
    # Call with override cache path (as Path) - should execute again (different cache)
    result5 = test_function(5, cache_path=Path(".cache/test_override_path"))
    assert result5 == 10
    assert call_count["count"] == 3  # Not cached (different location)
    assert (Path(".cache/test_override_path") / "test_function").exists()


def test_cache_path_parameter_with_memory_cache():
    """Test that cache_path parameter is NOT added when using memory cache."""
    @persist(memory=True)
    def test_function(x: int) -> int:
        return x * 2
    
    # Check that cache_path parameter does NOT exist for memory cache
    import inspect
    sig = inspect.signature(test_function)
    assert "cache_path" not in sig.parameters

