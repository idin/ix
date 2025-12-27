"""
Tests for move_file_into function.
"""

import pytest
import os

from ixmachina.tools.file_system.copy_move.move_file_into import move_file_into
from ixmachina.tools.file_system.compare_files import compare_files
from ixmachina.tools.file_system.empty_dir import empty_dir
from ixmachina.tools.file_system.path_utils import path_exists, path_is_dir
from ..constants import FILE_SYSTEM_TEST_DIR


def test_move_file_into_moves_file():
    """
    Move file into directory. Source is moved, keeps same name.
    
    Structure before:
    test_dir/
    ├── file.txt
    └── dest_dir/
    
    Structure after:
    test_dir/
    └── dest_dir/
        └── file.txt
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "file.txt")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "dest_dir")
    os.makedirs(dest_dir)
    
    with open(source_file, "w") as f:
        f.write("test content")
    
    result = move_file_into(source_path=source_file, destination_dir=dest_dir)
    
    assert result["success"] is True
    assert result["error"] is None
    assert not path_exists(source_file)  # Source should be gone
    assert path_exists(os.path.join(dest_dir, "file.txt"))  # File should be in dest_dir
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)


def test_move_file_into_destination_not_exists_fails():
    """
    Moving into non-existent directory should fail.
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "file.txt")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "nonexistent_dir")
    
    with open(source_file, "w") as f:
        f.write("test content")
    
    result = move_file_into(source_path=source_file, destination_dir=dest_dir)
    
    assert result["success"] is False
    assert "does not exist" in result["error"]
    assert path_exists(source_file)  # Source should still exist
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)


def test_move_file_into_destination_exists_fails():
    """
    Moving to directory where file already exists should fail.
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "file.txt")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "dest_dir")
    os.makedirs(dest_dir)
    existing_file = os.path.join(dest_dir, "file.txt")
    
    with open(source_file, "w") as f:
        f.write("source content")
    with open(existing_file, "w") as f:
        f.write("existing content")
    
    result = move_file_into(source_path=source_file, destination_dir=dest_dir)
    
    assert result["success"] is False
    assert "Overwrite is not allowed" in result["error"]
    assert path_exists(source_file)  # Source should still exist
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)


def test_move_file_into_source_not_exists_fails():
    """
    Moving non-existent file should fail.
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "nonexistent.txt")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "dest_dir")
    os.makedirs(dest_dir)
    
    result = move_file_into(source_path=source_file, destination_dir=dest_dir)
    
    assert result["success"] is False
    assert "does not exist" in result["error"]
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)

