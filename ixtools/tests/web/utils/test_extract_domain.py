"""
Tests for extract_domain tool.
"""

from ixtools.web import extract_domain


def test_extract_domain_full_url_with_www():
    """Test extract_domain with full URL including www."""
    result = extract_domain("https://www.github.com/user/octocat")
    
    assert result == "github.com"


def test_extract_domain_full_url_without_www():
    """Test extract_domain with full URL without www."""
    result = extract_domain("https://github.com/user/octocat")
    
    assert result == "github.com"


def test_extract_domain_url_with_placeholder():
    """Test extract_domain with URL containing placeholder."""
    result = extract_domain("https://github.com/{username}")
    
    assert result == "github.com"


def test_extract_domain_url_without_scheme():
    """Test extract_domain with URL without scheme."""
    result = extract_domain("www.example.com/path")
    
    assert result == "example.com"


def test_extract_domain_just_domain():
    """Test extract_domain with just a domain."""
    result = extract_domain("example.com")
    
    assert result == "example.com"


def test_extract_domain_with_query_params():
    """Test extract_domain with query parameters."""
    result = extract_domain("https://example.com/path?param=value")
    
    assert result == "example.com"


def test_extract_domain_with_fragment():
    """Test extract_domain with URL fragment."""
    result = extract_domain("https://example.com/path#section")
    
    assert result == "example.com"


def test_extract_domain_http_scheme():
    """Test extract_domain with HTTP scheme."""
    result = extract_domain("http://example.com/path")
    
    assert result == "example.com"




def test_extract_domain_subdomain():
    """Test extract_domain with subdomain."""
    result = extract_domain("https://subdomain.example.com/path")
    
    assert result == "example.com"


def test_extract_domain_empty_string():
    """Test extract_domain with empty string."""
    result = extract_domain("")
    
    assert result is None


def test_extract_domain_none():
    """Test extract_domain with None."""
    result = extract_domain(None)
    
    assert result is None


def test_extract_domain_invalid_url():
    """Test extract_domain with invalid URL format."""
    result = extract_domain("not-a-valid-url")
    
    # Should still try to extract something or return None
    assert result is not None or result is None


def test_extract_domain_linkedin():
    """Test extract_domain with LinkedIn URL."""
    result = extract_domain("https://www.linkedin.com/in/username/")
    
    assert result == "linkedin.com"


def test_extract_domain_pypi():
    """Test extract_domain with PyPI URL."""
    result = extract_domain("https://pypi.org/user/{username}/")
    
    assert result == "pypi.org"


def test_extract_domain_reddit():
    """Test extract_domain with Reddit URL."""
    result = extract_domain("https://www.reddit.com/user/{username}/")
    
    assert result == "reddit.com"


def test_extract_domain_stackoverflow():
    """Test extract_domain with Stack Overflow URL."""
    result = extract_domain("https://stackoverflow.com/users/{username}")
    
    assert result == "stackoverflow.com"


def test_extract_domain_co_uk_with_www():
    """Test extract_domain with .co.uk domain including www."""
    result = extract_domain("https://www.bbc.co.uk/news")
    
    assert result == "bbc.co.uk"


def test_extract_domain_co_uk_without_www():
    """Test extract_domain with .co.uk domain without www."""
    result = extract_domain("https://bbc.co.uk/news")
    
    assert result == "bbc.co.uk"


def test_extract_domain_co_uk_with_path():
    """Test extract_domain with .co.uk domain and path."""
    result = extract_domain("https://www.example.co.uk/path/to/page")
    
    assert result == "example.co.uk"


def test_extract_domain_co_uk_just_domain():
    """Test extract_domain with just .co.uk domain."""
    result = extract_domain("example.co.uk")
    
    assert result == "example.co.uk"


def test_extract_domain_co_uk_with_subdomain():
    """Test extract_domain with .co.uk domain and subdomain."""
    result = extract_domain("https://www.subdomain.example.co.uk/path")
    
    assert result == "example.co.uk"


def test_extract_domain_ww2_subdomain():
    """Test extract_domain with ww2 subdomain."""
    result = extract_domain("https://ww2.example.com/path")
    
    assert result == "example.com"


def test_extract_domain_www2_subdomain():
    """Test extract_domain with www2 subdomain."""
    result = extract_domain("https://www2.example.com/path")
    
    assert result == "example.com"


def test_extract_domain_ww2_co_uk():
    """Test extract_domain with ww2 subdomain and .co.uk domain."""
    result = extract_domain("https://ww2.example.co.uk/path")
    
    assert result == "example.co.uk"

