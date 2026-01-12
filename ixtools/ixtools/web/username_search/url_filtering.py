"""
URL filtering utilities for username URL pattern discovery.
"""


def filter_project_urls_if_user_urls_present(results: list) -> list:
    """
    Filter out URLs containing "project" if there are URLs containing "user" (but not both).
    
    This is a general heuristic: if search results mix project pages and user pages,
    prefer user pages by filtering out project pages.
    
    Args:
        results: List of search result dictionaries with "url" keys.
    
    Returns:
        Filtered list of results.
    """
    if not results:
        return results
    
    # Check if we have URLs with "user" and URLs with "project"
    has_user_urls = False
    has_project_urls = False
    
    for result in results:
        url = result.get("url", "").lower()
        if not url:
            continue
        
        # Check if URL contains "user" but not "project"
        if "/user" in url and "/project" not in url:
            has_user_urls = True
        # Check if URL contains "project" but not "user"
        elif "/project" in url and "/user" not in url:
            has_project_urls = True
    
    # If we have both user URLs and project URLs (but not URLs with both),
    # filter out project URLs
    if has_user_urls and has_project_urls:
        filtered = []
        for result in results:
            url = result.get("url", "").lower()
            # Keep URLs that don't have "project" (or have both "user" and "project")
            if "/project" not in url or ("/user" in url and "/project" in url):
                filtered.append(result)
        return filtered
    
    return results

