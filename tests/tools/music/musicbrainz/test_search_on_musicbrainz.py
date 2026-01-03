"""
Tests for search_on_musicbrainz tool.
"""

import pytest

from ixmachina.tools.music import search_on_musicbrainz


def test_search_artist_on_musicbrainz():
    """Test searching for artists on MusicBrainz."""
    result = search_on_musicbrainz(query="beatles", type="artist", limit=5)
    
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
    assert len(artist["name"]) > 0


def test_search_album_on_musicbrainz():
    """Test searching for albums on MusicBrainz."""
    result = search_on_musicbrainz(query="abbey road", type="album", limit=5)
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert "result" in result
    assert "releases" in result["result"]
    assert isinstance(result["result"]["releases"], list)
    assert len(result["result"]["releases"]) > 0
    assert result["result"]["count"] > 0
    assert result["error"] is None
    
    # Check release structure
    release = result["result"]["releases"][0]
    assert "id" in release
    assert "title" in release
    assert isinstance(release["title"], str)
    assert len(release["title"]) > 0


def test_search_track_on_musicbrainz():
    """Test searching for tracks on MusicBrainz."""
    result = search_on_musicbrainz(query="here comes the sun", type="track", limit=5)
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert "result" in result
    assert "recordings" in result["result"]
    assert isinstance(result["result"]["recordings"], list)
    assert len(result["result"]["recordings"]) > 0
    assert result["result"]["count"] > 0
    assert result["error"] is None
    
    # Check recording structure
    recording = result["result"]["recordings"][0]
    assert "id" in recording
    assert "title" in recording
    assert isinstance(recording["title"], str)
    assert len(recording["title"]) > 0


def test_search_on_musicbrainz_default_type():
    """Test search_on_musicbrainz uses artist as default type."""
    result = search_on_musicbrainz(query="beatles", limit=5)
    
    assert result["success"] is True
    assert "artists" in result["result"]
    assert "releases" not in result["result"]
    assert "recordings" not in result["result"]


def test_search_on_musicbrainz_invalid_type():
    """Test search_on_musicbrainz handles invalid type."""
    result = search_on_musicbrainz(query="test", type="invalid")
    
    assert result["success"] is False
    assert result["result"] is None
    assert "invalid" in result["error"].lower() or "type" in result["error"].lower()


def test_search_on_musicbrainz_limit():
    """Test search_on_musicbrainz respects limit parameter."""
    result = search_on_musicbrainz(query="beatles", type="artist", limit=3)
    
    assert result["success"] is True
    assert len(result["result"]["artists"]) <= 3


def test_search_on_musicbrainz_no_results():
    """Test search_on_musicbrainz handles queries with no results."""
    # Use a very unlikely query
    result = search_on_musicbrainz(query="xyzabc123nonexistentartist999", type="artist", limit=5)
    
    assert result["success"] is True
    assert result["result"]["count"] == 0
    assert len(result["result"]["artists"]) == 0

