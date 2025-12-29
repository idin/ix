"""
Tests for discover_username_signature function (public API).
"""

from ixmachina.tools.web import discover_username_signature
from tests.api_keys import get_brave_api_key


def test_discover_username_signature_with_url_pattern_github():
    """Test discover_username_signature with GitHub URL pattern."""
    result = discover_username_signature(
        url_pattern="https://github.com/{username}",
    )
    
    assert result["success"] is True
    assert result["domain"] == "github.com"
    assert result["url_pattern"] == "https://github.com/{username}"
    assert result["existing_signature"] is not None
    assert result["non_existing_signature"] is not None
    assert result["distinguishing_factors"] is not None
    assert len(result["distinguishing_factors"]) > 0
    assert result["error"] is None


def test_discover_username_signature_with_domain_github():
    """Test discover_username_signature with GitHub domain (should discover pattern first)."""
    result = discover_username_signature(
        domain="github.com",
        brave_api_key=get_brave_api_key(),
    )
    
    assert result["success"] is True
    assert result["domain"] == "github.com"
    assert result["url_pattern"] is not None
    assert "{username}" in result["url_pattern"]
    assert result["existing_signature"] is not None
    assert result["non_existing_signature"] is not None
    assert result["distinguishing_factors"] is not None
    assert len(result["distinguishing_factors"]) > 0
    assert result["error"] is None


def test_discover_username_signature_with_domain_reddit():
    """Test discover_username_signature with Reddit domain."""
    result = discover_username_signature(
        domain="reddit.com",
        brave_api_key=get_brave_api_key(),
    )
    
    assert result["success"] is True
    assert result["domain"] == "reddit.com"
    assert result["url_pattern"] is not None
    assert "{username}" in result["url_pattern"]
    assert result["existing_signature"] is not None
    assert result["non_existing_signature"] is not None
    assert result["distinguishing_factors"] is not None
    assert len(result["distinguishing_factors"]) > 0
    assert result["error"] is None


def test_discover_username_signature_with_url_pattern_pypi():
    """Test discover_username_signature with PyPI URL pattern."""
    result = discover_username_signature(
        url_pattern="https://pypi.org/user/{username}/",
    )
    
    assert result["success"] is True
    assert result["domain"] == "pypi.org"
    assert result["url_pattern"] == "https://pypi.org/user/{username}/"
    assert result["existing_signature"] is not None
    assert result["non_existing_signature"] is not None
    assert result["distinguishing_factors"] is not None
    assert len(result["distinguishing_factors"]) > 0
    assert result["error"] is None


def test_discover_username_signature_with_domain_and_existing_username():
    """Test discover_username_signature with domain and explicit existing username."""
    result = discover_username_signature(
        domain="github.com",
        existing_username="octocat",
        brave_api_key=get_brave_api_key(),
    )
    
    assert result["success"] is True
    assert result["domain"] == "github.com"
    assert result["url_pattern"] is not None
    assert result["existing_signature"] is not None
    assert result["non_existing_signature"] is not None
    assert result["distinguishing_factors"] is not None
    assert len(result["distinguishing_factors"]) > 0
    assert result["error"] is None


def test_discover_username_signature_with_url_pattern_and_existing_username():
    """Test discover_username_signature with URL pattern and explicit existing username."""
    result = discover_username_signature(
        url_pattern="https://github.com/{username}",
        existing_username="octocat",
    )
    
    assert result["success"] is True
    assert result["domain"] == "github.com"
    assert result["url_pattern"] == "https://github.com/{username}"
    assert result["existing_signature"] is not None
    assert result["non_existing_signature"] is not None
    assert result["distinguishing_factors"] is not None
    assert len(result["distinguishing_factors"]) > 0
    assert result["error"] is None


def test_discover_username_signature_neither_domain_nor_url_pattern():
    """Test discover_username_signature fails when neither domain nor url_pattern is provided."""
    result = discover_username_signature()
    
    assert result["success"] is False
    assert result["domain"] is None
    assert result["url_pattern"] is None
    assert result["error"] is not None
    assert "Either domain or url_pattern must be provided" in result["error"]


def test_discover_username_signature_both_domain_and_url_pattern():
    """Test discover_username_signature when both domain and url_pattern are provided (url_pattern takes precedence)."""
    result = discover_username_signature(
        domain="github.com",
        url_pattern="https://github.com/{username}",
    )
    
    # Should use url_pattern directly, not discover from domain
    assert result["success"] is True
    assert result["domain"] == "github.com"
    assert result["url_pattern"] == "https://github.com/{username}"
    assert result["existing_signature"] is not None
    assert result["non_existing_signature"] is not None
    assert result["error"] is None


def test_discover_username_signature_with_unknown_domain():
    """Test discover_username_signature with unknown domain (no known usernames)."""
    result = discover_username_signature(
        url_pattern="https://unknown-domain-12345.com/{username}",
    )
    
    assert result["success"] is False
    assert result["domain"] == "unknown-domain-12345.com"
    assert result["url_pattern"] == "https://unknown-domain-12345.com/{username}"
    assert result["error"] is not None
    assert "No known existing usernames" in result["error"]


def test_discover_username_signature_with_unknown_domain_but_existing_username():
    """Test discover_username_signature with unknown domain but providing existing username."""
    result = discover_username_signature(
        url_pattern="https://github.com/{username}",
        existing_username="octocat",
    )
    
    # Should succeed even if domain is not in known list, since we provided existing_username
    assert result["success"] is True
    assert result["domain"] == "github.com"
    assert result["url_pattern"] == "https://github.com/{username}"
    assert result["existing_signature"] is not None
    assert result["non_existing_signature"] is not None
    assert result["error"] is None

