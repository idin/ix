"""
Search for music using Spotify Web API.
"""

from typing import Dict, Any, Optional, Literal
import os
from ...web.fetch.fetch_url import fetch_json
from ...constants import SUCCESS_KEY, RESULT_KEY, ERROR_KEY
from ixutils import persist
from .constants import BASE_URL, DEFAULT_TIMEOUT


@persist(expire_seconds=15 * 60)  # Cache for 15 minutes
def search_on_spotify(
    query: str,
    access_token: Optional[str] = None,
    type: Literal["artist", "album", "track", "playlist"] = "track",
    limit: Optional[int] = 10,
) -> Dict[str, Any]:
    """
    Search for music using Spotify Web API.

    Args:
        query: Search query (artist name, album name, track name, etc.).
        access_token: Spotify OAuth access token. If not provided, will try to read from
                     SPOTIFY_ACCESS_TOKEN environment variable.
        type: Type of search (artist, album, track, playlist). Default: track.
        limit: Maximum number of results to return. Default: 10.

    Returns:
        Dictionary with:
            - success: Boolean indicating if search was successful
            - result: Dictionary containing search results based on type
            - error: Error message if search failed (None if successful)

    Note:
        To get an access token, you need to:
        1. Register your application at https://developer.spotify.com/dashboard
        2. Use OAuth 2.0 Client Credentials flow to get an access token
        3. Pass the token to this function or set SPOTIFY_ACCESS_TOKEN environment variable
    """
    try:
        # Get access token from parameter or environment
        if access_token is None:
            access_token = os.getenv("SPOTIFY_ACCESS_TOKEN")
        
        if not access_token:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: (
                    "Spotify access token is required. Provide access_token parameter or "
                    "set SPOTIFY_ACCESS_TOKEN environment variable. "
                    "See function docstring for instructions on obtaining a token."
                ),
            }

        url = f"{BASE_URL}/search"
        params = {
            "q": query,
            "type": type,
            "limit": limit or 10,
        }
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        # Build URL with query parameters
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{query_string}"

        response = fetch_json(url=full_url, headers=headers, timeout=DEFAULT_TIMEOUT)

        if not response["success"]:
            error_msg = response.get("error", "Unknown error")
            # Check if it's an authentication error
            if isinstance(error_msg, str) and "401" in error_msg:
                error_msg = "Invalid or expired access token. Please obtain a new token."
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Failed to search: {error_msg}",
            }

        data = response.get("data", {})
        results = {}

        # Extract results based on type
        if type == "artist" and data.get("artists"):
            artists = data["artists"].get("items", [])
            results["artists"] = [
                {
                    "id": artist.get("id"),
                    "name": artist.get("name"),
                    "genres": artist.get("genres", []),
                    "popularity": artist.get("popularity"),
                    "followers": artist.get("followers", {}).get("total") if artist.get("followers") else None,
                    "external_urls": artist.get("external_urls", {}),
                }
                for artist in artists
            ]
            results["count"] = len(results["artists"])

        elif type == "album" and data.get("albums"):
            albums = data["albums"].get("items", [])
            results["albums"] = [
                {
                    "id": album.get("id"),
                    "name": album.get("name"),
                    "artists": [a.get("name") for a in album.get("artists", [])],
                    "release_date": album.get("release_date"),
                    "total_tracks": album.get("total_tracks"),
                    "popularity": album.get("popularity"),
                    "external_urls": album.get("external_urls", {}),
                }
                for album in albums
            ]
            results["count"] = len(results["albums"])

        elif type == "track" and data.get("tracks"):
            tracks = data["tracks"].get("items", [])
            results["tracks"] = [
                {
                    "id": track.get("id"),
                    "name": track.get("name"),
                    "artists": [a.get("name") for a in track.get("artists", [])],
                    "album": track.get("album", {}).get("name") if track.get("album") else None,
                    "duration_ms": track.get("duration_ms"),
                    "popularity": track.get("popularity"),
                    "external_urls": track.get("external_urls", {}),
                }
                for track in tracks
            ]
            results["count"] = len(results["tracks"])

        elif type == "playlist" and data.get("playlists"):
            playlists = data["playlists"].get("items", [])
            results["playlists"] = [
                {
                    "id": playlist.get("id"),
                    "name": playlist.get("name"),
                    "description": playlist.get("description"),
                    "owner": playlist.get("owner", {}).get("display_name") if playlist.get("owner") else None,
                    "tracks_count": playlist.get("tracks", {}).get("total") if playlist.get("tracks") else None,
                    "external_urls": playlist.get("external_urls", {}),
                }
                for playlist in playlists
            ]
            results["count"] = len(results["playlists"])

        return {
            SUCCESS_KEY: True,
            RESULT_KEY: results,
            ERROR_KEY: None,
        }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error searching: {str(e)}",
        }

