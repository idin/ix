"""
MusicBrainz API tools.

MusicBrainz is a free, open music encyclopedia with comprehensive metadata.
No authentication required (just User-Agent header).
"""

from .search_on_musicbrainz import search_on_musicbrainz
from .get_from_musicbrainz import get_from_musicbrainz

__all__ = [
    "search_on_musicbrainz",
    "get_from_musicbrainz",
]

