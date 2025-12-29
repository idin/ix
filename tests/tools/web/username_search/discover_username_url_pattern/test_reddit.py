"""
Tests for discover_username_url_pattern with Reddit.
"""

from conftest import get_brave_api_key
from ixmachina.tools.web import discover_username_url_pattern


def test_discover_username_url_pattern_reddit_single():
    """Test discover_username_url_pattern with Reddit using a single username."""
    result = discover_username_url_pattern(
        domain="reddit.com",
        existing_username="spez",
        brave_api_key=get_brave_api_key(),
    )
    
    assert result["success"] is True
    assert result["domain"] == "reddit.com"
    # Normalized to no trailing slash
    assert result["url_pattern"] == "https://www.reddit.com/user/{username}"
    assert result["example_url"] == "https://www.reddit.com/user/spez"
    assert result["error"] is None


def test_discover_username_url_pattern_reddit_multiple():
    """Test discover_username_url_pattern with Reddit using multiple usernames."""
    result = discover_username_url_pattern(
        domain="reddit.com",
        existing_username=["spez", "kn0thing"],
        brave_api_key=get_brave_api_key(),
    )
    
    assert result["success"] is True
    assert result["domain"] == "reddit.com"
    # Normalized to no trailing slash
    assert result["url_pattern"] == "https://www.reddit.com/user/{username}"
    assert result["example_url"] == "https://www.reddit.com/user/spez"
    assert result["error"] is None


def test_discover_username_url_pattern_reddit_nonexistent():
    """Test discover_username_url_pattern fails with non-existent Reddit username."""
    result = discover_username_url_pattern(
        domain="reddit.com",
        existing_username="this_username_definitely_does_not_exist_12345",
        brave_api_key=get_brave_api_key(),
    )
    
    assert result["success"] is False
    assert result["url_pattern"] is None
    assert result["error"] is not None


def test_discover_username_url_pattern_reddit_mixed_existing_nonexistent():
    """Test discover_username_url_pattern fails with mixed existing and non-existent Reddit usernames."""
    result = discover_username_url_pattern(
        domain="reddit.com",
        existing_username=["spez", "this_username_definitely_does_not_exist_12345"],
        brave_api_key=get_brave_api_key(),
    )
    
    assert result["success"] is False
    assert result["url_pattern"] is None
    assert result["error"] is not None

