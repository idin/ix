"""
Tests for search_web and search_web_simple tools.
"""

import pytest

from ixmachina.tools.web import search_web, search_web_simple


def test_search_web_duckduckgo_success():
    """Test search_web successfully searches using DuckDuckGo."""
    result = search_web("python programming", max_results=5, search_engine="duckduckgo")
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert result["search_engine"] == "duckduckgo"
    assert result["query"] == "python programming"
    assert "results" in result
    assert isinstance(result["results"], list)
    assert result["count"] == len(result["results"])
    assert result["count"] <= 5
    assert result["error"] is None
    
    # Check result structure if we have results
    if result["count"] > 0:
        first_result = result["results"][0]
        assert "title" in first_result
        assert "url" in first_result
        assert "snippet" in first_result
        assert isinstance(first_result["title"], str)
        assert isinstance(first_result["url"], str)


def test_search_web_startpage_success():
    """Test search_web successfully searches using Startpage."""
    result = search_web("python programming", max_results=5, search_engine="startpage")
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert result["search_engine"] == "startpage"
    assert result["query"] == "python programming"
    assert "results" in result
    assert isinstance(result["results"], list)
    assert result["count"] == len(result["results"])
    assert result["count"] <= 5
    assert result["error"] is None
    
    # Check result structure if we have results
    if result["count"] > 0:
        first_result = result["results"][0]
        assert "title" in first_result
        assert "url" in first_result
        assert "snippet" in first_result


def test_search_web_default_engine():
    """Test search_web defaults to DuckDuckGo when no engine specified."""
    result = search_web("test query", max_results=3)
    
    assert isinstance(result, dict)
    assert result["search_engine"] == "duckduckgo"


def test_search_web_unknown_engine():
    """Test search_web handles unknown search engine."""
    result = search_web("test query", search_engine="unknown_engine")
    
    assert isinstance(result, dict)
    assert result["success"] is False
    assert result["search_engine"] == "unknown_engine"
    assert "error" in result
    assert "unknown" in result["error"].lower() or "supported" in result["error"].lower()
    assert result["results"] == []
    assert result["count"] == 0


def test_search_web_max_results():
    """Test search_web respects max_results parameter."""
    result = search_web("python", max_results=3, search_engine="duckduckgo")
    
    assert isinstance(result, dict)
    assert result["count"] <= 3
    assert len(result["results"]) <= 3


def test_search_web_case_insensitive_engine():
    """Test search_web handles case-insensitive search engine names."""
    result1 = search_web("test", search_engine="DUCKDUCKGO")
    result2 = search_web("test", search_engine="DuckDuckGo")
    result3 = search_web("test", search_engine="duckduckgo")
    
    # All should work (case-insensitive)
    assert result1["search_engine"] == "duckduckgo"
    assert result2["search_engine"] == "duckduckgo"
    assert result3["search_engine"] == "duckduckgo"


def test_search_web_simple_success():
    """Test search_web_simple returns results list."""
    results = search_web_simple("python", search_engine="duckduckgo")
    
    assert isinstance(results, list)
    # If search was successful, should have results
    if len(results) > 0:
        assert "title" in results[0]
        assert "url" in results[0]
        assert "snippet" in results[0]


def test_search_web_simple_empty_on_error():
    """Test search_web_simple returns empty list on error."""
    results = search_web_simple("test", search_engine="unknown_engine")
    
    assert isinstance(results, list)
    assert len(results) == 0


def test_search_web_simple_default_engine():
    """Test search_web_simple defaults to DuckDuckGo."""
    results = search_web_simple("test")
    
    # Should return a list (empty or with results)
    assert isinstance(results, list)


def test_search_web_special_characters():
    """Test search_web handles special characters in query."""
    result = search_web("python & programming", max_results=3, search_engine="duckduckgo")
    
    assert isinstance(result, dict)
    assert result["query"] == "python & programming"
    # Should either succeed or fail gracefully
    assert "success" in result


def test_search_web_empty_query():
    """Test search_web handles empty query."""
    result = search_web("", max_results=3, search_engine="duckduckgo")
    
    assert isinstance(result, dict)
    assert result["query"] == ""
    # Should either succeed or fail gracefully
    assert "success" in result

