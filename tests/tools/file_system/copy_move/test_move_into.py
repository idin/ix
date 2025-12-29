"""
Tests for move_into function (works with both files and directories).
"""

import pytest
import os

from ixmachina.tools.file_system import move_into
from ixmachina.tools.file_system import empty_dir
from ixmachina.tools.file_system import path_exists
from ..tools_file_system_constants import FILE_SYSTEM_TEST_DIR


def test_move_into_with_file():
    """
    move_into works with files.
    
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
    
    with open(source_file, "w") as f:
        f.write("test content")
    
    result = move_into(source_path=source_file, destination_dir=dest_dir)
    
    assert result["success"] is True
    assert not path_exists(source_file)
    assert path_exists(os.path.join(dest_dir, "file.txt"))
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_move_into_with_directory():
    """
    move_into works with directories.
    
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
    with open(source_file, "w") as f:
        f.write("test content")
    
    result = move_into(source_path=source_dir, destination_dir=dest_dir)
    
    assert result["success"] is True
    assert not path_exists(source_dir)
    assert path_exists(os.path.join(dest_dir, "source_dir"))
    assert path_exists(os.path.join(dest_dir, "source_dir", "file.txt"))
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)

