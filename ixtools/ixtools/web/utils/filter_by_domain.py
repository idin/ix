"""
Filter URLs by domain(s).

Supports both positive filtering (keep matching domains) and negative filtering
(keep non-matching domains).
"""

from typing import List, Union
from urllib.parse import urlparse


def filter_by_domain(
    urls: List[str],
    domains: Union[str, List[str]],
    filter_type: str = "include",
) -> List[str]:
    """
    Filter URLs by domain(s).
    
    Args:
        urls: List of URLs to filter.
        domains: Domain(s) to filter by. Can be a single domain string or a list of domains.
                Examples: "github.com" or ["github.com", "stackoverflow.com"].
        filter_type: Type of filter to apply. Options: "include" (keep matching domains) or
                    "exclude" (keep non-matching domains). Default: "include".
    
    Returns:
        Filtered list of URLs.
    
    Examples:
        >>> urls = ["https://github.com/user", "https://stackoverflow.com/question", "https://example.com/page"]
        >>> filter_by_domain(urls, "github.com", filter_type="include")
        ["https://github.com/user"]
        
        >>> filter_by_domain(urls, ["github.com", "stackoverflow.com"], filter_type="include")
        ["https://github.com/user", "https://stackoverflow.com/question"]
        
        >>> filter_by_domain(urls, "github.com", filter_type="exclude")
        ["https://stackoverflow.com/question", "https://example.com/page"]
    """
    if filter_type not in ["include", "exclude"]:
        raise ValueError(f'filter_type must be "include" or "exclude", got "{filter_type}"')
    
    # Normalize domains to a list
    if isinstance(domains, str):
        domains_list = [domains]
    else:
        domains_list = domains
    
    # Normalize domains to lowercase for comparison
    domains_lower = [domain.lower().strip() for domain in domains_list]
    
    filtered_urls = []
    
    for url in urls:
        if not url:
            continue
        
        try:
            parsed_url = urlparse(url)
            url_domain = parsed_url.netloc.lower()
            
            # Check if URL domain matches any of the filter domains
            # Match if any filter domain is contained in the URL domain (handles subdomains)
            matches = any(filter_domain in url_domain for filter_domain in domains_lower)
            
            # Include or exclude based on filter_type
            if filter_type == "include" and matches:
                filtered_urls.append(url)
            elif filter_type == "exclude" and not matches:
                filtered_urls.append(url)
        except Exception:
            # If URL parsing fails, skip it
            continue
    
    return filtered_urls

