"""
Tests for get_audio_info function.

Note: These tests require actual audio files (MP3, FLAC, etc.) to fully test
the functionality. For basic error handling tests, no audio files are needed.
"""

import pytest
import os

from ixmachina.tools.media import get_audio_info
from ixmachina.tools.file_system import empty_dir
from .constants import MEDIA_TEST_DIR


def test_get_audio_info_with_nonexistent_file():
    """Test get_audio_info returns error for nonexistent file."""
    result = get_audio_info(file_path="/nonexistent/path/audio.mp3")
    
    assert result["success"] is False
    assert result["error"] is not None
    assert "does not exist" in result["error"]
    assert result["file_size"] is None
    assert result["format"] is None


def test_get_audio_info_with_directory():
    """Test get_audio_info returns error when path is a directory."""
    os.makedirs(MEDIA_TEST_DIR, exist_ok=True)
    
    result = get_audio_info(file_path=MEDIA_TEST_DIR)
    
    assert result["success"] is False
    assert result["error"] is not None
    assert "not a file" in result["error"]
    
    # Clean up
    empty_dir(path=MEDIA_TEST_DIR)


def test_get_audio_info_with_invalid_file():
    """Test get_audio_info returns error for invalid audio file."""
    os.makedirs(MEDIA_TEST_DIR, exist_ok=True)
    
    test_file = os.path.join(MEDIA_TEST_DIR, "not_audio.txt")
    with open(test_file, "w") as f:
        f.write("This is not an audio file")
    
    result = get_audio_info(file_path=test_file)
    
    assert result["success"] is False
    assert result["error"] is not None
    assert result["file_size"] is not None  # File exists, so size should be reported
    
    # Clean up
    empty_dir(path=MEDIA_TEST_DIR)


def test_get_audio_info_with_mp3():
    """Test get_audio_info with actual MP3 file."""
    test_file = os.path.join(MEDIA_TEST_DIR, "audio", "test_audio_mp3.mp3")
    if not os.path.exists(test_file):
        pytest.skip(f"Test file not found: {test_file}")
    
    result = get_audio_info(file_path=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["file_path"] == test_file
    assert result["file_size"] is not None
    assert result["file_size"] > 0
    assert result["format"] is not None
    # MP3 files should have at least some metadata
    assert result["file_size"] is not None


def test_get_audio_info_with_flac():
    """Test get_audio_info with actual FLAC file."""
    test_file = os.path.join(MEDIA_TEST_DIR, "audio", "test_audio_flac.flac")
    if not os.path.exists(test_file):
        pytest.skip(f"Test file not found: {test_file}")
    
    result = get_audio_info(file_path=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["file_path"] == test_file
    assert result["file_size"] is not None
    assert result["file_size"] > 0
    assert result["format"] is not None


def test_get_audio_info_with_aiff():
    """Test get_audio_info with actual AIFF file."""
    test_file = os.path.join(MEDIA_TEST_DIR, "audio", "test_audio_aiff.aiff")
    if not os.path.exists(test_file):
        pytest.skip(f"Test file not found: {test_file}")
    
    result = get_audio_info(file_path=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["file_path"] == test_file
    assert result["file_size"] is not None
    assert result["file_size"] > 0
    # AIFF format may or may not be detected depending on mutagen support
    # At minimum, file should be readable


def test_get_audio_info_with_m4a():
    """Test get_audio_info with actual M4A file."""
    test_file = os.path.join(MEDIA_TEST_DIR, "audio", "test_audio_m4a.m4a")
    if not os.path.exists(test_file):
        pytest.skip(f"Test file not found: {test_file}")
    
    result = get_audio_info(file_path=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["file_path"] == test_file
    assert result["file_size"] is not None
    assert result["file_size"] > 0
    assert result["format"] is not None

