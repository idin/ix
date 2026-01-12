"""
Discover the URL pattern for username pages on a domain using web search.

IMPORTANT: NO WEBSITE SPECIFIC LOGIC IS ALLOWED.
This function must work generically for any domain without hardcoding
domain-specific behavior (e.g., no "if domain == 'pypi.org'" checks).
"""

from typing import Dict, Optional, Any, List, Union
from ..fetch.check_url_status import check_url_status
from ..search import search_web
from ..fetch.fetch_url import fetch_url
from ixutils import persist
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .url_validation import is_valid_username_url, normalize_trailing_slash
from .url_filtering import filter_project_urls_if_user_urls_present
from .pattern_extraction import extract_pattern_from_urls


@persist(expire_seconds=30 * 24 * 60 * 60)
def discover_username_url_pattern(
    domain: str,
    existing_username: Union[str, List[str]],
    timeout: Optional[int] = 10,
    brave_api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Discover the URL pattern for username pages on a domain by searching the web.
    
    Uses multiple search strategies to find the URL pattern:
    1. Search for the specific username(s) on the domain (site:domain.com username)
    2. Search for documentation about the domain's username URL format
    3. Search for examples of user profiles on the domain
    
    Validates that found URLs contain the exact domain and exact username.
    If multiple usernames are provided, verifies they all produce the same pattern.
    
    Args:
        domain: The domain to discover the pattern for (e.g., "github.com", "github.ca").
        existing_username: A username or list of usernames known to exist on this domain.
                          If multiple usernames are provided, all must match the same pattern.
        timeout: Request timeout in seconds. Default: 10.
        brave_api_key: Optional Brave API key. If not provided, will try to get from BRAVE_API_KEY environment variable.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if pattern discovery was successful
            - domain: The domain that was checked
            - url_pattern: The discovered URL pattern with {username} placeholder
                          (e.g., "https://github.com/{username}")
            - example_url: An example URL with the first username filled in
            - method: How the pattern was discovered ("search_username", "search_docs", "search_examples", or "combined")
            - error: Error message if discovery failed (None if successful)
    """
    # Normalize to list
    if isinstance(existing_username, str):
        usernames = [existing_username]
    else:
        usernames = existing_username
    
    if not usernames:
        return {
            "success": False,
            "domain": domain.lower().strip(),
            "url_pattern": None,
            "example_url": None,
            "method": None,
            "error": "At least one username must be provided.",
        }
    
    domain_lower = domain.lower().strip()
    usernames_lower = [u.lower() for u in usernames]
    
    # Normalize domain (remove www. if present, but keep it for matching)
    domain_for_matching = domain_lower
    if domain_for_matching.startswith("www."):
        domain_for_matching = domain_for_matching[4:]
    
    found_urls = []
    methods_used = []
    found_usernames = set()
    
    # Search for profile URLs for each username
    for i, username_lower in enumerate(usernames_lower):
        if username_lower in found_usernames:
            continue  # Already found this username
        
        # Get the original username (preserve case) for the search
        original_username = usernames[i] if i < len(usernames) else username_lower
        
        # Search for the username on the domain
        query = f'site:{domain_lower} {original_username}'
        search_result = search_web(query=query, max_results=20, search_engine="brave", brave_api_key=brave_api_key)
        
        if not search_result.get("success") or not search_result.get("results"):
            continue
        
        # Filter out "project" URLs if "user" URLs are present
        results = filter_project_urls_if_user_urls_present(search_result["results"])
        
        # Check direct search result URLs
        for result in results:
            url = result.get("url", "")
            if not url:
                continue
            
            if is_valid_username_url(url, domain_for_matching, username_lower):
                validation = check_url_status(url=url, timeout=timeout)
                status_code = validation.get("status_code")
                if validation.get("success") and status_code in [200, 999, 403]:
                    found_urls.append(url)
                    found_usernames.add(username_lower)
                    if "search_direct" not in methods_used:
                        methods_used.append("search_direct")
                    break
        
        # If not found in direct results, fetch pages and extract links
        if username_lower not in found_usernames:
            for result in results:
                page_url = result.get("url", "")
                if not page_url:
                    continue
                
                page_response = fetch_url(url=page_url, timeout=timeout)
                if not page_response.get("success") or not page_response.get("content"):
                    continue
                
                try:
                    soup = BeautifulSoup(page_response["content"], "html.parser")
                    for link in soup.find_all("a", href=True):
                        href = link.get("href", "")
                        if not href:
                            continue
                        
                        if href.startswith("/") or not href.startswith("http"):
                            href = urljoin(page_url, href)
                        
                        if is_valid_username_url(href, domain_for_matching, username_lower):
                            validation = check_url_status(url=href, timeout=timeout)
                            status_code = validation.get("status_code")
                            if validation.get("success") and status_code in [200, 999, 403]:
                                found_urls.append(href)
                                found_usernames.add(username_lower)
                                if "search_page_links" not in methods_used:
                                    methods_used.append("search_page_links")
                                break
                except Exception:
                    continue
                
                if username_lower in found_usernames:
                    break
    
    # If we found URLs, extract the pattern
    if found_urls:
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in found_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        # Extract patterns for each username
        patterns_by_username = {}
        for username_lower in usernames_lower:
            # Get URLs that match this username
            matching_urls = [
                url for url in unique_urls
                if is_valid_username_url(url, domain_for_matching, username_lower)
            ]
            
            if matching_urls:
                pattern = extract_pattern_from_urls(matching_urls, username_lower)
                if pattern:
                    patterns_by_username[username_lower] = pattern
        
        if not patterns_by_username:
            return {
                "success": False,
                "domain": domain_lower,
                "url_pattern": None,
                "example_url": None,
                "method": None,
                "error": "Could not extract URL pattern from found URLs.",
            }
        
        # Check that we have patterns for ALL usernames
        if len(patterns_by_username) < len(usernames_lower):
            missing_usernames = [u for u in usernames_lower if u not in patterns_by_username]
            return {
                "success": False,
                "domain": domain_lower,
                "url_pattern": None,
                "example_url": None,
                "method": None,
                "error": (
                    f"Could not find profile URLs for username(s): {', '.join(missing_usernames)}. "
                    "All provided usernames must have valid profile URLs."
                ),
            }
        
        # Normalize all patterns (remove trailing slashes) before comparison
        normalized_patterns = {}
        for username_lower, pattern in patterns_by_username.items():
            normalized_pattern = normalize_trailing_slash(pattern)
            normalized_patterns[username_lower] = normalized_pattern
        
        # Verify all usernames produce the same pattern (after normalization)
        unique_patterns = set(normalized_patterns.values())
        if len(unique_patterns) > 1:
            return {
                "success": False,
                "domain": domain_lower,
                "url_pattern": None,
                "example_url": None,
                "method": None,
                "error": (
                    f"Multiple different patterns found for usernames. "
                    f"Patterns: {', '.join(unique_patterns)}. "
                    f"All usernames must match the same pattern."
                ),
            }
        
        # All usernames match the same pattern (use normalized version)
        pattern = list(unique_patterns)[0]
        
        # Validate the pattern by checking if it works for all usernames
        for username in usernames:
            test_url = pattern.replace("{username}", username)
            # Normalize test URL for validation (remove trailing slash)
            test_url = normalize_trailing_slash(test_url)
            validation = check_url_status(url=test_url, timeout=timeout)
            
            status_code = validation.get("status_code")
            # Accept 200 (success) and 999 (bot detection/rate limiting - site exists but blocking)
            # Also accept 403 (forbidden) as it means the page exists but access is restricted
            if not validation.get("success") or (status_code not in [200, 999, 403]):
                return {
                    "success": False,
                    "domain": domain_lower,
                    "url_pattern": None,
                    "example_url": None,
                    "method": None,
                    "error": (
                        f"Pattern validation failed for username '{username}'. "
                        f"URL {test_url} returned status {status_code}."
                    ),
                }
        
        # All validations passed
        method = "combined" if len(methods_used) > 1 else (methods_used[0] if methods_used else "unknown")
        example_url = pattern.replace("{username}", usernames[0])
        # Normalize example URL (remove trailing slash)
        example_url = normalize_trailing_slash(example_url)
        return {
            "success": True,
            "domain": domain_lower,
            "url_pattern": pattern,  # Already normalized
            "example_url": example_url,
            "method": method,
            "error": None,
        }
    
    # If we got here, we couldn't find a valid pattern
    return {
        "success": False,
        "domain": domain_lower,
        "url_pattern": None,
        "example_url": None,
        "method": None,
        "error": (
            f"Could not discover URL pattern for domain '{domain_lower}' with username(s) '{', '.join(usernames)}'. "
            "Tried multiple search approaches but no valid URLs were found."
        ),
    }

