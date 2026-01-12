"""
Common tests for discover_username_url_pattern (not specific to any website).
"""

from tests.api_keys import get_brave_api_key
from ixtools.web import discover_username_url_pattern


def test_discover_username_url_pattern_empty_username_list():
    """Test discover_username_url_pattern fails with empty username list."""
    result = discover_username_url_pattern(
        domain="github.com",
        existing_username=[],
    )
    
    assert result["success"] is False
    assert result["url_pattern"] is None
    assert result["error"] is not None
    assert "At least one username must be provided" in result["error"]


def test_discover_username_url_pattern_invalid_domain():
    """Test discover_username_url_pattern with invalid domain."""
    result = discover_username_url_pattern(
        domain="this-domain-definitely-does-not-exist-12345.com",
        existing_username="testuser",
        timeout=2,
        brave_api_key=get_brave_api_key(),
    )
    
    # Should fail because domain doesn't exist
    assert result["success"] is False
    assert result["url_pattern"] is None
    assert result["error"] is not None

