"""
Tests for compare_dirs detecting missing files and directories.
"""

import os

from ixtools.file_system import compare_dirs, empty_dir
from ..tools_file_system_constants import FILE_SYSTEM_TEST_DIR


def test_compare_dirs_missing_file_top_level():
    """
    Test compare_dirs detects missing file at top level.
    
    Structure:
    dir1/          dir2/
    └── file.txt   (empty)
    """
    # Create test directories
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    dir1 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir1")
    dir2 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir2")
    os.makedirs(dir1)
    os.makedirs(dir2)
    
    # Create file only in dir1
    file1 = os.path.join(dir1, "file.txt")
    with open(file1, "w") as f:
        f.write("content")

    result = compare_dirs(dir_path_1=dir1, dir_path_2=dir2)

    assert result["success"] is True
    assert result["are_equal"] is False
    assert len(result["differences"]) > 0
    assert result["differences"][0]["type"] == "missing_in_dir2"
    assert result["differences"][0]["path"] == "file.txt"
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_compare_dirs_missing_file_nested():
    """
    Test compare_dirs detects missing file at nested level.
    
    Structure:
    dir1/          dir2/
    └── subdir/    └── subdir/
        └── file.txt    (empty)
    """
    # Create test directories
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    dir1 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir1")
    dir2 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir2")
    os.makedirs(dir1)
    os.makedirs(dir2)
    
    # Create subdirectories
    subdir1 = os.path.join(dir1, "subdir")
    subdir2 = os.path.join(dir2, "subdir")
    os.makedirs(subdir1)
    os.makedirs(subdir2)
    
    # Create file only in subdir1
    file1 = os.path.join(subdir1, "file.txt")
    with open(file1, "w") as f:
        f.write("content")

    result = compare_dirs(dir_path_1=dir1, dir_path_2=dir2)

    assert result["success"] is True
    assert result["are_equal"] is False
    assert len(result["differences"]) > 0
    assert result["differences"][0]["type"] == "missing_in_dir2"
    assert result["differences"][0]["path"] == "subdir/file.txt"
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_compare_dirs_missing_dir_top_level():
    """
    Test compare_dirs detects missing directory at top level.
    
    Structure:
    dir1/          dir2/
    └── subdir/   (empty)
        └── file.txt
    """
    # Create test directories
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    dir1 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir1")
    dir2 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir2")
    os.makedirs(dir1)
    os.makedirs(dir2)
    
    # Create subdirectory only in dir1
    subdir1 = os.path.join(dir1, "subdir")
    os.makedirs(subdir1)
    
    file1 = os.path.join(subdir1, "file.txt")
    with open(file1, "w") as f:
        f.write("content")

    result = compare_dirs(dir_path_1=dir1, dir_path_2=dir2)

    assert result["success"] is True
    assert result["are_equal"] is False
    assert len(result["differences"]) > 0
    assert result["differences"][0]["type"] == "missing_in_dir2"
    assert result["differences"][0]["path"] == "subdir"
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)

