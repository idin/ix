"""
Extract domain from URLs.
"""

from typing import Optional
from urllib.parse import urlparse


def extract_domain(url: str, remove_www: bool = True) -> Optional[str]:
    """
    Extract the domain from a URL.
    
    Handles various URL formats including:
    - Full URLs: https://www.example.com/path
    - URLs with placeholders: https://github.com/{username}
    - URLs without scheme: www.example.com/path
    - Just domains: example.com
    
    Args:
        url: The URL to extract the domain from.
        remove_www: If True, removes "www." prefix from the domain. Default: True.
    
    Returns:
        The extracted domain, or None if extraction failed.
    
    Examples:
        >>> extract_domain("https://www.github.com/user/octocat")
        'github.com'
        
        >>> extract_domain("https://github.com/{username}")
        'github.com'
        
        >>> extract_domain("www.example.com/path")
        'example.com'
        
        >>> extract_domain("example.com")
        'example.com'
    """
    if not url or not isinstance(url, str):
        return None
    
    url = url.strip()
    
    # If URL doesn't have a scheme, add one temporarily for parsing
    if not url.startswith(("http://", "https://")):
        test_url = "https://" + url
    else:
        test_url = url
    
    try:
        parsed = urlparse(test_url)
        domain = parsed.netloc
        
        # If netloc is empty, try parsing the path as domain (for cases like "example.com")
        if not domain:
            # Remove leading slashes and get first part
            path_parts = parsed.path.lstrip("/").split("/")
            if path_parts and path_parts[0]:
                domain = path_parts[0]
            else:
                # Try the original URL as domain
                domain = url.split("/")[0].split("?")[0].split("#")[0]
        
        if not domain:
            return None
        
        # Remove www. prefix if requested
        if remove_www and domain.lower().startswith("www."):
            domain = domain[4:]
        
        return domain.lower()
    except Exception:
        return None

