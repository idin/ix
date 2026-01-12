"""
Tests for file_system list utilities.
"""

import os
from ixutils.file_system import list_dir
from tests.file_system.test_paths import FILE_SYSTEM_TEST_DIR


def test_list_dir_with_files_and_directories():
    """Test that list_dir returns files and directories correctly."""
    test_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "list_test_dir")
    os.makedirs(test_dir, exist_ok=True)
    os.makedirs(os.path.join(test_dir, "subdir1"))
    os.makedirs(os.path.join(test_dir, "subdir2"))
    with open(os.path.join(test_dir, "file1.txt"), 'w') as f:
        f.write("content")
    with open(os.path.join(test_dir, "file2.txt"), 'w') as f:
        f.write("content")
    
    items = list_dir(test_dir)
    
    assert len(items) == 4
    assert items[0]["type"] == "directory"
    assert items[1]["type"] == "directory"
    assert items[2]["type"] == "file"
    assert items[3]["type"] == "file"
    
    names = [item["name"] for item in items]
    assert "subdir1" in names
    assert "subdir2" in names
    assert "file1.txt" in names
    assert "file2.txt" in names
    
    os.unlink(os.path.join(test_dir, "file1.txt"))
    os.unlink(os.path.join(test_dir, "file2.txt"))
    os.rmdir(os.path.join(test_dir, "subdir1"))
    os.rmdir(os.path.join(test_dir, "subdir2"))
    os.rmdir(test_dir)


def test_list_dir_excludes_hidden_files_by_default():
    """Test that list_dir excludes hidden files by default."""
    test_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "list_hidden_test")
    os.makedirs(test_dir, exist_ok=True)
    with open(os.path.join(test_dir, ".hidden"), 'w') as f:
        f.write("content")
    with open(os.path.join(test_dir, "visible.txt"), 'w') as f:
        f.write("content")
    
    items = list_dir(test_dir)
    
    names = [item["name"] for item in items]
    assert ".hidden" not in names
    assert "visible.txt" in names
    
    os.unlink(os.path.join(test_dir, ".hidden"))
    os.unlink(os.path.join(test_dir, "visible.txt"))
    os.rmdir(test_dir)


def test_list_dir_includes_hidden_files_when_requested():
    """Test that list_dir includes hidden files when include_hidden=True."""
    test_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "list_hidden_include_test")
    os.makedirs(test_dir, exist_ok=True)
    with open(os.path.join(test_dir, ".hidden"), 'w') as f:
        f.write("content")
    with open(os.path.join(test_dir, "visible.txt"), 'w') as f:
        f.write("content")
    
    items = list_dir(test_dir, include_hidden=True)
    
    names = [item["name"] for item in items]
    assert ".hidden" in names
    assert "visible.txt" in names
    
    os.unlink(os.path.join(test_dir, ".hidden"))
    os.unlink(os.path.join(test_dir, "visible.txt"))
    os.rmdir(test_dir)


def test_list_dir_with_empty_directory():
    """Test that list_dir returns empty list for empty directory."""
    test_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "list_empty_test")
    os.makedirs(test_dir, exist_ok=True)
    items = list_dir(test_dir)
    assert items == []
    os.rmdir(test_dir)


def test_list_dir_nonexistent_directory():
    """Test that list_dir raises FileNotFoundError for nonexistent directory."""
    import pytest
    with pytest.raises(FileNotFoundError):
        list_dir(os.path.join(FILE_SYSTEM_TEST_DIR, "nonexistent_directory"))


def test_list_dir_with_file_path():
    """Test that list_dir raises NotADirectoryError for file paths."""
    import pytest
    test_file = os.path.join(FILE_SYSTEM_TEST_DIR, "list_file_test.txt")
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    with open(test_file, 'w') as f:
        f.write("content")
    with pytest.raises(NotADirectoryError):
        list_dir(test_file)
    os.unlink(test_file)


def test_list_dir_items_have_correct_structure():
    """Test that list_dir items have correct dictionary structure."""
    test_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "list_structure_test")
    os.makedirs(test_dir, exist_ok=True)
    os.makedirs(os.path.join(test_dir, "subdir"))
    with open(os.path.join(test_dir, "file.txt"), 'w') as f:
        f.write("content")
    
    items = list_dir(test_dir)
    
    for item in items:
        assert "name" in item
        assert "type" in item
        assert "path" in item
        assert item["type"] in ["file", "directory"]
        assert os.path.exists(item["path"])
    
    os.unlink(os.path.join(test_dir, "file.txt"))
    os.rmdir(os.path.join(test_dir, "subdir"))
    os.rmdir(test_dir)


def test_list_dir_sorts_alphabetically():
    """Test that list_dir sorts items alphabetically."""
    test_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "list_sort_test")
    os.makedirs(test_dir, exist_ok=True)
    with open(os.path.join(test_dir, "zebra.txt"), 'w') as f:
        f.write("content")
    with open(os.path.join(test_dir, "apple.txt"), 'w') as f:
        f.write("content")
    with open(os.path.join(test_dir, "banana.txt"), 'w') as f:
        f.write("content")
    
    items = list_dir(test_dir)
    
    names = [item["name"] for item in items]
    assert names == ["apple.txt", "banana.txt", "zebra.txt"]
    
    os.unlink(os.path.join(test_dir, "zebra.txt"))
    os.unlink(os.path.join(test_dir, "apple.txt"))
    os.unlink(os.path.join(test_dir, "banana.txt"))
    os.rmdir(test_dir)
