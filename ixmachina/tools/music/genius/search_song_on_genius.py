"""
Search for songs using Genius API.
"""

from typing import Dict, Any, Optional
import os
from ...web.fetch.fetch_url import fetch_json
from ...constants import SUCCESS_KEY, RESULT_KEY, ERROR_KEY
from ....utils.persist import persist
from .constants import BASE_URL, DEFAULT_TIMEOUT


@persist(expire_seconds=30 * 60)  # Cache for 30 minutes
def search_song_on_genius(
    query: str,
    api_key: Optional[str] = None,
    limit: Optional[int] = 10,
) -> Dict[str, Any]:
    """
    Search for songs using Genius API.

    Args:
        query: Search query (song name, artist, etc.).
        api_key: Genius API key. If not provided, will try to read from GENIUS_API_KEY environment variable.
        limit: Maximum number of results to return. Default: 10.

    Returns:
        Dictionary with:
            - success: Boolean indicating if search was successful
            - result: Dictionary containing:
                - songs: List of song dictionaries with id, title, artist, url, etc.
                - count: Number of results returned
            - error: Error message if search failed (None if successful)
    """
    try:
        # Get API key from parameter or environment
        if api_key is None:
            api_key = os.getenv("GENIUS_API_KEY")
        
        if not api_key:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: "Genius API key is required. Provide api_key parameter or set GENIUS_API_KEY environment variable.",
            }

        url = f"{BASE_URL}/search"
        params = {
            "q": query,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
        }

        # Build URL with query parameters
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{query_string}"

        response = fetch_json(url=full_url, headers=headers, timeout=DEFAULT_TIMEOUT)

        if not response["success"]:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Failed to search songs: {response.get('error', 'Unknown error')}",
            }

        data = response.get("data", {})
        hits = data.get("response", {}).get("hits", [])[:limit or 10]

        # Extract relevant song information
        song_list = []
        for hit in hits:
            song = hit.get("result", {})
            song_list.append({
                "id": song.get("id"),
                "title": song.get("title"),
                "artist": song.get("primary_artist", {}).get("name") if song.get("primary_artist") else None,
                "url": song.get("url"),
                "thumbnail": song.get("song_art_image_thumbnail_url"),
                "release_date": song.get("release_date_for_display"),
            })

        return {
            SUCCESS_KEY: True,
            RESULT_KEY: {
                "songs": song_list,
                "count": len(song_list),
            },
            ERROR_KEY: None,
        }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error searching songs: {str(e)}",
        }

