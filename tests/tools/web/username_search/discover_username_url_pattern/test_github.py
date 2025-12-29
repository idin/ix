"""
Tests for discover_username_url_pattern with GitHub.
"""

from conftest import get_brave_api_key
from ixmachina.tools.web import discover_username_url_pattern


def test_discover_username_url_pattern_github_single():
    """Test discover_username_url_pattern with GitHub using a single username."""
    result = discover_username_url_pattern(
        domain="github.com",
        existing_username="octocat",
        brave_api_key=get_brave_api_key(),
    )
    
    assert result["success"] is True
    assert result["domain"] == "github.com"
    assert result["url_pattern"] == "https://github.com/{username}"
    assert result["example_url"] == "https://github.com/octocat"
    assert result["method"] is not None
    assert result["error"] is None


def test_discover_username_url_pattern_github_multiple():
    """Test discover_username_url_pattern with GitHub using multiple usernames."""
    result = discover_username_url_pattern(
        domain="github.com",
        existing_username=["octocat", "torvalds"],
        brave_api_key=get_brave_api_key(),
    )
    
    assert result["success"] is True
    assert result["domain"] == "github.com"
    assert result["url_pattern"] == "https://github.com/{username}"
    assert result["example_url"] == "https://github.com/octocat"
    assert result["method"] is not None
    assert result["error"] is None


def test_discover_username_url_pattern_github_nonexistent():
    """Test discover_username_url_pattern fails with non-existent GitHub username."""
    result = discover_username_url_pattern(
        domain="github.com",
        existing_username="this-username-definitely-does-not-exist-12345",
        brave_api_key=get_brave_api_key(),
    )
    
    assert result["success"] is False
    assert result["url_pattern"] is None
    assert result["error"] is not None


def test_discover_username_url_pattern_github_mixed_existing_nonexistent():
    """Test discover_username_url_pattern fails with mixed existing and non-existent GitHub usernames."""
    result = discover_username_url_pattern(
        domain="github.com",
        existing_username=["octocat", "this-username-definitely-does-not-exist-12345"],
        brave_api_key=get_brave_api_key(),
    )
    
    assert result["success"] is False
    assert result["url_pattern"] is None
    assert result["error"] is not None

