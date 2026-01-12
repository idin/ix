"""
Check which usernames are available and which are not on a domain.

Uses signature discovery to determine if usernames exist by comparing
their responses against known existing and non-existing signatures.
"""

from typing import Dict, Optional, Any, List, Union
from .discover_username_url_pattern import discover_username_url_pattern
from .discover_username_signature import discover_username_signature
from .match_signature import match_signature
from ..fetch.check_url_status import check_url_status
from ..fetch.fetch_url import fetch_url
from ..utils.extract_domain import extract_domain
from ixutils import persist


@persist(expire_seconds=7 * 24 * 60 * 60)
def check_single_username_exists(
    username: str,
    url_pattern: str,
    existing_signature: Dict[str, Any],
    non_existing_signature: Dict[str, Any],
    distinguishing_factors: List[str],
    timeout: Optional[int] = 10,
) -> Dict[str, Any]:
    """
    Check if a single username exists on a domain.
    
    Uses signature matching to determine if the username exists by comparing
    its response against known existing and non-existing signatures.
    
    This function is cached to avoid redundant checks for the same username.
    
    Args:
        username: The username to check.
        url_pattern: URL pattern with {username} placeholder (e.g., "https://github.com/{username}").
        existing_signature: The signature for existing usernames.
        non_existing_signature: The signature for non-existing usernames.
        distinguishing_factors: List of factors that distinguish existing from non-existing.
        timeout: Request timeout in seconds. Default: 10.
    
    Returns:
        Dictionary with:
            - exists: Boolean indicating if username exists (True/False/None)
            - url: The URL that was checked
            - status_code: HTTP status code
            - error: Error message if check failed (None if successful)
    """
    test_url = url_pattern.replace("{username}", username)
    status_result = check_url_status(url=test_url, timeout=timeout)
    
    # Get content keywords if content_keywords is a distinguishing factor
    content_keywords = []
    if "content_keywords" in distinguishing_factors:
        # Fetch content to check for keywords
        # We fetch regardless of status code since content_keywords is a distinguishing factor
        fetch_result = fetch_url(url=test_url, timeout=timeout)
        if fetch_result.get("success") and fetch_result.get("content"):
            content = fetch_result["content"].lower()
            
            # Check for existing username keywords
            profile_keywords = ["profile", "user", "username", "member", "joined", "followers", "following"]
            for keyword in profile_keywords:
                if keyword in content:
                    content_keywords.append(keyword)
            
            # Check for non-existing username keywords
            non_exist_keywords = [
                "not found", "doesn't exist", "does not exist", "no user", "user not found",
                "404", "page not found", "nobody", "doesn't go by", "account may have been banned",
                "javascript is disabled", "client challenge"
            ]
            for keyword in non_exist_keywords:
                if keyword in content:
                    content_keywords.append(keyword)
    
    # Build signature for this username
    username_signature = {
        "status_code": status_result.get("status_code"),
        "error_type": status_result.get("error_type"),
        "error_message": status_result.get("error_message"),
        "content_keywords": content_keywords,
    }
    
    # Use helper function to match signature
    match_result = match_signature(
        signature=username_signature,
        existing_signature=existing_signature,
        non_existing_signature=non_existing_signature,
        distinguishing_factors=distinguishing_factors,
    )
    
    exists = match_result["exists"]
    error = match_result["error"]
    
    return {
        "exists": exists,
        "url": test_url,
        "status_code": status_result.get("status_code"),
        "error": error,
    }


