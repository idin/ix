"""
Tests for delete_file function.
"""

import pytest
import os

from ixmachina.tools.file_system import delete, path_exists, empty_dir
from ..tools_file_system_constants import FILE_SYSTEM_TEST_DIR


def test_delete_file_success():
    """Test delete_file successfully deletes a file."""
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    test_file = os.path.join(FILE_SYSTEM_TEST_DIR, "file_to_delete.txt")
    with open(test_file, "w") as f:
        f.write("test content")
    
    assert path_exists(test_file)
    
    result = delete(paths=test_file)
    
    assert result["success"] is True
    assert result["error"] is None
    single_result = result["results"][test_file]
    assert single_result["path"] == test_file
    assert single_result["recycle_bin_path"] is not None
    assert not path_exists(test_file)  # File should be gone
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_delete_file_nonexistent():
    """Test delete returns error for nonexistent file."""
    result = delete(paths="/nonexistent/path/file.txt")
    
    assert result["success"] is False
    single_result = result["results"]["/nonexistent/path/file.txt"]
    assert single_result["error"] is not None
    assert "does not exist" in single_result["error"]
    assert single_result["recycle_bin_path"] is None


def test_delete_file_with_directory():
    """Test delete works with directory (should succeed, not error)."""
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    result = delete(paths=FILE_SYSTEM_TEST_DIR)
    
    # delete() handles both files and directories, so this should succeed
    assert result["success"] is True
    single_result = result["results"][FILE_SYSTEM_TEST_DIR]
    assert single_result["error"] is None
    assert single_result["recycle_bin_path"] is not None
    
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
    result1 = delete(paths=file1)
    assert result1["success"] is True
    assert not path_exists(file1)
    assert path_exists(file2)
    assert path_exists(file3)
    
    # Delete file2
    result2 = delete(paths=file2)
    assert result2["success"] is True
    assert not path_exists(file2)
    assert path_exists(file3)
    
    # Delete file3
    result3 = delete(paths=file3)
    assert result3["success"] is True
    assert not path_exists(file3)
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_delete_file_without_memory():
    """Test delete works without file_system_memory parameter."""
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    test_file = os.path.join(FILE_SYSTEM_TEST_DIR, "file.txt")
    with open(test_file, "w") as f:
        f.write("content")
    
    result = delete(paths=test_file)
    
    assert result["success"] is True
    single_result = result["results"][test_file]
    assert single_result["error"] is None
    assert not path_exists(test_file)
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)

