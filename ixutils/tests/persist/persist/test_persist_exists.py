"""
Tests for persist decorator exists method.
"""

from pathlib import Path
import shutil
from ixutils import delay
from ixutils import persist, set_cache_path, get_cache_path


def test_exists_method_checks_cached_value():
    """Test that exists method checks if cached value exists."""
    cache_dir = Path(".cache/ix_test/exists")
    
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
            return x * 40
        
        # Initially, cache should not exist
        assert test_function.exists(5) is False
        
        # Call function to create cache
        result1 = test_function(5)
        assert result1 == 200
        assert call_count["count"] == 1
        
        # Now cache should exist
        assert test_function.exists(5) is True
        
        # Different arguments should not exist
        assert test_function.exists(6) is False
        
        # Clean up
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
    finally:
        set_cache_path(original_cache_path)


def test_exists_method_with_kwargs():
    """Test that exists method works with keyword arguments."""
    cache_dir = Path(".cache/ix_test/exists_kwargs")
    
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
        
        # Initially, cache should not exist
        assert test_function.exists(5, y=20) is False
        
        # Call function to create cache
        result1 = test_function(5, y=20)
        assert result1 == 25
        assert call_count["count"] == 1
        
        # Now cache should exist
        assert test_function.exists(5, y=20) is True
        
        # Different kwargs should not exist
        assert test_function.exists(5, y=30) is False
        
        # Clean up
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
    finally:
        set_cache_path(original_cache_path)


def test_exists_method_ignores_cache_params():
    """Test that exists method ignores cache_path and use_cache parameters."""
    cache_dir = Path(".cache/ix_test/exists_ignore")
    override_cache = Path(".cache/ix_test/exists_override")
    
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
            return x * 45
        
        # Call function to create cache
        result1 = test_function(5)
        assert result1 == 225
        assert call_count["count"] == 1
        
        # Exists should return True even with cache_path parameter
        assert test_function.exists(5, cache_path=override_cache) is True
        
        # Exists should return True even with use_cache parameter
        assert test_function.exists(5, use_cache=False) is True
        
        # Clean up
        for cache in [cache_dir, override_cache]:
            if cache.exists():
                shutil.rmtree(cache)
    finally:
        set_cache_path(original_cache_path)


def test_exists_method_with_memory_cache():
    """Test that exists method works with memory cache."""
    # Save original
    original_cache_path = get_cache_path()
    
    try:
        call_count = {"count": 0}
        
        @persist(memory=True)
        def test_function(x: int) -> int:
            call_count["count"] += 1
            return x * 50
        
        # Initially, cache should not exist
        assert test_function.exists(5) is False
        
        # Call function to create cache
        result1 = test_function(5)
        assert result1 == 250
        assert call_count["count"] == 1
        
        # Now cache should exist
        assert test_function.exists(5) is True
        
        # Different arguments should not exist
        assert test_function.exists(6) is False
    finally:
        set_cache_path(original_cache_path)


def test_exists_method_with_expiration():
    """Test that exists method respects expiration."""
    cache_dir = Path(".cache/ix_test/exists_expire")
    
    # Clean up
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    
    # Save original
    original_cache_path = get_cache_path()
    
    try:
        # Set cache path
        set_cache_path(cache_dir)
        
        call_count = {"count": 0}
        
        @persist(expire_seconds=2)  # 2 second expiration
        def test_function(x: int) -> int:
            call_count["count"] += 1
            return x * 55
        
        # Call function to create cache
        result1 = test_function(5)
        assert result1 == 275
        assert call_count["count"] == 1
        
        # Cache should exist immediately
        assert test_function.exists(5) is True
        
        # Wait less than expiration time (1 second)
        delay(1)
        
        # Cache should still exist
        assert test_function.exists(5) is True
        
        # Wait for expiration (another 1.5 seconds to be sure)
        delay(1.5)
        
        # Cache should not exist after expiration
        assert test_function.exists(5) is False
        
        # Clean up
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
    finally:
        set_cache_path(original_cache_path)


def test_exists_method_after_delete():
    """Test that exists method returns False after delete."""
    cache_dir = Path(".cache/ix_test/exists_delete")
    
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
            return x * 60
        
        # Call function to create cache
        result1 = test_function(5)
        assert result1 == 300
        assert call_count["count"] == 1
        
        # Cache should exist
        assert test_function.exists(5) is True
        
        # Delete the cache
        test_function.delete(5)
        
        # Cache should not exist after delete
        assert test_function.exists(5) is False
        
        # Clean up
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
    finally:
        set_cache_path(original_cache_path)

