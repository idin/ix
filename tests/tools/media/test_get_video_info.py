"""
Tests for get_media_info function with video files.

Note: These tests require actual video files (MP4, AVI, etc.) and ffprobe
to be installed to fully test the functionality. Tests will skip if files are not found.
"""

import pytest
import os

from ixmachina.tools.media import get_media_info
from .constants import MEDIA_SOURCE_DIR


def test_get_video_info_with_nonexistent_file():
    """Test get_media_info returns error for nonexistent video file."""
    result = get_media_info(file_paths="/nonexistent/path/video.mp4")
    
    assert result["success"] is False
    assert result["error"] is not None
    assert "does not exist" in result["error"]
    assert result["file_size"] is None
    assert result["video_info"] is None


def test_get_video_info_with_mp4():
    """Test get_media_info with actual MP4 file."""
    test_file = os.path.join(MEDIA_SOURCE_DIR, "video", "test_video_mp4.mp4")
    if not os.path.exists(test_file):
        pytest.skip(f"Test file not found: {test_file}")
    
    result = get_media_info(file_paths=test_file)
    
    # Result depends on whether ffprobe is installed
    if result["success"]:
        assert result["error"] is None
        assert result["media_type"] == "video"
        assert result["file_path"] == test_file
        assert result["file_size"] is not None
        assert result["file_size"] > 0
        assert result["video_info"] is not None
        assert result["video_info"]["success"] is True
        assert result["video_info"]["format"] is not None
        # Video files should have video streams if successfully parsed
        if result["video_info"].get("video_streams") is not None:
            assert len(result["video_info"]["video_streams"]) > 0
    else:
        # If ffprobe is not installed, we should get an appropriate error
        assert result["error"] is not None
        assert "ffprobe" in result["error"].lower() or "ffmpeg" in result["error"].lower()


def test_get_video_info_with_mov():
    """Test get_media_info with actual MOV file."""
    test_file = os.path.join(MEDIA_SOURCE_DIR, "video", "test_video_mov.mov")
    if not os.path.exists(test_file):
        pytest.skip(f"Test file not found: {test_file}")
    
    result = get_media_info(file_paths=test_file)
    
    # Result depends on whether ffprobe is installed
    if result["success"]:
        assert result["error"] is None
        assert result["media_type"] == "video"
        assert result["file_path"] == test_file
        assert result["file_size"] is not None
        assert result["file_size"] > 0
        assert result["video_info"] is not None
        assert result["video_info"]["success"] is True
        assert result["video_info"]["format"] is not None
        # Video files should have video streams if successfully parsed
        if result["video_info"].get("video_streams") is not None:
            assert len(result["video_info"]["video_streams"]) > 0
    else:
        # If ffprobe is not installed, we should get an appropriate error
        assert result["error"] is not None
        assert "ffprobe" in result["error"].lower() or "ffmpeg" in result["error"].lower()
