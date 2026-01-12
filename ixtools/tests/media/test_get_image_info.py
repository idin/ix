"""
Tests for get_media_info function with image files.
"""

import pytest
import os

from ixtools.media import get_media_info
from .constants import MEDIA_SOURCE_DIR


def test_get_image_info_with_actual_jpeg():
    """Test get_media_info with actual JPEG file."""
    test_file = os.path.join(MEDIA_SOURCE_DIR, "image", "test_image_jpeg.jpeg")
    if not os.path.exists(test_file):
        raise FileNotFoundError(f"Test file not found: {test_file}")
    
    result = get_media_info(file_paths=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["result"]["media_type"] == "image"
    assert result["metadata"]["path"] == test_file
    assert result["result"]["file_size"] is not None
    assert result["result"]["file_size"] > 0
    assert result["result"]["image_info"] is not None
    assert result["result"]["image_info"]["format"] in ["JPEG", "JFIF"]
    assert result["result"]["image_info"]["width"] is not None
    assert result["result"]["image_info"]["height"] is not None
    assert result["result"]["image_info"]["width"] > 0
    assert result["result"]["image_info"]["height"] > 0
    assert result["result"]["image_info"]["resolution"] is not None


def test_get_image_info_with_actual_jpg():
    """Test get_media_info with actual JPG file."""
    test_file = os.path.join(MEDIA_SOURCE_DIR, "image", "test_image_jpg.jpg")
    if not os.path.exists(test_file):
        raise FileNotFoundError(f"Test file not found: {test_file}")
    
    result = get_media_info(file_paths=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["result"]["media_type"] == "image"
    assert result["metadata"]["path"] == test_file
    assert result["result"]["file_size"] is not None
    assert result["result"]["file_size"] > 0
    assert result["result"]["image_info"] is not None
    assert result["result"]["image_info"]["format"] in ["JPEG", "JFIF"]
    assert result["result"]["image_info"]["width"] is not None
    assert result["result"]["image_info"]["height"] is not None
    assert result["result"]["image_info"]["width"] > 0
    assert result["result"]["image_info"]["height"] > 0


def test_get_image_info_with_actual_png():
    """Test get_media_info with actual PNG file."""
    test_file = os.path.join(MEDIA_SOURCE_DIR, "image", "test_image_png.png")
    if not os.path.exists(test_file):
        raise FileNotFoundError(f"Test file not found: {test_file}")
    
    result = get_media_info(file_paths=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["result"]["media_type"] == "image"
    assert result["metadata"]["path"] == test_file
    assert result["result"]["file_size"] is not None
    assert result["result"]["file_size"] > 0
    assert result["result"]["image_info"] is not None
    # Removed - image_info is just data, not full response
    assert result["result"]["image_info"]["format"] == "PNG"
    assert result["result"]["image_info"]["width"] is not None
    assert result["result"]["image_info"]["height"] is not None
    assert result["result"]["image_info"]["width"] > 0
    assert result["result"]["image_info"]["height"] > 0


def test_get_image_info_with_actual_gif():
    """Test get_media_info with actual GIF file."""
    test_file = os.path.join(MEDIA_SOURCE_DIR, "image", "test_image_gif.gif")
    if not os.path.exists(test_file):
        raise FileNotFoundError(f"Test file not found: {test_file}")
    
    result = get_media_info(file_paths=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["result"]["media_type"] == "image"
    assert result["metadata"]["path"] == test_file
    assert result["result"]["file_size"] is not None
    assert result["result"]["file_size"] > 0
    assert result["result"]["image_info"] is not None
    # Removed - image_info is just data, not full response
    assert result["result"]["image_info"]["format"] == "GIF"
    assert result["result"]["image_info"]["width"] is not None
    assert result["result"]["image_info"]["height"] is not None
    assert result["result"]["image_info"]["width"] > 0
    assert result["result"]["image_info"]["height"] > 0


def test_get_image_info_with_nonexistent_file():
    """Test get_media_info returns error for nonexistent image file."""
    result = get_media_info(file_paths="/nonexistent/path/image.png")
    
    assert result["success"] is False
    assert result["error"] is not None
    assert "does not exist" in result["error"]
    assert result["result"] is None
