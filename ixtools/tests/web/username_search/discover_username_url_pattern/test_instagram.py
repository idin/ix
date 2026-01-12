"""
Tests for discover_username_url_pattern with Instagram.
"""

from tests.api_keys import get_brave_api_key
from ixtools.web import discover_username_url_pattern


def test_discover_username_url_pattern_instagram_single():
    """Test discover_username_url_pattern with Instagram using a single username."""
    result = discover_username_url_pattern(
        domain="instagram.com",
        existing_username="instagram",
        brave_api_key=get_brave_api_key(),
    )
    
    assert result["success"] is True
    assert result["domain"] == "instagram.com"
    # Instagram URLs can be with or without www, and with or without trailing slash
    assert result["url_pattern"] in [
        "https://www.instagram.com/{username}/",
        "https://www.instagram.com/{username}",
        "https://instagram.com/{username}/",
        "https://instagram.com/{username}",
    ]
    assert result["example_url"] in [
        "https://www.instagram.com/instagram/",
        "https://www.instagram.com/instagram",
        "https://instagram.com/instagram/",
        "https://instagram.com/instagram",
    ]
    assert result["method"] is not None
    assert result["error"] is None


def test_discover_username_url_pattern_instagram_multiple():
    """Test discover_username_url_pattern with Instagram using multiple usernames."""
    result = discover_username_url_pattern(
        domain="instagram.com",
        existing_username=["instagram", "cristiano"],
        brave_api_key=get_brave_api_key(),
    )
    
    assert result["success"] is True
    assert result["domain"] == "instagram.com"
    # Instagram URLs can be with or without www, and with or without trailing slash
    assert result["url_pattern"] in [
        "https://www.instagram.com/{username}/",
        "https://www.instagram.com/{username}",
        "https://instagram.com/{username}/",
        "https://instagram.com/{username}",
    ]
    assert result["example_url"] in [
        "https://www.instagram.com/instagram/",
        "https://www.instagram.com/instagram",
        "https://instagram.com/instagram/",
        "https://instagram.com/instagram",
    ]
    assert result["method"] is not None
    assert result["error"] is None


def test_discover_username_url_pattern_instagram_nonexistent():
    """Test discover_username_url_pattern fails with non-existent Instagram username."""
    result = discover_username_url_pattern(
        domain="instagram.com",
        existing_username="this-username-definitely-does-not-exist-12345",
        brave_api_key=get_brave_api_key(),
    )
    
    assert result["success"] is False
    assert result["url_pattern"] is None
    assert result["error"] is not None


def test_discover_username_url_pattern_instagram_mixed_existing_nonexistent():
    """Test discover_username_url_pattern fails with mixed existing and non-existent Instagram usernames."""
    result = discover_username_url_pattern(
        domain="instagram.com",
        existing_username=["instagram", "this-username-definitely-does-not-exist-12345"],
        brave_api_key=get_brave_api_key(),
    )
    
    assert result["success"] is False
    assert result["url_pattern"] is None
    assert result["error"] is not None

