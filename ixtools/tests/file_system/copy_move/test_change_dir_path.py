"""
Tests for change_dir_path function.
"""

import pytest
import os
import shutil

from ixtools.file_system import change_path, copy_into
from ixtools.file_system import compare_dirs
from ixtools.file_system import empty_dir
from ixtools.file_system import path_exists
from ..tools_file_system_constants import FILE_SYSTEM_TEST_DIR


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
    copied_dir = os.path.join(temp_dir, "old_dir")
    reference_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "reference_dir")
    shutil.move(copied_dir, reference_dir)
    # Clean up temp_dir
    os.rmdir(temp_dir)
    
    result = change_path(source_destination_pairs={"source_path": source_dir, "destination_path": dest_dir})
    
    assert result["success"] is True
    single_result = result["results"][source_dir]
    assert single_result["error"] is None
    assert not path_exists(source_dir)  # Source should be gone
    assert path_exists(dest_dir)  # Destination should exist
    assert path_exists(os.path.join(dest_dir, "file.txt"))  # File should be in new location
    
    # Verify moved directory structure and content matches reference
    compare_result = compare_dirs(
        dir_path_1=reference_dir,
        dir_path_2=dest_dir
    )
    assert compare_result["success"] is True
    assert compare_result["are_equal"] is True
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_change_dir_path_destination_exists_fails():
    """
    Moving to existing destination should fail.
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "source_dir")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "dest_dir")
    os.makedirs(source_dir)
    os.makedirs(dest_dir)
    
    result = change_path(source_destination_pairs={"source_path": source_dir, "destination_path": dest_dir})
    
    assert result["success"] is False
    single_result = result["results"][source_dir]
    assert "Overwrite is not allowed" in single_result["error"]
    assert path_exists(source_dir)  # Source should still exist
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


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
    
    result = change_path(source_destination_pairs={"source_path": source_dir, "destination_path": dest_dir})
    
    assert result["success"] is True
    assert path_exists(dest_dir)
    assert path_exists(os.path.join(dest_dir, "file.txt"))
    
    # Verify moved directory structure and content matches reference
    compare_result = compare_dirs(
        dir_path_1=reference_dir,
        dir_path_2=dest_dir
    )
    assert compare_result["success"] is True
    assert compare_result["are_equal"] is True
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)

