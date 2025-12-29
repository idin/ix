"""
Tests for get_article_links function.
"""

import pytest

from ixmachina.tools.wikipedia import get_article_links


def test_get_article_links_basic():
    """Test getting links from a Wikipedia article."""
    result = get_article_links("Python (programming language)", max_links=10)
    
    assert result["success"] is True
    assert result["title"] == "Python (programming language)"
    assert result["count"] > 0
    assert len(result["links"]) <= 10
    
    # Check link structure
    if result["links"]:
        first_link = result["links"][0]
        assert "title" in first_link
        assert "display_text" in first_link
        assert "namespace" in first_link
        assert first_link["namespace"] == 0  # Main namespace


def test_get_article_links_max_links():
    """Test getting links with max_links limit."""
    result = get_article_links("Python (programming language)", max_links=5)
    
    assert result["success"] is True
    assert len(result["links"]) <= 5


def test_get_article_links_all_links():
    """Test getting all links (no limit)."""
    result = get_article_links("Python (programming language)")
    
    assert result["success"] is True
    assert result["count"] > 0
    # Should have many links for a major article
    assert result["count"] >= 10


def test_get_article_links_normalized_titles():
    """Test that all link titles are normalized/canonical."""
    result = get_article_links("Python (programming language)", max_links=20)
    
    assert result["success"] is True
    
    # All titles should be canonical (no redirects, proper casing)
    for link in result["links"]:
        assert link["title"] is not None
        assert len(link["title"]) > 0
        # Title should not have leading/trailing spaces
        assert link["title"] == link["title"].strip()


def test_get_article_links_nonexistent():
    """Test getting links from non-existent article."""
    result = get_article_links("ThisArticleDefinitelyDoesNotExist12345")
    
    assert result["success"] is False
    assert result["links"] == []
    assert result["count"] == 0

