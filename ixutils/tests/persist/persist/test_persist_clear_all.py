"""
Tests for persist decorator clear_all method.
"""

from pathlib import Path
import shutil
from ixutils import persist, set_cache_path, get_cache_path


def test_clear_all_removes_all_cached_values_for_function():
    """Test that clear_all removes all cached values for a function."""
    cache_dir = Path(".cache/ix_test/clear_all")
    
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
        
        # Cache multiple values
        result1 = test_function(5)
        assert result1 == 100
        assert call_count["count"] == 1
        
        result2 = test_function(10)
        assert result2 == 200
        assert call_count["count"] == 2
        
        result3 = test_function(15)
        assert result3 == 300
        assert call_count["count"] == 3
        
        # All should be cached now
        result4 = test_function(5)
        assert result4 == 100
        assert call_count["count"] == 3  # Used cache
        
        result5 = test_function(10)
        assert result5 == 200
        assert call_count["count"] == 3  # Used cache
        
        # Clear all cached values for this function
        test_function.clear_all()
        
        # All calls should execute again
        result6 = test_function(5)
        assert result6 == 100
        assert call_count["count"] == 4  # Executed again
        
        result7 = test_function(10)
        assert result7 == 200
        assert call_count["count"] == 5  # Executed again
        
        result8 = test_function(15)
        assert result8 == 300
        assert call_count["count"] == 6  # Executed again
        
        # Clean up
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
    finally:
        set_cache_path(original_cache_path)


def test_clear_all_only_affects_one_function():
    """Test that clear_all only clears cache for the specific function."""
    cache_dir = Path(".cache/ix_test/clear_all_specific")
    
    # Clean up
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    
    # Save original
    original_cache_path = get_cache_path()
    
    try:
        # Set cache path
        set_cache_path(cache_dir)
        
        call_count1 = {"count": 0}
        call_count2 = {"count": 0}
        
        @persist()
        def function_one(x: int) -> int:
            call_count1["count"] += 1
            return x * 10
        
        @persist()
        def function_two(x: int) -> int:
            call_count2["count"] += 1
            return x * 20
        
        # Cache values for both functions
        result1 = function_one(5)
        assert result1 == 50
        assert call_count1["count"] == 1
        
        result2 = function_two(5)
        assert result2 == 100
        assert call_count2["count"] == 1
        
        # Both should be cached
        result3 = function_one(5)
        assert result3 == 50
        assert call_count1["count"] == 1  # Used cache
        
        result4 = function_two(5)
        assert result4 == 100
        assert call_count2["count"] == 1  # Used cache
        
        # Clear all for function_one only
        function_one.clear_all()
        
        # function_one should execute again
        result5 = function_one(5)
        assert result5 == 50
        assert call_count1["count"] == 2  # Executed again
        
        # function_two should still be cached
        result6 = function_two(5)
        assert result6 == 100
        assert call_count2["count"] == 1  # Still cached
        
        # Clean up
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
    finally:
        set_cache_path(original_cache_path)


def test_clear_all_with_memory_cache():
    """Test that clear_all works with memory cache."""
    # Save original
    original_cache_path = get_cache_path()
    
    try:
        call_count = {"count": 0}
        
        @persist(memory=True)
        def test_function(x: int) -> int:
            call_count["count"] += 1
            return x * 30
        
        # Cache multiple values
        result1 = test_function(5)
        assert result1 == 150
        assert call_count["count"] == 1
        
        result2 = test_function(10)
        assert result2 == 300
        assert call_count["count"] == 2
        
        # Both should be cached
        result3 = test_function(5)
        assert result3 == 150
        assert call_count["count"] == 2  # Used cache
        
        result4 = test_function(10)
        assert result4 == 300
        assert call_count["count"] == 2  # Used cache
        
        # Clear all cached values
        test_function.clear_all()
        
        # Both should execute again
        result5 = test_function(5)
        assert result5 == 150
        assert call_count["count"] == 3  # Executed again
        
        result6 = test_function(10)
        assert result6 == 300
        assert call_count["count"] == 4  # Executed again
    finally:
        set_cache_path(original_cache_path)


def test_clear_all_with_cache_path_override():
    """Test that clear_all works with cache_path_override parameter."""
    cache_dir = Path(".cache/ix_test/clear_all_default")
    override_cache = Path(".cache/ix_test/clear_all_override")
    
    # Clean up
    for cache in [cache_dir, override_cache]:
        if cache.exists():
            shutil.rmtree(cache)
    
    # Save original
    original_cache_path = get_cache_path()
    
    try:
        # Set default cache path
        set_cache_path(cache_dir)
        
        call_count = {"count": 0}
        
        @persist()
        def test_function(x: int) -> int:
            call_count["count"] += 1
            return x * 40
        
        # Cache in default location
        result1 = test_function(5, cache_path=cache_dir)
        assert result1 == 200
        assert call_count["count"] == 1
        
        # Cache in override location
        result2 = test_function(10, cache_path=override_cache)
        assert result2 == 400
        assert call_count["count"] == 2
        
        # Both should be cached
        result3 = test_function(5, cache_path=cache_dir)
        assert result3 == 200
        assert call_count["count"] == 2  # Used cache
        
        result4 = test_function(10, cache_path=override_cache)
        assert result4 == 400
        assert call_count["count"] == 2  # Used cache
        
        # Clear all from override location
        test_function.clear_all(cache_path_override=override_cache)
        
        # Override location should execute again
        result5 = test_function(10, cache_path=override_cache)
        assert result5 == 400
        assert call_count["count"] == 3  # Executed again
        
        # Default location should still be cached
        result6 = test_function(5, cache_path=cache_dir)
        assert result6 == 200
        assert call_count["count"] == 3  # Still cached
        
        # Clean up
        for cache in [cache_dir, override_cache]:
            if cache.exists():
                shutil.rmtree(cache)
    finally:
        set_cache_path(original_cache_path)


def test_clear_all_with_multiple_arguments():
    """Test that clear_all works with functions that have multiple arguments."""
    cache_dir = Path(".cache/ix_test/clear_all_multi")
    
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
        def test_function(x: int, y: int, z: int) -> int:
            call_count["count"] += 1
            return x + y + z
        
        # Cache multiple combinations
        result1 = test_function(1, 2, 3)
        assert result1 == 6
        assert call_count["count"] == 1
        
        result2 = test_function(4, 5, 6)
        assert result2 == 15
        assert call_count["count"] == 2
        
        result3 = test_function(7, 8, 9)
        assert result3 == 24
        assert call_count["count"] == 3
        
        # All should be cached
        result4 = test_function(1, 2, 3)
        assert result4 == 6
        assert call_count["count"] == 3  # Used cache
        
        # Clear all
        test_function.clear_all()
        
        # All should execute again
        result5 = test_function(1, 2, 3)
        assert result5 == 6
        assert call_count["count"] == 4  # Executed again
        
        result6 = test_function(4, 5, 6)
        assert result6 == 15
        assert call_count["count"] == 5  # Executed again
        
        # Clean up
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
    finally:
        set_cache_path(original_cache_path)
