"""
Tests for change_file_path function.
"""

import pytest
import os

from ixmachina.tools.file_system.copy_move.change_file_path import change_file_path
from ixmachina.tools.file_system.compare_files import compare_files
from ixmachina.tools.file_system.empty_dir import empty_dir
from ixmachina.tools.file_system.path_utils import path_exists
from ..constants import FILE_SYSTEM_TEST_DIR


def test_change_file_path_renames_file():
    """
    Move file to exact destination path. Source is moved/renamed.
    
    Structure before:
    test_dir/
    └── old.txt
    
    Structure after:
    test_dir/
    └── new.txt
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "old.txt")
    dest_file = os.path.join(FILE_SYSTEM_TEST_DIR, "new.txt")
    
    with open(source_file, "w") as f:
        f.write("test content")
    
    result = change_file_path(source_path=source_file, destination_path=dest_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert not path_exists(source_file)  # Source should be gone
    assert path_exists(dest_file)  # Destination should exist
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)


def test_change_file_path_moves_to_different_directory():
    """
    Move file to different directory with new name.
    
    Structure before:
    test_dir/
    ├── subdir/
    │   └── file.txt
    └── moved.txt
    
    Structure after:
    test_dir/
    ├── subdir/
    └── moved.txt
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    subdir = os.path.join(FILE_SYSTEM_TEST_DIR, "subdir")
    os.makedirs(subdir)
    
    source_file = os.path.join(subdir, "file.txt")
    dest_file = os.path.join(FILE_SYSTEM_TEST_DIR, "moved.txt")
    
    with open(source_file, "w") as f:
        f.write("test content")
    
    result = change_file_path(source_path=source_file, destination_path=dest_file)
    
    assert result["success"] is True
    assert not path_exists(source_file)
    assert path_exists(dest_file)
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)


def test_change_file_path_destination_exists_fails():
    """
    Moving to existing destination should fail.
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "source.txt")
    dest_file = os.path.join(FILE_SYSTEM_TEST_DIR, "dest.txt")
    
    with open(source_file, "w") as f:
        f.write("source content")
    with open(dest_file, "w") as f:
        f.write("dest content")
    
    result = change_file_path(source_path=source_file, destination_path=dest_file)
    
    assert result["success"] is False
    assert "Overwrite is not allowed" in result["error"]
    assert path_exists(source_file)  # Source should still exist
    assert path_exists(dest_file)  # Destination should still exist
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)


def test_change_file_path_source_not_exists_fails():
    """
    Moving non-existent file should fail.
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "nonexistent.txt")
    dest_file = os.path.join(FILE_SYSTEM_TEST_DIR, "dest.txt")
    
    result = change_file_path(source_path=source_file, destination_path=dest_file)
    
    assert result["success"] is False
    assert "does not exist" in result["error"]
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)


def test_change_file_path_creates_parent_directory():
    """
    Moving file should create parent directory if it doesn't exist.
    
    Structure before:
    test_dir/
    └── file.txt
    
    Structure after:
    test_dir/
    ├── file.txt
    └── nested/
        └── moved.txt
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "file.txt")
    dest_file = os.path.join(FILE_SYSTEM_TEST_DIR, "nested", "moved.txt")
    
    with open(source_file, "w") as f:
        f.write("test content")
    
    result = change_file_path(source_path=source_file, destination_path=dest_file)
    
    assert result["success"] is True
    assert path_exists(dest_file)
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)


def test_change_file_path_binary_content():
    """
    Move binary file. Binary content preserved.
    
    Structure before:
    test_dir/
    └── binary.bin
    
    Structure after:
    test_dir/
    └── binary_moved.bin
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "binary.bin")
    dest_file = os.path.join(FILE_SYSTEM_TEST_DIR, "binary_moved.bin")
    
    binary_data = b"\x00\x01\x02\x03\xff\xfe\xfd"
    with open(source_file, "wb") as f:
        f.write(binary_data)
    
    result = change_file_path(source_path=source_file, destination_path=dest_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert not path_exists(source_file)  # Source should not exist
    assert path_exists(dest_file)  # Destination should exist
    
    # Verify binary content
    with open(dest_file, "rb") as f:
        assert f.read() == binary_data
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)

