"""
Music-related tools for accessing music information from various APIs.

This package provides tools for interacting with music APIs including:
- MusicBrainz: Free, open music encyclopedia
- Spotify: Audio features, popularity, recommendations
- Genius: Lyrics and annotations
"""

from .musicbrainz import (
    search_on_musicbrainz,
    get_from_musicbrainz,
)
from .spotify import search_on_spotify
from .genius import search_song_on_genius, get_lyrics_from_genius

__all__ = [
    # MusicBrainz tools
    "search_on_musicbrainz",
    "get_from_musicbrainz",
    # Spotify tools
    "search_on_spotify",
    # Genius tools
    "search_song_on_genius",
    "get_lyrics_from_genius",
]

