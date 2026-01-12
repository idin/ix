"""
Tests for persist decorator with real web functions and expiration.
"""

from pathlib import Path
import shutil
from ixutils import current_timestamp, delay
from ixutils import persist, set_cache_path, get_cache_path
from tests.api_keys import get_brave_api_key

# These tests require ixtools package for web functionality
# Tests will fail if ixtools is not available
from ixtools.web import fetch_url, fetch_json, check_url_status, search_brave, discover_username_signature


def test_persist_caching_with_real_web_functions():
    """Test that persist decorator works correctly with real cached web functions."""
    cache_dir = Path(".cache/ix_test/web_functions")
    
    # Clean up
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    
    # Save original
    original_cache_path = get_cache_path()
    
    try:
        # Set cache path
        set_cache_path(cache_dir)
        
        # Test fetch_url caching
        url = "https://httpbin.org/get"
        
        # First call - should make network request
        start_time = current_timestamp()
        result1 = fetch_url(url)
        first_call_time = current_timestamp() - start_time
        
        assert result1["success"] is True
        assert result1["status_code"] == 200
        
        # Second call - should use cache (much faster)
        start_time = current_timestamp()
        result2 = fetch_url(url)
        second_call_time = current_timestamp() - start_time
        
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
            shutil.rmtree(cache_dir)
    finally:
        set_cache_path(original_cache_path)


def test_persist_expiration_before_and_after():
    """Test that persist expiration works correctly before and after expiration time."""
    cache_dir = Path(".cache/ix_test/expiration_test")
    
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
            return x * 70
        
        # First call - should execute function
        result1 = test_function(5)
        assert result1 == 350
        assert call_count["count"] == 1
        
        # Second call before expiration - should use cache
        delay(0.5)  # Wait less than expiration
        result2 = test_function(5)
        assert result2 == 350
        assert call_count["count"] == 1  # Still 1, used cache
        
        # Third call still before expiration - should use cache
        delay(0.5)  # Total 1 second
        result3 = test_function(5)
        assert result3 == 350
        assert call_count["count"] == 1  # Still 1, used cache
        
        # Wait for expiration (another 1.5 seconds to be sure we're past 2 seconds)
        delay(1.5)
        
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
            shutil.rmtree(cache_dir)
    finally:
        set_cache_path(original_cache_path)

