"""
Normalize Wikipedia article titles to their canonical form.

Handles redirects, case normalization, and disambiguation pages.
"""

"""
Normalize Wikipedia article titles to their canonical form.

Handles redirects, case normalization, and disambiguation pages.
"""

from typing import Dict, Any
from urllib.parse import urlencode

from ..web.fetch import fetch_json
from ..web.utils.constants import BROWSER_USER_AGENT


def normalize_article_title(
    title: str,
    language: str = "en",
) -> Dict[str, Any]:
    """
    Get the canonical Wikipedia article title from any input.
    
    Handles redirects, case variations, and returns the normalized title.
    Uses Wikipedia API to resolve redirects and get canonical form.
    
    Args:
        title: Article title (can be any variation, redirect, etc.).
        language: Wikipedia language code (e.g., "en", "fr", "de"). Default: "en".
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if normalization was successful
            - canonical_title: The canonical article title (None if not found)
            - normalized_title: Same as canonical_title (for consistency)
            - is_redirect: Boolean indicating if input was a redirect
            - language: The language code used
            - error: Error message if normalization failed (None if successful)
    """
    # Wikipedia API base URL
    api_url = f"https://{language}.wikipedia.org/w/api.php"
    
    # Normalize input: replace underscores with spaces, trim
    normalized_input = title.strip().replace("_", " ")
    
    params = {
        "action": "query",
        "format": "json",
        "titles": normalized_input,
        "redirects": "1",  # Follow redirects
        "converttitles": "1",  # Convert titles to canonical form
    }
    
    # Construct URL with query parameters
    url = f"{api_url}?{urlencode(params)}"
    
    # Wikipedia API requires User-Agent header
    headers = {"User-Agent": BROWSER_USER_AGENT}
    
    try:
        response = fetch_json(url=url, headers=headers, timeout=10)
        
        if not response.get("success"):
            return {
                "success": False,
                "canonical_title": None,
                "normalized_title": None,
                "is_redirect": False,
                "language": language,
                "error": f"Failed to fetch from Wikipedia API: {response.get('error')}",
            }
        
        data = response.get("data", {})
        query = data.get("query", {})
        
        # Check for redirects
        redirects = query.get("redirects", [])
        is_redirect = len(redirects) > 0
        
        # Get normalized pages
        pages = query.get("pages", {})
        
        if not pages:
            return {
                "success": False,
                "canonical_title": None,
                "normalized_title": None,
                "is_redirect": False,
                "language": language,
                "error": f"Article not found: {title}",
            }
        
        # Get the first (and usually only) page
        page_id = list(pages.keys())[0]
        page_data = pages[page_id]
        
        # Check if page is missing
        if page_id == "-1" or "missing" in page_data:
            return {
                "success": False,
                "canonical_title": None,
                "normalized_title": None,
                "is_redirect": False,
                "language": language,
                "error": f"Article not found: {title}",
            }
        
        canonical_title = page_data.get("title", normalized_input)
        
        return {
            "success": True,
            "canonical_title": canonical_title,
            "normalized_title": canonical_title,
            "is_redirect": is_redirect,
            "language": language,
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "canonical_title": None,
            "normalized_title": None,
            "is_redirect": False,
            "language": language,
            "error": f"Error normalizing title: {str(e)}",
        }

