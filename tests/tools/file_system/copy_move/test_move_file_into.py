"""
Tests for move_file_into function.
"""

import pytest
import os
import shutil

from ixmachina.tools.file_system import move_into
from ixmachina.tools.file_system import compare_files
from ixmachina.tools.file_system import empty_dir
from ixmachina.tools.file_system import path_exists, path_is_dir
from ..tools_file_system_constants import FILE_SYSTEM_TEST_DIR


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
    
    test_content = "test content"
    with open(source_file, "w") as f:
        f.write(test_content)
    
    # Create reference copy before moving (for comparison)
    reference_file = os.path.join(FILE_SYSTEM_TEST_DIR, "reference.txt")
    shutil.copy2(source_file, reference_file)
    
    result = move_into(source_paths=source_file, destination_dir=dest_dir)
    
    assert result["success"] is True
    single_result = result["results"][source_file]
    assert single_result["error"] is None
    assert not path_exists(source_file)  # Source should be gone
    moved_file = os.path.join(dest_dir, "file.txt")
    assert path_exists(moved_file)  # File should be in dest_dir
    
    # Verify moved file content matches reference using compare_files
    compare_result = compare_files(
        file_path_1=reference_file,
        file_path_2=moved_file
    )
    assert compare_result["success"] is True
    assert compare_result["are_equal"] is True
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_move_file_into_destination_not_exists_fails():
    """
    Moving into non-existent directory should fail.
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "file.txt")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "nonexistent_dir")
    
    with open(source_file, "w") as f:
        f.write("test content")
    
    result = move_into(source_paths=source_file, destination_dir=dest_dir)
    
    assert result["success"] is False
    single_result = result["results"][source_file]
    assert "does not exist" in single_result["error"]
    assert path_exists(source_file)  # Source should still exist
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


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
    
    result = move_into(source_paths=source_file, destination_dir=dest_dir)
    
    assert result["success"] is False
    single_result = result["results"][source_file]
    assert "Overwrite is not allowed" in single_result["error"]
    assert path_exists(source_file)  # Source should still exist
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_move_file_into_source_not_exists_fails():
    """
    Moving non-existent file should fail.
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "nonexistent.txt")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "dest_dir")
    os.makedirs(dest_dir)
    
    result = move_into(source_paths=source_file, destination_dir=dest_dir)
    
    assert result["success"] is False
    single_result = result["results"][source_file]
    assert "does not exist" in single_result["error"]
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)

