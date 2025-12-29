"""
Tests for copy_into function (works with both files and directories).
"""

import pytest
import os

from ixmachina.tools.file_system import (
    copy_into,
    compare_files,
    compare_dirs,
    empty_dir,
    path_exists,
)
from ..tools_file_system_constants import FILE_SYSTEM_TEST_DIR


def test_copy_into_with_file():
    """
    copy_into works with files.
    
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
    
    result = copy_into(source_path=source_file, destination_dir=dest_dir)
    
    assert result["success"] is True
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
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_copy_into_with_directory():
    """
    copy_into works with directories.
    
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
    
    result = copy_into(source_path=source_dir, destination_dir=dest_dir)
    
    assert result["success"] is True
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

