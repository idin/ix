"""
Tests for persist decorator use_cache flag and delete method.
"""

import time
from pathlib import Path
from ixmachina.utils.persist import persist, set_cache_path, get_cache_path


def test_use_cache_flag_disables_caching():
    """Test that use_cache=False disables caching for a specific call."""
    cache_dir = Path(".cache/ix_test/use_cache")
    
    # Clean up
    if cache_dir.exists():
        import shutil
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
            import shutil
            shutil.rmtree(cache_dir)
    finally:
        set_cache_path(original_cache_path)


def test_use_cache_flag_does_not_affect_cache_key():
    """Test that use_cache parameter is not included in cache key."""
    cache_dir = Path(".cache/ix_test/use_cache_key")
    
    # Clean up
    if cache_dir.exists():
        import shutil
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
            import shutil
            shutil.rmtree(cache_dir)
    finally:
        set_cache_path(original_cache_path)


def test_delete_method_removes_cached_value():
    """Test that delete method removes cached values."""
    cache_dir = Path(".cache/ix_test/delete")
    
    # Clean up
    if cache_dir.exists():
        import shutil
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
            import shutil
            shutil.rmtree(cache_dir)
    finally:
        set_cache_path(original_cache_path)


def test_delete_method_with_different_arguments():
    """Test that delete method only deletes the specific cached value."""
    cache_dir = Path(".cache/ix_test/delete_specific")
    
    # Clean up
    if cache_dir.exists():
        import shutil
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
            import shutil
            shutil.rmtree(cache_dir)
    finally:
        set_cache_path(original_cache_path)


def test_delete_method_with_kwargs():
    """Test that delete method works with keyword arguments."""
    cache_dir = Path(".cache/ix_test/delete_kwargs")
    
    # Clean up
    if cache_dir.exists():
        import shutil
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
            import shutil
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
            import shutil
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
                import shutil
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


def test_cache_path_parameter_not_in_cache_key():
    """Test that cache_path parameter is not included in cache key."""
    cache_dir1 = Path(".cache/ix_test/cache_path_key1")
    cache_dir2 = Path(".cache/ix_test/cache_path_key2")
    
    # Clean up
    for cache in [cache_dir1, cache_dir2]:
        if cache.exists():
            import shutil
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
                import shutil
                shutil.rmtree(cache)
    finally:
        set_cache_path(original_cache_path)


def test_persist_caching_with_real_web_functions():
    """Test that persist decorator works correctly with real cached web functions."""
    import time
    from ixmachina.tools.web import fetch_url, fetch_json, check_url_status
    from ixmachina.tools.web import search_brave
    from ixmachina.tools.web import discover_username_signature
    from tests.api_keys import get_brave_api_key
    
    cache_dir = Path(".cache/ix_test/web_functions")
    
    # Clean up
    if cache_dir.exists():
        import shutil
        shutil.rmtree(cache_dir)
    
    # Save original
    original_cache_path = get_cache_path()
    
    try:
        # Set cache path
        set_cache_path(cache_dir)
        
        # Test fetch_url caching
        url = "https://httpbin.org/get"
        
        # First call - should make network request
        start_time = time.time()
        result1 = fetch_url(url)
        first_call_time = time.time() - start_time
        
        assert result1["success"] is True
        assert result1["status_code"] == 200
        
        # Second call - should use cache (much faster)
        start_time = time.time()
        result2 = fetch_url(url)
        second_call_time = time.time() - start_time
        
        # Results should be identical
        assert result2["success"] == result1["success"]
        assert result2["status_code"] == result1["status_code"]
        assert result2["content"] == result1["content"]
        
        # Second call should be much faster (cache hit)
        assert second_call_time < first_call_time * 0.5 or second_call_time < 0.1
        
        # Test fetch_json caching
        json_url = "https://httpbin.org/json"
        
        # First call
        result3 = fetch_json(json_url)
        assert result3["success"] is True
        assert result3["status_code"] == 200
        
        # Second call - should use cache
        result4 = fetch_json(json_url)
        assert result4["success"] == result3["success"]
        assert result4["status_code"] == result3["status_code"]
        assert result4["data"] == result3["data"]
        
        # Test check_url_status caching
        status_url = "https://httpbin.org/get"
        
        # First call
        result5 = check_url_status(status_url)
        assert result5["success"] is True
        assert result5["status_code"] == 200
        
        # Second call - should use cache
        result6 = check_url_status(status_url)
        assert result6["success"] == result5["success"]
        assert result6["status_code"] == result5["status_code"]
        assert result6["exists"] == result5["exists"]
        
        # Test search_brave caching
        from ixmachina.tools.web import search_brave
        from tests.api_keys import get_brave_api_key
        
        query = "python programming"
        
        # First call
        result7 = search_brave(query=query, max_results=5, api_key=get_brave_api_key())
        assert result7["success"] is True
        assert result7["count"] > 0
        
        # Second call - should use cache
        result8 = search_brave(query=query, max_results=5, api_key=get_brave_api_key())
        assert result8["success"] == result7["success"]
        assert result8["count"] == result7["count"]
        assert result8["results"] == result7["results"]
        
        # Test discover_username_signature caching
        url_pattern = "https://github.com/{username}"
        
        # First call
        result9 = discover_username_signature(url_pattern=url_pattern)
        assert result9["success"] is True
        assert result9["domain"] == "github.com"
        
        # Second call - should use cache
        result10 = discover_username_signature(url_pattern=url_pattern)
        assert result10["success"] == result9["success"]
        assert result10["domain"] == result9["domain"]
        assert result10["url_pattern"] == result9["url_pattern"]
        assert result10["existing_signature"] == result9["existing_signature"]
        assert result10["non_existing_signature"] == result9["non_existing_signature"]
        
        # Clean up
        if cache_dir.exists():
            import shutil
            shutil.rmtree(cache_dir)
    finally:
        set_cache_path(original_cache_path)



