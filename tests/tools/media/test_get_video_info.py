"""
Tests for get_video_info function.

Note: These tests require actual video files (MP4, AVI, etc.) and ffprobe
to be installed to fully test the functionality. For basic error handling
tests, no video files are needed.
"""

import pytest
import os

from ixmachina.tools.media import get_video_info
from ixmachina.tools.file_system import empty_dir
from .constants import MEDIA_TEST_DIR


def test_get_video_info_with_nonexistent_file():
    """Test get_video_info returns error for nonexistent file."""
    result = get_video_info(file_path="/nonexistent/path/video.mp4")
    
    assert result["success"] is False
    assert result["error"] is not None
    assert "does not exist" in result["error"]
    assert result["file_size"] is None
    assert result["format"] is None


def test_get_video_info_with_directory():
    """Test get_video_info returns error when path is a directory."""
    os.makedirs(MEDIA_TEST_DIR, exist_ok=True)
    
    result = get_video_info(file_path=MEDIA_TEST_DIR)
    
    assert result["success"] is False
    assert result["error"] is not None
    assert "not a file" in result["error"]
    
    # Clean up
    empty_dir(path=MEDIA_TEST_DIR)


def test_get_video_info_with_invalid_file():
    """Test get_video_info returns error for invalid video file."""
    os.makedirs(MEDIA_TEST_DIR, exist_ok=True)
    
    test_file = os.path.join(MEDIA_TEST_DIR, "not_video.txt")
    with open(test_file, "w") as f:
        f.write("This is not a video file")
    
    result = get_video_info(file_path=test_file)
    
    # Result depends on whether ffprobe is installed
    # If ffprobe is not installed, we'll get that error
    # If it is installed, we'll get an ffprobe parsing error
    assert result["success"] is False
    assert result["error"] is not None
    assert result["file_size"] is not None  # File exists, so size should be reported
    
    # Clean up
    empty_dir(path=MEDIA_TEST_DIR)


def test_get_video_info_with_mp4():
    """Test get_video_info with actual MP4 file."""
    test_file = os.path.join(MEDIA_TEST_DIR, "video", "test_video_mp4.mp4")
    if not os.path.exists(test_file):
        pytest.skip(f"Test file not found: {test_file}")
    
    result = get_video_info(file_path=test_file)
    
    # Result depends on whether ffprobe is installed
    if result["success"]:
        assert result["error"] is None
        assert result["file_path"] == test_file
        assert result["file_size"] is not None
        assert result["file_size"] > 0
        assert result["format"] is not None
        # Video files should have video streams if successfully parsed
        if result.get("video_streams") is not None:
            assert len(result["video_streams"]) > 0
    else:
        # If ffprobe is not installed, we should get an appropriate error
        assert result["error"] is not None
        assert "ffprobe" in result["error"].lower() or "ffmpeg" in result["error"].lower()


def test_get_video_info_with_mov():
    """Test get_video_info with actual MOV file."""
    test_file = os.path.join(MEDIA_TEST_DIR, "video", "test_video_mov.mov")
    if not os.path.exists(test_file):
        pytest.skip(f"Test file not found: {test_file}")
    
    result = get_video_info(file_path=test_file)
    
    # Result depends on whether ffprobe is installed
    if result["success"]:
        assert result["error"] is None
        assert result["file_path"] == test_file
        assert result["file_size"] is not None
        assert result["file_size"] > 0
        assert result["format"] is not None
        # Video files should have video streams if successfully parsed
        if result.get("video_streams") is not None:
            assert len(result["video_streams"]) > 0
    else:
        # If ffprobe is not installed, we should get an appropriate error
        assert result["error"] is not None
        assert "ffprobe" in result["error"].lower() or "ffmpeg" in result["error"].lower()

