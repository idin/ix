"""
Tests for change_dir_path function.
"""

import pytest
import os

from ixmachina.tools.file_system.copy_move.change_dir_path import change_dir_path
from ixmachina.tools.file_system.compare_dirs import compare_dirs
from ixmachina.tools.file_system.empty_dir import empty_dir
from ixmachina.tools.file_system.path_utils import path_exists
from ..constants import FILE_SYSTEM_TEST_DIR


def test_change_dir_path_renames_directory():
    """
    Move directory to exact destination path. Source is moved/renamed.
    
    Structure before:
    test_dir/
    └── old_dir/
        └── file.txt
    
    Structure after:
    test_dir/
    └── new_dir/
        └── file.txt
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "old_dir")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "new_dir")
    os.makedirs(source_dir)
    
    source_file = os.path.join(source_dir, "file.txt")
    with open(source_file, "w") as f:
        f.write("test content")
    
    result = change_dir_path(source_path=source_dir, destination_path=dest_dir)
    
    assert result["success"] is True
    assert result["error"] is None
    assert not path_exists(source_dir)  # Source should be gone
    assert path_exists(dest_dir)  # Destination should exist
    assert path_exists(os.path.join(dest_dir, "file.txt"))  # File should be in new location
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)


def test_change_dir_path_destination_exists_fails():
    """
    Moving to existing destination should fail.
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "source_dir")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "dest_dir")
    os.makedirs(source_dir)
    os.makedirs(dest_dir)
    
    result = change_dir_path(source_path=source_dir, destination_path=dest_dir)
    
    assert result["success"] is False
    assert "Overwrite is not allowed" in result["error"]
    assert path_exists(source_dir)  # Source should still exist
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)


def test_change_dir_path_creates_parent_directory():
    """
    Moving directory should create parent directory if it doesn't exist.
    
    Structure before:
    test_dir/
    └── source_dir/
        └── file.txt
    
    Structure after:
    test_dir/
    └── nested/
        └── moved_dir/
            └── file.txt
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "source_dir")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "nested", "moved_dir")
    os.makedirs(source_dir)
    
    source_file = os.path.join(source_dir, "file.txt")
    with open(source_file, "w") as f:
        f.write("test content")
    
    result = change_dir_path(source_path=source_dir, destination_path=dest_dir)
    
    assert result["success"] is True
    assert path_exists(dest_dir)
    assert path_exists(os.path.join(dest_dir, "file.txt"))
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)

