"""
Tests for Brave search engine implementation.

WARNING: These tests make actual API calls to Brave Search API, which costs money.
Each test makes at least one API request. Keep tests minimal and efficient.
"""

import pytest
import os
from ixmachina.tools.web.search.brave import search_brave


def test_basic():
    """Test basic Brave search functionality - single API call."""
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        pytest.skip("BRAVE_API_KEY environment variable not set")
    
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
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        pytest.skip("BRAVE_API_KEY environment variable not set")
    
    result = search_brave(
        query="python",
        max_results=20,  # Use max to get value from single request
        domain_filter="python.org",
        api_key=api_key,
    )
    
    assert result["success"] is True
    assert result["search_engine"] == "brave"
    
    # If we have results, they should be from python.org
    if result["count"] > 0:
        for res in result["results"]:
            assert "python.org" in res["url"].lower()


def test_multiple_domain_filters():
    """Test Brave search with multiple domain filters - single API call."""
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        pytest.skip("BRAVE_API_KEY environment variable not set")
    
    result = search_brave(
        query="programming",
        max_results=20,  # Use max to get value from single request
        domain_filter=["github.com", "stackoverflow.com"],
        api_key=api_key,
    )
    
    assert result["success"] is True
    assert result["search_engine"] == "brave"
    
    # If we have results, they should be from one of the filtered domains
    if result["count"] > 0:
        for res in result["results"]:
            url_lower = res["url"].lower()
            assert "github.com" in url_lower or "stackoverflow.com" in url_lower


def test_no_api_key():
    """Test Brave search fails without API key - no API call."""
    result = search_brave(query="test", api_key=None)
    
    assert result["success"] is False
    assert result["search_engine"] == "brave"
    assert "brave api key" in result["error"].lower() or "api key" in result["error"].lower()
    assert result["count"] == 0
    assert result["results"] == []


def test_pagination_multiple_requests():
    """Test Brave search pagination - makes multiple API calls (costs more)."""
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        pytest.skip("BRAVE_API_KEY environment variable not set")
    
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

