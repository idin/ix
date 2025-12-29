"""
Tests for DuckDuckGo search engine implementation.
"""

import pytest
from ixmachina.tools.web.search.duckduckgo import search_duckduckgo


def test_basic():
    """Test basic DuckDuckGo search functionality."""
    result = search_duckduckgo(query="python programming", max_results=5)
    
    assert result["success"] is True
    assert result["search_engine"] == "duckduckgo"
    assert result["count"] > 0
    assert len(result["results"]) > 0
    assert result["error"] is None
    
    # Check result structure
    first_result = result["results"][0]
    assert "title" in first_result
    assert "url" in first_result
    assert "snippet" in first_result


def test_with_domain_filter():
    """Test DuckDuckGo search with domain filter."""
    result = search_duckduckgo(
        query="python",
        max_results=10,
        domain_filter="python.org",
    )
    
    assert result["success"] is True
    assert result["search_engine"] == "duckduckgo"
    assert result["count"] > 0
    
    # All results should be from python.org
    for res in result["results"]:
        assert "python.org" in res["url"].lower()


def test_multiple_domain_filters():
    """Test DuckDuckGo search with multiple domain filters."""
    result = search_duckduckgo(
        query="programming",
        max_results=10,
        domain_filter=["github.com", "stackoverflow.com"],
    )
    
    assert result["success"] is True
    assert result["search_engine"] == "duckduckgo"
    
    # Results should be from one of the filtered domains
    for res in result["results"]:
        url_lower = res["url"].lower()
        assert "github.com" in url_lower or "stackoverflow.com" in url_lower


def test_empty_query():
    """Test DuckDuckGo search with empty query."""
    result = search_duckduckgo(query="", max_results=5)
    
    # DuckDuckGo may return results even for empty query, or may fail
    # Just check that it doesn't crash
    assert "success" in result
    assert "search_engine" in result
    assert result["search_engine"] == "duckduckgo"


def test_special_characters():
    """Test DuckDuckGo search with special characters in query."""
    result = search_duckduckgo(
        query="python & javascript",
        max_results=5,
    )
    
    assert result["success"] is True
    assert result["search_engine"] == "duckduckgo"
    assert result["error"] is None

