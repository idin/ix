"""
Extract structured data from Wikipedia article infobox.
"""

from typing import Dict, Any
from urllib.parse import urlencode
import re

from ..web.fetch import fetch_json
from ..web.utils.constants import BROWSER_USER_AGENT
from .normalize_article_title import normalize_article_title


def get_article_infobox(
    title: str,
    language: str = "en",
) -> Dict[str, Any]:
    """
    Extract structured data from Wikipedia article infobox.
    
    Infoboxes contain key facts like dates, locations, statistics, etc.
    This function extracts the infobox data as a structured dictionary.
    
    Args:
        title: Article title (will be normalized automatically).
        language: Wikipedia language code (e.g., "en", "fr", "de"). Default: "en".
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if extraction was successful
            - title: The canonical article title
            - infobox: Dictionary of infobox fields (key-value pairs)
            - has_infobox: Boolean indicating if article has an infobox
            - language: The language code used
            - error: Error message if extraction failed (None if successful)
    """
    # First normalize the title to get canonical form
    normalize_result = normalize_article_title(title=title, language=language)
    
    if not normalize_result.get("success"):
        return {
            "success": False,
            "title": None,
            "infobox": {},
            "has_infobox": False,
            "language": language,
            "error": normalize_result.get("error"),
        }
    
    canonical_title = normalize_result["canonical_title"]
    
    # Wikipedia API base URL
    api_url = f"https://{language}.wikipedia.org/w/api.php"
    
    # Get the wikitext to parse infobox
    params = {
        "action": "query",
        "format": "json",
        "titles": canonical_title,
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
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
                "title": canonical_title,
                "infobox": {},
                "has_infobox": False,
                "language": language,
                "error": f"Failed to fetch from Wikipedia API: {response.get('error')}",
            }
        
        data = response.get("data", {})
        query = data.get("query", {})
        pages = query.get("pages", {})
        
        if not pages:
            return {
                "success": False,
                "title": canonical_title,
                "infobox": {},
                "has_infobox": False,
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
                "title": canonical_title,
                "infobox": {},
                "has_infobox": False,
                "language": language,
                "error": f"Article not found: {title}",
            }
        
        # Get wikitext content
        revisions = page_data.get("revisions", [])
        if not revisions:
            return {
                "success": True,
                "title": page_data.get("title", canonical_title),
                "infobox": {},
                "has_infobox": False,
                "language": language,
                "error": None,
            }
        
        wikitext = revisions[0].get("slots", {}).get("main", {}).get("*", "")
        
        # Parse infobox from wikitext
        # Infoboxes are in the format: {{Infobox ... | field = value | ... }}
        infobox_pattern = r"\{\{Infobox[^}]*\}\}"
        infobox_match = re.search(infobox_pattern, wikitext, re.DOTALL)
        
        if not infobox_match:
            return {
                "success": True,
                "title": page_data.get("title", canonical_title),
                "infobox": {},
                "has_infobox": False,
                "language": language,
                "error": None,
            }
        
        infobox_text = infobox_match.group(0)
        
        # Parse infobox fields (key = value pairs)
        # Pattern: | key = value
        field_pattern = r"\|\s*([^=]+?)\s*=\s*(.+?)(?=\||$)"
        fields = re.findall(field_pattern, infobox_text, re.DOTALL)
        
        infobox_data = {}
        for key, value in fields:
            key = key.strip().lower()
            # Clean up value: remove wikitext markup, newlines, extra spaces
            value = value.strip()
            value = re.sub(r"\[\[([^\]]+)\]\]", r"\1", value)  # Remove [[links]]
            value = re.sub(r"\{\{([^}]+)\}\}", r"\1", value)  # Remove {{templates}}
            value = re.sub(r"<[^>]+>", "", value)  # Remove HTML tags
            value = re.sub(r"\n+", " ", value)  # Replace newlines with space
            value = re.sub(r"\s+", " ", value).strip()  # Normalize whitespace
            infobox_data[key] = value
        
        return {
            "success": True,
            "title": page_data.get("title", canonical_title),
            "infobox": infobox_data,
            "has_infobox": True,
            "language": language,
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "title": canonical_title,
            "infobox": {},
            "has_infobox": False,
            "language": language,
            "error": f"Error extracting infobox: {str(e)}",
        }

