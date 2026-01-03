"""
Tests for get_from_musicbrainz tool.
"""

import pytest

from ixmachina.tools.music import get_from_musicbrainz, search_on_musicbrainz


def test_get_artist_from_musicbrainz():
    """Test getting artist details from MusicBrainz by ID."""
    # First search to get a real artist ID
    search_result = search_on_musicbrainz(query="beatles", type="artist", limit=1)
    assert search_result["success"] is True
    assert len(search_result["result"]["artists"]) > 0
    
    artist_id = search_result["result"]["artists"][0]["id"]
    
    # Now get the full artist details
    result = get_from_musicbrainz(entity_id=artist_id, type="artist")
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert "result" in result
    assert result["result"]["id"] == artist_id
    assert "name" in result["result"]
    assert isinstance(result["result"]["name"], str)
    assert len(result["result"]["name"]) > 0
    assert result["error"] is None


def test_get_artist_from_musicbrainz_with_releases():
    """Test getting artist with release groups included."""
    # First search to get a real artist ID
    search_result = search_on_musicbrainz(query="beatles", type="artist", limit=1)
    assert search_result["success"] is True
    assert len(search_result["result"]["artists"]) > 0
    
    artist_id = search_result["result"]["artists"][0]["id"]
    
    # Get artist with release groups
    result = get_from_musicbrainz(entity_id=artist_id, type="artist", include_related=True)
    
    assert result["success"] is True
    assert "release_groups" in result["result"]
    assert isinstance(result["result"]["release_groups"], list)


def test_get_album_from_musicbrainz():
    """Test getting album details from MusicBrainz by ID."""
    # First search to get a real release ID
    search_result = search_on_musicbrainz(query="abbey road", type="album", limit=1)
    assert search_result["success"] is True
    assert len(search_result["result"]["releases"]) > 0
    
    release_id = search_result["result"]["releases"][0]["id"]
    
    # Now get the full release details
    result = get_from_musicbrainz(entity_id=release_id, type="album")
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert "result" in result
    assert result["result"]["id"] == release_id
    assert "title" in result["result"]
    assert isinstance(result["result"]["title"], str)
    assert len(result["result"]["title"]) > 0
    assert result["error"] is None


def test_get_album_from_musicbrainz_with_recordings():
    """Test getting album with track recordings included."""
    # First search to get a real release ID
    search_result = search_on_musicbrainz(query="abbey road", type="album", limit=1)
    assert search_result["success"] is True
    assert len(search_result["result"]["releases"]) > 0
    
    release_id = search_result["result"]["releases"][0]["id"]
    
    # Get release with recordings
    result = get_from_musicbrainz(entity_id=release_id, type="album", include_related=True)
    
    assert result["success"] is True
    assert "tracks" in result["result"]
    assert isinstance(result["result"]["tracks"], list)
    if len(result["result"]["tracks"]) > 0:
        track = result["result"]["tracks"][0]
        assert "title" in track
        assert "id" in track


def test_get_track_from_musicbrainz():
    """Test getting track details from MusicBrainz by ID."""
    # First search to get a real recording ID
    search_result = search_on_musicbrainz(query="here comes the sun", type="track", limit=1)
    assert search_result["success"] is True
    assert len(search_result["result"]["recordings"]) > 0
    
    recording_id = search_result["result"]["recordings"][0]["id"]
    
    # Now get the full recording details
    result = get_from_musicbrainz(entity_id=recording_id, type="track")
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert "result" in result
    assert result["result"]["id"] == recording_id
    assert "title" in result["result"]
    assert isinstance(result["result"]["title"], str)
    assert len(result["result"]["title"]) > 0
    assert result["error"] is None


def test_get_from_musicbrainz_invalid_id():
    """Test get_from_musicbrainz handles invalid ID."""
    result = get_from_musicbrainz(entity_id="invalid-id-12345", type="artist")
    
    assert result["success"] is False
    assert result["result"] is None
    assert result["error"] is not None


def test_get_from_musicbrainz_invalid_type():
    """Test get_from_musicbrainz handles invalid type."""
    result = get_from_musicbrainz(entity_id="some-id", type="invalid")
    
    assert result["success"] is False
    assert result["result"] is None
    assert "invalid" in result["error"].lower() or "type" in result["error"].lower()

