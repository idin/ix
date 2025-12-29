"""
Web search tools for searching the internet.
"""

from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlparse

from .duckduckgo import search_duckduckgo
from .brave import search_brave


def search_web(
    query: str,
    max_results: Optional[int] = 10,
    search_engine: str = "brave",
    domain_filter: Optional[Union[str, List[str]]] = None,
    brave_api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Search the web using a specified search engine and return search results.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return. Default: 10.
        search_engine: Search engine to use. Options: "brave" (default), "duckduckgo".
        domain_filter: Optional domain filter(s) to restrict results to specific domains.
                      Can be a string (single domain) or list of strings (multiple domains).
                      Example: "openai.com" or ["openai.com", "anthropic.com"].
        brave_api_key: Optional Brave API key. Only used when search_engine="brave".
                      If not provided, will try to get from BRAVE_API_KEY environment variable.

    Returns:
        Dictionary with:
            - success: Boolean indicating if search was successful
            - results: List of search results, each containing:
                - title: Result title
                - url: Result URL
                - snippet: Result description/snippet
            - count: Number of results returned
            - query: The original search query
            - search_engine: The search engine used
            - error: Error message if search failed (None if successful)
    """
    # Normalize domain_filter to a list
    if domain_filter is not None:
        if isinstance(domain_filter, str):
            domain_filter = [domain_filter]
    
    search_engine_lower = search_engine.lower()
    
    if search_engine_lower == "brave":
        return search_brave(query=query, max_results=max_results, domain_filter=domain_filter, api_key=brave_api_key)
    elif search_engine_lower == "duckduckgo":
        return search_duckduckgo(query=query, max_results=max_results, domain_filter=domain_filter)
    else:
        return {
            "success": False,
            "results": [],
            "count": 0,
            "query": query,
            "search_engine": search_engine,
            "error": f"Unknown search engine: {search_engine}. Supported: brave, duckduckgo",
        }


def search_web_simple(
    query: str,
    search_engine: str = "brave",
) -> List[Dict[str, str]]:
    """
    Simple web search that returns just the results list.

    Args:
        query: The search query string.
        search_engine: Search engine to use. Options: "brave" (default), "duckduckgo".

    Returns:
        List of search results, each containing:
            - title: Result title
            - url: Result URL
            - snippet: Result description/snippet
    """
    result = search_web(query=query, search_engine=search_engine)
    if result["success"]:
        return result["results"]
    else:
        return []


__all__ = [
    "search_web",
    "search_web_simple",
    "search_duckduckgo",
    "search_brave",
]

