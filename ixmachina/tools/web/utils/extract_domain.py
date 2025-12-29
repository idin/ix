"""
Extract domain from URLs.
"""

from typing import Optional
from urllib.parse import urlparse


def extract_domain(url: str) -> Optional[str]:
    """
    Extract the normalized domain from a URL.
    
    Always returns lowercase domain with www. removed. Handles multi-level
    domains like bbc.co.uk correctly.
    
    Handles various URL formats including:
    - Full URLs: https://www.example.com/path
    - URLs with placeholders: https://github.com/{username}
    - URLs without scheme: www.example.com/path
    - Just domains: example.com
    - Multi-level domains: bbc.co.uk, example.co.uk
    
    Args:
        url: The URL to extract the domain from.
    
    Returns:
        The extracted normalized domain (lowercase, no www, no slashes),
        or None if extraction failed.
    
    Examples:
        >>> extract_domain("https://www.github.com/user/octocat")
        'github.com'
        
        >>> extract_domain("https://github.com/{username}")
        'github.com'
        
        >>> extract_domain("www.example.com/path")
        'example.com'
        
        >>> extract_domain("example.com")
        'example.com'
        
        >>> extract_domain("https://www.bbc.co.uk/news")
        'bbc.co.uk'
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
        
        domain_lower = domain.lower()
        
        # Remove common subdomain prefixes (www, ww2, www2, etc.)
        # Handle patterns like www.domain.com, ww2.domain.com, www2.domain.com
        common_prefixes = ["www.", "ww2.", "www2.", "ww3.", "www3."]
        for prefix in common_prefixes:
            if domain_lower.startswith(prefix):
                domain_lower = domain_lower[len(prefix):]
                break
        
        # For other subdomains, extract base domain
        # Split by dots to get parts
        parts = domain_lower.split(".")
        
        # Handle multi-level TLDs (e.g., .co.uk, .com.au, .org.uk)
        # Common two-part TLDs
        two_part_tlds = [
            "co.uk", "com.au", "org.uk", "net.au", "gov.uk", "ac.uk",
            "co.nz", "com.br", "co.za", "com.mx", "co.jp", "com.cn"
        ]
        
        # If we have at least 3 parts and last 2 form a known two-part TLD
        if len(parts) >= 3:
            last_two = ".".join(parts[-2:])
            if last_two in two_part_tlds:
                # Return last 3 parts (domain.tld1.tld2)
                return ".".join(parts[-3:])
        
        # For standard TLDs (.com, .org, etc.), return last 2 parts (domain.tld)
        if len(parts) >= 2:
            return ".".join(parts[-2:])
        
        return domain_lower
    except Exception:
        return None

