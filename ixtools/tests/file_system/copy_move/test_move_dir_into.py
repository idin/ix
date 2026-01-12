"""
Tests for move_dir_into function.
"""

import pytest
import os
import shutil

from ixtools.file_system import move_into, copy_into
from ixtools.file_system import compare_dirs
from ixtools.file_system import empty_dir
from ixtools.file_system import path_exists
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
    test_content = "test content"
    with open(source_file, "w") as f:
        f.write(test_content)
    
    # Create reference copy before moving (for comparison)
    # Copy to a temp location first, then move to reference_dir to avoid conflicts
    temp_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "temp_reference")
    os.makedirs(temp_dir, exist_ok=True)
    copy_result = copy_into(source_paths=source_dir, destination_dir=temp_dir)
    assert copy_result["success"] is True
    # Move the copied directory to reference_dir
    copied_dir = os.path.join(temp_dir, "source_dir")
    reference_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "reference_dir")
    shutil.move(copied_dir, reference_dir)
    # Clean up temp_dir
    os.rmdir(temp_dir)
    
    result = move_into(source_paths=source_dir, destination_dir=dest_dir)
    
    assert result["success"] is True
    single_result = result["results"][source_dir]
    assert single_result["error"] is None
    assert path_exists(source_dir)["result"] is False  # Source should be gone
    moved_dir = os.path.join(dest_dir, "source_dir")
    assert path_exists(moved_dir)["result"] is True  # Dir should be in dest_dir
    assert path_exists(os.path.join(moved_dir, "file.txt"))["result"] is True  # File should be moved too
    
    # Verify moved directory structure and content matches reference
    compare_result = compare_dirs(
        dir_path_1=reference_dir,
        dir_path_2=moved_dir
    )
    assert compare_result["success"] is True
    assert compare_result["are_equal"] is True
    
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
    
    result = move_into(source_paths=source_dir, destination_dir=dest_dir)
    
    assert result["success"] is False
    single_result = result["results"][source_dir]
    assert "Overwrite is not allowed" in single_result["error"]
    assert path_exists(source_dir)["result"] is True  # Source should still exist
    
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
    
    # Create reference copy before moving (for comparison)
    # Copy to a temp location first, then move to reference_dir to avoid conflicts
    temp_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "temp_reference")
    os.makedirs(temp_dir, exist_ok=True)
    copy_result = copy_into(source_paths=source_dir, destination_dir=temp_dir)
    assert copy_result["success"] is True
    # Move the copied directory to reference_dir
    copied_dir = os.path.join(temp_dir, "source_dir")
    reference_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "reference_dir")
    shutil.move(copied_dir, reference_dir)
    # Clean up temp_dir
    os.rmdir(temp_dir)
    
    result = move_into(source_paths=source_dir, destination_dir=dest_dir)
    
    assert result["success"] is True
    single_result = result["results"][source_dir]
    assert single_result["error"] is None
    assert path_exists(source_dir)["result"] is False  # Source should not exist
    
    # Verify nested structure
    moved_dir = os.path.join(dest_dir, "source_dir")
    moved_file1 = os.path.join(moved_dir, "file1.txt")
    moved_subdir = os.path.join(moved_dir, "subdir")
    moved_file2 = os.path.join(moved_subdir, "file2.txt")
    
    assert path_exists(moved_file1)["result"] is True
    assert path_exists(moved_subdir)["result"] is True
    assert path_exists(moved_file2)["result"] is True
    
    # Verify moved directory structure and content matches reference
    compare_result = compare_dirs(
        dir_path_1=reference_dir,
        dir_path_2=moved_dir
    )
    assert compare_result["success"] is True
    assert compare_result["are_equal"] is True
    
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
    
    result = move_into(source_paths=source_dir, destination_dir=dest_dir)
    
    assert result["success"] is False
    single_result = result["results"][source_dir]
    assert "does not exist" in single_result["error"]
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)

