"""
Tests for move_dir_into function.
"""

import pytest
import os

from ixmachina.tools.file_system import move_dir_into
from ixmachina.tools.file_system import compare_dirs
from ixmachina.tools.file_system import empty_dir
from ixmachina.tools.file_system import path_exists
from ..tools_file_system_constants import FILE_SYSTEM_TEST_DIR


def test_move_dir_into_moves_directory():
    """
    Move directory into another directory. Source is moved, keeps same name.
    
    Structure before:
    test_dir/
    ├── source_dir/
    │   └── file.txt
    └── dest_dir/
    
    Structure after:
    test_dir/
    └── dest_dir/
        └── source_dir/
            └── file.txt
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "source_dir")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "dest_dir")
    os.makedirs(source_dir)
    os.makedirs(dest_dir)
    
    source_file = os.path.join(source_dir, "file.txt")
    with open(source_file, "w") as f:
        f.write("test content")
    
    result = move_dir_into(source_path=source_dir, destination_dir=dest_dir)
    
    assert result["success"] is True
    assert result["error"] is None
    assert not path_exists(source_dir)  # Source should be gone
    assert path_exists(os.path.join(dest_dir, "source_dir"))  # Dir should be in dest_dir
    assert path_exists(os.path.join(dest_dir, "source_dir", "file.txt"))  # File should be moved too
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_move_dir_into_destination_exists_fails():
    """
    Moving to directory where subdirectory already exists should fail.
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "source_dir")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "dest_dir")
    existing_subdir = os.path.join(dest_dir, "source_dir")
    os.makedirs(source_dir)
    os.makedirs(existing_subdir)
    
    result = move_dir_into(source_path=source_dir, destination_dir=dest_dir)
    
    assert result["success"] is False
    assert "Overwrite is not allowed" in result["error"]
    assert path_exists(source_dir)  # Source should still exist
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_move_dir_into_nested_structure():
    """
    Move nested directory structure. All levels preserved in destination.
    
    Structure before:
    test_dir/
    ├── source_dir/
    │   ├── file1.txt
    │   └── subdir/
    │       └── file2.txt
    └── dest_dir/
        (empty)
    
    Structure after:
    test_dir/
    └── dest_dir/
        └── source_dir/
            ├── file1.txt
            └── subdir/
                └── file2.txt
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "source_dir")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "dest_dir")
    os.makedirs(source_dir)
    os.makedirs(dest_dir)
    
    # Create nested structure
    file1 = os.path.join(source_dir, "file1.txt")
    with open(file1, "w") as f:
        f.write("content1")
    
    subdir = os.path.join(source_dir, "subdir")
    os.makedirs(subdir)
    file2 = os.path.join(subdir, "file2.txt")
    with open(file2, "w") as f:
        f.write("content2")
    
    result = move_dir_into(source_path=source_dir, destination_dir=dest_dir)
    
    assert result["success"] is True
    assert result["error"] is None
    assert not path_exists(source_dir)  # Source should not exist
    
    # Verify nested structure
    moved_dir = os.path.join(dest_dir, "source_dir")
    moved_file1 = os.path.join(moved_dir, "file1.txt")
    moved_subdir = os.path.join(moved_dir, "subdir")
    moved_file2 = os.path.join(moved_subdir, "file2.txt")
    
    assert path_exists(moved_file1)
    assert path_exists(moved_subdir)
    assert path_exists(moved_file2)
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_move_dir_into_source_not_exists():
    """
    Moving non-existent directory should fail.
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "nonexistent")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "dest_dir")
    os.makedirs(dest_dir, exist_ok=True)
    
    result = move_dir_into(source_path=source_dir, destination_dir=dest_dir)
    
    assert result["success"] is False
    assert "does not exist" in result["error"]
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)

