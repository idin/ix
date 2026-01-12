"""
Tests for change_path function (works with both files and directories).
"""

import pytest
import os

from ixtools.file_system import change_path
from ixtools.file_system import empty_dir
from ixtools.file_system import path_exists
from ..tools_file_system_constants import FILE_SYSTEM_TEST_DIR


def test_change_path_with_file():
    """
    change_path works with files.
    
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
    
    with open(source_file, "w") as f:
        f.write("test content")
    
    result = change_path(source_destination_pairs={"source_path": source_file, "destination_path": dest_file})
    
    assert result["success"] is True
    assert result["results"][source_file]["success"] is True
    assert not path_exists(source_file)
    assert path_exists(dest_file)
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_change_path_with_directory():
    """
    change_path works with directories.
    
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
    with open(source_file, "w") as f:
        f.write("test content")
    
    result = change_path(source_destination_pairs={"source_path": source_dir, "destination_path": dest_dir})
    
    assert result["success"] is True
    assert result["results"][source_dir]["success"] is True
    assert not path_exists(source_dir)
    assert path_exists(dest_dir)
    assert path_exists(os.path.join(dest_dir, "file.txt"))
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)

