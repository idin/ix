"""
Tests for undoing move operations.
"""

import pytest
import os

from ixmachina.tools.file_system.memory import FileSystemMemory
from ixmachina.tools.file_system.copy_move.change_file_path import change_file_path
from ixmachina.tools.file_system.copy_move.change_dir_path import change_dir_path
from ixmachina.tools.file_system.copy_move.move_file_into import move_file_into
from ixmachina.tools.file_system.copy_move.move_dir_into import move_dir_into
from ixmachina.tools.file_system.empty_dir import empty_dir
from ixmachina.tools.file_system.path_utils import path_exists
from ..constants import FILE_SYSTEM_TEST_DIR


def test_undo_change_file_path():
    """
    Undo moving a file to exact path. Other files should remain untouched.
    
    Structure:
    Before move:        After move:         After undo:
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
    
    # Move file1 to new location
    moved_file = os.path.join(FILE_SYSTEM_TEST_DIR, "moved.txt")
    memory = FileSystemMemory()
    
    result = change_file_path(
        source_path=file1,
        destination_path=moved_file,
        file_system_memory=memory,
    )
    
    assert result["success"] is True
    assert not path_exists(file1)  # Source should be gone
    assert path_exists(moved_file)  # Destination should exist
    assert path_exists(file2)  # Other files should still exist
    assert path_exists(file3)  # Other files should still exist
    
    # Undo the move
    undo_result = memory.undo()
    assert undo_result["success"] is True
    assert undo_result["action_name"] == "change_file_path"
    
    # Verify undo worked
    assert path_exists(file1)  # File should be back
    assert not path_exists(moved_file)  # Moved file should be gone
    assert path_exists(file2)  # Other files should still exist
    assert path_exists(file3)  # Other files should still exist
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)


def test_undo_change_dir_path():
    """
    Undo moving a directory to exact path. Other directories should remain untouched.
    
    Structure:
    Before move:        After move:         After undo:
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
    os.makedirs(dir1, exist_ok=True)
    os.makedirs(dir2, exist_ok=True)
    os.makedirs(dir3, exist_ok=True)
    
    with open(os.path.join(dir1, "file.txt"), "w") as f:
        f.write("dir1 content")
    with open(os.path.join(dir2, "file.txt"), "w") as f:
        f.write("dir2 content")
    with open(os.path.join(dir3, "file.txt"), "w") as f:
        f.write("dir3 content")
    
    # Move dir1 to new location
    moved_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "moved_dir")
    memory = FileSystemMemory()
    
    result = change_dir_path(
        source_path=dir1,
        destination_path=moved_dir,
        file_system_memory=memory,
    )
    
    assert result["success"] is True
    assert not path_exists(dir1)  # Source should be gone
    assert path_exists(moved_dir)  # Destination should exist
    assert path_exists(dir2)  # Other dirs should still exist
    assert path_exists(dir3)  # Other dirs should still exist
    
    # Undo the move
    undo_result = memory.undo()
    assert undo_result["success"] is True
    assert undo_result["action_name"] == "change_dir_path"

    # Verify undo worked
    assert path_exists(dir1)  # Dir should be back
    assert not path_exists(moved_dir)  # Moved dir should be gone
    assert path_exists(dir2)  # Other dirs should still exist
    assert path_exists(dir3)  # Other dirs should still exist
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)


def test_undo_move_file_into():
    """
    Undo moving a file into a directory. Other files should remain untouched.
    
    Structure:
    Before move:        After move:         After undo:
    test_dir/           test_dir/           test_dir/
    ├── file1.txt       ├── file2.txt       ├── file1.txt
    ├── file2.txt       └── dest_dir/       ├── file2.txt
    └── dest_dir/           ├── file3.txt   └── dest_dir/
        └── file3.txt       └── file1.txt       └── file3.txt
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    # Create other files
    file1 = os.path.join(FILE_SYSTEM_TEST_DIR, "file1.txt")
    file2 = os.path.join(FILE_SYSTEM_TEST_DIR, "file2.txt")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "dest_dir")
    os.makedirs(dest_dir, exist_ok=True)
    file3 = os.path.join(dest_dir, "file3.txt")
    
    with open(file1, "w") as f:
        f.write("file1 content")
    with open(file2, "w") as f:
        f.write("file2 content")
    with open(file3, "w") as f:
        f.write("file3 content")
    
    # Move file1 into directory
    memory = FileSystemMemory()
    
    result = move_file_into(
        source_path=file1,
        destination_dir=dest_dir,
        file_system_memory=memory,
    )
    
    assert result["success"] is True
    assert not path_exists(file1)  # Source should be gone
    assert path_exists(os.path.join(dest_dir, "file1.txt"))  # File should be in dest_dir
    assert path_exists(file2)  # Other files should still exist
    assert path_exists(file3)  # Other files should still exist
    
    # Undo the move
    undo_result = memory.undo()
    assert undo_result["success"] is True
    assert undo_result["action_name"] == "move_file_into"
    
    # Verify undo worked
    assert path_exists(file1)  # File should be back
    assert not path_exists(os.path.join(dest_dir, "file1.txt"))  # File should be gone from dest_dir
    assert path_exists(file2)  # Other files should still exist
    assert path_exists(file3)  # Other files should still exist
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)


def test_undo_move_dir_into():
    """
    Undo moving a directory into another directory. Other directories should remain untouched.
    
    Structure:
    Before move:        After move:         After undo:
    test_dir/           test_dir/           test_dir/
    ├── source_dir/     ├── other_dir/      ├── source_dir/
    │   └── file.txt    │   └── file.txt    │   └── file.txt
    ├── other_dir/      └── dest_dir/       ├── other_dir/
    │   └── file.txt        ├── other_file.txt  │   └── file.txt
    └── dest_dir/           └── source_dir/  └── dest_dir/
        └── other_file.txt      └── file.txt     └── other_file.txt
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    
    # Create other directories
    source_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "source_dir")
    other_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "other_dir")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "dest_dir")
    os.makedirs(source_dir, exist_ok=True)
    os.makedirs(other_dir, exist_ok=True)
    os.makedirs(dest_dir, exist_ok=True)
    
    with open(os.path.join(source_dir, "file.txt"), "w") as f:
        f.write("source content")
    with open(os.path.join(other_dir, "file.txt"), "w") as f:
        f.write("other content")
    with open(os.path.join(dest_dir, "other_file.txt"), "w") as f:
        f.write("dest content")
    
    # Move source_dir into dest_dir
    memory = FileSystemMemory()
    
    result = move_dir_into(
        source_path=source_dir,
        destination_dir=dest_dir,
        file_system_memory=memory,
    )
    
    assert result["success"] is True
    assert not path_exists(source_dir)  # Source should be gone
    assert path_exists(os.path.join(dest_dir, "source_dir"))  # Dir should be in dest_dir
    assert path_exists(other_dir)  # Other dirs should still exist
    assert path_exists(os.path.join(dest_dir, "other_file.txt"))  # Other files should still exist
    
    # Undo the move
    undo_result = memory.undo()
    assert undo_result["success"] is True
    assert undo_result["action_name"] == "move_dir_into"
    
    # Verify undo worked
    assert path_exists(source_dir)  # Dir should be back
    assert not path_exists(os.path.join(dest_dir, "source_dir"))  # Dir should be gone from dest_dir
    assert path_exists(other_dir)  # Other dirs should still exist
    assert path_exists(os.path.join(dest_dir, "other_file.txt"))  # Other files should still exist
    
    # Clean up
    empty_dir(dir_path=FILE_SYSTEM_TEST_DIR)

