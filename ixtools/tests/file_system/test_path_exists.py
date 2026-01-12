"""
Tests for path_exists function.
"""

import pytest
import os

from ixtools.file_system import path_exists, empty_dir
from .tools_file_system_constants import FILE_SYSTEM_TEST_DIR


def test_path_exists_with_existing_file():
    """Test path_exists returns True for an existing file."""
    # Create test directory
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    # Create a test file
    test_file = os.path.join(FILE_SYSTEM_TEST_DIR, "test_file.txt")
    with open(test_file, "w") as f:
        f.write("test content")

    result = path_exists(test_file)
    assert result["success"] is True
    assert result["result"] is True
    assert result["error"] is None
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_path_exists_with_existing_directory():
    """Test path_exists returns True for an existing directory."""
    # Create test directory
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)

    result = path_exists(FILE_SYSTEM_TEST_DIR)
    assert result["success"] is True
    assert result["result"] is True
    assert result["error"] is None


def test_path_exists_with_nonexistent_path():
    """Test path_exists returns False for a non-existent path."""
    result = path_exists("/nonexistent/path/that/does/not/exist")
    assert result["success"] is True
    assert result["result"] is False
    assert result["error"] is None

