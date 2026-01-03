"""
Get internal Wikipedia links from an article.
"""

from typing import Dict, Any, Optional
from urllib.parse import urlencode

from ..web.fetch import fetch_json
from ..web.utils.constants import BROWSER_USER_AGENT
from .normalize_article_title import normalize_article_title


def get_article_links(
    title: str,
    language: str = "en",
    max_links: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Get internal Wikipedia links (links to other Wikipedia articles) from an article.
    
    Returns normalized/canonical titles for all linked articles.
    
    Args:
        title: Article title (will be normalized automatically).
        language: Wikipedia language code (e.g., "en", "fr", "de"). Default: "en".
        max_links: Maximum number of links to return. If None, returns all links. Default: None.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if retrieval was successful
            - title: The canonical article title
            - links: List of linked articles, each containing:
                - title: Canonical title of the linked article
                - display_text: Display text used in the link (may differ from title)
                - namespace: Wikipedia namespace (0 for articles)
            - count: Number of links returned
            - language: The language code used
            - error: Error message if retrieval failed (None if successful)
    """
    # First normalize the title to get canonical form
    normalize_result = normalize_article_title(title=title, language=language)
    
    if not normalize_result.get("success"):
        return {
            "success": False,
            "title": None,
            "links": [],
            "count": 0,
            "language": language,
            "error": normalize_result.get("error"),
        }
    
    canonical_title = normalize_result["canonical_title"]
    
    # Wikipedia API base URL
    api_url = f"https://{language}.wikipedia.org/w/api.php"
    
    params = {
        "action": "query",
        "format": "json",
        "titles": canonical_title,
        "prop": "links",
        "plnamespace": "0",  # Only main namespace (articles)
        "pllimit": "500",  # Max links per request
    }
    
    all_links = []
    continue_param = None
    
    try:
        while True:
            # Add continuation parameter if we have one
            current_params = params.copy()
            if continue_param:
                current_params["plcontinue"] = continue_param
            
            # Construct URL with query parameters
            url = f"{api_url}?{urlencode(current_params)}"
            
            # Wikipedia API requires User-Agent header
            headers = {"User-Agent": BROWSER_USER_AGENT}
            
            response = fetch_json(url=url, headers=headers, timeout=10)
            
            if not response.get("success"):
                return {
                    "success": False,
                    "title": canonical_title,
                    "links": [],
                    "count": 0,
                    "language": language,
                    "error": f"Failed to fetch from Wikipedia API: {response.get('error')}",
                }
            
            data = response.get("data", {})
            query = data.get("query", {})
            pages = query.get("pages", {})
            
            if not pages:
                break
            
            # Get the first (and usually only) page
            page_id = list(pages.keys())[0]
            page_data = pages[page_id]
            
            # Check if page is missing
            if page_id == "-1" or "missing" in page_data:
                return {
                    "success": False,
                    "title": canonical_title,
                    "links": [],
                    "count": 0,
                    "language": language,
                    "error": f"Article not found: {title}",
                }
            
            # Get links from this page
            links = page_data.get("links", [])
            
            for link in links:
                link_title = link.get("title", "")
                # Normalize each linked title to get canonical form
                link_normalize = normalize_article_title(title=link_title, language=language)
                if link_normalize.get("success"):
                    all_links.append({
                        "title": link_normalize["canonical_title"],
                        "display_text": link_title,  # Original display text
                        "namespace": link.get("ns", 0),
                    })
            
            # Check for continuation
            if "continue" in data:
                continue_param = data["continue"].get("plcontinue")
                if not continue_param:
                    break
            else:
                break
            
            # Limit total links if max_links is specified
            if max_links and len(all_links) >= max_links:
                all_links = all_links[:max_links]
                break
        
        return {
            "success": True,
            "title": page_data.get("title", canonical_title),
            "links": all_links,
            "count": len(all_links),
            "language": language,
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "title": canonical_title,
            "links": [],
            "count": 0,
            "language": language,
            "error": f"Error fetching article links: {str(e)}",
        }

