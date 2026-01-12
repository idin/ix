"""
Get genre and style information from AllMusic pages.
"""

from typing import Dict, Any, Optional
from ...web.fetch.fetch_url import fetch_url
from ...constants import SUCCESS_KEY, RESULT_KEY, ERROR_KEY, METADATA_KEY
from ...web.utils.constants import BROWSER_USER_AGENT
from ...web.parse.parse_html import extract_text, parse_html
from ...string.smart_truncate import smart_truncate_text
from ixutils import persist
from .constants import DEFAULT_TIMEOUT
from .find_url import find_allmusic_url


@persist(expire_seconds=60 * 60 * 24 * 365)  # Cache for 1 year
def get_genre_and_style(
    query: Optional[str] = None,
    url: Optional[str] = None,
    llm: Any = None,
    result_type: Optional[str] = None,
    max_trials: int = 3,
) -> Dict[str, Any]:
    """
    Get genre and style information from an AllMusic page.
    
    Extracts genre and style tags from AllMusic artist, album, or song pages.
    Can search AllMusic for a query and automatically find the correct page, or
    use a direct URL if provided.
    
    Args:
        query: Search query (artist name, album name, or song name). If provided,
               will search AllMusic to find the correct page. Either query or url
               must be provided.
        url: AllMusic URL (artist, album, or song page). If provided, will use
             this URL directly. Either query or url must be provided.
        llm: LLM instance to use for extraction and search result parsing.
             Required if query is provided.
        result_type: Optional type filter for search - "artist", "album", or "song".
                     Only used when query is provided. If provided, will prioritize
                     results of that type.
        max_trials: Maximum number of search results to try when using query.
                    Only used when query is provided. Default: 3.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if extraction was successful
            - result: Dictionary containing:
                - genre: List of genres (if found)
                - style: List of styles (if found)
                - title: Page title (artist/album/song name)
                - url: The AllMusic URL used
            - metadata: Dictionary with:
                - url: The AllMusic URL used
                - query: The search query (if provided)
            - error: Error message if extraction failed (None if successful)
    """
    try:
        # Validate inputs
        if not query and not url:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                METADATA_KEY: {
                    "query": query,
                    "url": None,
                },
                ERROR_KEY: "Either query or url must be provided",
            }
        
        if not llm:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                METADATA_KEY: {
                    "query": query,
                    "url": url,
                },
                ERROR_KEY: "LLM is required for extraction",
            }
        
        # If query is provided, find the URL first
        if query:
            find_result = find_allmusic_url(
                query=query,
                llm=llm,
                result_type=result_type,
                max_trials=max_trials,
            )
            
            if not find_result["success"]:
                return {
                    SUCCESS_KEY: False,
                    RESULT_KEY: None,
                    METADATA_KEY: {
                        "query": query,
                        "url": None,
                    },
                    ERROR_KEY: f"Failed to find AllMusic URL: {find_result.get('error', 'Unknown error')}",
                }
            
            url = find_result["result"]["url"]
        
        # Fetch the page
        headers = {"User-Agent": BROWSER_USER_AGENT}
        page_response = fetch_url(url=url, headers=headers, timeout=DEFAULT_TIMEOUT)
        
        if not page_response["success"]:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                METADATA_KEY: {
                    "url": url,
                },
                ERROR_KEY: f"Failed to fetch AllMusic page: {page_response.get('error', 'Unknown error')}",
            }
        
        # Extract text from HTML and use LLM to extract genre and style
        html_content = page_response.get("content", "")
        page_text = extract_text(html_content)
        
        # Smart truncation focusing on genre/style sections
        limited_text = smart_truncate_text(
            text=page_text,
            search_terms=["genre", "genres", "style", "styles"],
            max_length=8000,
        )
        
        # Use LLM to extract genre and style
        prompt = (
            "Extract the genres and styles for this music from the AllMusic page content below.\n\n"
            "Return in this exact format: 'Genres: genre1, genre2 | Styles: style1, style2'\n"
            "If genres or styles are not found, use empty lists.\n\n"
            f"Page content:\n{limited_text}\n\n"
            "Return only the formatted result, nothing else."
        )
        
        llm_response = llm.query(user_prompt=prompt)
        
        # Parse LLM response
        if isinstance(llm_response, dict):
            extracted_text = llm_response.get("content", str(llm_response))
        else:
            extracted_text = str(llm_response)
        
        extracted_text = extracted_text.strip()
        
        # Parse genres and styles
        genres = []
        styles = []
        
        if extracted_text.lower() not in ["information not found", "not found", "none", ""]:
            # Parse the format: "Genres: genre1, genre2 | Styles: style1, style2"
            if "Genres:" in extracted_text:
                genre_part = extracted_text.split("Genres:")[1].split("|")[0].strip()
                genres = [g.strip() for g in genre_part.split(",") if g.strip()]
            
            if "Styles:" in extracted_text:
                style_part = extracted_text.split("Styles:")[1].strip()
                styles = [s.strip() for s in style_part.split(",") if s.strip()]
        
        # Extract title from page
        parsed = parse_html(html_content)
        title = parsed.get("title", "").split("|")[0].strip() if parsed.get("title") else None
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: {
                "genre": genres,
                "style": styles,
                "title": title,
                "url": url,
            },
            METADATA_KEY: {
                "url": url,
                "query": query,
            },
            ERROR_KEY: None,
        }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            METADATA_KEY: {
                "url": url,
                "query": query,
            },
            ERROR_KEY: f"Error getting genre and style from AllMusic: {str(e)}",
        }

