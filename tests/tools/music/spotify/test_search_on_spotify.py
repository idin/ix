"""
Tests for search_on_spotify tool.

WARNING: These tests require a valid Spotify access token.
Set SPOTIFY_ACCESS_TOKEN environment variable or tests will fail.
"""

import pytest
import os

from ixmachina.tools.music import search_on_spotify


def get_spotify_access_token():
    """Get Spotify access token from environment."""
    token = os.getenv("SPOTIFY_ACCESS_TOKEN")
    if not token:
        pytest.fail("SPOTIFY_ACCESS_TOKEN environment variable not set")
    return token


def test_search_artist_on_spotify():
    """Test searching for artists on Spotify."""
    access_token = get_spotify_access_token()
    
    result = search_on_spotify(query="beatles", type="artist", access_token=access_token, limit=5)
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert "result" in result
    assert "artists" in result["result"]
    assert isinstance(result["result"]["artists"], list)
    assert len(result["result"]["artists"]) > 0
    assert result["result"]["count"] > 0
    assert result["error"] is None
    
    # Check artist structure
    artist = result["result"]["artists"][0]
    assert "id" in artist
    assert "name" in artist
    assert isinstance(artist["name"], str)


def test_search_album_on_spotify():
    """Test searching for albums on Spotify."""
    access_token = get_spotify_access_token()
    
    result = search_on_spotify(query="abbey road", type="album", access_token=access_token, limit=5)
    
    assert result["success"] is True
    assert "albums" in result["result"]
    assert len(result["result"]["albums"]) > 0
    
    # Check album structure
    album = result["result"]["albums"][0]
    assert "id" in album
    assert "name" in album
    assert isinstance(album["name"], str)


def test_search_track_on_spotify():
    """Test searching for tracks on Spotify."""
    access_token = get_spotify_access_token()
    
    result = search_on_spotify(query="here comes the sun", type="track", access_token=access_token, limit=5)
    
    assert result["success"] is True
    assert "tracks" in result["result"]
    assert len(result["result"]["tracks"]) > 0
    
    # Check track structure
    track = result["result"]["tracks"][0]
    assert "id" in track
    assert "name" in track
    assert isinstance(track["name"], str)


def test_search_playlist_on_spotify():
    """Test searching for playlists on Spotify."""
    access_token = get_spotify_access_token()
    
    result = search_on_spotify(query="beatles", type="playlist", access_token=access_token, limit=5)
    
    assert result["success"] is True
    assert "playlists" in result["result"]
    assert len(result["result"]["playlists"]) > 0


def test_search_on_spotify_no_token():
    """Test search_on_spotify fails without access token."""
    # Temporarily unset the environment variable
    original_token = os.environ.get("SPOTIFY_ACCESS_TOKEN")
    try:
        if "SPOTIFY_ACCESS_TOKEN" in os.environ:
            del os.environ["SPOTIFY_ACCESS_TOKEN"]
        
        result = search_on_spotify(query="test", type="track", access_token=None)
        
        assert result["success"] is False
        assert result["result"] is None
        assert "token" in result["error"].lower() or "access" in result["error"].lower()
    finally:
        # Restore the original token
        if original_token is not None:
            os.environ["SPOTIFY_ACCESS_TOKEN"] = original_token


def test_search_on_spotify_invalid_token():
    """Test search_on_spotify handles invalid access token."""
    result = search_on_spotify(query="test", type="track", access_token="invalid_token_12345")
    
    assert result["success"] is False
    assert result["result"] is None
    assert result["error"] is not None

