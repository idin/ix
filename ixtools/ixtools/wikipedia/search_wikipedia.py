"""
Search Wikipedia for articles.
"""

from typing import Dict, Any
from urllib.parse import urlencode

from ..web.fetch import fetch_json
from ..web.utils.constants import BROWSER_USER_AGENT


def search_wikipedia(
    query: str,
    max_results: int = 10,
    language: str = "en",
) -> Dict[str, Any]:
    """
    Search Wikipedia for articles matching a query.
    
    Args:
        query: Search query string.
        max_results: Maximum number of results to return. Default: 10.
        language: Wikipedia language code (e.g., "en", "fr", "de"). Default: "en".
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if search was successful
            - results: List of search results, each containing:
                - title: Article title
                - snippet: Article snippet/description
                - page_id: Wikipedia page ID
            - count: Number of results returned
            - query: The original search query
            - language: The language code used
            - error: Error message if search failed (None if successful)
    """
    # Wikipedia API base URL
    api_url = f"https://{language}.wikipedia.org/w/api.php"
    
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
        "srlimit": min(max_results, 50),  # Wikipedia API max is 50
        "srprop": "snippet|title|size",
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
                "results": [],
                "count": 0,
                "query": query,
                "language": language,
                "error": f"Failed to fetch from Wikipedia API: {response.get('error')}",
            }
        
        data = response.get("data", {})
        query_data = data.get("query", {})
        search_results = query_data.get("search", [])
        
        results = []
        for item in search_results[:max_results]:
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "page_id": item.get("pageid"),
            })
        
        return {
            "success": True,
            "results": results,
            "count": len(results),
            "query": query,
            "language": language,
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "results": [],
            "count": 0,
            "query": query,
            "language": language,
            "error": f"Error searching Wikipedia: {str(e)}",
        }

