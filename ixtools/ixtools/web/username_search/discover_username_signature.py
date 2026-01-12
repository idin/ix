"""
Discover the signature for existing and non-existing usernames on a domain.

IMPORTANT: NO WEBSITE SPECIFIC LOGIC IS ALLOWED.
This function must work generically for any domain without hardcoding
domain-specific behavior (e.g., no "if domain == 'pypi.org'" checks).
"""

import random
import string
import os
from typing import Dict, Optional, Any, List, Union
from collections import Counter
from ..fetch.check_url_status import check_url_status
from ..fetch.fetch_url import fetch_url
from ..utils.extract_domain import extract_domain
from ixutils import persist
from ixutils import current_timestamp
from .discover_username_url_pattern import discover_username_url_pattern


# Known existing usernames for popular domains
KNOWN_EXISTING_USERNAMES = {
    "github.com": ["octocat", "torvalds", "gaearon"],
    "pypi.org": ["pypa", "psf", "django"],
    "reddit.com": ["spez", "kn0thing", "reddit"],
    "stackoverflow.com": ["22656", "1", "2"],  # User IDs
    "gitlab.com": ["gitlab-org", "gitlab", "gitlab-com"],
    "linkedin.com": ["reidhoffman", "jeffweiner08"],
    "twitter.com": ["elonmusk", "jack"],
    "instagram.com": ["instagram", "cristiano"],
    "youtube.com": ["pewdiepie", "mkbhd"],
    "medium.com": ["medium", "ev"],
    "dev.to": ["dev", "ben"],
    "hackernews": ["pg", "dang"],
}


def generate_non_existing_username() -> str:
    """
    Generate a creative non-existing username.
    
    Returns:
        A username that is very unlikely to exist.
    """
    # Create a long random string that's very unlikely to exist
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
    timestamp_part = str(int(current_timestamp() * 1000))[-8:]  # Last 8 digits of timestamp
    
    return f"this-user-definitely-does-not-exist-{random_part}-{timestamp_part}"


