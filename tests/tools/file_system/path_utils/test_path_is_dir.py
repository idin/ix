"""
Tests for path_is_dir function.
"""

import pytest
import os

from ixmachina.tools.file_system.path_utils import path_is_dir, path_exists
from ixmachina.tools.file_system.empty_dir import empty_dir
from ..constants import FILE_SYSTEM_TEST_DIR


def test_path_is_dir_with_existing_directory():
    """Test path_is_dir returns True for an existing directory."""
    # Create test directory
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)

    result = path_is_dir(FILE_SYSTEM_TEST_DIR)
    assert result is True


def test_path_is_dir_with_existing_file():
    """Test path_is_dir returns False for an existing file."""
    # Create test directory
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    # Create a test file
    test_file = os.path.join(FILE_SYSTEM_TEST_DIR, "test_file.txt")
    with open(test_file, "w") as f:
        f.write("test content")

    result = path_is_dir(test_file)
    assert result is False
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)

    # empty_dir should not remove the directory
    assert path_exists(FILE_SYSTEM_TEST_DIR)
    assert path_is_dir(FILE_SYSTEM_TEST_DIR)


def test_path_is_dir_with_nonexistent_path():
    """Test path_is_dir returns False for a non-existent path."""
    result = path_is_dir("/nonexistent/path/that/does/not/exist")
    assert result is False

