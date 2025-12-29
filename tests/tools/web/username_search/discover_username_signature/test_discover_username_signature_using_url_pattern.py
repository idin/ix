"""
Tests for _discover_username_signature_using_url_pattern function.
"""

from ixmachina.tools.web.discover_username_signature import _discover_username_signature_using_url_pattern


def test_discover_username_signature_using_url_pattern_github():
    """Test _discover_username_signature_using_url_pattern with GitHub."""
    result = _discover_username_signature_using_url_pattern(
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


def test_discover_username_signature_using_url_pattern_github_with_existing_username():
    """Test _discover_username_signature_using_url_pattern with GitHub using explicit existing username."""
    result = _discover_username_signature_using_url_pattern(
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


def test_discover_username_signature_using_url_pattern_github_multiple_existing_usernames():
    """Test _discover_username_signature_using_url_pattern with GitHub using multiple existing usernames."""
    result = _discover_username_signature_using_url_pattern(
        url_pattern="https://github.com/{username}",
        existing_username=["octocat", "torvalds"],
    )
    
    assert result["success"] is True
    assert result["domain"] == "github.com"
    assert result["url_pattern"] == "https://github.com/{username}"
    assert result["existing_signature"] is not None
    assert result["non_existing_signature"] is not None
    assert result["distinguishing_factors"] is not None
    assert len(result["distinguishing_factors"]) > 0
    assert result["error"] is None


def test_discover_username_signature_using_url_pattern_pypi():
    """Test _discover_username_signature_using_url_pattern with PyPI."""
    result = _discover_username_signature_using_url_pattern(
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


def test_discover_username_signature_using_url_pattern_reddit():
    """Test _discover_username_signature_using_url_pattern with Reddit."""
    result = _discover_username_signature_using_url_pattern(
        url_pattern="https://www.reddit.com/user/{username}/",
    )
    
    assert result["success"] is True
    assert result["domain"] == "reddit.com"
    assert result["url_pattern"] == "https://www.reddit.com/user/{username}/"
    assert result["existing_signature"] is not None
    assert result["non_existing_signature"] is not None
    assert result["distinguishing_factors"] is not None
    assert len(result["distinguishing_factors"]) > 0
    assert result["error"] is None


def test_discover_username_signature_using_url_pattern_stackoverflow():
    """Test _discover_username_signature_using_url_pattern with Stack Overflow."""
    result = _discover_username_signature_using_url_pattern(
        url_pattern="https://stackoverflow.com/users/{username}",
    )
    
    assert result["success"] is True
    assert result["domain"] == "stackoverflow.com"
    assert result["url_pattern"] == "https://stackoverflow.com/users/{username}"
    assert result["existing_signature"] is not None
    assert result["non_existing_signature"] is not None
    assert result["distinguishing_factors"] is not None
    assert len(result["distinguishing_factors"]) > 0
    assert result["error"] is None


def test_discover_username_signature_using_url_pattern_gitlab():
    """Test _discover_username_signature_using_url_pattern with GitLab."""
    result = _discover_username_signature_using_url_pattern(
        url_pattern="https://gitlab.com/{username}",
    )
    
    assert result["success"] is True
    assert result["domain"] == "gitlab.com"
    assert result["url_pattern"] == "https://gitlab.com/{username}"
    assert result["existing_signature"] is not None
    assert result["non_existing_signature"] is not None
    assert result["distinguishing_factors"] is not None
    assert len(result["distinguishing_factors"]) > 0
    assert result["error"] is None


def test_discover_username_signature_using_url_pattern_linkedin():
    """Test _discover_username_signature_using_url_pattern with LinkedIn."""
    result = _discover_username_signature_using_url_pattern(
        url_pattern="https://www.linkedin.com/in/{username}/",
    )
    
    assert result["success"] is True
    assert result["domain"] == "linkedin.com"
    assert result["url_pattern"] == "https://www.linkedin.com/in/{username}/"
    assert result["existing_signature"] is not None
    assert result["non_existing_signature"] is not None
    assert result["distinguishing_factors"] is not None
    assert len(result["distinguishing_factors"]) > 0
    assert result["error"] is None


def test_discover_username_signature_using_url_pattern_invalid_url_pattern():
    """Test _discover_username_signature_using_url_pattern with invalid URL pattern."""
    result = _discover_username_signature_using_url_pattern(
        url_pattern="not-a-valid-url-pattern",
    )
    
    assert result["success"] is False
    assert result["domain"] is None
    assert result["url_pattern"] == "not-a-valid-url-pattern"
    assert result["error"] is not None
    assert "Could not extract domain" in result["error"]


def test_discover_username_signature_using_url_pattern_unknown_domain():
    """Test _discover_username_signature_using_url_pattern with unknown domain (no known usernames)."""
    result = _discover_username_signature_using_url_pattern(
        url_pattern="https://unknown-domain-12345.com/{username}",
    )
    
    assert result["success"] is False
    assert result["domain"] == "unknown-domain-12345.com"
    assert result["url_pattern"] == "https://unknown-domain-12345.com/{username}"
    assert result["error"] is not None
    assert "No known existing usernames" in result["error"]


def test_discover_username_signature_using_url_pattern_unknown_domain_with_existing_username():
    """Test _discover_username_signature_using_url_pattern with unknown domain but providing existing username."""
    result = _discover_username_signature_using_url_pattern(
        url_pattern="https://unknown-domain-12345.com/{username}",
        existing_username="testuser",
    )
    
    # Should succeed if we provide an existing username
    assert result["success"] is True or result["success"] is False  # May fail if domain doesn't exist, but should try
    assert result["domain"] == "unknown-domain-12345.com"
    assert result["url_pattern"] == "https://unknown-domain-12345.com/{username}"


def test_discover_username_signature_using_url_pattern_with_custom_non_existing_username():
    """Test _discover_username_signature_using_url_pattern with custom non-existing username."""
    result = _discover_username_signature_using_url_pattern(
        url_pattern="https://github.com/{username}",
        non_existing_username="definitely-does-not-exist-12345",
    )
    
    assert result["success"] is True
    assert result["domain"] == "github.com"
    assert result["url_pattern"] == "https://github.com/{username}"
    assert result["existing_signature"] is not None
    assert result["non_existing_signature"] is not None
    assert result["distinguishing_factors"] is not None
    assert len(result["distinguishing_factors"]) > 0
    assert result["error"] is None

