"""
Web search tools for searching the internet.
"""

from typing import Dict, List, Optional, Any, Union

from .brave import search_brave
from ..utils.filter_by_domain import filter_by_domain


def search_web(
    query: str,
    max_results: Optional[int] = 10,
    search_engine: str = "brave",
    domain_whitelist: Optional[Union[str, List[str]]] = None,
    domain_blacklist: Optional[Union[str, List[str]]] = None,
    brave_api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Search the web using a specified search engine and return search results.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return. Default: 10.
        search_engine: Search engine to use. Options: "brave" (default).
        domain_whitelist: Optional domain(s) to include. Can be a string (single domain) or
                        list of strings (multiple domains). Only URLs from these domains will be returned.
                        Example: "openai.com" or ["openai.com", "anthropic.com"].
        domain_blacklist: Optional domain(s) to exclude. Can be a string (single domain) or
                         list of strings (multiple domains). URLs from these domains will be excluded.
                         Example: "spam.com" or ["spam.com", "ads.com"].
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
    search_engine_lower = search_engine.lower()
    
    if search_engine_lower == "brave":
        search_result = search_brave(query=query, max_results=max_results, api_key=brave_api_key)
        
        # Apply domain filtering if provided
        if search_result.get("success"):
            # Extract URLs from results
            urls = [result.get("url", "") for result in search_result.get("results", [])]
            
            # Apply blacklist first (if provided)
            if domain_blacklist is not None:
                urls = filter_by_domain(urls=urls, domains=domain_blacklist, filter_type="exclude")
            
            # Apply whitelist (if provided)
            if domain_whitelist is not None:
                urls = filter_by_domain(urls=urls, domains=domain_whitelist, filter_type="include")
            
            # Filter results to only include URLs that passed the filters
            filtered_results = [
                result for result in search_result.get("results", [])
                if result.get("url", "") in urls
            ]
            
            # Limit to max_results
            filtered_results = filtered_results[:max_results]
            
            # Update search result with filtered results
            search_result["results"] = filtered_results
            search_result["count"] = len(filtered_results)
            
            # If filtering resulted in 0 results, mark as unsuccessful
            if len(filtered_results) == 0:
                search_result["success"] = False
                search_result["error"] = "No results found after domain filtering."
        
        return search_result
    else:
        return {
            "success": False,
            "results": [],
            "count": 0,
            "query": query,
            "search_engine": search_engine,
            "error": f"Unknown search engine: {search_engine}. Supported: brave",
        }


def search_web_simple(
    query: str,
    search_engine: str = "brave",
) -> List[Dict[str, str]]:
    """
    Simple web search that returns just the results list.

    Args:
        query: The search query string.
        search_engine: Search engine to use. Options: "brave" (default).

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
    "search_brave",
]

