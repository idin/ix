"""
Tests for get_lyrics_from_genius tool.

WARNING: These tests require a valid Genius API key and make actual HTTP requests.
Set GENIUS_API_KEY environment variable or tests will fail.
"""

import pytest
import os

from ixmachina.tools.music import search_song_on_genius, get_lyrics_from_genius


def get_genius_api_key():
    """Get Genius API key from environment."""
    api_key = os.getenv("GENIUS_API_KEY")
    if not api_key:
        pytest.fail("GENIUS_API_KEY environment variable not set")
    return api_key


def test_get_lyrics_from_genius():
    """Test getting lyrics from Genius song URL."""
    api_key = get_genius_api_key()
    
    # First search to get a song URL
    search_result = search_song_on_genius(query="here comes the sun beatles", api_key=api_key, limit=1)
    assert search_result["success"] is True
    assert len(search_result["result"]["songs"]) > 0
    
    song_url = search_result["result"]["songs"][0]["url"]
    assert song_url is not None
    assert isinstance(song_url, str)
    assert len(song_url) > 0
    
    # Now get the lyrics
    result = get_lyrics_from_genius(song_url=song_url, api_key=api_key)
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert "result" in result
    assert "lyrics" in result["result"]
    assert isinstance(result["result"]["lyrics"], str)
    assert result["result"]["url"] == song_url
    assert result["error"] is None


def test_get_lyrics_from_genius_invalid_url():
    """Test get_lyrics_from_genius handles invalid URL."""
    api_key = get_genius_api_key()
    
    result = get_lyrics_from_genius(song_url="https://genius.com/invalid-url-12345", api_key=api_key)
    
    # Should either fail or return empty lyrics
    assert isinstance(result, dict)
    # The function may succeed but return empty lyrics, or fail
    if result["success"]:
        assert "lyrics" in result["result"]
    else:
        assert result["error"] is not None

