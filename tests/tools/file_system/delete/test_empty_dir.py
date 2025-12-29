"""
Tests for empty_dir function.
"""

import pytest
import os

from ixmachina.tools.file_system import empty_dir, path_exists, list_dir
from ..tools_file_system_constants import FILE_SYSTEM_TEST_DIR


def test_empty_dir_success():
    """Test empty_dir successfully removes all contents from a directory."""
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    test_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "dir_to_empty")
    os.makedirs(test_dir)
    
    # Add files and subdirectories
    file1 = os.path.join(test_dir, "file1.txt")
    file2 = os.path.join(test_dir, "file2.txt")
    subdir = os.path.join(test_dir, "subdir")
    
    with open(file1, "w") as f:
        f.write("content1")
    with open(file2, "w") as f:
        f.write("content2")
    os.makedirs(subdir)
    
    with open(os.path.join(subdir, "file3.txt"), "w") as f:
        f.write("content3")
    
    result = empty_dir(path=test_dir)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["dir_path"] == test_dir
    assert len(result["deleted_items"]) == 3  # 2 files + 1 directory
    assert path_exists(test_dir)  # Directory itself should still exist
    assert not path_exists(file1)
    assert not path_exists(file2)
    assert not path_exists(subdir)
    
    # Directory should be empty
    list_result = list_dir(path=test_dir)
    assert list_result["success"] is True
    assert len(list_result["items"]) == 0
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_empty_dir_already_empty():
    """Test empty_dir works on an already empty directory."""
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    test_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "empty_dir")
    os.makedirs(test_dir)
    
    result = empty_dir(path=test_dir)
    
    assert result["success"] is True
    assert result["error"] is None
    assert result["deleted_items"] == []
    assert path_exists(test_dir)  # Directory should still exist
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_empty_dir_nonexistent():
    """Test empty_dir returns error for nonexistent directory."""
    result = empty_dir(path="/nonexistent/path/dir")
    
    assert result["success"] is False
    assert result["error"] is not None
    assert "does not exist" in result["error"]
    assert result["deleted_items"] == []


def test_empty_dir_with_file():
    """Test empty_dir returns error when path is a file."""
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    test_file = os.path.join(FILE_SYSTEM_TEST_DIR, "file.txt")
    with open(test_file, "w") as f:
        f.write("content")
    
    result = empty_dir(path=test_file)
    
    assert result["success"] is False
    assert result["error"] is not None
    assert "not a directory" in result["error"]
    assert result["deleted_items"] == []
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_empty_dir_with_nested_structure():
    """Test empty_dir removes deeply nested structures."""
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    test_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "nested_dir")
    level1 = os.path.join(test_dir, "level1")
    level2 = os.path.join(level1, "level2")
    os.makedirs(level2)
    
    file1 = os.path.join(test_dir, "file1.txt")
    file2 = os.path.join(level1, "file2.txt")
    file3 = os.path.join(level2, "file3.txt")
    
    with open(file1, "w") as f:
        f.write("content1")
    with open(file2, "w") as f:
        f.write("content2")
    with open(file3, "w") as f:
        f.write("content3")
    
    result = empty_dir(path=test_dir)
    
    assert result["success"] is True
    assert path_exists(test_dir)  # Directory should still exist
    assert not path_exists(file1)
    assert not path_exists(level1)
    assert not path_exists(level2)
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_empty_dir_without_memory():
    """Test empty_dir works without file_system_memory parameter."""
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    test_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "dir")
    os.makedirs(test_dir)
    
    file1 = os.path.join(test_dir, "file1.txt")
    with open(file1, "w") as f:
        f.write("content")
    
    result = empty_dir(path=test_dir)
    
    assert result["success"] is True
    assert result["error"] is None
    assert path_exists(test_dir)
    assert not path_exists(file1)
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)

