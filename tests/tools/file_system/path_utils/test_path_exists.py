"""
Tests for path_exists function.
"""

import pytest
import os

from ixmachina.tools.file_system.path_utils import path_exists
from ixmachina.tools.file_system.empty_dir import empty_dir
from ..constants import FILE_SYSTEM_TEST_DIR


def test_path_exists_with_existing_file():
    """Test path_exists returns True for an existing file."""
    # Create test directory
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    # Create a test file
    test_file = os.path.join(FILE_SYSTEM_TEST_DIR, "test_file.txt")
    with open(test_file, "w") as f:
        f.write("test content")

    result = path_exists(test_file)
    assert result is True
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_path_exists_with_existing_directory():
    """Test path_exists returns True for an existing directory."""
    # Create test directory
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)

    result = path_exists(FILE_SYSTEM_TEST_DIR)
    assert result is True


def test_path_exists_with_nonexistent_path():
    """Test path_exists returns False for a non-existent path."""
    result = path_exists("/nonexistent/path/that/does/not/exist")
    assert result is False

