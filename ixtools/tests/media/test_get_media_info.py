"""
Tests for get_media_info function.
"""

import pytest
import os

from ixtools.media import get_media_info
from .constants import MEDIA_SOURCE_DIR


def test_get_media_info_with_nonexistent_file():
    """Test get_media_info returns error for nonexistent file."""
    result = get_media_info(file_paths="/nonexistent/path/file.ext")
    
    assert result["success"] is False
    assert result["error"] is not None
    assert result["result"] is None


def test_get_media_info_with_audio():
    """Test get_media_info correctly identifies and processes audio file."""
    test_file = os.path.join(MEDIA_SOURCE_DIR, "audio", "test_audio_mp3.mp3")
    if not os.path.exists(test_file):
        raise FileNotFoundError(f"Test file not found: {test_file}")
    
    result = get_media_info(file_paths=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["result"]["media_type"] == "audio"
    assert result["result"]["audio_info"] is not None
    # Removed - audio_info is just data, not full response


def test_get_media_info_with_video():
    """Test get_media_info correctly identifies and processes video file."""
    test_file = os.path.join(MEDIA_SOURCE_DIR, "video", "test_video_mp4.mp4")
    if not os.path.exists(test_file):
        raise FileNotFoundError(f"Test file not found: {test_file}")
    
    result = get_media_info(file_paths=test_file)
    
    # Result depends on whether ffprobe is installed
    if result["success"]:
        assert result["error"] is None
        assert result["result"]["media_type"] == "video"
        assert result["result"]["video_info"] is not None
    else:
        # If ffprobe is not installed, we should get an appropriate error
        assert result["error"] is not None
        assert "ffprobe" in result["error"].lower() or "ffmpeg" in result["error"].lower()


def test_get_media_info_with_actual_image():
    """Test get_media_info with actual image file."""
    test_file = os.path.join(MEDIA_SOURCE_DIR, "image", "test_image_jpeg.jpeg")
    if not os.path.exists(test_file):
        raise FileNotFoundError(f"Test file not found: {test_file}")
    
    result = get_media_info(file_paths=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["result"]["media_type"] == "image"
    assert result["result"]["image_info"] is not None
    # Removed - image_info is just data, not full response
    assert result["result"]["image_info"]["width"] is not None
    assert result["result"]["image_info"]["height"] is not None


def test_get_media_info_batch_success():
    """Test get_media_info with multiple files."""
    audio_file = os.path.join(MEDIA_SOURCE_DIR, "audio", "test_audio_mp3.mp3")
    image_file = os.path.join(MEDIA_SOURCE_DIR, "image", "test_image_jpeg.jpeg")
    
    test_files = []
    if os.path.exists(audio_file):
        test_files.append(audio_file)
    if os.path.exists(image_file):
        test_files.append(image_file)
    
    if len(test_files) < 2:
        raise ValueError("Need at least 2 test files (audio and image) for batch test")
    
    result = get_media_info(file_paths=test_files)
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert "file_data" in result["result"]
    assert len(result["result"]["file_data"]) == len(test_files)
    assert result["result"]["total_count"] == len(test_files)
    assert result["result"]["success_count"] == len(test_files)
    assert result["result"]["failure_count"] == 0
    assert len(result["result"]["successful_paths"]) == len(test_files)
    assert len(result["result"]["failed_paths"]) == 0
    
    # Check each result (file_data contains just the data, not full response)
    for file_path in test_files:
        assert file_path in result["result"]["file_data"]
        file_result = result["result"]["file_data"][file_path]
        assert file_result is not None  # Successful files have data
        assert file_result["media_type"] in ["audio", "image", "video"]


def test_get_media_info_batch_mixed_success_failure():
    """Test get_media_info with multiple files where some succeed and some fail."""
    audio_file = os.path.join(MEDIA_SOURCE_DIR, "audio", "test_audio_mp3.mp3")
    nonexistent_file = os.path.join(MEDIA_SOURCE_DIR, "nonexistent_file.mp3")
    
    test_files = [nonexistent_file]  # Start with nonexistent
    if os.path.exists(audio_file):
        test_files.append(audio_file)
    
    if not os.path.exists(audio_file):
        raise FileNotFoundError("Need audio test file for mixed success/failure test")
    
    result = get_media_info(file_paths=test_files)
    
    assert isinstance(result, dict)
    assert result["success"] is True  # At least one succeeded
    assert "file_data" in result["result"]
    assert len(result["result"]["file_data"]) == len(test_files)
    assert result["result"]["total_count"] == len(test_files)
    assert result["result"]["success_count"] == 1
    assert result["result"]["failure_count"] == 1
    assert len(result["result"]["successful_paths"]) == 1
    assert len(result["result"]["failed_paths"]) == 1
    
    # Check successful file (file_data contains just the data, not full response)
    assert audio_file in result["result"]["successful_paths"]
    assert result["result"]["file_data"][audio_file] is not None
    assert result["result"]["file_data"][audio_file]["media_type"] == "audio"
    
    # Check failed file (failed files have None in file_data)
    assert nonexistent_file in result["result"]["failed_paths"]
    assert result["result"]["file_data"][nonexistent_file] is None
