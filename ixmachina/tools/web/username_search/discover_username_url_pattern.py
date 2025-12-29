"""
Discover the URL pattern for username pages on a domain using web search.

IMPORTANT: NO WEBSITE SPECIFIC LOGIC IS ALLOWED.
This function must work generically for any domain without hardcoding
domain-specific behavior (e.g., no "if domain == 'pypi.org'" checks).
"""

import re
from typing import Dict, Optional, Any, List, Union
from urllib.parse import urlparse, urlunparse
from ..fetch.check_url_status import check_url_status
from ..search import search_web
from ..fetch.fetch_url import fetch_url
from ....utils.persist import persist
from bs4 import BeautifulSoup
from urllib.parse import urljoin


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
        results = _filter_project_urls_if_user_urls_present(search_result["results"])
        
        # Check direct search result URLs
        for result in results:
            url = result.get("url", "")
            if not url:
                continue
            
            if _is_valid_username_url(url, domain_for_matching, username_lower):
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
                        
                        if _is_valid_username_url(href, domain_for_matching, username_lower):
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
                if _is_valid_username_url(url, domain_for_matching, username_lower)
            ]
            
            if matching_urls:
                pattern = _extract_pattern_from_urls(matching_urls, username_lower)
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
            normalized_pattern = _normalize_trailing_slash(pattern)
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
            test_url = _normalize_trailing_slash(test_url)
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
        example_url = _normalize_trailing_slash(example_url)
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


def _is_valid_username_url(url: str, domain: str, username: str) -> bool:
    """
    Check if a URL contains the exact domain and exact username.
    
    Args:
        url: The URL to check.
        domain: The domain to match (without www. prefix).
        username: The username to match.
    
    Returns:
        True if the URL contains both the domain and username, False otherwise.
    """
    if not url or not isinstance(url, str):
        return False
    
    url_lower = url.lower()
    domain_lower = domain.lower()
    username_lower = username.lower()
    
    try:
        parsed = urlparse(url_lower)
        url_domain = parsed.netloc.lower()
        
        # Remove www. prefix for comparison
        if url_domain.startswith("www."):
            url_domain = url_domain[4:]
        
        # Check if domain matches (exact match)
        if url_domain != domain_lower:
            return False
        
        # Check if username appears in the URL path
        # Username should be in the path, not just anywhere (to avoid false positives)
        path = parsed.path.lower()
        
        # Reject known non-profile URL patterns
        non_profile_patterns = [
            "/posts/",
            "/post/",
            "/comments/",
            "/comment/",
            "/activity/",
            "/status/",
            "/tweet/",
            "/tweets/",
            "/replies/",
            "/media/",
            "/photos/",
            "/videos/",
            "/about/",
            "/settings/",
            "/edit/",
        ]
        for pattern in non_profile_patterns:
            if pattern in path:
                return False
        
        # Username should appear as a path segment that looks like a profile URL
        # Reject URLs that have extra segments after username (like /posts/, /comments/, etc.)
        path_segments = [seg for seg in path.split("/") if seg]
        
        # Find where username appears
        # First try exact segment match, then fall back to substring match
        username_index = None
        for i, seg in enumerate(path_segments):
            seg_lower = seg.lower()
            # Prefer exact match
            if seg_lower == username_lower:
                username_index = i
                break
        # If no exact match, try substring match
        if username_index is None:
            for i, seg in enumerate(path_segments):
                if username_lower in seg.lower():
                    username_index = i
                    break
        
        if username_index is None:
            return False
        
        # Check if username appears in a profile-like context
        # Valid patterns: /{username}, /user/{username}, /users/{username}, /in/{username}, etc.
        valid_prefixes = ["", "user", "users", "u", "in", "profile", "profiles"]
        
        # Check if the segment before username is a valid prefix (or username is first segment)
        if username_index == 0:
            # Username is first segment: /{username}
            # Check that there's nothing after it (or just trailing slash)
            if len(path_segments) == 1 or (len(path_segments) == 2 and path_segments[1] == ""):
                return True
        elif username_index > 0:
            # Username has a prefix segment
            prefix = path_segments[username_index - 1].lower()
            if prefix in valid_prefixes:
                # Check that username is the last meaningful segment (or followed only by empty/trailing)
                if len(path_segments) == username_index + 1:
                    # Username is last segment
                    return True
                elif len(path_segments) == username_index + 2 and path_segments[username_index + 1] == "":
                    # Username followed by trailing slash
                    return True
        
        # Also check @username format (for platforms like Twitter, Medium)
        if f"@{username_lower}" in path:
            # For @username, check it's not in a longer path like /posts/@username/something
            at_index = path.find(f"@{username_lower}")
            after_at = path[at_index + len(f"@{username_lower}"):]
            # Should be end of path or followed by / or ?
            if not after_at or after_at.startswith("/") or after_at.startswith("?") or after_at.startswith("#"):
                return True
        
        return False
    except Exception:
        return False


