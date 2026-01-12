"""
Tests for undoing copy operations.
"""

import pytest
import os

from ixtools.file_system import (
    FileSystemMemory,
    clone_to_path,
    copy_into,
    delete,
    empty_dir,
    path_exists,
)
from ..tools_file_system_constants import FILE_SYSTEM_TEST_DIR


def test_undo_clone_file_to_path():
    """
    Undo cloning a file. Other files should remain untouched.
    Structure:
    Before clone:        After clone:        After undo:
    test_dir/           test_dir/           test_dir/
    ├── file1.txt       ├── file1.txt       ├── file1.txt
    ├── file2.txt       ├── file2.txt       ├── file2.txt
    └── file3.txt       ├── file3.txt       ├── file3.txt
                        └── cloned.txt      (cloned.txt removed)
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
    # Clone a file
    source_file = file1
    cloned_file = os.path.join(FILE_SYSTEM_TEST_DIR, "cloned.txt")
    memory = FileSystemMemory()
    result = clone_to_path(
        source_destination_pairs={"source_path": source_file, "destination_path": cloned_file},
        file_system_memory=memory,
    )
    assert result["success"] is True
    single_result = result["results"][source_file]
    assert single_result["success"] is True
    assert path_exists(cloned_file)
    assert path_exists(file1)  # Source should still exist
    assert path_exists(file2)  # Other files should still exist
    assert path_exists(file3)  # Other files should still exist
    # Undo the clone
    undo_result = memory.undo()
    assert undo_result["success"] is True
    assert undo_result["action_name"] == "clone_to_path"
    # Verify undo worked
    assert not path_exists(cloned_file)  # Cloned file should be gone
    assert path_exists(file1)  # Source should still exist
    assert path_exists(file2)  # Other files should still exist
    assert path_exists(file3)  # Other files should still exist
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)
def test_undo_clone_dir_to_path():
    """
    Undo cloning a directory. Other directories should remain untouched.
    Structure:
    Before clone:        After clone:        After undo:
    test_dir/           test_dir/           test_dir/
    ├── dir1/           ├── dir1/           ├── dir1/
    │   └── file.txt    │   └── file.txt    │   └── file.txt
    ├── dir2/           ├── dir2/           ├── dir2/
    │   └── file.txt    │   └── file.txt    │   └── file.txt
    └── dir3/           ├── dir3/           ├── dir3/
        └── file.txt    │   └── file.txt    │   └── file.txt
                        └── cloned_dir/     (cloned_dir removed)
                            └── file.txt
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
    # Clone a directory
    cloned_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "cloned_dir")
    memory = FileSystemMemory()
    result = clone_to_path(
        source_destination_pairs={"source_path": dir1, "destination_path": cloned_dir},
        file_system_memory=memory,
    )
    assert result["success"] is True
    single_result = result["results"][dir1]
    assert single_result["success"] is True
    assert path_exists(cloned_dir)
    assert path_exists(dir1)  # Source should still exist
    assert path_exists(dir2)  # Other dirs should still exist
    assert path_exists(dir3)  # Other dirs should still exist
    # Undo the clone
    undo_result = memory.undo()
    assert undo_result["success"] is True
    assert undo_result["action_name"] == "clone_to_path"
    # Verify undo worked
    assert not path_exists(cloned_dir)  # Cloned dir should be gone
    assert path_exists(dir1)  # Source should still exist
    assert path_exists(dir2)  # Other dirs should still exist
    assert path_exists(dir3)  # Other dirs should still exist
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)
def test_undo_copy_file_into():
    """
    Undo copying a file into a directory. Other files should remain untouched.
    Structure:
    Before copy:        After copy:         After undo:
    test_dir/           test_dir/           test_dir/
    ├── file1.txt       ├── file1.txt       ├── file1.txt
    ├── file2.txt       ├── file2.txt       ├── file2.txt
    └── dest_dir/       └── dest_dir/       └── dest_dir/
        └── file3.txt      ├── file3.txt      └── file3.txt
                            └── file1.txt      (file1.txt removed)
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
    # Copy file into directory
    memory = FileSystemMemory()
    result = copy_into(
        source_paths=file1,
        destination_dir=dest_dir,
        file_system_memory=memory,
    )
    assert result["success"] is True
    single_result = result["results"][file1]
    assert single_result["success"] is True
    assert path_exists(os.path.join(dest_dir, "file1.txt"))
    assert path_exists(file1)  # Source should still exist
    assert path_exists(file2)  # Other files should still exist
    assert path_exists(file3)  # Other files should still exist
    # Undo the copy
    undo_result = memory.undo()
    assert undo_result["success"] is True
    assert undo_result["action_name"] == "copy_into"
    # Verify undo worked
    assert not path_exists(os.path.join(dest_dir, "file1.txt"))  # Copy should be gone
    assert path_exists(file1)  # Source should still exist
    assert path_exists(file2)  # Other files should still exist
    assert path_exists(file3)  # Other files should still exist
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)
def test_undo_copy_dir_into():
    """
    Undo copying a directory into another directory. Other directories should remain untouched.
    Structure:
    Before copy:        After copy:         After undo:
    test_dir/           test_dir/           test_dir/
    ├── source_dir/     ├── source_dir/     ├── source_dir/
    │   └── file.txt    │   └── file.txt    │   └── file.txt
    ├── other_dir/      ├── other_dir/      ├── other_dir/
    │   └── file.txt    │   └── file.txt    │   └── file.txt
    └── dest_dir/       └── dest_dir/       └── dest_dir/
                            ├── other_file.txt   └── other_file.txt
                            └── source_dir/      (source_dir removed)
                                └── file.txt
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    # Create other directories
    source_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "source_dir")
    other_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "other_dir")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "dest_dir")
    os.makedirs(source_dir)
    os.makedirs(other_dir)
    os.makedirs(dest_dir, exist_ok=True)
    with open(os.path.join(source_dir, "file.txt"), "w") as f:
        f.write("source content")
    with open(os.path.join(other_dir, "file.txt"), "w") as f:
        f.write("other content")
    with open(os.path.join(dest_dir, "other_file.txt"), "w") as f:
        f.write("dest content")
    # Copy directory into directory
    memory = FileSystemMemory()
    result = copy_into(
        source_paths=source_dir,
        destination_dir=dest_dir,
        file_system_memory=memory,
    )
    assert result["success"] is True
    single_result = result["results"][source_dir]
    assert single_result["success"] is True
    assert path_exists(os.path.join(dest_dir, "source_dir"))
    assert path_exists(source_dir)  # Source should still exist
    assert path_exists(other_dir)  # Other dirs should still exist
    assert path_exists(os.path.join(dest_dir, "other_file.txt"))  # Other files should still exist
    # Undo the copy
    undo_result = memory.undo()
    assert undo_result["success"] is True
    assert undo_result["action_name"] == "copy_into"
    # Verify undo worked
    assert not path_exists(os.path.join(dest_dir, "source_dir"))  # Copy should be gone
    assert path_exists(source_dir)  # Source should still exist
    assert path_exists(other_dir)  # Other dirs should still exist
    assert path_exists(os.path.join(dest_dir, "other_file.txt"))  # Other files should still exist
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)


def test_undo_copy_uses_delete():
    """
    Verify that undo for copy operations uses the delete function.
    This ensures the undo mechanism correctly removes copied items.
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "source.txt")
    dest_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "dest_dir")
    os.makedirs(dest_dir, exist_ok=True)
    
    with open(source_file, "w") as f:
        f.write("test content")
    
    memory = FileSystemMemory()
    result = copy_into(
        source_paths=source_file,
        destination_dir=dest_dir,
        file_system_memory=memory,
    )
    assert result["success"] is True
    copied_file = os.path.join(dest_dir, "source.txt")
    assert path_exists(copied_file)
    
    # Verify the undo action is set up to use delete
    assert memory.size() == 1
    action, undo_action = memory.get_last_action()
    assert undo_action is not None
    assert undo_action.function_name == "delete"
    assert undo_action.function == delete
    
    # Verify undo actually deletes the copied file
    undo_result = memory.undo()
    assert undo_result["success"] is True
    assert not path_exists(copied_file)  # Copied file should be deleted
    assert path_exists(source_file)  # Source should still exist
    
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)
