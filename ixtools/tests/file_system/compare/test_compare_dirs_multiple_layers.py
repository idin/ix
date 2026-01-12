"""
Tests for compare_dirs with multiple layers of directories.
"""

import os

from ixtools.file_system import compare_dirs, empty_dir
from ..tools_file_system_constants import FILE_SYSTEM_TEST_DIR


def test_compare_dirs_multiple_layers_same():
    """
    Test compare_dirs with multiple layers of files and directories, all same.
    
    Structure:
    dir1/                  dir2/
    ├── top.txt            ├── top.txt
    └── level1/            └── level1/
        ├── file1.txt         ├── file1.txt
        └── level2/            └── level2/
            └── file2.txt         └── file2.txt
    """
    # Create test directories
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    dir1 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir1")
    dir2 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir2")
    os.makedirs(dir1)
    os.makedirs(dir2)
    
    # Create multiple layers
    # Top level file
    file1_top = os.path.join(dir1, "top.txt")
    file2_top = os.path.join(dir2, "top.txt")
    with open(file1_top, "w") as f:
        f.write("top content")
    with open(file2_top, "w") as f:
        f.write("top content")
    
    # First level subdirectory
    subdir1_1 = os.path.join(dir1, "level1")
    subdir2_1 = os.path.join(dir2, "level1")
    os.makedirs(subdir1_1)
    os.makedirs(subdir2_1)
    
    file1_l1 = os.path.join(subdir1_1, "file1.txt")
    file2_l1 = os.path.join(subdir2_1, "file1.txt")
    with open(file1_l1, "w") as f:
        f.write("level1 content")
    with open(file2_l1, "w") as f:
        f.write("level1 content")
    
    # Second level subdirectory
    subdir1_2 = os.path.join(subdir1_1, "level2")
    subdir2_2 = os.path.join(subdir2_1, "level2")
    os.makedirs(subdir1_2)
    os.makedirs(subdir2_2)
    
    file1_l2 = os.path.join(subdir1_2, "file2.txt")
    file2_l2 = os.path.join(subdir2_2, "file2.txt")
    with open(file1_l2, "w") as f:
        f.write("level2 content")
    with open(file2_l2, "w") as f:
        f.write("level2 content")

    result = compare_dirs(dir_path_1=dir1, dir_path_2=dir2)

    assert result["success"] is True
    assert result["are_equal"] is True
    assert len(result["differences"]) == 0
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_compare_dirs_multiple_layers_different_top():
    """
    Test compare_dirs with difference at top level.
    
    Structure:
    dir1/                  dir2/
    ├── top.txt (diff)     ├── top.txt (diff)
    └── subdir/            └── subdir/
        └── file.txt           └── file.txt (same)
    """
    # Create test directories
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    dir1 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir1")
    dir2 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir2")
    os.makedirs(dir1)
    os.makedirs(dir2)
    
    # Create different files at top level
    file1_top = os.path.join(dir1, "top.txt")
    file2_top = os.path.join(dir2, "top.txt")
    with open(file1_top, "w") as f:
        f.write("content1")
    with open(file2_top, "w") as f:
        f.write("content2")
    
    # Create same subdirectory structure
    subdir1 = os.path.join(dir1, "subdir")
    subdir2 = os.path.join(dir2, "subdir")
    os.makedirs(subdir1)
    os.makedirs(subdir2)
    
    file1_sub = os.path.join(subdir1, "file.txt")
    file2_sub = os.path.join(subdir2, "file.txt")
    with open(file1_sub, "w") as f:
        f.write("same")
    with open(file2_sub, "w") as f:
        f.write("same")

    result = compare_dirs(dir_path_1=dir1, dir_path_2=dir2)

    assert result["success"] is True
    assert result["are_equal"] is False
    assert len(result["differences"]) > 0
    # Should stop at top level, not check nested
    assert result["differences"][0]["path"] == "top.txt"
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_compare_dirs_multiple_layers_different_nested():
    """
    Test compare_dirs with difference at nested level.
    
    Structure:
    dir1/                  dir2/
    ├── top.txt (same)     ├── top.txt (same)
    └── subdir/            └── subdir/
        └── file.txt           └── file.txt (diff)
    """
    # Create test directories
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    dir1 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir1")
    dir2 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir2")
    os.makedirs(dir1)
    os.makedirs(dir2)
    
    # Create same files at top level
    file1_top = os.path.join(dir1, "top.txt")
    file2_top = os.path.join(dir2, "top.txt")
    with open(file1_top, "w") as f:
        f.write("same")
    with open(file2_top, "w") as f:
        f.write("same")
    
    # Create subdirectory structure
    subdir1 = os.path.join(dir1, "subdir")
    subdir2 = os.path.join(dir2, "subdir")
    os.makedirs(subdir1)
    os.makedirs(subdir2)
    
    # Different files in subdirectory
    file1_sub = os.path.join(subdir1, "file.txt")
    file2_sub = os.path.join(subdir2, "file.txt")
    with open(file1_sub, "w") as f:
        f.write("content1")
    with open(file2_sub, "w") as f:
        f.write("content2")

    result = compare_dirs(dir_path_1=dir1, dir_path_2=dir2)

    assert result["success"] is True
    assert result["are_equal"] is False
    assert len(result["differences"]) > 0
    assert result["differences"][0]["path"] == "subdir/file.txt"
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)

