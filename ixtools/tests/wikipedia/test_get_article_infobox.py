"""
Tests for get_article_infobox function.
"""

import pytest

from ixtools.wikipedia import get_article_infobox


def test_get_article_infobox_with_infobox():
    """Test getting infobox from article that has one."""
    # Many articles have infoboxes, try a well-known one
    result = get_article_infobox("Python (programming language)")
    
    assert result["success"] is True
    assert result["title"] == "Python (programming language)"
    
    # Some articles may not have infoboxes, so check has_infobox
    if result["has_infobox"]:
        assert len(result["infobox"]) > 0
        # Infobox should have key-value pairs
        assert isinstance(result["infobox"], dict)


def test_get_article_infobox_without_infobox():
    """Test getting infobox from article without one."""
    # Try a stub or very short article
    result = get_article_infobox("Python")
    
    # May or may not have infobox, but should succeed
    assert result["success"] is True
    assert "has_infobox" in result


def test_get_article_infobox_structure():
    """Test that infobox returns proper structure."""
    result = get_article_infobox("United States")
    
    assert result["success"] is True
    assert isinstance(result["infobox"], dict)
    
    if result["has_infobox"]:
        # Infobox keys should be lowercase
        for key in result["infobox"].keys():
            assert key == key.lower()


def test_get_article_infobox_nonexistent():
    """Test getting infobox from non-existent article."""
    result = get_article_infobox("ThisArticleDefinitelyDoesNotExist12345")
    
    assert result["success"] is False
    assert result["infobox"] == {}
    assert result["has_infobox"] is False

