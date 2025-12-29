"""
DuckDuckGo search engine implementation.
"""

from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

try:
    from ddgs import DDGS
except ImportError:
    DDGS = None


def search_duckduckgo(
    query: str,
    max_results: int,
    domain_filter: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Search using DuckDuckGo via the duckduckgo-search package.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return.
        domain_filter: Optional list of domain filters.

    Returns:
        Dictionary with search results.
    """
    if DDGS is None:
        return {
            "success": False,
            "results": [],
            "count": 0,
            "query": query,
            "search_engine": "duckduckgo",
            "error": "ddgs package is required. Install it with: pip install ddgs",
        }
    
    try:
        # If domain filter is used, fetch more results initially to account for filtering
        fetch_count = max_results * 5 if domain_filter else max_results
        
        with DDGS() as ddgs:
            # Use text() method to get web search results
            search_results = ddgs.text(
                query=query,
                max_results=fetch_count,
            )
        
        # Convert to our format
        all_results = []
        for result in search_results:
            all_results.append({
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "snippet": result.get("body", ""),
            })
        
        # Apply domain filter if provided
        if domain_filter:
            filtered_results = []
            for result in all_results:
                url = result.get("url", "")
                if not url:
                    continue
                parsed_url = urlparse(url)
                domain = parsed_url.netloc.lower()
                # Check if domain matches any filter (subdomain matching)
                if any(filter_domain in domain for filter_domain in domain_filter):
                    filtered_results.append(result)
                    # Stop if we have enough
                    if len(filtered_results) >= max_results:
                        break
            results = filtered_results
        else:
            results = all_results[:max_results]
        
        # 0 results is NOT success
        if len(results) == 0:
            return {
                "success": False,
                "results": [],
                "count": 0,
                "query": query,
                "search_engine": "duckduckgo",
                "error": "No search results found. This may indicate HTML parsing issues or the search engine blocking requests.",
            }
        
        return {
            "success": True,
            "results": results,
            "count": len(results),
            "query": query,
            "search_engine": "duckduckgo",
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "results": [],
            "count": 0,
            "query": query,
            "search_engine": "duckduckgo",
            "error": f"Error performing search: {str(e)}",
        }

