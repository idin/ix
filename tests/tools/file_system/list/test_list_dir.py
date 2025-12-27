"""
Tests for list_dir function.
"""

import pytest
import os

from ixmachina.tools.file_system.list_dir import list_dir
from ixmachina.tools.file_system.empty_dir import empty_dir
from ixmachina.tools.file_system.path_utils import path_exists, path_is_dir
from ..constants import FILE_SYSTEM_TEST_DIR


def test_list_dir_with_existing_directory():
    """Test list_dir successfully lists directory contents."""
    # Create test directory
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    # Create some test files and directories
    test_file = os.path.join(FILE_SYSTEM_TEST_DIR, "test_file.txt")
    test_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "test_dir")
    
    with open(test_file, "w") as f:
        f.write("test content")
    os.makedirs(test_dir)

    result = list_dir(directory_path=FILE_SYSTEM_TEST_DIR)

    assert result["success"] is True
    assert result["error"] is None
    assert len(result["items"]) == 2
    
    # Check that both items are present
    item_names = [item["name"] for item in result["items"]]
    assert "test_file.txt" in item_names
    assert "test_dir" in item_names
    
    # Check item types
    for item in result["items"]:
        assert "name" in item
        assert "type" in item
        assert "path" in item
        assert item["type"] in ["file", "directory"]
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)

    # check to see the directory is empty now
    assert path_exists(FILE_SYSTEM_TEST_DIR)
    assert path_is_dir(FILE_SYSTEM_TEST_DIR)
    assert list_dir(FILE_SYSTEM_TEST_DIR)["items"] == []


def test_list_dir_with_nonexistent_directory():
    """Test list_dir returns error for non-existent directory."""
    result = list_dir(directory_path="/nonexistent/path/that/does/not/exist")
    
    assert result["success"] is False
    assert result["error"] is not None
    assert len(result["items"]) == 0


def test_list_dir_with_file_path():
    """Test list_dir returns error when path is a file, not a directory."""
    # Create test directory
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    # Create a test file
    test_file = os.path.join(FILE_SYSTEM_TEST_DIR, "test_file.txt")
    with open(test_file, "w") as f:
        f.write("test content")

    result = list_dir(directory_path=test_file)
    
    assert result["success"] is False
    assert result["error"] is not None
    assert len(result["items"]) == 0
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_list_dir_excludes_hidden_files():
    """Test list_dir excludes hidden files by default."""
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

    result = list_dir(directory_path=FILE_SYSTEM_TEST_DIR, include_hidden=False)

    assert result["success"] is True
    item_names = [item["name"] for item in result["items"]]
    assert ".hidden_file" not in item_names
    assert "visible_file.txt" in item_names
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_list_dir_includes_hidden_files():
    """Test list_dir includes hidden files when include_hidden=True."""
    # Create test directory
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    # Create a hidden file
    hidden_file = os.path.join(FILE_SYSTEM_TEST_DIR, ".hidden_file")
    with open(hidden_file, "w") as f:
        f.write("hidden")

    result = list_dir(directory_path=FILE_SYSTEM_TEST_DIR, include_hidden=True)

    assert result["success"] is True
    item_names = [item["name"] for item in result["items"]]
    assert ".hidden_file" in item_names
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)

