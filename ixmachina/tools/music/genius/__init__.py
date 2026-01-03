"""
Genius API tools.

Genius provides song lyrics and annotations.
Requires API key (free registration).
"""

from .search_song_on_genius import search_song_on_genius
from .get_lyrics_from_genius import get_lyrics_from_genius

__all__ = [
    "search_song_on_genius",
    "get_lyrics_from_genius",
]
