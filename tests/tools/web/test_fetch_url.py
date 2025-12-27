"""
Tests for fetch_url, fetch_json, and post_request tools.
"""

import pytest

from ixmachina.tools.web import fetch_url, fetch_json, post_request


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

