"""
Tests for undo error cases.
"""

import pytest
import os

from ixmachina.tools.file_system import (
    FileSystemMemory, undo,
    clone_file_to_path,
    empty_dir,
    path_exists,
)
from ..tools_file_system_constants import FILE_SYSTEM_TEST_DIR
def test_undo_when_no_actions():
    """
    Undoing when there are no actions should return an error.
    """
    memory = FileSystemMemory()
    result = memory.undo()
    assert result["success"] is False
    assert "No actions to undo" in result["error"]
def test_undo_twice_should_fail():
    """
    Undoing twice should fail on the second attempt.
    Structure:
    Before clone:        After clone:        After first undo:    After second undo:
    test_dir/           test_dir/           test_dir/             (error)
    └── file.txt        ├── file.txt        └── file.txt
                        └── cloned.txt      (cloned.txt removed)
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "file.txt")
    cloned_file = os.path.join(FILE_SYSTEM_TEST_DIR, "cloned.txt")
    with open(source_file, "w") as f:
        f.write("test content")
    memory = FileSystemMemory()
    # Clone file
    result = clone_file_to_path(
        source_path=source_file,
        destination_path=cloned_file,
        file_system_memory=memory,
    )
    assert result["success"] is True
    assert path_exists(cloned_file)
    # First undo should succeed
    undo_result = memory.undo()
    assert undo_result["success"] is True
    assert undo_result["action_name"] == "clone_file_to_path"
    assert not path_exists(cloned_file)
    # Second undo should fail
    undo_result2 = memory.undo()
    assert undo_result2["success"] is False
    assert "No actions to undo" in undo_result2["error"]
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)
def test_undo_using_standalone_function():
    """
    Test that the standalone undo() function works.
    """
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(FILE_SYSTEM_TEST_DIR, "file.txt")
    cloned_file = os.path.join(FILE_SYSTEM_TEST_DIR, "cloned.txt")
    with open(source_file, "w") as f:
        f.write("test content")
    memory = FileSystemMemory()
    # Clone file
    result = clone_file_to_path(
        source_path=source_file,
        destination_path=cloned_file,
        file_system_memory=memory,
    )
    assert result["success"] is True
    assert path_exists(cloned_file)
    # Undo using standalone function
    undo_result = undo(file_system_memory=memory)
    assert undo_result["success"] is True
    assert undo_result["action_name"] == "clone_file_to_path"
    assert not path_exists(cloned_file)
    # Clean up
    empty_dir(path=FILE_SYSTEM_TEST_DIR)
