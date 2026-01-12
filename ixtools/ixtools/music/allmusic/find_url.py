"""
Find AllMusic URL from a search query.
"""

from typing import Dict, Any, Optional
from urllib.parse import quote
from bs4 import BeautifulSoup
from ...web.fetch.fetch_url import fetch_url
from ...constants import SUCCESS_KEY, RESULT_KEY, ERROR_KEY, METADATA_KEY
from ...web.utils.constants import BROWSER_USER_AGENT
from ...web.parse.parse_html import extract_text, parse_html
from ...web.parse.extract_from_page import extract_from_page
from ixutils import persist
from .constants import BASE_URL, DEFAULT_TIMEOUT
from .verify_url import verify_allmusic_url


@persist(expire_seconds=60 * 60 * 24 * 7)  # Cache for 1 week
def find_allmusic_url(
    query: str,
    llm: Any,
    result_type: Optional[str] = None,
    max_trials: int = 3,
) -> Dict[str, Any]:
    """
    Find AllMusic URL from a search query.
    
    Searches AllMusic for the given query and extracts the most relevant
    URL (artist, album, or song page). If verification fails, tries the next
    search results up to max_trials times.
    
    Args:
        query: Search query (artist name, album name, or song name).
        llm: LLM instance to use for extracting the URL from search results.
        result_type: Optional type filter - "artist", "album", or "song".
                     If provided, will prioritize results of that type.
        max_trials: Maximum number of search results to try. If the first result
                    doesn't match the query, will try the next ones up to this limit.
                    Default: 3.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if URL was found
            - result: Dictionary containing:
                - url: The AllMusic URL found
                - title: The title/name of the result
                - type: The type of result ("artist", "album", or "song")
                - trial_number: Which trial succeeded (1-based)
            - metadata: Dictionary with:
                - query: The search query
                - result_type: The requested result type (if provided)
                - max_trials: Maximum number of trials attempted
            - error: Error message if search failed (None if successful)
    """
    try:
        # Build search URL
        encoded_query = quote(query)
        search_url = f"{BASE_URL}/search/all/{encoded_query}"
        
        # Fetch the search page
        headers = {"User-Agent": BROWSER_USER_AGENT}
        search_response = fetch_url(url=search_url, headers=headers, timeout=DEFAULT_TIMEOUT)
        
        if not search_response["success"]:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                METADATA_KEY: {
                    "query": query,
                    "result_type": result_type,
                },
                ERROR_KEY: f"Failed to fetch AllMusic search page: {search_response.get('error', 'Unknown error')}",
            }
        
        html_content = search_response.get("content", "")
        
        # Parse HTML to extract links
        parsed = parse_html(html_content)
        page_text = extract_text(html_content)
        
        # Extract all AllMusic links from the page
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Find all links that point to AllMusic artist/album/song pages
        allmusic_links = []
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            if not href:
                continue
            
            # Convert relative URLs to absolute
            if href.startswith("/"):
                href = f"{BASE_URL}{href}"
            elif not href.startswith("http"):
                continue
            
            # Only include AllMusic links to artist/album/song pages
            if "allmusic.com" not in href:
                continue
            
            link_type = None
            if "/artist/" in href:
                link_type = "artist"
            elif "/album/" in href:
                link_type = "album"
            elif "/song/" in href:
                link_type = "song"
            else:
                continue
            
            # Get link text/title
            link_text = link.get_text(strip=True)
            if link_text:
                allmusic_links.append({
                    "url": href,
                    "title": link_text,
                    "type": link_type,
                })
        
        # Filter by result_type if specified
        if result_type:
            allmusic_links = [link for link in allmusic_links if link["type"] == result_type]
        
        # Use LLM to find the most relevant URL from the extracted links
        type_instruction = ""
        if result_type:
            type_instruction = f" Prioritize {result_type} results."
        
        # Limit candidates to max_trials * 2 to have enough options
        max_candidates = max(max_trials * 2, 20)
        candidates = allmusic_links[:max_candidates] if allmusic_links else []
        
        # Try up to max_trials candidates, verifying each one
        for trial in range(1, max_trials + 1):
            # Get candidates for this trial (skip already tried ones)
            if trial == 1:
                # First trial: use LLM to pick the best candidate
                if candidates:
                    candidates_text = "\n".join([
                        f"- {link['title']} ({link['type']}): {link['url']}"
                        for link in candidates[:20]  # Limit to first 20 to avoid token limits
                    ])
                    prompt = (
                        f"From the AllMusic search results below, find the most relevant result for: '{query}'.{type_instruction}\n\n"
                        "Here are the candidate results:\n"
                        f"{candidates_text}\n\n"
                        "IMPORTANT: The query is '{query}'. You must find a result that matches BOTH the artist name AND the album/song name from the query.\n"
                        "For example, if the query is 'Metallica Master of Puppets', you must find the album by Metallica, not by another artist.\n"
                        "Extract the URL and title of the best matching result that matches the full query.\n\n"
                        "Return in this exact format: 'URL: https://www.allmusic.com/... | Title: ... | Type: artist/album/song'\n"
                        "If no relevant result is found, return 'URL: None | Title: None | Type: None'.\n\n"
                        "Return only the formatted result, nothing else."
                    )
                else:
                    # Fallback to text extraction if no links found
                    prompt = (
                        f"From the AllMusic search results below, find the most relevant result for: '{query}'.{type_instruction}\n\n"
                        "Extract the URL and title of the best matching result.\n\n"
                        "Return in this exact format: 'URL: https://www.allmusic.com/... | Title: ... | Type: artist/album/song'\n"
                        "If no relevant result is found, return 'URL: None | Title: None | Type: None'.\n\n"
                        f"Search results page content:\n{page_text[:10000]}\n\n"
                        "Return only the formatted result, nothing else."
                    )
                
                llm_response = llm.query(user_prompt=prompt)
                
                # Parse LLM response
                if isinstance(llm_response, dict):
                    extracted_text = llm_response.get("content", str(llm_response))
                else:
                    extracted_text = str(llm_response)
                
                extracted_text = extracted_text.strip()
                
                # Parse the response
                url = None
                title = None
                result_type_found = None
                
                if "URL:" in extracted_text and "None" not in extracted_text:
                    # Extract URL
                    url_part = extracted_text.split("URL:")[1].split("|")[0].strip()
                    if url_part and url_part != "None" and url_part.startswith("http"):
                        url = url_part
                    
                    # Extract title
                    if "Title:" in extracted_text:
                        title_part = extracted_text.split("Title:")[1].split("|")[0].strip()
                        if title_part and title_part != "None":
                            title = title_part
                    
                    # Extract type
                    if "Type:" in extracted_text:
                        type_part = extracted_text.split("Type:")[1].strip()
                        if type_part and type_part != "None":
                            result_type_found = type_part.lower()
            else:
                # Subsequent trials: try the next candidate from the list
                if trial - 1 < len(candidates):
                    candidate = candidates[trial - 1]
                    url = candidate["url"]
                    title = candidate["title"]
                    result_type_found = candidate["type"]
                else:
                    # No more candidates
                    break
            
            if not url:
                continue
            
            # Verify this URL matches the query
            verification = verify_allmusic_url(url=url, query=query, llm=llm)
            
            if verification.get("success") and verification.get("result", {}).get("matches"):
                # Found a matching URL
                confidence = verification.get("result", {}).get("confidence", "low")
                # Only accept high or medium confidence matches
                if confidence in ["high", "medium"]:
                    return {
                        SUCCESS_KEY: True,
                        RESULT_KEY: {
                            "url": url,
                            "title": title or verification.get("result", {}).get("title"),
                            "type": result_type_found,
                            "trial_number": trial,
                        },
                        METADATA_KEY: {
                            "query": query,
                            "result_type": result_type,
                            "max_trials": max_trials,
                        },
                        ERROR_KEY: None,
                    }
        
        # No matching URL found after all trials
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            METADATA_KEY: {
                "query": query,
                "result_type": result_type,
                "max_trials": max_trials,
            },
            ERROR_KEY: f"No matching AllMusic URL found for query: {query} after {max_trials} trial(s)",
        }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            METADATA_KEY: {
                "query": query,
                "result_type": result_type,
            },
            ERROR_KEY: f"Error finding AllMusic URL: {str(e)}",
        }

