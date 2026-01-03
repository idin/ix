"""
Web fetching tools for HTTP requests.
"""

from typing import Dict, Optional, Any, List, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

from ..utils.constants import BROWSER_USER_AGENT
from ....utils.persist import persist


def _fetch_url_single(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: Optional[int] = 30,
) -> Dict[str, Any]:
    """
    Fetch content from a URL using HTTP GET request.

    Args:
        url: The URL to fetch.
        headers: Optional HTTP headers to include in the request.
        timeout: Request timeout in seconds. Default: 30.

    Returns:
        Dictionary with:
            - status_code: HTTP status code
            - content: Response content as string
            - headers: Response headers as dictionary
            - content_type: Content type from headers
            - url: Final URL after redirects
            - success: Boolean indicating if request was successful
            - error: Error message if request failed (None if successful)
    """
    try:
        response = requests.get(url=url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return {
            "status_code": response.status_code,
            "content": response.text,
            "headers": dict(response.headers),
            "content_type": response.headers.get("Content-Type", ""),
            "url": response.url,
            "success": True,
            "error": None,
        }
    except requests.RequestException as e:
        return {
            "status_code": getattr(e.response, "status_code", None) if hasattr(e, "response") else None,
            "content": None,
            "headers": dict(e.response.headers) if hasattr(e, "response") and e.response else {},
            "content_type": None,
            "url": url,
            "success": False,
            "error": str(e),
        }


@persist(expire_seconds=30 * 60)  # Cache for 30 minutes
def fetch_url(
    url: Union[str, List[str]],
    headers: Optional[Dict[str, str]] = None,
    timeout: Optional[int] = 30,
    max_workers: int = 10,
) -> Dict[str, Any]:
    """
    Fetch content from one or more URLs using HTTP GET requests.

    When processing multiple URLs, they are processed in parallel for better performance.

    Args:
        url: A single URL (string) or list of URLs to fetch.
        headers: Optional HTTP headers to include in the request(s).
        timeout: Request timeout in seconds. Default: 30.
        max_workers: Maximum number of parallel workers (only used for multiple URLs).
            Default: 10.

    Returns:
        For a single URL:
            Dictionary with:
                - status_code: HTTP status code
                - content: Response content as string
                - headers: Response headers as dictionary
                - content_type: Content type from headers
                - url: Final URL after redirects
                - success: Boolean indicating if request was successful
                - error: Error message if request failed (None if successful)

        For multiple URLs:
            Dictionary with:
                - success: Boolean indicating if the overall operation completed
                    (True if at least one URL was fetched successfully, False if all failed)
                - results: Dictionary mapping each URL to its fetch result
                - successful_urls: List of URLs that were successfully fetched
                - failed_urls: List of URLs that failed to fetch
                - total_count: Total number of URLs attempted
                - success_count: Number of URLs successfully fetched
                - failure_count: Number of URLs that failed to fetch
                - error: Error message if the overall operation failed (None if successful)
    """
    # Normalize url to list
    if isinstance(url, str):
        url_list = [url]
    else:
        url_list = url

    if not url_list:
        return {
            "success": False,
            "error": "At least one URL must be provided.",
        }

    # Single URL case - return result directly
    if len(url_list) == 1:
        return _fetch_url_single(url=url_list[0], headers=headers, timeout=timeout)

    # Multiple URLs case - process in parallel
    results = {}
    successful_urls = []
    failed_urls = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {
            executor.submit(_fetch_url_single, url=url, headers=headers, timeout=timeout): url
            for url in url_list
        }

        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                results[url] = result

                if result.get("success"):
                    successful_urls.append(url)
                else:
                    failed_urls.append(url)
            except Exception as e:
                results[url] = {
                    "status_code": None,
                    "content": None,
                    "headers": {},
                    "content_type": None,
                    "url": url,
                    "success": False,
                    "error": f"Error fetching URL: {str(e)}",
                }
                failed_urls.append(url)

    success_count = len(successful_urls)
    failure_count = len(failed_urls)
    overall_success = success_count > 0

    return {
        "success": overall_success,
        "results": results,
        "successful_urls": successful_urls,
        "failed_urls": failed_urls,
        "total_count": len(url_list),
        "success_count": success_count,
        "failure_count": failure_count,
        "error": None if overall_success else "All URL fetches failed.",
    }


def _fetch_json_single(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: Optional[int] = 30,
) -> Dict[str, Any]:
    """
    Fetch a URL and parse the response as JSON.

    Uses fetch_url internally and then parses the content as JSON.

    Args:
        url: The URL to fetch.
        headers: Optional HTTP headers to include in the request.
        timeout: Request timeout in seconds. Default: 30.

    Returns:
        Dictionary with:
            - status_code: HTTP status code
            - data: Parsed JSON data (dict or list) if successful
            - headers: Response headers as dictionary
            - url: Final URL after redirects
            - success: Boolean indicating if request and parsing were successful
            - error: Error message if request or parsing failed (None if successful)
    """
    # Use _fetch_url_single to get the response
    response = _fetch_url_single(url=url, headers=headers, timeout=timeout)
    
    # If the HTTP request failed, return the error
    if not response["success"]:
        return {
            "status_code": response["status_code"],
            "data": None,
            "headers": response["headers"],
            "url": response["url"],
            "success": False,
            "error": response["error"],
        }
    
    # Try to parse the content as JSON
    try:
        import json
        json_data = json.loads(response["content"])
        return {
            "status_code": response["status_code"],
            "data": json_data,
            "headers": response["headers"],
            "url": response["url"],
            "success": True,
            "error": None,
        }
    except (ValueError, json.JSONDecodeError) as e:
        return {
            "status_code": response["status_code"],
            "data": None,
            "headers": response["headers"],
            "url": response["url"],
            "success": False,
            "error": f"Error parsing JSON: {str(e)}",
        }


@persist(expire_seconds=15 * 60)  # Cache for 15 minutes
def fetch_json(
    url: Union[str, List[str]],
    headers: Optional[Dict[str, str]] = None,
    timeout: Optional[int] = 30,
    max_workers: int = 10,
) -> Dict[str, Any]:
    """
    Fetch one or more URLs and parse their responses as JSON.

    When processing multiple URLs, they are processed in parallel for better performance.

    Args:
        url: A single URL (string) or list of URLs to fetch.
        headers: Optional HTTP headers to include in all requests.
        timeout: Request timeout in seconds. Default: 30.
        max_workers: Maximum number of parallel workers (only used for multiple URLs).
            Default: 10.

    Returns:
        For a single URL:
            Dictionary with:
                - status_code: HTTP status code
                - data: Parsed JSON data (dict or list) if successful
                - headers: Response headers as dictionary
                - url: Final URL after redirects
                - success: Boolean indicating if request and parsing were successful
                - error: Error message if request or parsing failed (None if successful)

        For multiple URLs:
            Dictionary with:
                - success: Boolean indicating if the overall operation completed
                    (True if at least one URL was fetched successfully, False if all failed)
                - results: Dictionary mapping each URL to its fetch result
                - successful_urls: List of URLs that were successfully fetched and parsed
                - failed_urls: List of URLs that failed to fetch or parse
                - total_count: Total number of URLs attempted
                - success_count: Number of URLs successfully fetched
                - failure_count: Number of URLs that failed to fetch
                - error: Error message if the overall operation failed (None if successful)
    """
    # Normalize url to list
    if isinstance(url, str):
        url_list = [url]
    else:
        url_list = url

    if not url_list:
        return {
            "success": False,
            "error": "At least one URL must be provided.",
        }

    # Single URL case - return result directly
    if len(url_list) == 1:
        return _fetch_json_single(url=url_list[0], headers=headers, timeout=timeout)

    # Multiple URLs case - process in parallel
    results = {}
    successful_urls = []
    failed_urls = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {
            executor.submit(_fetch_json_single, url=url, headers=headers, timeout=timeout): url
            for url in url_list
        }

        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                results[url] = result

                if result.get("success"):
                    successful_urls.append(url)
                else:
                    failed_urls.append(url)
            except Exception as e:
                results[url] = {
                    "status_code": None,
                    "data": None,
                    "headers": {},
                    "url": url,
                    "success": False,
                    "error": f"Error fetching URL: {str(e)}",
                }
                failed_urls.append(url)

    success_count = len(successful_urls)
    failure_count = len(failed_urls)
    overall_success = success_count > 0

    return {
        "success": overall_success,
        "results": results,
        "successful_urls": successful_urls,
        "failed_urls": failed_urls,
        "total_count": len(url_list),
        "success_count": success_count,
        "failure_count": failure_count,
        "error": None if overall_success else "All JSON fetches failed.",
    }


def post_request(
    url: str,
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: Optional[int] = 30,
) -> Dict[str, Any]:
    """
    Send an HTTP POST request to a URL.

    Args:
        url: The URL to post to.
        data: Data to send (will be JSON encoded). Default: None.
        headers: Optional HTTP headers to include in the request.
        timeout: Request timeout in seconds. Default: 30.

    Returns:
        Dictionary with:
            - status_code: HTTP status code
            - content: Response content as string
            - headers: Response headers as dictionary
            - content_type: Content type from headers
            - url: Final URL after redirects
            - success: Boolean indicating if request was successful
            - error: Error message if request failed (None if successful)
    """
    try:
        json_data = data if data else None
        response = requests.post(
            url=url,
            json=json_data,
            headers=headers,
            timeout=timeout,
        )
        response.raise_for_status()
        return {
            "status_code": response.status_code,
            "content": response.text,
            "headers": dict(response.headers),
            "content_type": response.headers.get("Content-Type", ""),
            "url": response.url,
            "success": True,
            "error": None,
        }
    except requests.RequestException as e:
        return {
            "status_code": getattr(e.response, "status_code", None) if hasattr(e, "response") else None,
            "content": None,
            "headers": dict(e.response.headers) if hasattr(e, "response") and e.response else {},
            "content_type": None,
            "url": url,
            "success": False,
            "error": str(e),
        }

