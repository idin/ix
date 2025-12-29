"""
Tests for get_image_info function.
"""

import pytest
import os

from ixmachina.tools.media import get_image_info
from ixmachina.tools.file_system import empty_dir
from .constants import MEDIA_TEST_DIR
from .create_test_files import create_test_image


def test_get_image_info_with_png():
    """Test get_image_info returns correct metadata for PNG image."""
    os.makedirs(MEDIA_TEST_DIR, exist_ok=True)
    
    test_file = os.path.join(MEDIA_TEST_DIR, "test.png")
    create_test_image(file_path=test_file, width=200, height=150, format="PNG")
    
    result = get_image_info(file_path=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["file_path"] == test_file
    assert result["file_size"] is not None
    assert result["file_size"] > 0
    assert result["format"] == "PNG"
    assert result["width"] == 200
    assert result["height"] == 150
    assert result["resolution"] == "200x150"
    assert result["mode"] == "RGB"
    assert result["aspect_ratio"] == pytest.approx(200 / 150, rel=1e-6)
    
    # Clean up
    empty_dir(path=MEDIA_TEST_DIR)


def test_get_image_info_with_jpeg():
    """Test get_image_info returns correct metadata for JPEG image."""
    os.makedirs(MEDIA_TEST_DIR, exist_ok=True)
    
    test_file = os.path.join(MEDIA_TEST_DIR, "test.jpg")
    create_test_image(file_path=test_file, width=300, height=200, format="JPEG")
    
    result = get_image_info(file_path=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["format"] == "JPEG"
    assert result["width"] == 300
    assert result["height"] == 200
    assert result["resolution"] == "300x200"
    
    # Clean up
    empty_dir(path=MEDIA_TEST_DIR)


def test_get_image_info_with_actual_jpeg():
    """Test get_image_info with actual JPEG file."""
    test_file = os.path.join(MEDIA_TEST_DIR, "image", "test_image_jpeg.jpeg")
    if not os.path.exists(test_file):
        pytest.skip(f"Test file not found: {test_file}")
    
    result = get_image_info(file_path=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["file_path"] == test_file
    assert result["file_size"] is not None
    assert result["file_size"] > 0
    assert result["format"] in ["JPEG", "JFIF"]
    assert result["width"] is not None
    assert result["height"] is not None
    assert result["width"] > 0
    assert result["height"] > 0
    assert result["resolution"] is not None


def test_get_image_info_with_actual_jpg():
    """Test get_image_info with actual JPG file."""
    test_file = os.path.join(MEDIA_TEST_DIR, "image", "test_image_jpg.jpg")
    if not os.path.exists(test_file):
        pytest.skip(f"Test file not found: {test_file}")
    
    result = get_image_info(file_path=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["file_path"] == test_file
    assert result["file_size"] is not None
    assert result["file_size"] > 0
    assert result["format"] in ["JPEG", "JFIF"]
    assert result["width"] is not None
    assert result["height"] is not None
    assert result["width"] > 0
    assert result["height"] > 0


def test_get_image_info_with_actual_png():
    """Test get_image_info with actual PNG file."""
    test_file = os.path.join(MEDIA_TEST_DIR, "image", "test_image_png.png")
    if not os.path.exists(test_file):
        pytest.skip(f"Test file not found: {test_file}")
    
    result = get_image_info(file_path=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["file_path"] == test_file
    assert result["file_size"] is not None
    assert result["file_size"] > 0
    assert result["format"] == "PNG"
    assert result["width"] is not None
    assert result["height"] is not None
    assert result["width"] > 0
    assert result["height"] > 0


def test_get_image_info_with_actual_gif():
    """Test get_image_info with actual GIF file."""
    test_file = os.path.join(MEDIA_TEST_DIR, "image", "test_image_gif.gif")
    if not os.path.exists(test_file):
        pytest.skip(f"Test file not found: {test_file}")
    
    result = get_image_info(file_path=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["file_path"] == test_file
    assert result["file_size"] is not None
    assert result["file_size"] > 0
    assert result["format"] == "GIF"
    assert result["width"] is not None
    assert result["height"] is not None
    assert result["width"] > 0
    assert result["height"] > 0


def test_get_image_info_with_nonexistent_file():
    """Test get_image_info returns error for nonexistent file."""
    result = get_image_info(file_path="/nonexistent/path/image.png")
    
    assert result["success"] is False
    assert result["error"] is not None
    assert "does not exist" in result["error"]
    assert result["file_size"] is None
    assert result["format"] is None


def test_get_image_info_with_directory():
    """Test get_image_info returns error when path is a directory."""
    os.makedirs(MEDIA_TEST_DIR, exist_ok=True)
    
    result = get_image_info(file_path=MEDIA_TEST_DIR)
    
    assert result["success"] is False
    assert result["error"] is not None
    assert "not a file" in result["error"]
    
    # Clean up
    empty_dir(path=MEDIA_TEST_DIR)


def test_get_image_info_with_invalid_file():
    """Test get_image_info returns error for invalid image file."""
    os.makedirs(MEDIA_TEST_DIR, exist_ok=True)
    
    test_file = os.path.join(MEDIA_TEST_DIR, "not_an_image.txt")
    with open(test_file, "w") as f:
        f.write("This is not an image file")
    
    result = get_image_info(file_path=test_file)
    
    assert result["success"] is False
    assert result["error"] is not None
    
    # Clean up
    empty_dir(path=MEDIA_TEST_DIR)

