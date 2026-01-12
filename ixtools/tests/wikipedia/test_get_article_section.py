"""
Tests for get_article_section function.
"""

import pytest

from ixtools.wikipedia import get_article_section


def test_get_article_section_existing():
    """Test getting an existing section from article."""
    result = get_article_section("Python (programming language)", "History")
    
    assert result["success"] is True
    assert result["title"] == "Python (programming language)"
    assert result["found"] is True
    assert result["content"] is not None
    assert len(result["content"]) > 0
    assert result["section_name"] == "History"


def test_get_article_section_case_insensitive():
    """Test that section name matching is case-insensitive."""
    result1 = get_article_section("Python (programming language)", "History")
    result2 = get_article_section("Python (programming language)", "history")
    result3 = get_article_section("Python (programming language)", "HISTORY")
    
    # All should find the same section
    if result1["found"]:
        assert result2["found"] is True
        assert result3["found"] is True
        assert result1["content"] == result2["content"]
        assert result1["content"] == result3["content"]


def test_get_article_section_nonexistent():
    """Test getting a section that doesn't exist."""
    result = get_article_section("Python (programming language)", "ThisSectionDoesNotExist12345")
    
    assert result["success"] is True
    assert result["found"] is False
    assert result["content"] is None


def test_get_article_section_nonexistent_article():
    """Test getting section from non-existent article."""
    result = get_article_section("ThisArticleDefinitelyDoesNotExist12345", "History")
    
    assert result["success"] is False
    assert result["found"] is False
    assert result["content"] is None

