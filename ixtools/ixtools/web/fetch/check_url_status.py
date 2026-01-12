"""
Web status checking tools for URL validation.
"""

from typing import Dict, Optional, Any, List, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from requests.exceptions import (
    RequestException,
    ConnectionError,
    Timeout,
    TooManyRedirects,
    HTTPError,
)

from ..utils.constants import BROWSER_USER_AGENT
from ixutils import persist


def _check_url_status_single(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: Optional[int] = 10,
    use_head: bool = True,
) -> Dict[str, Any]:
    """
    Check if a website exists and what status/error it returns.
    
    This function checks the accessibility of a URL without downloading
    the full content. It uses HEAD requests by default for efficiency,
    but falls back to GET if HEAD is not supported.
    
    Args:
        url: The URL to check.
        headers: Optional HTTP headers to include in the request.
                If not provided, uses browser User-Agent by default.
        timeout: Request timeout in seconds. Default: 10.
        use_head: If True, use HEAD request (more efficient).
                 If False, use GET request. Default: True.
    
    Returns:
        Dictionary with:
            - exists: Boolean indicating if the website is accessible
            - status_code: HTTP status code (if available)
            - error_type: Type of error if request failed (e.g., "ConnectionError", "Timeout", "HTTPError", "DNS", etc.)
            - error_message: Human-readable error message
            - url: Final URL after redirects (if any)
            - headers: Response headers as dictionary (if available)
            - redirect_count: Number of redirects followed
            - success: Boolean indicating if the check completed successfully
            - error: Detailed error message if check failed (None if successful)
    """
    # Set default headers if not provided
    if headers is None:
        headers = {"User-Agent": BROWSER_USER_AGENT}
    
    # Ensure URL has a scheme
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    redirect_count = 0
    final_url = url
    
    try:
        # Try HEAD request first if requested
        if use_head:
            try:
                response = requests.head(
                    url=url,
                    headers=headers,
                    timeout=timeout,
                    allow_redirects=True,
                )
                # Some servers don't support HEAD, so check status
                if response.status_code == 405:  # Method Not Allowed
                    # Fall back to GET request
                    response = requests.get(
                        url=url,
                        headers=headers,
                        timeout=timeout,
                        allow_redirects=True,
                    )
            except RequestException:
                # If HEAD fails, try GET
                response = requests.get(
                    url=url,
                    headers=headers,
                    timeout=timeout,
                    allow_redirects=True,
                )
        else:
            response = requests.get(
                url=url,
                headers=headers,
                timeout=timeout,
                allow_redirects=True,
            )
        
        # Count redirects by comparing URLs
        if response.url != url:
            redirect_count = len(response.history)
        
        final_url = response.url
        
        # If we got any HTTP response, the site exists
        # This includes 2xx (success), 3xx (redirect), 4xx (client error), 5xx (server error)
        # The site doesn't exist only if we can't connect at all (DNS, connection refused, timeout)
        exists = True
        
        # Determine if it's a successful response or an error response
        is_success = 200 <= response.status_code < 400
        error_type = None
        error_message = None
        
        if not is_success:
            error_type = "HTTPError"
            status_code_str = str(response.status_code)
            if 400 <= response.status_code < 500:
                error_message = f"HTTP {status_code_str}: Client error - The server returned error {status_code_str}"
            elif response.status_code >= 500:
                error_message = f"HTTP {status_code_str}: Server error - The server encountered error {status_code_str}"
            else:
                error_message = f"HTTP {status_code_str}: Error {status_code_str}"
        
        return {
            "exists": exists,
            "status_code": response.status_code,
            "error_type": error_type,
            "error_message": error_message,
            "url": final_url,
            "headers": dict(response.headers),
            "redirect_count": redirect_count,
            "success": True,
            "error": error_message,
        }
    
    except ConnectionError as e:
        # DNS resolution failure, connection refused, etc.
        error_msg = str(e)
        error_type = "ConnectionError"
        
        # Try to determine more specific error type
        if "Name or service not known" in error_msg or "nodename nor servname provided" in error_msg:
            error_type = "DNS"
            error_message = f"DNS resolution failed: Cannot resolve hostname for {url}"
        elif "Connection refused" in error_msg:
            error_type = "ConnectionRefused"
            error_message = f"Connection refused: The server at {url} is not accepting connections"
        else:
            error_message = f"Connection error: {error_msg}"
        
        return {
            "exists": False,
            "status_code": None,
            "error_type": error_type,
            "error_message": error_message,
            "url": url,
            "headers": {},
            "redirect_count": 0,
            "success": False,
            "error": error_message,
        }
    
    except Timeout as e:
        error_message = f"Request timeout: The server at {url} did not respond within {timeout} seconds"
        return {
            "exists": False,
            "status_code": None,
            "error_type": "Timeout",
            "error_message": error_message,
            "url": url,
            "headers": {},
            "redirect_count": 0,
            "success": False,
            "error": error_message,
        }
    
    except TooManyRedirects as e:
        error_message = f"Too many redirects: The server at {url} redirected too many times"
        return {
            "exists": False,
            "status_code": None,
            "error_type": "TooManyRedirects",
            "error_message": error_message,
            "url": url,
            "headers": {},
            "redirect_count": 0,
            "success": False,
            "error": error_message,
        }
    
    except HTTPError as e:
        # HTTP error (4xx, 5xx) - site exists but returned error
        status_code = e.response.status_code if hasattr(e, "response") and e.response else None
        status_code_str = str(status_code) if status_code else "unknown"
        error_message = f"HTTP {status_code_str}: {str(e)}"
        
        # For HTTP errors, the site exists (we got a response from the server)
        # 4xx errors mean the site exists but the resource doesn't
        # 5xx errors mean the site exists but server error
        exists = status_code is not None
        
        return {
            "exists": exists,
            "status_code": status_code,
            "error_type": "HTTPError",
            "error_message": error_message,
            "url": e.response.url if hasattr(e, "response") and e.response else url,
            "headers": dict(e.response.headers) if hasattr(e, "response") and e.response else {},
            "redirect_count": 0,
            "success": True,  # Request completed, just got error status
            "error": error_message,
        }
    
    except RequestException as e:
        # Other request exceptions
        error_message = f"Request error: {str(e)}"
        
        # Try to extract status code if available
        status_code = None
        if hasattr(e, "response") and e.response:
            status_code = e.response.status_code
        
        return {
            "exists": False,
            "status_code": status_code,
            "error_type": "RequestException",
            "error_message": error_message,
            "url": url,
            "headers": {},
            "redirect_count": 0,
            "success": False,
            "error": error_message,
        }
    
    except Exception as e:
        # Unexpected errors
        error_message = f"Unexpected error: {str(e)}"
        return {
            "exists": False,
            "status_code": None,
            "error_type": "UnexpectedError",
            "error_message": error_message,
            "url": url,
            "headers": {},
            "redirect_count": 0,
            "success": False,
            "error": error_message,
        }


