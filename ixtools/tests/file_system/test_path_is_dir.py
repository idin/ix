"""
Tests for path_is_dir function.
"""

import pytest
import os

from ixtools.file_system import path_is_dir, path_exists, empty_dir
from .tools_file_system_constants import FILE_SYSTEM_TEST_DIR


def test_path_is_dir_with_existing_directory():
    """Test path_is_dir returns True for an existing directory."""
    # Create test directory
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)

    result = path_is_dir(FILE_SYSTEM_TEST_DIR)
    assert result["success"] is True
    assert result["result"] is True
    assert result["error"] is None


def test_path_is_dir_with_existing_file():
    """Test path_is_dir returns False for an existing file."""
    # Create test directory
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    # Create a test file
    test_file = os.path.join(FILE_SYSTEM_TEST_DIR, "test_file.txt")
    with open(test_file, "w") as f:
        f.write("test content")

    result = path_is_dir(test_file)
    assert result["success"] is True
    assert result["result"] is False
    assert result["error"] is None
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)

    # empty_dir should not remove the directory
    exists_result = path_exists(FILE_SYSTEM_TEST_DIR)
    assert exists_result["success"] is True
    assert exists_result["result"] is True
    dir_result = path_is_dir(FILE_SYSTEM_TEST_DIR)
    assert dir_result["success"] is True
    assert dir_result["result"] is True


def test_path_is_dir_with_nonexistent_path():
    """Test path_is_dir returns False for a non-existent path."""
    result = path_is_dir("/nonexistent/path/that/does/not/exist")
    assert result["success"] is True
    assert result["result"] is False
    assert result["error"] is None

