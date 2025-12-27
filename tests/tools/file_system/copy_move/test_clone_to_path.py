"""
Tests for clone_to_path function (works with both files and directories).
"""

import pytest
import os

from ixmachina.tools.file_system.copy_move.clone_to_path import clone_to_path
from ixmachina.tools.file_system.compare_files import compare_files
from ixmachina.tools.file_system.compare_dirs import compare_dirs
from ixmachina.tools.file_system.empty_dir import empty_dir
from ixmachina.tools.file_system.path_utils import path_exists
from ..constants import FILE_SYSTEM_TEST_DIR


def test_clone_to_path_with_file():
    """
    clone_to_path works with files.
    
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
    
    result = clone_to_path(source_path=source_file, destination_path=dest_file)
    
    assert result["success"] is True
    assert path_exists(source_file)  # Source should still exist
    assert path_exists(dest_file)  # Clone should exist
    
    # Verify files are identical
    compare_result = compare_files(file_path_1=source_file, file_path_2=dest_file)
    assert compare_result["success"] is True
    assert compare_result["are_equal"] is True
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)


def test_clone_to_path_with_directory():
    """
    clone_to_path works with directories.
    
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
    
    result = clone_to_path(source_path=source_dir, destination_path=dest_dir)
    
    assert result["success"] is True
    assert path_exists(source_dir)  # Source should still exist
    assert path_exists(dest_dir)  # Clone should exist
    
    # Verify directories are identical
    compare_result = compare_dirs(dir_path_1=source_dir, dir_path_2=dest_dir)
    assert compare_result["success"] is True
    assert compare_result["are_equal"] is True
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)