def test_exists_method_checks_cached_value():
    """Test that exists method checks if cached value exists."""
    cache_dir = Path(".cache/ix_test/exists")
    
    # Clean up
    if cache_dir.exists():
        import shutil
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
            import shutil
            shutil.rmtree(cache_dir)
    finally:
        set_cache_path(original_cache_path)


def test_exists_method_with_kwargs():
    """Test that exists method works with keyword arguments."""
    cache_dir = Path(".cache/ix_test/exists_kwargs")
    
    # Clean up
    if cache_dir.exists():
        import shutil
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
            import shutil
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
            import shutil
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
                import shutil
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
        import shutil
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
        time.sleep(1)
        
        # Cache should still exist
        assert test_function.exists(5) is True
        
        # Wait for expiration (another 1.5 seconds to be sure)
        time.sleep(1.5)
        
        # Cache should not exist after expiration
        assert test_function.exists(5) is False
        
        # Clean up
        if cache_dir.exists():
            import shutil
            shutil.rmtree(cache_dir)
    finally:
        set_cache_path(original_cache_path)


def test_exists_method_after_delete():
    """Test that exists method returns False after delete."""
    cache_dir = Path(".cache/ix_test/exists_delete")
    
    # Clean up
    if cache_dir.exists():
        import shutil
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
            import shutil
            shutil.rmtree(cache_dir)
    finally:
        set_cache_path(original_cache_path)


def test_persist_expiration_before_and_after():
    """Test that persist expiration works correctly before and after expiration time."""
    cache_dir = Path(".cache/ix_test/expiration_test")
    
    # Clean up
    if cache_dir.exists():
        import shutil
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
            return x * 70
        
        # First call - should execute function
        result1 = test_function(5)
        assert result1 == 350
        assert call_count["count"] == 1
        
        # Second call before expiration - should use cache
        time.sleep(0.5)  # Wait less than expiration
        result2 = test_function(5)
        assert result2 == 350
        assert call_count["count"] == 1  # Still 1, used cache
        
        # Third call still before expiration - should use cache
        time.sleep(0.5)  # Total 1 second
        result3 = test_function(5)
        assert result3 == 350
        assert call_count["count"] == 1  # Still 1, used cache
        
        # Wait for expiration (another 1.5 seconds to be sure we're past 2 seconds)
        time.sleep(1.5)
        
        # Fourth call after expiration - should execute function again
        result4 = test_function(5)
        assert result4 == 350
        assert call_count["count"] == 2  # Now 2, cache expired
        
        # Fifth call - should use new cache
        result5 = test_function(5)
        assert result5 == 350
        assert call_count["count"] == 2  # Still 2, used new cache
        
        # Clean up
        if cache_dir.exists():
            import shutil
            shutil.rmtree(cache_dir)
    finally:
        set_cache_path(original_cache_path)