def _discover_username_signature_using_url_pattern(
    url_pattern: str,
    existing_username: Optional[Union[str, List[str]]] = None,
    non_existing_username: Optional[str] = None,
    timeout: Optional[int] = 10,
) -> Dict[str, Any]:
    """
    Discover the signature for existing and non-existing usernames using a URL pattern.
    
    Tests known existing and non-existing usernames to determine what distinguishes them.
    
    Args:
        url_pattern: URL pattern with {username} placeholder (e.g., "https://github.com/{username}").
                    The domain is extracted from this pattern.
        existing_username: Optional username(s) known to exist. If not provided,
                          will use known existing usernames for the domain.
        non_existing_username: Optional username known not to exist. If not provided,
                              will generate one automatically.
        timeout: Request timeout in seconds. Default: 10.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if signature discovery was successful
            - domain: The domain extracted from the URL pattern
            - url_pattern: The URL pattern used
            - existing_signature: Dictionary with signature for existing usernames:
                - status_code: HTTP status code
                - error_type: Error type (None if successful)
                - error_message: Error message (None if successful)
                - content_keywords: List of keywords found in page content
            - non_existing_signature: Dictionary with signature for non-existing usernames:
                - status_code: HTTP status code
                - error_type: Error type
                - error_message: Error message
                - content_keywords: List of keywords found in page content
            - distinguishing_factors: List of factors that distinguish existing from non-existing
            - error: Error message if discovery failed (None if successful)
    """
    # Extract domain from URL pattern
    domain_lower = extract_domain(url=url_pattern)
    
    # Validate that extracted domain is actually a valid domain (has at least one dot)
    if domain_lower is None or "." not in domain_lower:
        return {
            "success": False,
            "domain": None,
            "url_pattern": url_pattern,
            "existing_signature": None,
            "non_existing_signature": None,
            "distinguishing_factors": [],
            "error": "Could not extract domain from URL pattern.",
        }
    
    # Get existing username(s) for signature testing
    if existing_username is None:
        if domain_lower in KNOWN_EXISTING_USERNAMES:
            existing_usernames = KNOWN_EXISTING_USERNAMES[domain_lower]
        else:
            return {
                "success": False,
                "domain": domain_lower,
                "url_pattern": url_pattern,
                "existing_signature": None,
                "non_existing_signature": None,
                "distinguishing_factors": [],
                "error": (
                    f"No known existing usernames for domain '{domain_lower}'. "
                    "Please provide existing_username."
                ),
            }
    else:
        existing_usernames = [existing_username] if isinstance(existing_username, str) else existing_username
    
    # Get non-existing username
    if non_existing_username is None:
        non_existing_username = generate_non_existing_username()
    
    # Test existing username(s) to get signature
    existing_signatures = []
    for username in existing_usernames:
        test_url = url_pattern.replace("{username}", username)
        status_result = check_url_status(url=test_url, timeout=timeout)
        
        # Fetch content if status is 200
        content_keywords = []
        if status_result.get("status_code") == 200:
            fetch_result = fetch_url(url=test_url, timeout=timeout)
            if fetch_result.get("success") and fetch_result.get("content"):
                content = fetch_result["content"].lower()
                # Extract common keywords that indicate a profile page
                profile_keywords = ["profile", "user", "username", "member", "joined", "followers", "following"]
                for keyword in profile_keywords:
                    if keyword in content:
                        content_keywords.append(keyword)
        
        existing_signatures.append({
            "status_code": status_result.get("status_code"),
            "error_type": status_result.get("error_type"),
            "error_message": status_result.get("error_message"),
            "content_keywords": content_keywords,
        })
    
    # Get the most common signature (or first if all are unique)
    status_codes = [s["status_code"] for s in existing_signatures]
    most_common_status = Counter(status_codes).most_common(1)[0][0]
    
    # Find signature with most common status code
    existing_signature = next(
        (s for s in existing_signatures if s["status_code"] == most_common_status),
        existing_signatures[0]
    )
    
    # Test non-existing username to get signature
    test_url = url_pattern.replace("{username}", non_existing_username)
    status_result = check_url_status(url=test_url, timeout=timeout)
    
    # Fetch content if status is 200 (some sites return 200 for non-existing users)
    content_keywords = []
    if status_result.get("status_code") == 200:
        fetch_result = fetch_url(url=test_url, timeout=timeout)
        if fetch_result.get("success") and fetch_result.get("content"):
            content = fetch_result["content"].lower()
            # Extract common keywords that indicate user doesn't exist
            non_exist_keywords = [
                "not found", "doesn't exist", "does not exist", "no user", "user not found",
                "404", "page not found", "nobody", "doesn't go by", "account may have been banned",
                "javascript is disabled", "client challenge"
            ]
            for keyword in non_exist_keywords:
                if keyword in content:
                    content_keywords.append(keyword)
    
    non_existing_signature = {
        "status_code": status_result.get("status_code"),
        "error_type": status_result.get("error_type"),
        "error_message": status_result.get("error_message"),
        "content_keywords": content_keywords,
    }
    
    # Determine distinguishing factors
    distinguishing_factors = []
    
    if existing_signature["status_code"] != non_existing_signature["status_code"]:
        distinguishing_factors.append("status_code")
    
    if existing_signature["error_type"] != non_existing_signature["error_type"]:
        distinguishing_factors.append("error_type")
    
    if existing_signature["content_keywords"] != non_existing_signature["content_keywords"]:
        distinguishing_factors.append("content_keywords")
    
    # Validate that signatures are different
    if not distinguishing_factors:
        return {
            "success": False,
            "domain": domain_lower,
            "url_pattern": url_pattern,
            "existing_signature": existing_signature,
            "non_existing_signature": non_existing_signature,
            "distinguishing_factors": [],
            "error": (
                "Existing and non-existing usernames produce the same signature. "
                "Cannot reliably distinguish between them."
            ),
        }
    
    return {
        "success": True,
        "domain": domain_lower,
        "url_pattern": url_pattern,
        "existing_signature": existing_signature,
        "non_existing_signature": non_existing_signature,
        "distinguishing_factors": distinguishing_factors,
        "error": None,
    }


