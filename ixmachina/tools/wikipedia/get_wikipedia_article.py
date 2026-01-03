"""
Get Wikipedia article content.
"""

from typing import Dict, Any, Optional
from urllib.parse import urlencode

from ..web.fetch import fetch_json
from ..web.utils.constants import BROWSER_USER_AGENT
from .normalize_article_title import normalize_article_title


def get_wikipedia_article(
    title: str,
    language: str = "en",
    summary_only: bool = False,
) -> Dict[str, Any]:
    """
    Get Wikipedia article content.
    
    Args:
        title: Article title (will be normalized automatically).
        language: Wikipedia language code (e.g., "en", "fr", "de"). Default: "en".
        summary_only: If True, return only the summary/extract. If False, return full content.
                     Default: False.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if retrieval was successful
            - title: The canonical article title
            - content: Article content (full text or summary)
            - extract: Article summary/extract (if summary_only=False, this is the first paragraph)
            - page_id: Wikipedia page ID
            - language: The language code used
            - url: URL to the article
            - error: Error message if retrieval failed (None if successful)
    """
    # First normalize the title to get canonical form
    normalize_result = normalize_article_title(title=title, language=language)
    
    if not normalize_result.get("success"):
        return {
            "success": False,
            "title": None,
            "content": None,
            "extract": None,
            "page_id": None,
            "language": language,
            "url": None,
            "error": normalize_result.get("error"),
        }
    
    canonical_title = normalize_result["canonical_title"]
    
    # Wikipedia API base URL
    api_url = f"https://{language}.wikipedia.org/w/api.php"
    
    params = {
        "action": "query",
        "format": "json",
        "titles": canonical_title,
        "prop": "extracts|info",
        "explaintext": "1",  # Plain text, no HTML
        "inprop": "url",  # Include URL in response
    }
    
    if summary_only:
        params["exintro"] = "1"  # Only first section
        params["exsentences"] = "3"  # First 3 sentences
    else:
        params["exsectionformat"] = "plain"  # Plain text sections
    
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
                "content": None,
                "extract": None,
                "page_id": None,
                "language": language,
                "url": None,
                "error": f"Failed to fetch from Wikipedia API: {response.get('error')}",
            }
        
        data = response.get("data", {})
        query = data.get("query", {})
        pages = query.get("pages", {})
        
        if not pages:
            return {
                "success": False,
                "title": canonical_title,
                "content": None,
                "extract": None,
                "page_id": None,
                "language": language,
                "url": None,
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
                "content": None,
                "extract": None,
                "page_id": None,
                "language": language,
                "url": None,
                "error": f"Article not found: {title}",
            }
        
        content = page_data.get("extract", "")
        article_url = page_data.get("fullurl", "")
        
        # Extract first paragraph as summary
        extract = content.split("\n\n")[0] if content else ""
        
        return {
            "success": True,
            "title": page_data.get("title", canonical_title),
            "content": content,
            "extract": extract,
            "page_id": int(page_id),
            "language": language,
            "url": article_url,
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "title": canonical_title,
            "content": None,
            "extract": None,
            "page_id": None,
            "language": language,
            "url": None,
            "error": f"Error fetching article: {str(e)}",
        }

