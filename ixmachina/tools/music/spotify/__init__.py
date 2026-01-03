"""
Spotify Web API tools.

Spotify provides audio features, popularity metrics, and recommendations.
Requires OAuth 2.0 authentication.
"""

from .search_on_spotify import search_on_spotify

__all__ = [
    "search_on_spotify",
]
