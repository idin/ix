"""
Tests for path_is_file function.
"""

import pytest
import os

from ixmachina.tools.file_system import path_is_file, empty_dir
from .tools_file_system_constants import FILE_SYSTEM_TEST_DIR


def test_path_is_file_with_existing_file():
    """Test path_is_file returns True for an existing file."""
    # Create test directory
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    # Create a test file
    test_file = os.path.join(FILE_SYSTEM_TEST_DIR, "test_file.txt")
    with open(test_file, "w") as f:
        f.write("test content")

    result = path_is_file(test_file)
    assert result is True
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_path_is_file_with_existing_directory():
    """Test path_is_file returns False for an existing directory."""
    # Create test directory
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)

    result = path_is_file(FILE_SYSTEM_TEST_DIR)
    assert result is False


def test_path_is_file_with_nonexistent_path():
    """Test path_is_file returns False for a non-existent path."""
    result = path_is_file("/nonexistent/path/that/does/not/exist")
    assert result is False

