"""
Tests for clone_dir_to_path function.
"""

import pytest
import os

from ixmachina.tools.file_system import clone_dir_to_path
from ixmachina.tools.file_system import compare_dirs
from ixmachina.tools.file_system import empty_dir
from ixmachina.tools.file_system import path_exists
from ..tools_file_system_constants import FILE_SYSTEM_TEST_DIR


def test_clone_dir_to_path_copies_directory():
    """
    Clone directory to exact destination. Source remains, destination created.
    
    Structure before:
    test_dir/
    └── source_dir/
        └── file.txt
    
    Structure after:
    test_dir/
    ├── source_dir/
    │   └── file.txt
    └── cloned_dir/
        └── file.txt
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "source_dir")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "cloned_dir")
    os.makedirs(source_dir)
    
    source_file = os.path.join(source_dir, "file.txt")
    with open(source_file, "w") as f:
        f.write("test content")
    
    result = clone_dir_to_path(source_path=source_dir, destination_path=dest_dir)
    
    assert result["success"] is True
    assert result["error"] is None
    assert path_exists(source_dir)  # Source should still exist
    assert path_exists(dest_dir)  # Destination should exist
    
    # Verify directories are identical
    compare_result = compare_dirs(dir_path_1=source_dir, dir_path_2=dest_dir)
    assert compare_result["success"] is True
    assert compare_result["are_equal"] is True
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_clone_dir_to_path_destination_exists_fails():
    """
    Cloning to existing destination should fail.
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "source_dir")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "dest_dir")
    os.makedirs(source_dir)
    os.makedirs(dest_dir)
    
    result = clone_dir_to_path(source_path=source_dir, destination_path=dest_dir)
    
    assert result["success"] is False
    assert "Overwrite is not allowed" in result["error"]
    assert path_exists(source_dir)  # Source should still exist
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_clone_dir_to_path_nested_structure():
    """
    Clone nested directory structure. All levels preserved.
    
    Structure before:
    test_dir/
    └── source_dir/
        ├── file1.txt
        └── subdir/
            ├── file2.txt
            └── nested/
                └── file3.txt
    
    Structure after:
    test_dir/
    ├── source_dir/
    │   ├── file1.txt
    │   └── subdir/
    │       ├── file2.txt
    │       └── nested/
    │           └── file3.txt
    └── cloned_dir/
        ├── file1.txt
        └── subdir/
            ├── file2.txt
            └── nested/
                └── file3.txt
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "source_dir")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "cloned_dir")
    os.makedirs(source_dir)
    
    # Create nested structure
    file1 = os.path.join(source_dir, "file1.txt")
    with open(file1, "w") as f:
        f.write("content1")
    
    subdir = os.path.join(source_dir, "subdir")
    os.makedirs(subdir)
    file2 = os.path.join(subdir, "file2.txt")
    with open(file2, "w") as f:
        f.write("content2")
    
    nested = os.path.join(subdir, "nested")
    os.makedirs(nested)
    file3 = os.path.join(nested, "file3.txt")
    with open(file3, "w") as f:
        f.write("content3")
    
    result = clone_dir_to_path(source_path=source_dir, destination_path=dest_dir)
    
    assert result["success"] is True
    assert result["error"] is None
    
    # Verify directories are identical
    compare_result = compare_dirs(dir_path_1=source_dir, dir_path_2=dest_dir)
    assert compare_result["success"] is True
    assert compare_result["are_equal"] is True
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_clone_dir_to_path_source_not_exists():
    """
    Cloning non-existent directory should fail.
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "nonexistent")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "dest")
    
    result = clone_dir_to_path(source_path=source_dir, destination_path=dest_dir)
    
    assert result["success"] is False
    assert "does not exist" in result["error"]
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)

