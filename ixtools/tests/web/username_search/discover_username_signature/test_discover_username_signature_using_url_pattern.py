"""
Tests for _discover_username_signature_using_url_pattern function.
"""

from ixtools.web.username_search.discover_username_signature import _discover_username_signature_using_url_pattern


def _assert_success_result_structure(result: dict) -> None:
    """
    Assert that a successful result has the correct structure with all required fields.
    
    Args:
        result: The result dictionary to validate.
    """
    assert result["success"] is True
    assert result["error"] is None
    
    # Check existing_signature structure
    assert isinstance(result["existing_signature"], dict)
    assert "status_code" in result["existing_signature"]
    assert "error_type" in result["existing_signature"]
    assert "error_message" in result["existing_signature"]
    assert "content_keywords" in result["existing_signature"]
    assert isinstance(result["existing_signature"]["content_keywords"], list)
    
    # Check non_existing_signature structure
    assert isinstance(result["non_existing_signature"], dict)
    assert "status_code" in result["non_existing_signature"]
    assert "error_type" in result["non_existing_signature"]
    assert "error_message" in result["non_existing_signature"]
    assert "content_keywords" in result["non_existing_signature"]
    assert isinstance(result["non_existing_signature"]["content_keywords"], list)
    
    # Check distinguishing_factors
    assert isinstance(result["distinguishing_factors"], list)
    assert len(result["distinguishing_factors"]) > 0


def test_discover_username_signature_using_url_pattern_github():
    """Test _discover_username_signature_using_url_pattern with GitHub."""
    result = _discover_username_signature_using_url_pattern(
        url_pattern="https://github.com/{username}",
    )
    
    assert result["domain"] == "github.com"
    assert result["url_pattern"] == "https://github.com/{username}"
    _assert_success_result_structure(result=result)


def test_discover_username_signature_using_url_pattern_github_with_existing_username():
    """Test _discover_username_signature_using_url_pattern with GitHub using explicit existing username."""
    result = _discover_username_signature_using_url_pattern(
        url_pattern="https://github.com/{username}",
        existing_username="octocat",
    )
    
    assert result["domain"] == "github.com"
    assert result["url_pattern"] == "https://github.com/{username}"
    _assert_success_result_structure(result=result)


def test_discover_username_signature_using_url_pattern_github_multiple_existing_usernames():
    """Test _discover_username_signature_using_url_pattern with GitHub using multiple existing usernames."""
    result = _discover_username_signature_using_url_pattern(
        url_pattern="https://github.com/{username}",
        existing_username=["octocat", "torvalds"],
    )
    
    assert result["domain"] == "github.com"
    assert result["url_pattern"] == "https://github.com/{username}"
    _assert_success_result_structure(result=result)


def test_discover_username_signature_using_url_pattern_pypi():
    """Test _discover_username_signature_using_url_pattern with PyPI."""
    result = _discover_username_signature_using_url_pattern(
        url_pattern="https://pypi.org/user/{username}/",
    )
    
    assert result["domain"] == "pypi.org"
    assert result["url_pattern"] == "https://pypi.org/user/{username}/"
    _assert_success_result_structure(result=result)


def test_discover_username_signature_using_url_pattern_reddit():
    """Test _discover_username_signature_using_url_pattern with Reddit."""
    result = _discover_username_signature_using_url_pattern(
        url_pattern="https://www.reddit.com/user/{username}/",
    )
    
    assert result["domain"] == "reddit.com"
    assert result["url_pattern"] == "https://www.reddit.com/user/{username}/"
    _assert_success_result_structure(result=result)


def test_discover_username_signature_using_url_pattern_stackoverflow():
    """Test _discover_username_signature_using_url_pattern with Stack Overflow."""
    result = _discover_username_signature_using_url_pattern(
        url_pattern="https://stackoverflow.com/users/{username}",
    )
    
    assert result["domain"] == "stackoverflow.com"
    assert result["url_pattern"] == "https://stackoverflow.com/users/{username}"
    _assert_success_result_structure(result=result)


def test_discover_username_signature_using_url_pattern_gitlab():
    """Test _discover_username_signature_using_url_pattern with GitLab."""
    result = _discover_username_signature_using_url_pattern(
        url_pattern="https://gitlab.com/{username}",
    )
    
    assert result["domain"] == "gitlab.com"
    assert result["url_pattern"] == "https://gitlab.com/{username}"
    _assert_success_result_structure(result=result)


def test_discover_username_signature_using_url_pattern_linkedin():
    """Test _discover_username_signature_using_url_pattern with LinkedIn."""
    result = _discover_username_signature_using_url_pattern(
        url_pattern="https://www.linkedin.com/in/{username}/",
    )
    
    assert result["domain"] == "linkedin.com"
    assert result["url_pattern"] == "https://www.linkedin.com/in/{username}/"
    
    # LinkedIn may block requests (HTTP 999), so handle both success and blocking cases
    if not result["success"]:
        # If blocked, verify the error indicates the issue
        assert "error" in result
        assert result["error"] is not None
        # Skip the structure assertion if LinkedIn is blocking
        return
    
    _assert_success_result_structure(result=result)


def test_discover_username_signature_using_url_pattern_invalid_url_pattern():
    """Test _discover_username_signature_using_url_pattern with invalid URL pattern."""
    result = _discover_username_signature_using_url_pattern(
        url_pattern="not-a-valid-url-pattern",
    )
    
    assert result["success"] is False
    assert result["domain"] is None
    assert result["url_pattern"] == "not-a-valid-url-pattern"
    assert result["existing_signature"] is None
    assert result["non_existing_signature"] is None
    assert isinstance(result["distinguishing_factors"], list)
    assert len(result["distinguishing_factors"]) == 0
    assert isinstance(result["error"], str)
    assert len(result["error"]) > 0
    assert "Could not extract domain" in result["error"]


def test_discover_username_signature_using_url_pattern_unknown_domain():
    """Test _discover_username_signature_using_url_pattern with unknown domain (no known usernames)."""
    result = _discover_username_signature_using_url_pattern(
        url_pattern="https://unknown-domain-12345.com/{username}",
    )
    
    assert result["success"] is False
    assert result["domain"] == "unknown-domain-12345.com"
    assert result["url_pattern"] == "https://unknown-domain-12345.com/{username}"
    assert result["existing_signature"] is None
    assert result["non_existing_signature"] is None
    assert isinstance(result["distinguishing_factors"], list)
    assert len(result["distinguishing_factors"]) == 0
    assert isinstance(result["error"], str)
    assert len(result["error"]) > 0
    assert "No known existing usernames" in result["error"]


def test_discover_username_signature_using_url_pattern_with_existing_username_parameter():
    """Test _discover_username_signature_using_url_pattern with explicit existing username parameter."""
    # Test that providing existing_username parameter works correctly
    result = _discover_username_signature_using_url_pattern(
        url_pattern="https://github.com/{username}",
        existing_username="octocat",
    )
    
    # Should succeed when existing username is provided
    assert result["domain"] == "github.com"
    assert result["url_pattern"] == "https://github.com/{username}"
    _assert_success_result_structure(result=result)


def test_discover_username_signature_using_url_pattern_with_custom_non_existing_username():
    """Test _discover_username_signature_using_url_pattern with custom non-existing username."""
    result = _discover_username_signature_using_url_pattern(
        url_pattern="https://github.com/{username}",
        non_existing_username="definitely-does-not-exist-12345",
    )
    
    assert result["domain"] == "github.com"
    assert result["url_pattern"] == "https://github.com/{username}"
    _assert_success_result_structure(result=result)

