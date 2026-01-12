"""
Search for music using MusicBrainz API.

Supports searching for artists, albums (releases), and tracks (recordings).
"""

from typing import Dict, Any, Optional, Literal
from ...web.fetch.fetch_url import fetch_json
from ...constants import SUCCESS_KEY, RESULT_KEY, ERROR_KEY
from ixutils import persist
from .constants import BASE_URL, USER_AGENT, DEFAULT_TIMEOUT


@persist(expire_seconds=30 * 60)  # Cache for 30 minutes
def search_on_musicbrainz(
    query: str,
    type: Literal["artist", "album", "track"] = "artist",
    limit: Optional[int] = 10,
) -> Dict[str, Any]:
    """
    Search for music using MusicBrainz API.

    Args:
        query: Search query (artist name, album name, or track name).
        type: Type of search - "artist", "album" (releases), or "track" (recordings).
              Default: "artist".
        limit: Maximum number of results to return. Default: 10.

    Returns:
        Dictionary with:
            - success: Boolean indicating if search was successful
            - result: Dictionary containing search results based on type:
                - For "artist": artists list and count
                - For "album": releases list and count
                - For "track": recordings list and count
            - error: Error message if search failed (None if successful)

    Note:
        - "album" searches for releases (specific album releases)
        - "track" searches for recordings (specific recorded performances)
    """
    try:
        # Map type to MusicBrainz endpoint
        endpoint_map = {
            "artist": "artist",
            "album": "release",
            "track": "recording",
        }

        if type not in endpoint_map:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Invalid type: {type}. Must be 'artist', 'album', or 'track'.",
            }

        endpoint = endpoint_map[type]
        url = f"{BASE_URL}/{endpoint}/"
        params = {
            "query": query,
            "fmt": "json",
            "limit": limit or 10,
        }
        headers = {"User-Agent": USER_AGENT}

        # Build URL with query parameters
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{query_string}"

        response = fetch_json(url=full_url, headers=headers, timeout=DEFAULT_TIMEOUT)

        if not response["success"]:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Failed to search {type}s: {response.get('error', 'Unknown error')}",
            }

        data = response.get("data", {})
        count = data.get("count", 0)

        if type == "artist":
            artists = data.get("artists", [])
            artist_list = []
            for artist in artists:
                artist_list.append({
                    "id": artist.get("id"),
                    "name": artist.get("name"),
                    "disambiguation": artist.get("disambiguation"),
                    "type": artist.get("type"),
                    "country": artist.get("country"),
                    "area": artist.get("area", {}).get("name") if artist.get("area") else None,
                    "begin_date": artist.get("life-span", {}).get("begin") if artist.get("life-span") else None,
                    "end_date": artist.get("life-span", {}).get("end") if artist.get("life-span") else None,
                })
            return {
                SUCCESS_KEY: True,
                RESULT_KEY: {
                    "artists": artist_list,
                    "count": count,
                },
                ERROR_KEY: None,
            }

        elif type == "album":
            releases = data.get("releases", [])
            release_list = []
            for release in releases:
                # Get primary artist credit
                artist_credit = release.get("artist-credit", [])
                artist_name = None
                if artist_credit and len(artist_credit) > 0:
                    artist_name = artist_credit[0].get("name") or artist_credit[0].get("artist", {}).get("name")

                release_list.append({
                    "id": release.get("id"),
                    "title": release.get("title"),
                    "artist": artist_name,
                    "date": release.get("date"),
                    "country": release.get("country"),
                    "status": release.get("status"),
                    "type": release.get("release-group", {}).get("type") if release.get("release-group") else None,
                })
            return {
                SUCCESS_KEY: True,
                RESULT_KEY: {
                    "releases": release_list,
                    "count": count,
                },
                ERROR_KEY: None,
            }

        elif type == "track":
            recordings = data.get("recordings", [])
            recording_list = []
            for recording in recordings:
                # Get primary artist credit
                artist_credit = recording.get("artist-credit", [])
                artist_name = None
                if artist_credit and len(artist_credit) > 0:
                    artist_name = artist_credit[0].get("name") or artist_credit[0].get("artist", {}).get("name")

                # Convert length from milliseconds to seconds
                length_ms = recording.get("length")
                length_seconds = length_ms / 1000 if length_ms else None

                recording_list.append({
                    "id": recording.get("id"),
                    "title": recording.get("title"),
                    "artist": artist_name,
                    "length": length_seconds,
                    "disambiguation": recording.get("disambiguation"),
                })
            return {
                SUCCESS_KEY: True,
                RESULT_KEY: {
                    "recordings": recording_list,
                    "count": count,
                },
                ERROR_KEY: None,
            }

    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error searching {type}s: {str(e)}",
        }