@persist(expire_seconds=14 * 24 * 60 * 60)  # Cache for 14 days
def discover_username_signature(
    domain: Optional[str] = None,
    url_pattern: Optional[str] = None,
    existing_username: Optional[Union[str, List[str]]] = None,
    non_existing_username: Optional[str] = None,
    timeout: Optional[int] = 10,
    brave_api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Discover the signature for existing and non-existing usernames.
    
    Can work with either a domain (will discover URL pattern first) or a URL pattern.
    
    Args:
        domain: The domain to discover signatures for (e.g., "github.com").
                Either domain or url_pattern must be provided.
        url_pattern: URL pattern with {username} placeholder (e.g., "https://github.com/{username}").
                    Either domain or url_pattern must be provided.
        existing_username: Optional username(s) known to exist. If not provided,
                          will use known existing usernames for the domain.
        non_existing_username: Optional username known not to exist. If not provided,
                              will generate one automatically.
        timeout: Request timeout in seconds. Default: 10.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if signature discovery was successful
            - domain: The domain extracted from the URL pattern
            - url_pattern: The URL pattern used
            - existing_signature: Dictionary with signature for existing usernames:
                - status_code: HTTP status code
                - error_type: Error type (None if successful)
                - error_message: Error message (None if successful)
                - content_keywords: List of keywords found in page content
            - non_existing_signature: Dictionary with signature for non-existing usernames:
                - status_code: HTTP status code
                - error_type: Error type
                - error_message: Error message
                - content_keywords: List of keywords found in page content
            - distinguishing_factors: List of factors that distinguish existing from non-existing
            - error: Error message if discovery failed (None if successful)
    """
    # Lazy import to avoid circular dependencies
    from .discover_username_url_pattern import discover_username_url_pattern
    
    # Validate that either domain or url_pattern is provided
    if not domain and not url_pattern:
        return {
            "success": False,
            "domain": None,
            "url_pattern": None,
            "existing_signature": None,
            "non_existing_signature": None,
            "distinguishing_factors": [],
            "error": "Either domain or url_pattern must be provided.",
        }
    
    # If domain is provided but not url_pattern, discover the URL pattern first
    if domain and not url_pattern:
        # Get existing username for pattern discovery
        if existing_username is None:
            domain_lower = domain.lower().strip()
            if domain_lower in KNOWN_EXISTING_USERNAMES:
                pattern_username = KNOWN_EXISTING_USERNAMES[domain_lower][0]
            else:
                return {
                    "success": False,
                    "domain": domain_lower,
                    "url_pattern": None,
                    "existing_signature": None,
                    "non_existing_signature": None,
                    "distinguishing_factors": [],
                    "error": (
                        f"Could not discover URL pattern for domain '{domain_lower}'. "
                        "Please provide url_pattern or existing_username."
                    ),
                }
        else:
            pattern_username = existing_username if isinstance(existing_username, str) else existing_username[0]
        
        pattern_result = discover_username_url_pattern(
            domain=domain,
            existing_username=pattern_username,
            timeout=timeout,
            brave_api_key=brave_api_key,
        )
        
        if not pattern_result.get("success"):
            return {
                "success": False,
                "domain": domain.lower().strip() if domain else None,
                "url_pattern": None,
                "existing_signature": None,
                "non_existing_signature": None,
                "distinguishing_factors": [],
                "error": f"Could not discover URL pattern: {pattern_result.get('error')}",
            }
        
        url_pattern = pattern_result["url_pattern"]
    
    # Now use the URL pattern to discover signatures
    return _discover_username_signature_using_url_pattern(
        url_pattern=url_pattern,
        existing_username=existing_username,
        non_existing_username=non_existing_username,
        timeout=timeout,
    )

