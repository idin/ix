"""
Tests for get_wikipedia_article function.
"""

import pytest

from ixtools.wikipedia import get_wikipedia_article


def test_get_wikipedia_article_full():
    """Test getting full Wikipedia article."""
    result = get_wikipedia_article("Python (programming language)", summary_only=False)
    
    assert result["success"] is True
    assert result["title"] == "Python (programming language)"
    assert result["content"] is not None
    assert len(result["content"]) > 0
    assert result["extract"] is not None  # First paragraph
    assert result["page_id"] is not None
    assert result["url"] is not None
    assert "wikipedia.org" in result["url"]


def test_get_wikipedia_article_summary_only():
    """Test getting Wikipedia article summary only."""
    result = get_wikipedia_article("Python (programming language)", summary_only=True)
    
    assert result["success"] is True
    assert result["title"] == "Python (programming language)"
    assert result["content"] is not None
    assert len(result["content"]) > 0
    # Summary should be shorter than full content
    assert len(result["content"]) < 5000  # Rough check


def test_get_wikipedia_article_with_redirect():
    """Test getting article via redirect."""
    result = get_wikipedia_article("USA", summary_only=True)
    
    assert result["success"] is True
    assert result["title"] == "United States"


def test_get_wikipedia_article_nonexistent():
    """Test getting non-existent article."""
    result = get_wikipedia_article("ThisArticleDefinitelyDoesNotExist12345", summary_only=True)
    
    assert result["success"] is False
    assert result["content"] is None
    assert result["error"] is not None


def test_get_wikipedia_article_different_language():
    """Test getting article in different language."""
    result = get_wikipedia_article("Python", language="fr", summary_only=True)
    
    assert result["success"] is True
    assert result["language"] == "fr"

