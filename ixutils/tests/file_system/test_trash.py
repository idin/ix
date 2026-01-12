"""
Tests for file_system trash utilities.
"""

import os
from pathlib import Path
from ixutils.file_system import move_to_trash
from tests.file_system.test_paths import FILE_SYSTEM_TEST_DIR    
import pytest


def test_move_to_trash_with_file():
    """Test that move_to_trash moves a file to Trash."""
    test_file = os.path.join(FILE_SYSTEM_TEST_DIR, "trash_test_file.txt")
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    with open(test_file, 'w') as f:
        f.write("test content")
    
    assert os.path.exists(test_file)
    
    move_to_trash(test_file)
    
    # File should no longer exist at original location
    assert not os.path.exists(test_file)


def test_move_to_trash_with_directory():
    """Test that move_to_trash moves a directory to Trash."""
    test_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "trash_test_dir")
    os.makedirs(test_dir, exist_ok=True)
    with open(os.path.join(test_dir, "test.txt"), 'w') as f:
        f.write("content")
    
    assert os.path.exists(test_dir)
    
    move_to_trash(test_dir)
    
    # Directory should no longer exist at original location
    assert not os.path.exists(test_dir)


def test_move_to_trash_with_nonexistent_path():
    """Test that move_to_trash raises FileNotFoundError for nonexistent paths."""
    with pytest.raises(FileNotFoundError):
        move_to_trash(os.path.join(FILE_SYSTEM_TEST_DIR, "nonexistent_path"))


def test_move_to_trash_handles_name_conflicts():
    """Test that move_to_trash handles name conflicts by appending numbers."""
    test_file_1 = os.path.join(FILE_SYSTEM_TEST_DIR, "trash_conflict_test.txt")
    test_file_2 = os.path.join(FILE_SYSTEM_TEST_DIR, "trash_conflict_test_2.txt")
    os.makedirs(os.path.dirname(test_file_1), exist_ok=True)
    
    with open(test_file_1, 'w') as f:
        f.write("content 1")
    with open(test_file_2, 'w') as f:
        f.write("content 2")
    
    # Move first file
    move_to_trash(test_file_1)
    assert not os.path.exists(test_file_1)
    
    # Rename second file to match first file's name
    test_file_1_again = os.path.join(FILE_SYSTEM_TEST_DIR, "trash_conflict_test.txt")
    os.rename(test_file_2, test_file_1_again)
    
    # Move second file with same name - should handle conflict
    move_to_trash(test_file_1_again)
    assert not os.path.exists(test_file_1_again)
