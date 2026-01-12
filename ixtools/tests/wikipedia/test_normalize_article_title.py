"""
Tests for normalize_article_title function.
"""

import pytest

from ixtools.wikipedia import normalize_article_title


def test_normalize_article_title_basic():
    """Test normalizing a basic article title."""
    result = normalize_article_title("Python (programming language)")
    
    assert result["success"] is True
    assert result["canonical_title"] == "Python (programming language)"
    assert result["normalized_title"] == "Python (programming language)"
    assert result["language"] == "en"


def test_normalize_article_title_with_redirect():
    """Test normalizing a title that redirects."""
    # "USA" redirects to "United States"
    result = normalize_article_title("USA")
    
    assert result["success"] is True
    assert result["canonical_title"] == "United States"
    assert result["is_redirect"] is True


def test_normalize_article_title_with_underscores():
    """Test normalizing a title with underscores."""
    result = normalize_article_title("Python_(programming_language)")
    
    assert result["success"] is True
    assert result["canonical_title"] == "Python (programming language)"


def test_normalize_article_title_nonexistent():
    """Test normalizing a non-existent article."""
    result = normalize_article_title("ThisArticleDefinitelyDoesNotExist12345")
    
    assert result["success"] is False
    assert result["canonical_title"] is None
    assert result["error"] is not None


def test_normalize_article_title_different_language():
    """Test normalizing with a different language."""
    result = normalize_article_title("Python", language="fr")
    
    assert result["success"] is True
    assert result["language"] == "fr"
    # Should still work, might be different title in French

