"""
Tests for fetch_url, fetch_json, and post_request tools.
"""

import pytest

from ixtools.web import fetch_url, fetch_json, post_request


def test_fetch_url_success():
    """Test fetch_url successfully fetches a URL."""
    result = fetch_url("https://httpbin.org/get")
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert result["status_code"] == 200
    assert "content" in result
    assert isinstance(result["content"], str)
    assert len(result["content"]) > 0
    assert "headers" in result
    assert isinstance(result["headers"], dict)
    assert result["error"] is None


def test_fetch_url_with_headers():
    """Test fetch_url with custom headers."""
    headers = {"User-Agent": "test-agent"}
    result = fetch_url("https://httpbin.org/headers", headers=headers)
    
    assert result["success"] is True
    assert result["status_code"] == 200
    assert "test-agent" in result["content"].lower() or "user-agent" in result["content"].lower()


def test_fetch_url_not_found():
    """Test fetch_url handles 404 errors."""
    result = fetch_url("https://httpbin.org/status/404")
    
    assert isinstance(result, dict)
    assert result["success"] is False
    assert result["status_code"] == 404
    assert result["error"] is not None


def test_fetch_url_invalid_url():
    """Test fetch_url handles invalid URLs."""
    result = fetch_url("https://this-domain-does-not-exist-12345.com")
    
    assert isinstance(result, dict)
    assert result["success"] is False
    assert result["error"] is not None


def test_fetch_url_timeout():
    """Test fetch_url handles timeout."""
    result = fetch_url("https://httpbin.org/delay/10", timeout=1)
    
    assert isinstance(result, dict)
    assert result["success"] is False
    assert result["error"] is not None


def test_fetch_json_success():
    """Test fetch_json successfully fetches and parses JSON."""
    result = fetch_json("https://httpbin.org/json")
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert result["status_code"] == 200
    assert "data" in result
    assert isinstance(result["data"], dict)
    assert result["error"] is None


def test_fetch_json_uses_fetch_url():
    """Test fetch_json uses fetch_url internally."""
    # Test that fetch_json handles HTTP errors the same way
    result = fetch_json("https://httpbin.org/status/404")
    
    assert isinstance(result, dict)
    assert result["success"] is False
    assert result["status_code"] == 404
    assert result["data"] is None
    assert result["error"] is not None


def test_fetch_json_invalid_json():
    """Test fetch_json handles non-JSON responses."""
    # httpbin.org/html returns HTML, not JSON
    result = fetch_json("https://httpbin.org/html")
    
    assert isinstance(result, dict)
    assert result["success"] is False
    assert "error" in result["error"].lower() or "json" in result["error"].lower()


def test_post_request_success():
    """Test post_request successfully sends POST request."""
    data = {"test": "value", "number": 42}
    result = post_request("https://httpbin.org/post", data=data)
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert result["status_code"] == 200
    assert "content" in result
    assert "test" in result["content"] or "value" in result["content"]


def test_post_request_without_data():
    """Test post_request works without data."""
    result = post_request("https://httpbin.org/post")
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert result["status_code"] == 200


def test_post_request_error():
    """Test post_request handles errors."""
    result = post_request("https://httpbin.org/status/500")
    
    assert isinstance(result, dict)
    assert result["success"] is False
    assert result["status_code"] == 500
    assert result["error"] is not None


def test_fetch_url_batch_success():
    """Test fetch_url with multiple URLs."""
    urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/json",
        "https://httpbin.org/uuid",
    ]
    result = fetch_url(url=urls)
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert "results" in result
    assert len(result["results"]) == 3
    assert result["total_count"] == 3
    assert result["success_count"] == 3
    assert result["failure_count"] == 0
    assert len(result["successful_urls"]) == 3
    assert len(result["failed_urls"]) == 0
    
    # Check each result
    for url in urls:
        assert url in result["results"]
        assert result["results"][url]["success"] is True
        assert result["results"][url]["status_code"] == 200


def test_fetch_url_batch_mixed_success_failure():
    """Test fetch_url with multiple URLs where some succeed and some fail."""
    urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/status/404",
        "https://httpbin.org/json",
    ]
    result = fetch_url(url=urls)
    
    assert isinstance(result, dict)
    assert result["success"] is True  # At least one succeeded
    assert "results" in result
    assert len(result["results"]) == 3
    assert result["total_count"] == 3
    assert result["success_count"] == 2
    assert result["failure_count"] == 1
    assert len(result["successful_urls"]) == 2
    assert len(result["failed_urls"]) == 1
    
    # Check successful URLs
    assert "https://httpbin.org/get" in result["successful_urls"]
    assert "https://httpbin.org/json" in result["successful_urls"]
    assert result["results"]["https://httpbin.org/get"]["success"] is True
    assert result["results"]["https://httpbin.org/json"]["success"] is True
    
    # Check failed URL
    assert "https://httpbin.org/status/404" in result["failed_urls"]
    assert result["results"]["https://httpbin.org/status/404"]["success"] is False


def test_fetch_json_batch_success():
    """Test fetch_json with multiple URLs."""
    urls = [
        "https://httpbin.org/json",
        "https://httpbin.org/uuid",
    ]
    result = fetch_json(url=urls)
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert "results" in result
    assert len(result["results"]) == 2
    assert result["total_count"] == 2
    assert result["success_count"] == 2
    assert result["failure_count"] == 0
    
    # Check each result
    for url in urls:
        assert url in result["results"]
        assert result["results"][url]["success"] is True
        assert result["results"][url]["status_code"] == 200
        assert "data" in result["results"][url]


def test_fetch_json_batch_mixed_success_failure():
    """Test fetch_json with multiple URLs where some succeed and some fail."""
    urls = [
        "https://httpbin.org/json",
        "https://httpbin.org/html",  # Not JSON, will fail parsing
        "https://httpbin.org/status/404",  # HTTP error
    ]
    result = fetch_json(url=urls)
    
    assert isinstance(result, dict)
    assert result["success"] is True  # At least one succeeded
    assert "results" in result
    assert len(result["results"]) == 3
    assert result["total_count"] == 3
    assert result["success_count"] == 1
    assert result["failure_count"] == 2
    
    # Check successful URL
    assert "https://httpbin.org/json" in result["successful_urls"]
    assert result["results"]["https://httpbin.org/json"]["success"] is True
    assert "data" in result["results"]["https://httpbin.org/json"]
    
    # Check failed URLs
    assert "https://httpbin.org/html" in result["failed_urls"]
    assert "https://httpbin.org/status/404" in result["failed_urls"]

