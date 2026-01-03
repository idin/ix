"""
Tests for delete_dir function.
"""

import pytest
import os

from ixmachina.tools.file_system import delete, path_exists, empty_dir
from ..tools_file_system_constants import FILE_SYSTEM_TEST_DIR


def test_delete_dir_success():
    """Test delete_dir successfully deletes a directory."""
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    test_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "dir_to_delete")
    os.makedirs(test_dir)
    
    # Add a file inside the directory
    test_file = os.path.join(test_dir, "file.txt")
    with open(test_file, "w") as f:
        f.write("content")
    
    assert path_exists(test_dir)
    
    result = delete(paths=test_dir)
    
    assert result["success"] is True
    single_result = result["results"][test_dir]
    assert single_result["error"] is None
    assert single_result["path"] == test_dir
    assert single_result["recycle_bin_path"] is not None
    assert not path_exists(test_dir)  # Directory should be gone
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_delete_dir_nonexistent():
    """Test delete returns error for nonexistent directory."""
    result = delete(paths="/nonexistent/path/dir")
    
    assert result["success"] is False
    single_result = result["results"]["/nonexistent/path/dir"]
    assert single_result["error"] is not None
    assert "does not exist" in single_result["error"]
    assert single_result["recycle_bin_path"] is None


def test_delete_dir_with_file():
    """Test delete works with file (should succeed, not error)."""
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    test_file = os.path.join(FILE_SYSTEM_TEST_DIR, "file.txt")
    with open(test_file, "w") as f:
        f.write("content")
    
    result = delete(paths=test_file)
    
    # delete() handles both files and directories, so this should succeed
    assert result["success"] is True
    single_result = result["results"][test_file]
    assert single_result["error"] is None
    assert single_result["recycle_bin_path"] is not None
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_delete_dir_with_nested_structure():
    """Test delete_dir deletes directory with nested files and subdirectories."""
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    test_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "nested_dir")
    subdir = os.path.join(test_dir, "subdir")
    os.makedirs(subdir)
    
    file1 = os.path.join(test_dir, "file1.txt")
    file2 = os.path.join(subdir, "file2.txt")
    
    with open(file1, "w") as f:
        f.write("content1")
    with open(file2, "w") as f:
        f.write("content2")
    
    result = delete(paths=test_dir)
    
    assert result["success"] is True
    assert not path_exists(test_dir)
    assert not path_exists(subdir)
    assert not path_exists(file1)
    assert not path_exists(file2)
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_delete_dir_multiple_directories():
    """Test delete_dir can delete multiple directories independently."""
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    dir1 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir1")
    dir2 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir2")
    dir3 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir3")
    
    for dir_path in [dir1, dir2, dir3]:
        os.makedirs(dir_path)
        with open(os.path.join(dir_path, "file.txt"), "w") as f:
            f.write("content")
    
    # Delete dir1
    result1 = delete(paths=dir1)
    assert result1["success"] is True
    assert not path_exists(dir1)
    assert path_exists(dir2)
    assert path_exists(dir3)
    
    # Delete dir2
    result2 = delete(paths=dir2)
    assert result2["success"] is True
    assert not path_exists(dir2)
    assert path_exists(dir3)
    
    # Delete dir3
    result3 = delete(paths=dir3)
    assert result3["success"] is True
    assert not path_exists(dir3)
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_delete_dir_without_memory():
    """Test delete_dir works without file_system_memory parameter."""
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    test_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "dir.txt")
    os.makedirs(test_dir)
    
    result = delete(paths=test_dir)
    
    assert result["success"] is True
    single_result = result["results"][test_dir]
    assert single_result["error"] is None
    assert not path_exists(test_dir)
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)

