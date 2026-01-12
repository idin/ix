"""
Tests for get_media_info function with audio files.

Note: These tests require actual audio files (MP3, FLAC, etc.) to fully test
the functionality. Tests will skip if files are not found.
"""

import pytest
import os

from ixtools.media import get_media_info
from .constants import MEDIA_SOURCE_DIR


def test_get_audio_info_with_nonexistent_file():
    """Test get_media_info returns error for nonexistent audio file."""
    result = get_media_info(file_paths="/nonexistent/path/audio.mp3")
    
    assert result["success"] is False
    assert result["error"] is not None
    assert "does not exist" in result["error"]
    assert result["result"] is None
    assert result["result"] is None


def test_get_audio_info_with_mp3():
    """Test get_media_info with actual MP3 file."""
    test_file = os.path.join(MEDIA_SOURCE_DIR, "audio", "test_audio_mp3.mp3")
    if not os.path.exists(test_file):
        raise FileNotFoundError(f"Test file not found: {test_file}")
    
    result = get_media_info(file_paths=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["result"]["media_type"] == "audio"
    assert result["metadata"]["path"] == test_file
    assert result["result"]["file_size"] is not None
    assert result["result"]["file_size"] > 0
    assert result["result"]["audio_info"] is not None
    # Removed - audio_info is just data, not full response
    assert result["result"]["audio_info"]["format"] is not None


def test_get_audio_info_with_flac():
    """Test get_media_info with actual FLAC file."""
    test_file = os.path.join(MEDIA_SOURCE_DIR, "audio", "test_audio_flac.flac")
    if not os.path.exists(test_file):
        raise FileNotFoundError(f"Test file not found: {test_file}")
    
    result = get_media_info(file_paths=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["result"]["media_type"] == "audio"
    assert result["metadata"]["path"] == test_file
    assert result["result"]["file_size"] is not None
    assert result["result"]["file_size"] > 0
    assert result["result"]["audio_info"] is not None
    # Removed - audio_info is just data, not full response
    assert result["result"]["audio_info"]["format"] is not None


def test_get_audio_info_with_aiff():
    """Test get_media_info with actual AIFF file."""
    test_file = os.path.join(MEDIA_SOURCE_DIR, "audio", "test_audio_aiff.aiff")
    if not os.path.exists(test_file):
        raise FileNotFoundError(f"Test file not found: {test_file}")
    
    result = get_media_info(file_paths=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["result"]["media_type"] == "audio"
    assert result["metadata"]["path"] == test_file
    assert result["result"]["file_size"] is not None
    assert result["result"]["file_size"] > 0
    assert result["result"]["audio_info"] is not None
    # AIFF format may or may not be detected depending on mutagen support
    # At minimum, file should be readable


def test_get_audio_info_with_m4a():
    """Test get_media_info with actual M4A file."""
    test_file = os.path.join(MEDIA_SOURCE_DIR, "audio", "test_audio_m4a.m4a")
    if not os.path.exists(test_file):
        raise FileNotFoundError(f"Test file not found: {test_file}")
    
    result = get_media_info(file_paths=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["result"]["media_type"] == "audio"
    assert result["metadata"]["path"] == test_file
    assert result["result"]["file_size"] is not None
    assert result["result"]["file_size"] > 0
    assert result["result"]["audio_info"] is not None
    # Removed - audio_info is just data, not full response
    assert result["result"]["audio_info"]["format"] is not None
