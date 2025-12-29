"""
Tests for copy_dir_into function.
"""

import pytest
import os

from ixmachina.tools.file_system import copy_dir_into
from ixmachina.tools.file_system import compare_dirs
from ixmachina.tools.file_system import empty_dir
from ixmachina.tools.file_system import path_exists
from ..tools_file_system_constants import FILE_SYSTEM_TEST_DIR


def test_copy_dir_into_copies_directory():
    """
    Copy directory into another directory. Source remains, copy created in directory.
    
    Structure before:
    test_dir/
    ├── source_dir/
    │   └── file.txt
    └── dest_dir/
    
    Structure after:
    test_dir/
    ├── source_dir/
    │   └── file.txt
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
    
    result = copy_dir_into(source_path=source_dir, destination_dir=dest_dir)
    
    assert result["success"] is True
    assert result["error"] is None
    assert path_exists(source_dir)  # Source should still exist
    assert path_exists(os.path.join(dest_dir, "source_dir"))  # Copy should exist
    
    # Verify directories are identical
    compare_result = compare_dirs(
        dir_path_1=source_dir,
        dir_path_2=os.path.join(dest_dir, "source_dir")
    )
    assert compare_result["success"] is True
    assert compare_result["are_equal"] is True
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_copy_dir_into_destination_exists_fails():
    """
    Copying to directory where subdirectory already exists should fail.
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "source_dir")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "dest_dir")
    existing_subdir = os.path.join(dest_dir, "source_dir")
    os.makedirs(source_dir)
    os.makedirs(existing_subdir)
    
    result = copy_dir_into(source_path=source_dir, destination_dir=dest_dir)
    
    assert result["success"] is False
    assert "Overwrite is not allowed" in result["error"]
    assert path_exists(source_dir)  # Source should still exist
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_copy_dir_into_source_not_exists():
    """
    Copying non-existent directory should fail.
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "nonexistent")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "dest_dir")
    os.makedirs(dest_dir, exist_ok=True)
    
    result = copy_dir_into(source_path=source_dir, destination_dir=dest_dir)
    
    assert result["success"] is False
    assert "does not exist" in result["error"]
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)

