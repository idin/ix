"""
Tests for copy_file_into function.
"""

import pytest
import os

from ixmachina.tools.file_system.copy_move.copy_file_into import copy_file_into
from ixmachina.tools.file_system.compare_files import compare_files
from ixmachina.tools.file_system.empty_dir import empty_dir
from ixmachina.tools.file_system.path_utils import path_exists
from ..constants import FILE_SYSTEM_TEST_DIR


def test_copy_file_into_copies_file():
    """
    Copy file into directory. Source remains, copy created in directory.
    
    Structure before:
    test_dir/
    ├── file.txt
    └── dest_dir/
    
    Structure after:
    test_dir/
    ├── file.txt
    └── dest_dir/
        └── file.txt
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "file.txt")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "dest_dir")
    os.makedirs(dest_dir)
    
    with open(source_file, "w") as f:
        f.write("test content")
    
    result = copy_file_into(source_path=source_file, destination_dir=dest_dir)
    
    assert result["success"] is True
    assert result["error"] is None
    assert path_exists(source_file)  # Source should still exist
    assert path_exists(os.path.join(dest_dir, "file.txt"))  # Copy should exist
    
    # Verify files are identical
    compare_result = compare_files(
        file_path_1=source_file,
        file_path_2=os.path.join(dest_dir, "file.txt")
    )
    assert compare_result["success"] is True
    assert compare_result["are_equal"] is True
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)


def test_copy_file_into_destination_exists_fails():
    """
    Copying to directory where file already exists should fail.
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
    
    result = copy_file_into(source_path=source_file, destination_dir=dest_dir)
    
    assert result["success"] is False
    assert "Overwrite is not allowed" in result["error"]
    assert path_exists(source_file)  # Source should still exist
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)


def test_copy_file_into_source_not_exists():
    """
    Copying non-existent file should fail.
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "nonexistent.txt")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "dest_dir")
    os.makedirs(dest_dir, exist_ok=True)
    
    result = copy_file_into(source_path=source_file, destination_dir=dest_dir)
    
    assert result["success"] is False
    assert "does not exist" in result["error"]
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)

