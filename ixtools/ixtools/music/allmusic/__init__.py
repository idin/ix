"""
AllMusic tools for extracting music information.
"""

from .get_genre_and_style import get_genre_and_style
from .find_url import find_allmusic_url
from .verify_url import verify_allmusic_url

__all__ = [
    "get_genre_and_style",
    "find_allmusic_url",
    "verify_allmusic_url",
]

