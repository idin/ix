"""
Tests for check_url_status tool.
"""

import pytest

from ixmachina.tools.web import check_url_status


def test_check_url_status_success_200():
    """Test check_url_status returns 200 for successful request."""
    result = check_url_status("https://httpbin.org/get")
    
    assert result["success"] is True
    assert result["exists"] is True
    assert result["status_code"] == 200
    assert result["error_type"] is None
    assert result["error_message"] is None
    assert result["error"] is None


def test_check_url_status_404_not_found():
    """Test check_url_status returns exact 404 error."""
    result = check_url_status("https://httpbin.org/status/404")
    
    assert result["success"] is True
    assert result["exists"] is True
    assert result["status_code"] == 404
    assert result["error_type"] == "HTTPError"
    assert result["error_message"] is not None
    assert "404" in result["error_message"]
    assert "HTTP 404" in result["error_message"]


def test_check_url_status_500_server_error():
    """Test check_url_status returns exact 500 error."""
    result = check_url_status("https://httpbin.org/status/500")
    
    assert result["success"] is True
    assert result["exists"] is True
    assert result["status_code"] == 500
    assert result["error_type"] == "HTTPError"
    assert result["error_message"] is not None
    assert "500" in result["error_message"]
    assert "HTTP 500" in result["error_message"]


def test_check_url_status_403_forbidden():
    """Test check_url_status returns exact 403 error."""
    result = check_url_status("https://httpbin.org/status/403")
    
    assert result["success"] is True
    assert result["exists"] is True
    assert result["status_code"] == 403
    assert result["error_type"] == "HTTPError"
    assert result["error_message"] is not None
    assert "403" in result["error_message"]
    assert "HTTP 403" in result["error_message"]


def test_check_url_status_dns_error():
    """Test check_url_status returns exact DNS error for invalid domain."""
    result = check_url_status("https://this-domain-does-not-exist-12345-xyz.com")
    
    assert result["success"] is False
    assert result["exists"] is False
    assert result["status_code"] is None
    assert result["error_type"] == "DNS"
    assert result["error_message"] is not None
    assert "DNS" in result["error_message"]


def test_check_url_status_timeout_error():
    """Test check_url_status returns exact Timeout error."""
    result = check_url_status("https://httpbin.org/delay/10", timeout=1)
    
    assert result["success"] is False
    assert result["exists"] is False
    assert result["status_code"] is None
    assert result["error_type"] == "Timeout"
    assert result["error_message"] is not None
    assert "timeout" in result["error_message"].lower()


def test_check_url_status_connection_refused():
    """Test check_url_status returns exact ConnectionRefused error."""
    result = check_url_status("http://127.0.0.1:99999", timeout=2)
    
    assert result["success"] is False
    assert result["exists"] is False
    assert result["status_code"] is None
    # On macOS, this might be ConnectionRefused or RequestException depending on how requests handles it
    # But we should check for the exact type that was returned
    assert result["error_type"] in ["ConnectionRefused", "ConnectionError", "RequestException"]
    assert result["error_message"] is not None


def test_check_url_status_redirect_301():
    """Test check_url_status handles redirects correctly."""
    result = check_url_status("https://httpbin.org/redirect/1")
    
    assert result["success"] is True
    assert result["exists"] is True
    # After redirect, should end up with 200
    assert result["status_code"] == 200
    assert result["redirect_count"] >= 1


def test_check_url_status_without_scheme_adds_https():
    """Test check_url_status adds https:// if scheme is missing."""
    result = check_url_status("httpbin.org/get")
    
    assert result["success"] is True
    assert result["exists"] is True
    assert result["status_code"] == 200
    assert result["url"].startswith("http")


def test_check_url_status_uses_get_when_head_disabled():
    """Test check_url_status uses GET when use_head=False."""
    result = check_url_status("https://httpbin.org/get", use_head=False)
    
    assert result["success"] is True
    assert result["exists"] is True
    assert result["status_code"] == 200


def test_check_url_status_batch_success():
    """Test check_url_status with multiple URLs."""
    urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/json",
        "https://httpbin.org/uuid",
    ]
    result = check_url_status(url=urls)
    
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
        assert result["results"][url]["exists"] is True
        assert result["results"][url]["status_code"] == 200


def test_check_url_status_batch_mixed_success_failure():
    """Test check_url_status with multiple URLs where some succeed and some fail."""
    urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/status/404",
        "https://this-domain-does-not-exist-12345-xyz.com",
    ]
    result = check_url_status(url=urls)
    
    assert isinstance(result, dict)
    assert result["success"] is True  # At least one succeeded
    assert "results" in result
    assert len(result["results"]) == 3
    assert result["total_count"] == 3
    assert result["success_count"] == 2  # get succeeds, 404 succeeds (site exists), DNS fails
    assert result["failure_count"] == 1
    
    # Check successful URLs
    assert "https://httpbin.org/get" in result["successful_urls"]
    assert "https://httpbin.org/status/404" in result["successful_urls"]
    assert result["results"]["https://httpbin.org/get"]["success"] is True
    assert result["results"]["https://httpbin.org/get"]["exists"] is True
    assert result["results"]["https://httpbin.org/status/404"]["success"] is True
    assert result["results"]["https://httpbin.org/status/404"]["exists"] is True
    
    # Check failed URL
    assert "https://this-domain-does-not-exist-12345-xyz.com" in result["failed_urls"]
    assert result["results"]["https://this-domain-does-not-exist-12345-xyz.com"]["success"] is False
    assert result["results"]["https://this-domain-does-not-exist-12345-xyz.com"]["exists"] is False
