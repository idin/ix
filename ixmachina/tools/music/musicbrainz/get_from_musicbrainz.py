"""
Get detailed music information by MusicBrainz ID.

Supports getting artists, albums (releases), and tracks (recordings) by their MBID.
"""

from typing import Dict, Any, Optional, Literal
from ...web.fetch.fetch_url import fetch_json
from ...constants import SUCCESS_KEY, RESULT_KEY, ERROR_KEY
from ....utils.persist import persist
from .constants import BASE_URL, USER_AGENT, DEFAULT_TIMEOUT


@persist(expire_seconds=30 * 60)  # Cache for 30 minutes
def get_from_musicbrainz(
    entity_id: str,
    type: Literal["artist", "album", "track"],
    include_related: bool = False,
) -> Dict[str, Any]:
    """
    Get detailed music information by MusicBrainz ID.

    Args:
        entity_id: MusicBrainz ID (MBID) for the entity.
        type: Type of entity - "artist", "album" (release), or "track" (recording).
        include_related: Whether to include related entities:
            - For "artist": includes release groups if True
            - For "album": includes track/recording information if True
            - For "track": ignored (no related entities to include)
            Default: False.

    Returns:
        Dictionary with:
            - success: Boolean indicating if retrieval was successful
            - result: Dictionary containing entity details based on type
            - error: Error message if retrieval failed (None if successful)

    Note:
        - "album" gets release information (specific album release)
        - "track" gets recording information (specific recorded performance)
    """
    try:
        # Map type to MusicBrainz endpoint and parameter names
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
        url = f"{BASE_URL}/{endpoint}/{entity_id}"
        params = {
            "fmt": "json",
        }

        # Add include parameters based on type
        if type == "artist" and include_related:
            params["inc"] = "release-groups"
        elif type == "album" and include_related:
            params["inc"] = "recordings"

        headers = {"User-Agent": USER_AGENT}

        # Build URL with query parameters
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{query_string}"

        response = fetch_json(url=full_url, headers=headers, timeout=DEFAULT_TIMEOUT)

        if not response["success"]:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Failed to get {type}: {response.get('error', 'Unknown error')}",
            }

        data = response.get("data", {})

        if type == "artist":
            # Extract relevant artist information
            artist_info = {
                "id": data.get("id"),
                "name": data.get("name"),
                "disambiguation": data.get("disambiguation"),
                "type": data.get("type"),
                "country": data.get("country"),
                "area": data.get("area", {}).get("name") if data.get("area") else None,
                "begin_date": data.get("life-span", {}).get("begin") if data.get("life-span") else None,
                "end_date": data.get("life-span", {}).get("end") if data.get("life-span") else None,
                "ended": data.get("life-span", {}).get("ended") if data.get("life-span") else None,
            }

            if include_related and data.get("release-groups"):
                release_groups = []
                for rg in data.get("release-groups", []):
                    release_groups.append({
                        "id": rg.get("id"),
                        "title": rg.get("title"),
                        "type": rg.get("type"),
                        "first_release_date": rg.get("first-release-date"),
                    })
                artist_info["release_groups"] = release_groups

            return {
                SUCCESS_KEY: True,
                RESULT_KEY: artist_info,
                ERROR_KEY: None,
            }

        elif type == "album":
            # Get primary artist credit
            artist_credit = data.get("artist-credit", [])
            artist_name = None
            if artist_credit and len(artist_credit) > 0:
                artist_name = artist_credit[0].get("name") or artist_credit[0].get("artist", {}).get("name")

            # Extract relevant release information
            release_info = {
                "id": data.get("id"),
                "title": data.get("title"),
                "artist": artist_name,
                "date": data.get("date"),
                "country": data.get("country"),
                "status": data.get("status"),
                "barcode": data.get("barcode"),
                "type": data.get("release-group", {}).get("type") if data.get("release-group") else None,
            }

            if include_related and data.get("media"):
                tracks = []
                for medium in data.get("media", []):
                    for track in medium.get("tracks", []):
                        recording = track.get("recording", {})
                        # Get track artist
                        track_artist_credit = recording.get("artist-credit", [])
                        track_artist = None
                        if track_artist_credit and len(track_artist_credit) > 0:
                            track_artist = track_artist_credit[0].get("name") or track_artist_credit[0].get("artist", {}).get("name")

                        length_ms = recording.get("length")
                        length_seconds = length_ms / 1000 if length_ms else None

                        tracks.append({
                            "position": track.get("position"),
                            "title": recording.get("title"),
                            "artist": track_artist,
                            "length": length_seconds,
                            "id": recording.get("id"),
                        })
                release_info["tracks"] = tracks

            return {
                SUCCESS_KEY: True,
                RESULT_KEY: release_info,
                ERROR_KEY: None,
            }

        elif type == "track":
            # Get primary artist credit
            artist_credit = data.get("artist-credit", [])
            artist_name = None
            if artist_credit and len(artist_credit) > 0:
                artist_name = artist_credit[0].get("name") or artist_credit[0].get("artist", {}).get("name")

            # Convert length from milliseconds to seconds
            length_ms = data.get("length")
            length_seconds = length_ms / 1000 if length_ms else None

            # Extract relevant recording information
            recording_info = {
                "id": data.get("id"),
                "title": data.get("title"),
                "artist": artist_name,
                "length": length_seconds,
                "disambiguation": data.get("disambiguation"),
                "isrcs": data.get("isrcs", []),
            }

            return {
                SUCCESS_KEY: True,
                RESULT_KEY: recording_info,
                ERROR_KEY: None,
            }

    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error getting {type}: {str(e)}",
        }

