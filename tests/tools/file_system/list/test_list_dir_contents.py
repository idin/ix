"""
Tests for list_dir_contents function.
"""

import pytest
import os

from ixmachina.tools.file_system import list_dir_contents, empty_dir
from ..tools_file_system_constants import FILE_SYSTEM_TEST_DIR


def test_list_dir_contents_separates_files_and_directories():
    """Test list_dir_contents separates files and directories."""
    # Create test directory
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    # Create test files and directories
    test_file1 = os.path.join(FILE_SYSTEM_TEST_DIR, "file1.txt")
    test_file2 = os.path.join(FILE_SYSTEM_TEST_DIR, "file2.txt")
    test_dir1 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir1")
    test_dir2 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir2")
    
    with open(test_file1, "w") as f:
        f.write("content1")
    with open(test_file2, "w") as f:
        f.write("content2")
    os.makedirs(test_dir1)
    os.makedirs(test_dir2)

    result = list_dir_contents(path=FILE_SYSTEM_TEST_DIR)

    assert result["success"] is True
    assert result["error"] is None
    assert len(result["files"]) == 2
    assert len(result["directories"]) == 2
    
    # Check file names
    file_names = [f["name"] for f in result["files"]]
    assert "file1.txt" in file_names
    assert "file2.txt" in file_names
    
    # Check directory names
    dir_names = [d["name"] for d in result["directories"]]
    assert "dir1" in dir_names
    assert "dir2" in dir_names
    
    # Check structure of file items
    for file_item in result["files"]:
        assert "name" in file_item
        assert "path" in file_item
    
    # Check structure of directory items
    for dir_item in result["directories"]:
        assert "name" in dir_item
        assert "path" in dir_item
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_list_dir_contents_with_empty_directory():
    """Test list_dir_contents with empty directory."""
    # Create test directory
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)

    result = list_dir_contents(path=FILE_SYSTEM_TEST_DIR)

    assert result["success"] is True
    assert result["error"] is None
    assert len(result["files"]) == 0
    assert len(result["directories"]) == 0
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_list_dir_contents_with_nonexistent_directory():
    """Test list_dir_contents returns error for non-existent directory."""
    result = list_dir_contents(path="/nonexistent/path/that/does/not/exist")
    
    assert result["success"] is False
    assert result["error"] is not None
    assert len(result["files"]) == 0
    assert len(result["directories"]) == 0


def test_list_dir_contents_excludes_hidden_files():
    """Test list_dir_contents excludes hidden files by default."""
    # Create test directory
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    # Create a hidden file
    hidden_file = os.path.join(FILE_SYSTEM_TEST_DIR, ".hidden_file")
    with open(hidden_file, "w") as f:
        f.write("hidden")
    
    # Create a visible file
    visible_file = os.path.join(FILE_SYSTEM_TEST_DIR, "visible_file.txt")
    with open(visible_file, "w") as f:
        f.write("visible")

    result = list_dir_contents(path=FILE_SYSTEM_TEST_DIR, include_hidden=False)

    assert result["success"] is True
    file_names = [f["name"] for f in result["files"]]
    assert ".hidden_file" not in file_names
    assert "visible_file.txt" in file_names
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_list_dir_contents_includes_hidden_files():
    """Test list_dir_contents includes hidden files when include_hidden=True."""
    # Create test directory
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    # Create a hidden file
    hidden_file = os.path.join(FILE_SYSTEM_TEST_DIR, ".hidden_file")
    with open(hidden_file, "w") as f:
        f.write("hidden")

    result = list_dir_contents(path=FILE_SYSTEM_TEST_DIR, include_hidden=True)

    assert result["success"] is True
    file_names = [f["name"] for f in result["files"]]
    assert ".hidden_file" in file_names
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)

