"""
Tests for search_song_on_genius tool.

WARNING: These tests require a valid Genius API key.
Set GENIUS_API_KEY environment variable or tests will fail.
"""

import pytest
import os

from ixmachina.tools.music import search_song_on_genius


def get_genius_api_key():
    """Get Genius API key from environment."""
    api_key = os.getenv("GENIUS_API_KEY")
    if not api_key:
        pytest.fail("GENIUS_API_KEY environment variable not set")
    return api_key


def test_search_song_on_genius():
    """Test searching for songs on Genius."""
    api_key = get_genius_api_key()
    
    result = search_song_on_genius(query="here comes the sun beatles", api_key=api_key, limit=5)
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert "result" in result
    assert "songs" in result["result"]
    assert isinstance(result["result"]["songs"], list)
    assert len(result["result"]["songs"]) > 0
    assert result["result"]["count"] > 0
    assert result["error"] is None
    
    # Check song structure
    song = result["result"]["songs"][0]
    assert "id" in song
    assert "title" in song
    assert isinstance(song["title"], str)
    assert len(song["title"]) > 0


def test_search_song_on_genius_limit():
    """Test search_song_on_genius respects limit parameter."""
    api_key = get_genius_api_key()
    
    result = search_song_on_genius(query="beatles", api_key=api_key, limit=3)
    
    assert result["success"] is True
    assert len(result["result"]["songs"]) <= 3


def test_search_song_on_genius_no_api_key():
    """Test search_song_on_genius fails without API key."""
    # Temporarily unset the environment variable
    original_key = os.environ.get("GENIUS_API_KEY")
    try:
        if "GENIUS_API_KEY" in os.environ:
            del os.environ["GENIUS_API_KEY"]
        
        result = search_song_on_genius(query="test", api_key=None)
        
        assert result["success"] is False
        assert result["result"] is None
        assert "api key" in result["error"].lower() or "genius" in result["error"].lower()
    finally:
        # Restore the original key
        if original_key is not None:
            os.environ["GENIUS_API_KEY"] = original_key


def test_search_song_on_genius_invalid_key():
    """Test search_song_on_genius handles invalid API key."""
    result = search_song_on_genius(query="test", api_key="invalid_key_12345")
    
    assert result["success"] is False
    assert result["result"] is None
    assert result["error"] is not None

