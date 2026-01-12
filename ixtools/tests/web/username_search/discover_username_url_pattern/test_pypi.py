"""
Tests for discover_username_url_pattern with PyPI.
"""

from tests.api_keys import get_brave_api_key
from ixtools.web import discover_username_url_pattern


def test_discover_username_url_pattern_pypi_single():
    """Test discover_username_url_pattern with PyPI using a single username."""
    result = discover_username_url_pattern(
        domain="pypi.org",
        existing_username="idin",
        brave_api_key=get_brave_api_key(),
    )
    
    assert result["success"] is True
    assert result["domain"] == "pypi.org"
    assert result["url_pattern"] == "https://pypi.org/user/{username}"
    assert result["example_url"] == "https://pypi.org/user/idin"
    assert result["error"] is None


def test_discover_username_url_pattern_pypi_multiple():
    """Test discover_username_url_pattern with PyPI using multiple usernames."""
    result = discover_username_url_pattern(
        domain="pypi.org",
        existing_username=["idin", "guido"],
        brave_api_key=get_brave_api_key(),
    )
    
    assert result["success"] is True
    assert result["domain"] == "pypi.org"
    assert result["url_pattern"] == "https://pypi.org/user/{username}"
    assert result["example_url"] == "https://pypi.org/user/idin"
    assert result["error"] is None


def test_discover_username_url_pattern_pypi_nonexistent():
    """Test discover_username_url_pattern fails with non-existent PyPI username."""
    result = discover_username_url_pattern(
        domain="pypi.org",
        existing_username="this-username-definitely-does-not-exist-12345",
        brave_api_key=get_brave_api_key(),
    )
    
    assert result["success"] is False
    assert result["url_pattern"] is None
    assert result["error"] is not None


def test_discover_username_url_pattern_pypi_mixed_existing_nonexistent():
    """Test discover_username_url_pattern fails with mixed existing and non-existent PyPI usernames."""
    result = discover_username_url_pattern(
        domain="pypi.org",
        existing_username=["idin", "this-username-definitely-does-not-exist-12345"],
        brave_api_key=get_brave_api_key(),
    )
    
    assert result["success"] is False
    assert result["url_pattern"] is None
    assert result["error"] is not None

