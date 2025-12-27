"""
Tests for undoing delete operations.
"""

import pytest
import os

from ixmachina.tools.file_system.memory import FileSystemMemory
from ixmachina.tools.file_system.delete_file import delete_file
from ixmachina.tools.file_system.delete_dir import delete_dir
from ixmachina.tools.file_system.empty_dir import empty_dir
from ixmachina.tools.file_system.path_utils import path_exists
from ..constants import FILE_SYSTEM_TEST_DIR


def test_undo_delete_file():
    """
    Undo deleting a file. Other files should remain untouched.
    
    Structure:
    Before delete:      After delete:       After undo:
    test_dir/          test_dir/           test_dir/
    ├── file1.txt      ├── file2.txt       ├── file1.txt
    ├── file2.txt      └── file3.txt       ├── file2.txt
    └── file3.txt                          └── file3.txt
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    # Create other files that should not be touched
    file1 = os.path.join(FILE_SYSTEM_TEST_DIR, "file1.txt")
    file2 = os.path.join(FILE_SYSTEM_TEST_DIR, "file2.txt")
    file3 = os.path.join(FILE_SYSTEM_TEST_DIR, "file3.txt")
    
    with open(file1, "w") as f:
        f.write("file1 content")
    with open(file2, "w") as f:
        f.write("file2 content")
    with open(file3, "w") as f:
        f.write("file3 content")
    
    # Delete file1
    memory = FileSystemMemory()
    
    result = delete_file(
        file_path=file1,
        file_system_memory=memory,
    )
    
    assert result["success"] is True
    assert not path_exists(file1)  # File should be gone
    assert path_exists(file2)  # Other files should still exist
    assert path_exists(file3)  # Other files should still exist
    
    # Undo the delete
    undo_result = memory.undo()
    assert undo_result["success"] is True
    assert undo_result["action_name"] == "delete_file"
    
    # Verify undo worked
    assert path_exists(file1)  # File should be back
    assert path_exists(file2)  # Other files should still exist
    assert path_exists(file3)  # Other files should still exist
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)


def test_undo_delete_dir():
    """
    Undo deleting a directory. Other directories should remain untouched.
    
    Structure:
    Before delete:      After delete:       After undo:
    test_dir/           test_dir/           test_dir/
    ├── dir1/           ├── dir2/           ├── dir1/
    │   └── file.txt    │   └── file.txt    │   └── file.txt
    ├── dir2/           └── dir3/           ├── dir2/
    │   └── file.txt        └── file.txt    │   └── file.txt
    └── dir3/                               └── dir3/
        └── file.txt                            └── file.txt
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    # Create other directories that should not be touched
    dir1 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir1")
    dir2 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir2")
    dir3 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir3")
    os.makedirs(dir1)
    os.makedirs(dir2)
    os.makedirs(dir3)
    
    with open(os.path.join(dir1, "file.txt"), "w") as f:
        f.write("dir1 content")
    with open(os.path.join(dir2, "file.txt"), "w") as f:
        f.write("dir2 content")
    with open(os.path.join(dir3, "file.txt"), "w") as f:
        f.write("dir3 content")
    
    # Delete dir1
    memory = FileSystemMemory()
    
    result = delete_dir(
        dir_path=dir1,
        file_system_memory=memory,
    )
    
    assert result["success"] is True
    assert not path_exists(dir1)  # Dir should be gone
    assert path_exists(dir2)  # Other dirs should still exist
    assert path_exists(dir3)  # Other dirs should still exist
    
    # Undo the delete
    undo_result = memory.undo()
    assert undo_result["success"] is True
    assert undo_result["action_name"] == "delete_dir"
    
    # Verify undo worked
    assert path_exists(dir1)  # Dir should be back
    assert path_exists(dir2)  # Other dirs should still exist
    assert path_exists(dir3)  # Other dirs should still exist
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)

