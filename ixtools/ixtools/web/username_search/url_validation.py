"""
URL validation utilities for username URL pattern discovery.
"""

from urllib.parse import urlparse, urlunparse


def is_valid_username_url(url: str, domain: str, username: str) -> bool:
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


def normalize_trailing_slash(url: str) -> str:
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

