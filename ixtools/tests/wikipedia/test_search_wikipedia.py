"""
Tests for search_wikipedia function.
"""

import pytest

from ixtools.wikipedia import search_wikipedia


def test_search_wikipedia_basic():
    """Test basic Wikipedia search."""
    result = search_wikipedia("Python programming", max_results=5)
    
    assert result["success"] is True
    assert result["count"] > 0
    assert len(result["results"]) <= 5
    assert result["query"] == "Python programming"
    assert result["language"] == "en"
    
    # Check result structure
    if result["results"]:
        first_result = result["results"][0]
        assert "title" in first_result
        assert "snippet" in first_result
        assert "page_id" in first_result


def test_search_wikipedia_max_results():
    """Test search with max_results limit."""
    result = search_wikipedia("Python", max_results=3)
    
    assert result["success"] is True
    assert len(result["results"]) <= 3


def test_search_wikipedia_no_results():
    """Test search with query that returns no results."""
    result = search_wikipedia("ThisQueryShouldReturnNoResults12345xyz", max_results=5)
    
    # Search might still succeed but return 0 results
    assert result["success"] is True
    assert result["count"] == 0
    assert result["results"] == []


def test_search_wikipedia_different_language():
    """Test search with different language."""
    result = search_wikipedia("Python", language="fr", max_results=3)
    
    assert result["success"] is True
    assert result["language"] == "fr"

