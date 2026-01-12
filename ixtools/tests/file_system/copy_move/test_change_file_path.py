"""
Tests for change_file_path function.
"""

import pytest
import os
import shutil

from ixtools.file_system import change_path, copy_into
from ixtools.file_system import compare_files
from ixtools.file_system import empty_dir
from ixtools.file_system import path_exists
from ..tools_file_system_constants import FILE_SYSTEM_TEST_DIR


def test_change_file_path_renames_file():
    """
    Move file to exact destination path. Source is moved/renamed.
    
    Structure before:
    test_dir/
    └── old.txt
    
    Structure after:
    test_dir/
    └── new.txt
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "old.txt")
    dest_file = os.path.join(FILE_SYSTEM_TEST_DIR, "new.txt")
    
    test_content = "test content"
    with open(source_file, "w") as f:
        f.write(test_content)
    
    # Create reference copy before moving (for comparison)
    reference_file = os.path.join(FILE_SYSTEM_TEST_DIR, "reference.txt")
    shutil.copy2(source_file, reference_file)
    
    result = change_path(source_destination_pairs={"source_path": source_file, "destination_path": dest_file})
    
    assert result["success"] is True
    single_result = result["results"][source_file]
    assert single_result["error"] is None
    assert not path_exists(source_file)  # Source should be gone
    assert path_exists(dest_file)  # Destination should exist
    
    # Verify moved file content matches reference
    compare_result = compare_files(
        file_path_1=reference_file,
        file_path_2=dest_file
    )
    assert compare_result["success"] is True
    assert compare_result["are_equal"] is True
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_change_file_path_moves_to_different_directory():
    """
    Move file to different directory with new name.
    
    Structure before:
    test_dir/
    ├── subdir/
    │   └── file.txt
    └── moved.txt
    
    Structure after:
    test_dir/
    ├── subdir/
    └── moved.txt
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    subdir = os.path.join(FILE_SYSTEM_TEST_DIR, "subdir")
    os.makedirs(subdir)
    
    source_file = os.path.join(subdir, "file.txt")
    dest_file = os.path.join(FILE_SYSTEM_TEST_DIR, "moved.txt")
    
    test_content = "test content"
    with open(source_file, "w") as f:
        f.write(test_content)
    
    # Create reference copy before moving (for comparison)
    reference_file = os.path.join(FILE_SYSTEM_TEST_DIR, "reference_moved.txt")
    shutil.copy2(source_file, reference_file)
    
    result = change_path(source_destination_pairs={"source_path": source_file, "destination_path": dest_file})
    
    assert result["success"] is True
    assert not path_exists(source_file)
    assert path_exists(dest_file)
    
    # Verify moved file content matches reference
    compare_result = compare_files(
        file_path_1=reference_file,
        file_path_2=dest_file
    )
    assert compare_result["success"] is True
    assert compare_result["are_equal"] is True
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_change_file_path_destination_exists_fails():
    """
    Moving to existing destination should fail.
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "source.txt")
    dest_file = os.path.join(FILE_SYSTEM_TEST_DIR, "dest.txt")
    
    with open(source_file, "w") as f:
        f.write("source content")
    with open(dest_file, "w") as f:
        f.write("dest content")
    
    result = change_path(source_destination_pairs={"source_path": source_file, "destination_path": dest_file})
    
    assert result["success"] is False
    single_result = result["results"][source_file]
    assert "Overwrite is not allowed" in single_result["error"]
    assert path_exists(source_file)  # Source should still exist
    assert path_exists(dest_file)  # Destination should still exist
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_change_file_path_source_not_exists_fails():
    """
    Moving non-existent file should fail.
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "nonexistent.txt")
    dest_file = os.path.join(FILE_SYSTEM_TEST_DIR, "dest.txt")
    
    result = change_path(source_destination_pairs={"source_path": source_file, "destination_path": dest_file})
    
    assert result["success"] is False
    single_result = result["results"][source_file]
    assert "does not exist" in single_result["error"]
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_change_file_path_creates_parent_directory():
    """
    Moving file should create parent directory if it doesn't exist.
    
    Structure before:
    test_dir/
    └── file.txt
    
    Structure after:
    test_dir/
    ├── file.txt
    └── nested/
        └── moved.txt
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "file.txt")
    dest_file = os.path.join(FILE_SYSTEM_TEST_DIR, "nested", "moved.txt")
    
    test_content = "test content"
    with open(source_file, "w") as f:
        f.write(test_content)
    
    # Create reference copy before moving (for comparison)
    reference_file = os.path.join(FILE_SYSTEM_TEST_DIR, "reference_nested.txt")
    shutil.copy2(source_file, reference_file)
    
    result = change_path(source_destination_pairs={"source_path": source_file, "destination_path": dest_file})
    
    assert result["success"] is True
    assert path_exists(dest_file)
    
    # Verify moved file content matches reference
    compare_result = compare_files(
        file_path_1=reference_file,
        file_path_2=dest_file
    )
    assert compare_result["success"] is True
    assert compare_result["are_equal"] is True
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_change_file_path_binary_content():
    """
    Move binary file. Binary content preserved.
    
    Structure before:
    test_dir/
    └── binary.bin
    
    Structure after:
    test_dir/
    └── binary_moved.bin
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "binary.bin")
    dest_file = os.path.join(FILE_SYSTEM_TEST_DIR, "binary_moved.bin")
    
    binary_data = b"\x00\x01\x02\x03\xff\xfe\xfd"
    with open(source_file, "wb") as f:
        f.write(binary_data)
    
    # Create reference copy before moving (for comparison)
    reference_file = os.path.join(FILE_SYSTEM_TEST_DIR, "reference_binary.bin")
    shutil.copy2(source_file, reference_file)
    
    result = change_path(source_destination_pairs={"source_path": source_file, "destination_path": dest_file})
    
    assert result["success"] is True
    single_result = result["results"][source_file]
    assert single_result["error"] is None
    assert not path_exists(source_file)  # Source should not exist
    assert path_exists(dest_file)  # Destination should exist
    
    # Verify moved file content matches reference using compare_files
    compare_result = compare_files(
        file_path_1=reference_file,
        file_path_2=dest_file
    )
    assert compare_result["success"] is True
    assert compare_result["are_equal"] is True
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)

