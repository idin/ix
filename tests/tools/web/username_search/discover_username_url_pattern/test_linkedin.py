"""
Tests for discover_username_url_pattern with LinkedIn.
"""

from conftest import get_brave_api_key
from ixmachina.tools.web import discover_username_url_pattern


def test_discover_username_url_pattern_linkedin_single():
    """Test discover_username_url_pattern with LinkedIn using a single username."""
    result = discover_username_url_pattern(
        domain="linkedin.com",
        existing_username="reidhoffman",
        brave_api_key=get_brave_api_key(),
    )
    
    assert result["success"] is True
    assert result["domain"] == "linkedin.com"
    # Accept both with and without trailing slash (both work)
    assert result["url_pattern"] in ["https://www.linkedin.com/in/{username}/", "https://www.linkedin.com/in/{username}"]
    assert result["example_url"] in ["https://www.linkedin.com/in/reidhoffman/", "https://www.linkedin.com/in/reidhoffman"]
    assert result["error"] is None


def test_discover_username_url_pattern_linkedin_multiple():
    """Test discover_username_url_pattern with LinkedIn using multiple usernames."""
    result = discover_username_url_pattern(
        domain="linkedin.com",
        existing_username=["reidhoffman", "jeffweiner08"],
        brave_api_key=get_brave_api_key(),
    )
    
    assert result["success"] is True
    assert result["domain"] == "linkedin.com"
    # Accept both with and without trailing slash (both work)
    assert result["url_pattern"] in ["https://www.linkedin.com/in/{username}/", "https://www.linkedin.com/in/{username}"]
    assert result["example_url"] in ["https://www.linkedin.com/in/reidhoffman/", "https://www.linkedin.com/in/reidhoffman"]
    assert result["error"] is None


def test_discover_username_url_pattern_linkedin_nonexistent():
    """Test discover_username_url_pattern fails with non-existent LinkedIn username."""
    result = discover_username_url_pattern(
        domain="linkedin.com",
        existing_username="this-username-definitely-does-not-exist-12345",
        brave_api_key=get_brave_api_key(),
    )
    
    assert result["success"] is False
    assert result["url_pattern"] is None
    assert result["error"] is not None


def test_discover_username_url_pattern_linkedin_mixed_existing_nonexistent():
    """Test discover_username_url_pattern fails with mixed existing and non-existent LinkedIn usernames."""
    result = discover_username_url_pattern(
        domain="linkedin.com",
        existing_username=["reidhoffman", "this-username-definitely-does-not-exist-12345"],
        brave_api_key=get_brave_api_key(),
    )
    
    assert result["success"] is False
    assert result["url_pattern"] is None
    assert result["error"] is not None