@persist(expire_seconds=60 * 60)  # Cache for 1 hour
def check_url_status(
    url: Union[str, List[str]],
    headers: Optional[Dict[str, str]] = None,
    timeout: Optional[int] = 10,
    use_head: bool = True,
    max_workers: int = 10,
) -> Dict[str, Any]:
    """
    Check if one or more websites exist and what status/error they return.

    When processing multiple URLs, they are processed in parallel for better performance.

    This function checks the accessibility of URLs without downloading
    the full content. It uses HEAD requests by default for efficiency,
    but falls back to GET if HEAD is not supported.

    Args:
        url: A single URL (string) or list of URLs to check.
        headers: Optional HTTP headers to include in the request(s).
                If not provided, uses browser User-Agent by default.
        timeout: Request timeout in seconds. Default: 10.
        use_head: If True, use HEAD request (more efficient).
                 If False, use GET request. Default: True.
        max_workers: Maximum number of parallel workers (only used for multiple URLs).
            Default: 10.

    Returns:
        For a single URL:
            Dictionary with:
                - exists: Boolean indicating if the website is accessible
                - status_code: HTTP status code (if available)
                - error_type: Type of error if request failed (e.g., "ConnectionError", "Timeout", "HTTPError", "DNS", etc.)
                - error_message: Human-readable error message
                - url: Final URL after redirects (if any)
                - headers: Response headers as dictionary (if available)
                - redirect_count: Number of redirects followed
                - success: Boolean indicating if the check completed successfully
                - error: Detailed error message if check failed (None if successful)

        For multiple URLs:
            Dictionary with:
                - success: Boolean indicating if the overall operation completed
                    (True if at least one URL was checked successfully, False if all failed)
                - results: Dictionary mapping each URL to its status check result
                - successful_urls: List of URLs that were successfully checked
                - failed_urls: List of URLs that failed to check
                - total_count: Total number of URLs attempted
                - success_count: Number of URLs successfully checked
                - failure_count: Number of URLs that failed to check
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
        return _check_url_status_single(
            url=url_list[0],
            headers=headers,
            timeout=timeout,
            use_head=use_head,
        )

    # Multiple URLs case - process in parallel
    results = {}
    successful_urls = []
    failed_urls = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {
            executor.submit(
                _check_url_status_single,
                url=url,
                headers=headers,
                timeout=timeout,
                use_head=use_head,
            ): url
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
                    "exists": False,
                    "status_code": None,
                    "error_type": "Exception",
                    "error_message": str(e),
                    "url": url,
                    "headers": {},
                    "redirect_count": 0,
                    "success": False,
                    "error": f"Error checking URL: {str(e)}",
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
        "error": None if overall_success else "All URL status checks failed.",
    }

