"""
Tests for compare_files function.
"""

import pytest
import os

from ixmachina.tools.file_system import compare_files, empty_dir
from ..tools_file_system_constants import FILE_SYSTEM_TEST_DIR


def test_compare_files_same_content_same_dir():
    """Test compare_files returns True for files with same content in same directory."""
    # Create test directory
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    # Create two files with same content
    file1 = os.path.join(FILE_SYSTEM_TEST_DIR, "file1.txt")
    file2 = os.path.join(FILE_SYSTEM_TEST_DIR, "file2.txt")
    
    with open(file1, "w") as f:
        f.write("same content")
    with open(file2, "w") as f:
        f.write("same content")

    result = compare_files(file_path_1=file1, file_path_2=file2)

    assert result["success"] is True
    assert result["are_equal"] is True
    assert result["sizes_equal"] is True
    assert result["error"] is None
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_compare_files_same_content_different_dirs():
    """Test compare_files returns True for files with same content in different directories."""
    # Create test directories
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    subdir1 = os.path.join(FILE_SYSTEM_TEST_DIR, "subdir1")
    subdir2 = os.path.join(FILE_SYSTEM_TEST_DIR, "subdir2")
    os.makedirs(subdir1)
    os.makedirs(subdir2)
    
    # Create two files with same content in different directories
    file1 = os.path.join(subdir1, "file.txt")
    file2 = os.path.join(subdir2, "file.txt")
    
    with open(file1, "w") as f:
        f.write("same content")
    with open(file2, "w") as f:
        f.write("same content")

    result = compare_files(file_path_1=file1, file_path_2=file2)

    assert result["success"] is True
    assert result["are_equal"] is True
    assert result["sizes_equal"] is True
    assert result["error"] is None
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_compare_files_different_content_same_size():
    """Test compare_files returns False for files with different content but same size."""
    # Create test directory
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    # Create two files with different content but same size
    file1 = os.path.join(FILE_SYSTEM_TEST_DIR, "file1.txt")
    file2 = os.path.join(FILE_SYSTEM_TEST_DIR, "file2.txt")
    
    with open(file1, "w") as f:
        f.write("content1")
    with open(file2, "w") as f:
        f.write("content2")

    result = compare_files(file_path_1=file1, file_path_2=file2)

    assert result["success"] is True
    assert result["are_equal"] is False
    assert result["sizes_equal"] is True  # Same size but different content
    assert result["error"] is None
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_compare_files_different_size():
    """Test compare_files returns False for files with different sizes."""
    # Create test directory
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    # Create two files with different sizes
    file1 = os.path.join(FILE_SYSTEM_TEST_DIR, "file1.txt")
    file2 = os.path.join(FILE_SYSTEM_TEST_DIR, "file2.txt")
    
    with open(file1, "w") as f:
        f.write("short")
    with open(file2, "w") as f:
        f.write("much longer content")

    result = compare_files(file_path_1=file1, file_path_2=file2)

    assert result["success"] is True
    assert result["are_equal"] is False
    assert result["sizes_equal"] is False  # Different sizes
    assert result["error"] is None
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_compare_files_one_missing():
    """Test compare_files returns error when one file doesn't exist."""
    # Create test directory
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    # Create one file
    file1 = os.path.join(FILE_SYSTEM_TEST_DIR, "file1.txt")
    file2 = os.path.join(FILE_SYSTEM_TEST_DIR, "nonexistent.txt")
    
    with open(file1, "w") as f:
        f.write("content")

    result = compare_files(file_path_1=file1, file_path_2=file2)

    assert result["success"] is False
    assert "error" in result
    assert "does not exist" in result["error"]
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_compare_files_both_missing():
    """Test compare_files returns error when both files don't exist."""
    # Create test directory
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    file1 = os.path.join(FILE_SYSTEM_TEST_DIR, "nonexistent1.txt")
    file2 = os.path.join(FILE_SYSTEM_TEST_DIR, "nonexistent2.txt")

    result = compare_files(file_path_1=file1, file_path_2=file2)

    assert result["success"] is False
    assert "error" in result
    assert "does not exist" in result["error"]
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_compare_files_empty_files():
    """Test compare_files returns True for two empty files."""
    # Create test directory
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    file1 = os.path.join(FILE_SYSTEM_TEST_DIR, "empty1.txt")
    file2 = os.path.join(FILE_SYSTEM_TEST_DIR, "empty2.txt")
    
    # Create empty files
    with open(file1, "w"):
        pass
    with open(file2, "w"):
        pass

    result = compare_files(file_path_1=file1, file_path_2=file2)

    assert result["success"] is True
    assert result["are_equal"] is True
    assert result["sizes_equal"] is True
    assert result["error"] is None
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_compare_files_binary_content():
    """Test compare_files works with binary content."""
    # Create test directory
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    file1 = os.path.join(FILE_SYSTEM_TEST_DIR, "binary1.bin")
    file2 = os.path.join(FILE_SYSTEM_TEST_DIR, "binary2.bin")
    
    # Create binary files with same content
    binary_data = b"\x00\x01\x02\x03\xff\xfe\xfd"
    with open(file1, "wb") as f:
        f.write(binary_data)
    with open(file2, "wb") as f:
        f.write(binary_data)

    result = compare_files(file_path_1=file1, file_path_2=file2)

    assert result["success"] is True
    assert result["are_equal"] is True
    assert result["sizes_equal"] is True
    assert result["error"] is None
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)

