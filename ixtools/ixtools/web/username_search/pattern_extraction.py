"""
Pattern extraction utilities for username URL pattern discovery.
"""

import re
from collections import Counter
from typing import List, Optional
from urllib.parse import urlparse, urlunparse

from .url_validation import normalize_trailing_slash


def extract_pattern_from_urls(urls: List[str], username: str) -> Optional[str]:
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
            pattern_url = normalize_trailing_slash(pattern_url)
            
            patterns.append(pattern_url)
        except Exception:
            continue
    
    if not patterns:
        return None
    
    # Return the most common pattern (or first if all are unique)
    pattern_counts = Counter(patterns)
    most_common = pattern_counts.most_common(1)[0][0]
    
    return most_common

