"""
Tests for get_media_info function.
"""

import pytest
import os

from ixmachina.tools.media import get_media_info
from ixmachina.tools.file_system import empty_dir
from .constants import MEDIA_TEST_DIR
from .create_test_files import create_test_image


def test_get_media_info_with_image():
    """Test get_media_info correctly identifies and processes image file."""
    os.makedirs(MEDIA_TEST_DIR, exist_ok=True)
    
    test_file = os.path.join(MEDIA_TEST_DIR, "test.png")
    create_test_image(file_path=test_file, width=200, height=150, format="PNG")
    
    result = get_media_info(file_path=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["media_type"] == "image"
    assert result["image_info"] is not None
    assert result["image_info"]["success"] is True
    assert result["image_info"]["width"] == 200
    assert result["image_info"]["height"] == 150
    assert result["audio_info"] is None
    assert result["video_info"] is None
    
    # Clean up
    empty_dir(path=MEDIA_TEST_DIR)


def test_get_media_info_with_nonexistent_file():
    """Test get_media_info returns error for nonexistent file."""
    result = get_media_info(file_path="/nonexistent/path/file.ext")
    
    assert result["success"] is False
    assert result["error"] is not None
    assert result["media_type"] == "unknown"
    assert result["file_size"] is None


def test_get_media_info_with_directory():
    """Test get_media_info returns error when path is a directory."""
    os.makedirs(MEDIA_TEST_DIR, exist_ok=True)
    
    result = get_media_info(file_path=MEDIA_TEST_DIR)
    
    assert result["success"] is False
    assert result["error"] is not None
    assert result["media_type"] == "unknown"
    
    # Clean up
    empty_dir(path=MEDIA_TEST_DIR)


def test_get_media_info_with_invalid_file():
    """Test get_media_info returns error for file that is not media."""
    os.makedirs(MEDIA_TEST_DIR, exist_ok=True)
    
    test_file = os.path.join(MEDIA_TEST_DIR, "not_media.txt")
    with open(test_file, "w") as f:
        f.write("This is not a media file")
    
    result = get_media_info(file_path=test_file)
    
    assert result["success"] is False
    assert result["media_type"] == "unknown"
    assert result["error"] is not None
    
    # Clean up
    empty_dir(path=MEDIA_TEST_DIR)


def test_get_media_info_with_audio():
    """Test get_media_info correctly identifies and processes audio file."""
    test_file = os.path.join(MEDIA_TEST_DIR, "audio", "test_audio_mp3.mp3")
    if not os.path.exists(test_file):
        pytest.skip(f"Test file not found: {test_file}")
    
    result = get_media_info(file_path=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["media_type"] == "audio"
    assert result["audio_info"] is not None
    assert result["audio_info"]["success"] is True
    assert result["image_info"] is None
    assert result["video_info"] is None


def test_get_media_info_with_video():
    """Test get_media_info correctly identifies and processes video file."""
    test_file = os.path.join(MEDIA_TEST_DIR, "video", "test_video_mp4.mp4")
    if not os.path.exists(test_file):
        pytest.skip(f"Test file not found: {test_file}")
    
    result = get_media_info(file_path=test_file)
    
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
    """Test get_media_info with actual image file (not programmatically created)."""
    test_file = os.path.join(MEDIA_TEST_DIR, "image", "test_image_jpeg.jpeg")
    if not os.path.exists(test_file):
        pytest.skip(f"Test file not found: {test_file}")
    
    result = get_media_info(file_path=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["media_type"] == "image"
    assert result["image_info"] is not None
    assert result["image_info"]["success"] is True
    assert result["image_info"]["width"] is not None
    assert result["image_info"]["height"] is not None
    assert result["audio_info"] is None
    assert result["video_info"] is None

