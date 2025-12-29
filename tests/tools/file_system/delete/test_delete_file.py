"""
Tests for delete_file function.
"""

import pytest
import os

from ixmachina.tools.file_system import delete_file, path_exists, empty_dir
from ..tools_file_system_constants import FILE_SYSTEM_TEST_DIR


def test_delete_file_success():
    """Test delete_file successfully deletes a file."""
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    test_file = os.path.join(FILE_SYSTEM_TEST_DIR, "file_to_delete.txt")
    with open(test_file, "w") as f:
        f.write("test content")
    
    assert path_exists(test_file)
    
    result = delete_file(path=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["file_path"] == test_file
    assert result["recycle_bin_path"] is not None
    assert not path_exists(test_file)  # File should be gone
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_delete_file_nonexistent():
    """Test delete_file returns error for nonexistent file."""
    result = delete_file(path="/nonexistent/path/file.txt")
    
    assert result["success"] is False
    assert result["error"] is not None
    assert "does not exist" in result["error"]
    assert result["recycle_bin_path"] is None


def test_delete_file_with_directory():
    """Test delete_file returns error when path is a directory."""
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    result = delete_file(path=FILE_SYSTEM_TEST_DIR)
    
    assert result["success"] is False
    assert result["error"] is not None
    assert "not a file" in result["error"]
    assert result["recycle_bin_path"] is None
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_delete_file_multiple_files():
    """Test delete_file can delete multiple files independently."""
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    file1 = os.path.join(FILE_SYSTEM_TEST_DIR, "file1.txt")
    file2 = os.path.join(FILE_SYSTEM_TEST_DIR, "file2.txt")
    file3 = os.path.join(FILE_SYSTEM_TEST_DIR, "file3.txt")
    
    for file_path in [file1, file2, file3]:
        with open(file_path, "w") as f:
            f.write("content")
    
    # Delete file1
    result1 = delete_file(path=file1)
    assert result1["success"] is True
    assert not path_exists(file1)
    assert path_exists(file2)
    assert path_exists(file3)
    
    # Delete file2
    result2 = delete_file(path=file2)
    assert result2["success"] is True
    assert not path_exists(file2)
    assert path_exists(file3)
    
    # Delete file3
    result3 = delete_file(path=file3)
    assert result3["success"] is True
    assert not path_exists(file3)
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_delete_file_without_memory():
    """Test delete_file works without file_system_memory parameter."""
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    test_file = os.path.join(FILE_SYSTEM_TEST_DIR, "file.txt")
    with open(test_file, "w") as f:
        f.write("content")
    
    result = delete_file(path=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert not path_exists(test_file)
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)

