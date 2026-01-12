"""
Brave search engine implementation using Brave Search API.

Reference: https://api-dashboard.search.brave.com/app/documentation/web-search/get-started
"""

from typing import Dict, List, Optional, Any
import os
import requests
from ixutils import persist


@persist(expire_seconds=86400)
def search_brave(
    query: str,
    max_results: Optional[int] = 20,
    api_key: Optional[str] = None,
    safesearch: Optional[str] = None,
    freshness: Optional[str] = None,
    country: Optional[str] = None,
    search_lang: Optional[str] = None,
    ui_lang: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Search using Brave Search API.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return. Default: 20 (maximum per request).
                    Brave API charges per request, not per result, so 10 and 20 results cost the same.
                    For more than 20 results, the function will make multiple paginated requests
                    (up to 200 results total, each page is a separate charge).
        api_key: Brave API key. If not provided, will try to get from BRAVE_API_KEY environment variable.
        safesearch: Optional safe search setting. Options: "off", "moderate", "strict". Default: "moderate".
        freshness: Optional freshness filter. Options: "pd" (past day), "pw" (past week), "pm" (past month), "py" (past year).
        country: Optional country code (ISO 3166-1 alpha-2) to bias results toward a specific country.
        search_lang: Optional language code (ISO 639-1) for the search query language.
        ui_lang: Optional language code (ISO 639-1) for the user interface language.

    Returns:
        Dictionary with:
            - success: Boolean indicating if search was successful
            - results: List of search results, each containing:
                - title: Result title
                - url: Result URL
                - snippet: Result description/snippet
            - count: Number of results returned
            - query: The original search query
            - search_engine: The search engine used ("brave")
            - error: Error message if search failed (None if successful)
    """
    # Get API key from parameter or environment variable
    if api_key is None:
        api_key = os.getenv("BRAVE_API_KEY")
    
    if not api_key:
        return {
            "success": False,
            "results": [],
            "count": 0,
            "query": query,
            "search_engine": "brave",
            "error": "Brave API key is required. Set BRAVE_API_KEY environment variable or pass api_key parameter.",
        }
    
    try:
        # Brave Search API endpoint
        api_url = "https://api.search.brave.com/res/v1/web/search"
        
        # Brave API allows up to 20 results per request, max offset is 9 (200 results total)
        # Calculate how many requests we need
        max_api_results = 200  # 20 results × 10 pages (offset 0-9)
        if max_results > max_api_results:
            max_results = max_api_results
        
        # Calculate number of pages needed (each page has max 20 results)
        results_per_page = 20
        num_pages = (max_results + results_per_page - 1) // results_per_page  # Ceiling division
        
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key,
        }
        
        # Collect results from all pages
        all_results = []
        
        for page in range(num_pages):
            # Calculate offset (0-indexed page number)
            offset = page
            
            # Check if offset exceeds maximum (max offset is 9)
            if offset > 9:
                break
            
            # Prepare request parameters for this page
            params = {
                "q": query,
                "count": results_per_page,
                "offset": offset,
            }
            
            # Add optional parameters
            if safesearch:
                params["safesearch"] = safesearch
            if freshness:
                params["freshness"] = freshness
            if country:
                params["country"] = country
            if search_lang:
                params["search_lang"] = search_lang
            if ui_lang:
                params["ui_lang"] = ui_lang
            
            # Make API request for this page
            response = requests.get(api_url, params=params, headers=headers, timeout=30)
            
            if response.status_code != 200:
                error_text = response.text
                try:
                    error_json = response.json()
                    error_text = error_json.get("message", error_text)
                except (ValueError, KeyError):
                    pass
                
                # If it's the first page, return error. Otherwise, break and return what we have.
                if page == 0:
                    return {
                        "success": False,
                        "results": [],
                        "count": 0,
                        "query": query,
                        "search_engine": "brave",
                        "error": f"Brave API returned status code {response.status_code}: {error_text}",
                    }
                else:
                    # Partial success - return what we have so far
                    break
            
            data = response.json()
            
            # Extract results from Brave API response
            # The response structure is: { "web": { "results": [...] } }
            web_results = data.get("web", {}).get("results", [])
            
            if not web_results:
                # No more results available
                break
            
            for result in web_results:
                all_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("description", ""),
                })
            
            # If we got fewer results than requested, we've reached the end
            if len(web_results) < results_per_page:
                break
            
            # If we have enough results, stop
            if len(all_results) >= max_results:
                break
        
        # Limit to requested number of results
        results = all_results[:max_results]
        
        # 0 results is NOT success
        if len(results) == 0:
            return {
                "success": False,
                "results": [],
                "count": 0,
                "query": query,
                "search_engine": "brave",
                "error": "No search results found.",
            }
        
        return {
            "success": True,
            "results": results,
            "count": len(results),
            "query": query,
            "search_engine": "brave",
            "error": None,
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "results": [],
            "count": 0,
            "query": query,
            "search_engine": "brave",
            "error": "Request to Brave API timed out after 30 seconds.",
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "results": [],
            "count": 0,
            "query": query,
            "search_engine": "brave",
            "error": f"Network error performing search: {str(e)}",
        }
    except ValueError as e:
        # JSON parsing error
        return {
            "success": False,
            "results": [],
            "count": 0,
            "query": query,
            "search_engine": "brave",
            "error": f"Invalid response from Brave API: {str(e)}",
        }
    except Exception as e:
        return {
            "success": False,
            "results": [],
            "count": 0,
            "query": query,
            "search_engine": "brave",
            "error": f"Unexpected error performing search: {str(e)}",
        }

