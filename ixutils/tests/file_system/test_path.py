"""
Tests for file_system path utilities.
"""

import os
from pathlib import Path
from ixutils.file_system import path_exists, path_is_dir, path_is_file
from tests.file_system.test_paths import FILE_SYSTEM_TEST_DIR


def test_path_exists_with_existing_file():
    """Test that path_exists returns True for existing files."""
    test_file = os.path.join(FILE_SYSTEM_TEST_DIR, "path_test_file.txt")
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    with open(test_file, 'w') as f:
        f.write("test")
    assert path_exists(test_file) is True
    os.unlink(test_file)


def test_path_exists_with_existing_directory():
    """Test that path_exists returns True for existing directories."""
    test_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "path_test_dir")
    os.makedirs(test_dir, exist_ok=True)
    assert path_exists(test_dir) is True
    os.rmdir(test_dir)


def test_path_exists_with_nonexistent_path():
    """Test that path_exists returns False for nonexistent paths."""
    assert path_exists(os.path.join(FILE_SYSTEM_TEST_DIR, "nonexistent", "path")) is False


def test_path_is_file_with_file():
    """Test that path_is_file returns True for files."""
    test_file = os.path.join(FILE_SYSTEM_TEST_DIR, "path_test_file.txt")
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    with open(test_file, 'w') as f:
        f.write("test")
    assert path_is_file(test_file) is True
    os.unlink(test_file)


def test_path_is_file_with_directory():
    """Test that path_is_file returns False for directories."""
    test_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "path_test_dir")
    os.makedirs(test_dir, exist_ok=True)
    assert path_is_file(test_dir) is False
    os.rmdir(test_dir)


def test_path_is_file_with_nonexistent_path():
    """Test that path_is_file returns False for nonexistent paths."""
    assert path_is_file(os.path.join(FILE_SYSTEM_TEST_DIR, "nonexistent", "path")) is False


def test_path_is_dir_with_directory():
    """Test that path_is_dir returns True for directories."""
    test_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "path_test_dir")
    os.makedirs(test_dir, exist_ok=True)
    assert path_is_dir(test_dir) is True
    os.rmdir(test_dir)


def test_path_is_dir_with_file():
    """Test that path_is_dir returns False for files."""
    test_file = os.path.join(FILE_SYSTEM_TEST_DIR, "path_test_file.txt")
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    with open(test_file, 'w') as f:
        f.write("test")
    assert path_is_dir(test_file) is False
    os.unlink(test_file)


def test_path_is_dir_with_nonexistent_path():
    """Test that path_is_dir returns False for nonexistent paths."""
    assert path_is_dir(os.path.join(FILE_SYSTEM_TEST_DIR, "nonexistent", "path")) is False
