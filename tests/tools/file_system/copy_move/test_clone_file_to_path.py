"""
Tests for clone_file_to_path function.
"""

import pytest
import os

from ixmachina.tools.file_system.copy_move.clone_file_to_path import clone_file_to_path
from ixmachina.tools.file_system.compare_files import compare_files
from ixmachina.tools.file_system.empty_dir import empty_dir
from ixmachina.tools.file_system.path_utils import path_exists
from ..constants import FILE_SYSTEM_TEST_DIR


def test_clone_file_to_path_copies_file():
    """
    Clone file to exact destination. Source remains, destination created.
    
    Structure before:
    test_dir/
    └── source.txt
    
    Structure after:
    test_dir/
    ├── source.txt
    └── cloned.txt
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "source.txt")
    dest_file = os.path.join(FILE_SYSTEM_TEST_DIR, "cloned.txt")
    
    with open(source_file, "w") as f:
        f.write("test content")
    
    result = clone_file_to_path(source_path=source_file, destination_path=dest_file)
    
    assert result["success"] is True
    assert result["error"] is None
    assert path_exists(source_file)  # Source should still exist
    assert path_exists(dest_file)  # Destination should exist
    
    # Verify files are identical
    compare_result = compare_files(file_path_1=source_file, file_path_2=dest_file)
    assert compare_result["success"] is True
    assert compare_result["are_equal"] is True
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)


def test_clone_file_to_path_destination_exists_fails():
    """
    Cloning to existing destination should fail.
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "source.txt")
    dest_file = os.path.join(FILE_SYSTEM_TEST_DIR, "dest.txt")
    
    with open(source_file, "w") as f:
        f.write("source content")
    with open(dest_file, "w") as f:
        f.write("dest content")
    
    result = clone_file_to_path(source_path=source_file, destination_path=dest_file)
    
    assert result["success"] is False
    assert "Overwrite is not allowed" in result["error"]
    assert path_exists(source_file)  # Source should still exist
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)


def test_clone_file_to_path_creates_parent_directory():
    """
    Cloning should create parent directory if it doesn't exist.
    
    Structure before:
    test_dir/
    └── file.txt
    
    Structure after:
    test_dir/
    ├── file.txt
    └── nested/
        └── cloned.txt
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "file.txt")
    dest_file = os.path.join(FILE_SYSTEM_TEST_DIR, "nested", "cloned.txt")
    
    with open(source_file, "w") as f:
        f.write("test content")
    
    result = clone_file_to_path(source_path=source_file, destination_path=dest_file)
    
    assert result["success"] is True
    assert path_exists(dest_file)
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)


def test_clone_file_to_path_binary_content():
    """
    Clone binary file. Binary content preserved.
    
    Structure before:
    test_dir/
    └── binary.bin
    
    Structure after:
    test_dir/
    ├── binary.bin
    └── binary_cloned.bin
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "binary.bin")
    dest_file = os.path.join(FILE_SYSTEM_TEST_DIR, "binary_cloned.bin")
    
    binary_data = b"\x00\x01\x02\x03\xff\xfe\xfd"
    with open(source_file, "wb") as f:
        f.write(binary_data)
    
    result = clone_file_to_path(source_path=source_file, destination_path=dest_file)
    
    assert result["success"] is True
    assert result["error"] is None
    
    # Verify files are identical
    compare_result = compare_files(file_path_1=source_file, file_path_2=dest_file)
    assert compare_result["success"] is True
    assert compare_result["are_equal"] is True
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)


def test_clone_file_to_path_source_not_exists():
    """
    Cloning non-existent file should fail.
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "nonexistent.txt")
    dest_file = os.path.join(FILE_SYSTEM_TEST_DIR, "dest.txt")
    
    result = clone_file_to_path(source_path=source_file, destination_path=dest_file)
    
    assert result["success"] is False
    assert "does not exist" in result["error"]
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)

