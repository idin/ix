"""
Tests for get_media_info function.
"""

import pytest
import os

from ixmachina.tools.media import get_media_info
from .constants import MEDIA_SOURCE_DIR


def test_get_media_info_with_nonexistent_file():
    """Test get_media_info returns error for nonexistent file."""
    result = get_media_info(file_paths="/nonexistent/path/file.ext")
    
    assert result["success"] is False
    assert result["error"] is not None
    assert result["media_type"] == "unknown"
    assert result["file_size"] is None


def test_get_media_info_with_audio():
    """Test get_media_info correctly identifies and processes audio file."""
    test_file = os.path.join(MEDIA_SOURCE_DIR, "audio", "test_audio_mp3.mp3")
    if not os.path.exists(test_file):
        pytest.skip(f"Test file not found: {test_file}")
    
    result = get_media_info(file_paths=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["media_type"] == "audio"
    assert result["audio_info"] is not None
    assert result["audio_info"]["success"] is True
    assert result["image_info"] is None
    assert result["video_info"] is None


def test_get_media_info_with_video():
    """Test get_media_info correctly identifies and processes video file."""
    test_file = os.path.join(MEDIA_SOURCE_DIR, "video", "test_video_mp4.mp4")
    if not os.path.exists(test_file):
        pytest.skip(f"Test file not found: {test_file}")
    
    result = get_media_info(file_paths=test_file)
    
    # Result depends on whether ffprobe is installed
    if result["success"]:
        assert result["error"] is None
        assert result["media_type"] == "video"
        assert result["video_info"] is not None
        assert result["audio_info"] is None
        assert result["image_info"] is None
    else:
        # If ffprobe is not installed, we should get an appropriate error
        assert result["error"] is not None
        assert "ffprobe" in result["error"].lower() or "ffmpeg" in result["error"].lower()


def test_get_media_info_with_actual_image():
    """Test get_media_info with actual image file."""
    test_file = os.path.join(MEDIA_SOURCE_DIR, "image", "test_image_jpeg.jpeg")
    if not os.path.exists(test_file):
        pytest.skip(f"Test file not found: {test_file}")
    
    result = get_media_info(file_paths=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["media_type"] == "image"
    assert result["image_info"] is not None
    assert result["image_info"]["success"] is True
    assert result["image_info"]["width"] is not None
    assert result["image_info"]["height"] is not None
    assert result["audio_info"] is None
    assert result["video_info"] is None


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
        pytest.skip("Need at least 2 test files (audio and image) for batch test")
    
    result = get_media_info(file_paths=test_files)
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert "results" in result
    assert len(result["results"]) == len(test_files)
    assert result["total_count"] == len(test_files)
    assert result["success_count"] == len(test_files)
    assert result["failure_count"] == 0
    assert len(result["successful_paths"]) == len(test_files)
    assert len(result["failed_paths"]) == 0
    
    # Check each result
    for file_path in test_files:
        assert file_path in result["results"]
        assert result["results"][file_path]["success"] is True
        assert result["results"][file_path]["media_type"] in ["audio", "image", "video"]


def test_get_media_info_batch_mixed_success_failure():
    """Test get_media_info with multiple files where some succeed and some fail."""
    audio_file = os.path.join(MEDIA_SOURCE_DIR, "audio", "test_audio_mp3.mp3")
    nonexistent_file = os.path.join(MEDIA_SOURCE_DIR, "nonexistent_file.mp3")
    
    test_files = [nonexistent_file]  # Start with nonexistent
    if os.path.exists(audio_file):
        test_files.append(audio_file)
    
    if not os.path.exists(audio_file):
        pytest.skip("Need audio test file for mixed success/failure test")
    
    result = get_media_info(file_paths=test_files)
    
    assert isinstance(result, dict)
    assert result["success"] is True  # At least one succeeded
    assert "results" in result
    assert len(result["results"]) == len(test_files)
    assert result["total_count"] == len(test_files)
    assert result["success_count"] == 1
    assert result["failure_count"] == 1
    assert len(result["successful_paths"]) == 1
    assert len(result["failed_paths"]) == 1
    
    # Check successful file
    assert audio_file in result["successful_paths"]
    assert result["results"][audio_file]["success"] is True
    assert result["results"][audio_file]["media_type"] == "audio"
    
    # Check failed file
    assert nonexistent_file in result["failed_paths"]
    assert result["results"][nonexistent_file]["success"] is False
