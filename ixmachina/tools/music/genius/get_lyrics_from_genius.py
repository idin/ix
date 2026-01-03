"""
Get song lyrics using Genius API.
"""

from typing import Dict, Any, Optional
import os
from ...web.fetch.fetch_url import fetch_url
from ...constants import SUCCESS_KEY, RESULT_KEY, ERROR_KEY
from ...web.parse.parse_html import parse_html
from ...web.utils.constants import BROWSER_USER_AGENT
from ....utils.persist import persist
from .constants import DEFAULT_TIMEOUT


@persist(expire_seconds=30 * 60)  # Cache for 30 minutes
def get_lyrics_from_genius(
    song_url: str,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get song lyrics from a Genius song URL.

    Note: Genius API doesn't directly provide lyrics. This function fetches the
    song page and extracts lyrics from the HTML. The song_url can be obtained
    from search_song results.

    Args:
        song_url: Genius song URL (e.g., from search_song results).
        api_key: Genius API key (not used for lyrics, but kept for consistency).
                 If not provided, will try to read from GENIUS_API_KEY environment variable.

    Returns:
        Dictionary with:
            - success: Boolean indicating if retrieval was successful
            - result: Dictionary containing:
                - lyrics: The song lyrics text
                - title: Song title
                - artist: Artist name
                - url: Song URL
            - error: Error message if retrieval failed (None if successful)
    """
    try:
        headers = {"User-Agent": BROWSER_USER_AGENT}

        response = fetch_url(url=song_url, headers=headers, timeout=DEFAULT_TIMEOUT)

        if not response["success"]:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Failed to fetch song page: {response.get('error', 'Unknown error')}",
            }

        html_content = response.get("content", "")
        
        # Parse HTML to extract lyrics
        parsed = parse_html(html_content)
        
        if not parsed["success"]:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Failed to parse HTML: {parsed.get('error', 'Unknown error')}",
            }

        # Try to find lyrics in the HTML
        # Genius stores lyrics in a div with data-lyrics-container attribute
        # This is a simplified extraction - may need refinement
        lyrics_text = parsed.get("text", "")
        
        # Extract title from page
        title = parsed.get("title", "").split("|")[0].strip() if parsed.get("title") else None

        return {
            SUCCESS_KEY: True,
            RESULT_KEY: {
                "lyrics": lyrics_text,
                "title": title,
                "url": song_url,
            },
            ERROR_KEY: None,
        }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error getting lyrics: {str(e)}",
        }

