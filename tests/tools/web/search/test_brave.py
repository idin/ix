"""
Tests for Brave search engine implementation.

WARNING: These tests make actual API calls to Brave Search API, which costs money.
Each test makes at least one API request. Keep tests minimal and efficient.
"""

import pytest
from tests.api_keys import get_brave_api_key
from ixmachina.tools.web import search_brave, search_web


def test_basic():
    """Test basic Brave search functionality - single API call."""
    api_key = get_brave_api_key()
    
    # Use default max_results (20) to maximize value per request
    result = search_brave(query="python programming", api_key=api_key)
    
    assert result["success"] is True
    assert result["search_engine"] == "brave"
    assert result["count"] > 0
    assert len(result["results"]) > 0
    assert result["error"] is None
    assert result["query"] == "python programming"
    
    # Check result structure
    first_result = result["results"][0]
    assert "title" in first_result
    assert "url" in first_result
    assert "snippet" in first_result
    assert isinstance(first_result["title"], str)
    assert isinstance(first_result["url"], str)


def test_with_domain_filter():
    """Test Brave search with domain filter - single API call."""
    api_key = get_brave_api_key()
    
    # Domain filtering is now done via search_web, not search_brave
    result = search_web(
        query="python",
        max_results=20,  # Use max to get value from single request
        domain_whitelist="python.org",
        brave_api_key=api_key,
    )
    
    assert result["success"] is True
    assert result["search_engine"] == "brave"
    
    # If we have results, they should be from python.org
    if result["count"] > 0:
        for res in result["results"]:
            assert "python.org" in res["url"].lower()


def test_multiple_domain_filters():
    """Test Brave search with multiple domain filters - single API call."""
    api_key = get_brave_api_key()
    
    # Use a query that's very likely to return results from these domains
    # "python" is a common topic on both github.com and stackoverflow.com
    result = search_web(
        query="python",
        max_results=20,  # Use max to get value from single request
        domain_whitelist=["github.com", "stackoverflow.com"],
        brave_api_key=api_key,
    )
    
    assert result["search_engine"] == "brave"
    # With a common query like "python", we should get results from these domains
    assert result["success"] is True, f"Expected success but got error: {result.get('error')}"
    assert result["count"] > 0, "Expected at least one result from filtered domains"
    
    # All results should be from one of the filtered domains
    for res in result["results"]:
        url_lower = res["url"].lower()
        assert "github.com" in url_lower or "stackoverflow.com" in url_lower, (
            f"Result URL {res['url']} is not from an allowed domain"
        )


def test_no_api_key():
    """Test Brave search fails without API key - no API call."""
    import os
    
    # Temporarily unset the environment variable to test the no-key scenario
    original_key = os.environ.get("BRAVE_API_KEY")
    try:
        if "BRAVE_API_KEY" in os.environ:
            del os.environ["BRAVE_API_KEY"]
        
        result = search_brave(query="test", api_key=None)
        
        assert result["success"] is False
        assert result["search_engine"] == "brave"
        assert "brave api key" in result["error"].lower() or "api key" in result["error"].lower()
        assert result["count"] == 0
        assert result["results"] == []
    finally:
        # Restore the original environment variable
        if original_key is not None:
            os.environ["BRAVE_API_KEY"] = original_key


def test_pagination_multiple_requests():
    """Test Brave search pagination - makes multiple API calls (costs more)."""
    api_key = get_brave_api_key()
    
    # Request 50 results - will make 3 API calls (20 + 20 + 10)
    # This test costs more, so we only test if explicitly needed
    result = search_brave(
        query="python",
        max_results=50,
        api_key=api_key,
    )
    
    assert result["success"] is True
    assert result["search_engine"] == "brave"
    # Should have at least some results (may not get full 50)
    assert result["count"] > 0
    assert result["count"] <= 50