def _filter_project_urls_if_user_urls_present(results: list) -> list:
    """
    Filter out URLs containing "project" if there are URLs containing "user" (but not both).
    
    This is a general heuristic: if search results mix project pages and user pages,
    prefer user pages by filtering out project pages.
    
    Args:
        results: List of search result dictionaries with "url" keys.
    
    Returns:
        Filtered list of results.
    """
    if not results:
        return results
    
    # Check if we have URLs with "user" and URLs with "project"
    has_user_urls = False
    has_project_urls = False
    
    for result in results:
        url = result.get("url", "").lower()
        if not url:
            continue
        
        # Check if URL contains "user" but not "project"
        if "/user" in url and "/project" not in url:
            has_user_urls = True
        # Check if URL contains "project" but not "user"
        elif "/project" in url and "/user" not in url:
            has_project_urls = True
    
    # If we have both user URLs and project URLs (but not URLs with both),
    # filter out project URLs
    if has_user_urls and has_project_urls:
        filtered = []
        for result in results:
            url = result.get("url", "").lower()
            # Keep URLs that don't have "project" (or have both "user" and "project")
            if "/project" not in url or ("/user" in url and "/project" in url):
                filtered.append(result)
        return filtered
    
    return results


def _normalize_trailing_slash(url: str) -> str:
    """
    Normalize trailing slash in URL - always remove it for consistency.
    
    Args:
        url: The URL to normalize.
    
    Returns:
        URL with trailing slash removed (if it was a path-only trailing slash).
    """
    if not url:
        return url
    
    # Only remove trailing slash from the path, not from the root
    # e.g., "https://example.com/" -> "https://example.com" (root, keep as is)
    # but "https://example.com/path/" -> "https://example.com/path"
    parsed = urlparse(url)
    path = parsed.path
    
    # Remove trailing slash from path (unless it's just "/")
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    
    # Reconstruct URL
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc,
        path,
        parsed.params,
        parsed.query,
        parsed.fragment,
    ))
    
    return normalized


def _extract_pattern_from_urls(urls: List[str], username: str) -> Optional[str]:
    """
    Extract a URL pattern from a list of URLs by replacing the username with {username}.
    
    Cleans up the pattern to remove extra path segments after the username.
    Normalizes trailing slashes for deterministic output.
    
    Args:
        urls: List of URLs that contain the username.
        username: The username to replace with {username} placeholder.
    
    Returns:
        The most common cleaned URL pattern (without trailing slash), or None if no pattern could be extracted.
    """
    if not urls:
        return None
    
    patterns = []
    username_lower = username.lower()
    
    for url in urls:
        try:
            parsed = urlparse(url)
            original_path = parsed.path
            
            # Replace username in path with {username}
            path = original_path
            path_lower = path.lower()
            
            # First, try to find the username as a complete path segment
            path_segments = path.split("/")
            replaced_segments = []
            username_found = False
            
            for i, segment in enumerate(path_segments):
                segment_lower = segment.lower()
                # Check if this segment exactly matches the username
                if segment_lower == username_lower:
                    replaced_segments.append("{username}")
                    username_found = True
                # Check if this segment is @username
                elif segment_lower == f"@{username_lower}":
                    replaced_segments.append("@{username}")
                    username_found = True
                else:
                    replaced_segments.append(segment)
            
            # If we didn't find username as a complete segment, try substring replacement
            # but only if the username appears as a whole word (not part of another word)
            if not username_found:
                # Use word boundaries to ensure we're replacing the whole username, not part of it
                # Match username that's either at word boundary or surrounded by / or start/end
                pattern_path = re.sub(
                    rf'(^|/)({re.escape(username_lower)})(/|$)',
                    r'\1{username}\3',
                    path_lower,
                    flags=re.IGNORECASE,
                )
                # Also handle @username format
                pattern_path = re.sub(
                    rf'(^|/)(@{re.escape(username_lower)})(/|$)',
                    r'\1@{username}\3',
                    pattern_path,
                    flags=re.IGNORECASE,
                )
            else:
                pattern_path = "/".join(replaced_segments)
            
            # Clean up the pattern: remove everything after {username} segment
            # This handles cases like /user/{username}/comments/ -> /user/{username}
            if "{username}" in pattern_path:
                # Find the segment containing {username}
                segments = pattern_path.split("/")
                username_segment_index = None
                for i, seg in enumerate(segments):
                    if "{username}" in seg:
                        username_segment_index = i
                        break
                
                if username_segment_index is not None:
                    # Keep only up to and including the username segment
                    # Remove trailing empty segment (trailing slash)
                    cleaned_segments = segments[:username_segment_index + 1]
                    # Filter out empty segments at the end
                    while cleaned_segments and cleaned_segments[-1] == "":
                        cleaned_segments.pop()
                    
                    pattern_path = "/".join(cleaned_segments)
            
            # Reconstruct URL with pattern (remove params, query, fragment)
            pattern_url = urlunparse((
                parsed.scheme,
                parsed.netloc,
                pattern_path,
                "",  # Remove params
                "",  # Remove query
                "",  # Remove fragment
            ))
            
            # Normalize trailing slash - always remove it for consistency
            pattern_url = _normalize_trailing_slash(pattern_url)
            
            patterns.append(pattern_url)
        except Exception:
            continue
    
    if not patterns:
        return None
    
    # Return the most common pattern (or first if all are unique)
    from collections import Counter
    pattern_counts = Counter(patterns)
    most_common = pattern_counts.most_common(1)[0][0]
    
    return most_common