def check_username_availability(
    usernames: Union[str, List[str]],
    domain: Optional[str] = None,
    url_pattern: Optional[str] = None,
    existing_username: Optional[Union[str, List[str]]] = None,
    timeout: Optional[int] = 10,
) -> Dict[str, Any]:
    """
    Check which usernames are available and which are not on a domain.
    
    Uses signature discovery to determine if usernames exist by comparing
    their responses against known existing and non-existing signatures.
    
    Args:
        usernames: A single username (string) or list of usernames to check.
        domain: The domain to check usernames on (e.g., "github.com").
                Either domain or url_pattern must be provided.
        url_pattern: URL pattern with {username} placeholder (e.g., "https://github.com/{username}").
                    Either domain or url_pattern must be provided.
        existing_username: Optional username(s) known to exist. Used for discovering
                          URL pattern and signatures if not already known.
        timeout: Request timeout in seconds. Default: 10.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the check completed successfully
            - domain: The domain that was checked
            - url_pattern: The URL pattern used
            - results: Dictionary mapping each username to its availability status:
                - exists: Boolean indicating if username exists (True/False/None)
                - url: The URL that was checked
                - status_code: HTTP status code
                - error: Error message if check failed (None if successful)
            - available_usernames: List of usernames that are available (do not exist)
            - unavailable_usernames: List of usernames that are unavailable (exist)
            - undetermined_usernames: List of usernames that could not be determined
            - error: Error message if the overall operation failed (None if successful)
    """
    # Normalize usernames to list
    if isinstance(usernames, str):
        username_list = [usernames]
    else:
        username_list = usernames
    
    if not username_list:
        return {
            "success": False,
            "domain": None,
            "url_pattern": None,
            "results": {},
            "available_usernames": [],
            "unavailable_usernames": [],
            "undetermined_usernames": [],
            "error": "At least one username must be provided.",
        }
    
    # Validate that either domain or url_pattern is provided
    if not domain and not url_pattern:
        return {
            "success": False,
            "domain": None,
            "url_pattern": None,
            "results": {},
            "available_usernames": [],
            "unavailable_usernames": [],
            "undetermined_usernames": [],
            "error": "Either domain or url_pattern must be provided.",
        }
    
    # If both domain and url_pattern are provided, validate they match
    if domain and url_pattern:
        pattern_domain = extract_domain(url=url_pattern)
        domain_normalized = extract_domain(url=domain)
        
        if pattern_domain != domain_normalized:
            raise ValueError(
                f"Domain mismatch: provided domain '{domain_normalized}' does not match "
                f"domain in url_pattern '{pattern_domain}'."
            )
    
    # Get URL pattern (either provided or discover it)
    if url_pattern:
        final_url_pattern = url_pattern
        final_domain = extract_domain(url=url_pattern)
    else:
        # Discover URL pattern using domain
        pattern_result = discover_username_url_pattern(
            domain=domain,
            existing_username=existing_username,
            timeout=timeout,
        )
        
        if not pattern_result.get("success"):
            domain_normalized = extract_domain(url=domain) if domain else None
            return {
                "success": False,
                "domain": domain_normalized,
                "url_pattern": None,
                "results": {},
                "available_usernames": [],
                "unavailable_usernames": [],
                "undetermined_usernames": [],
                "error": f"Could not discover URL pattern: {pattern_result.get('error')}",
            }
        
        final_url_pattern = pattern_result["url_pattern"]
        final_domain = pattern_result["domain"]
    
    # Discover signatures for existing and non-existing usernames
    signature_result = discover_username_signature(
        domain=final_domain,
        url_pattern=final_url_pattern,
        existing_username=existing_username,
        timeout=timeout,
    )
    
    if not signature_result.get("success"):
        return {
            "success": False,
            "domain": final_domain,
            "url_pattern": final_url_pattern,
            "results": {},
            "available_usernames": [],
            "unavailable_usernames": [],
            "undetermined_usernames": [],
            "error": f"Could not discover username signatures: {signature_result.get('error')}",
        }
    
    existing_signature = signature_result["existing_signature"]
    non_existing_signature = signature_result["non_existing_signature"]
    distinguishing_factors = signature_result["distinguishing_factors"]
    
    # Check each username using the cached single-username function
    results = {}
    available_usernames = []
    unavailable_usernames = []
    undetermined_usernames = []
    
    for username in username_list:
        result = check_single_username_exists(
            username=username,
            url_pattern=final_url_pattern,
            existing_signature=existing_signature,
            non_existing_signature=non_existing_signature,
            distinguishing_factors=distinguishing_factors,
            timeout=timeout,
        )
        
        exists = result["exists"]
        
        if exists is True:
            unavailable_usernames.append(username)
        elif exists is False:
            available_usernames.append(username)
        else:
            undetermined_usernames.append(username)
        
        results[username] = result
    
    return {
        "success": True,
        "domain": final_domain,
        "url_pattern": final_url_pattern,
        "results": results,
        "available_usernames": available_usernames,
        "unavailable_usernames": unavailable_usernames,
        "undetermined_usernames": undetermined_usernames,
        "error": None,
    }

