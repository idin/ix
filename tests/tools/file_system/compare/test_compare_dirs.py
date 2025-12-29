"""
Tests for compare_dirs function.
"""

import pytest
import os

from ixmachina.tools.file_system import compare_dirs, empty_dir
from ..tools_file_system_constants import FILE_SYSTEM_TEST_DIR


def test_compare_dirs_single_file_same():
    """
    Test compare_dirs with single file in each directory, same content.
    
    Structure:
    dir1/          dir2/
    └── file.txt    └── file.txt
    """
    # Create test directories
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    dir1 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir1")
    dir2 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir2")
    os.makedirs(dir1)
    os.makedirs(dir2)
    
    # Create same file in both directories
    file1 = os.path.join(dir1, "file.txt")
    file2 = os.path.join(dir2, "file.txt")
    
    with open(file1, "w") as f:
        f.write("content")
    with open(file2, "w") as f:
        f.write("content")

    result = compare_dirs(dir_path_1=dir1, dir_path_2=dir2)

    assert result["success"] is True
    assert result["are_equal"] is True
    assert len(result["differences"]) == 0
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_compare_dirs_single_file_different():
    """
    Test compare_dirs with single file in each directory, different content.
    
    Structure:
    dir1/          dir2/
    └── file.txt   └── file.txt  (different content)
    """
    # Create test directories
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    dir1 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir1")
    dir2 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir2")
    os.makedirs(dir1)
    os.makedirs(dir2)
    
    # Create different files in both directories
    file1 = os.path.join(dir1, "file.txt")
    file2 = os.path.join(dir2, "file.txt")
    
    with open(file1, "w") as f:
        f.write("content1")
    with open(file2, "w") as f:
        f.write("content2")

    result = compare_dirs(dir_path_1=dir1, dir_path_2=dir2)

    assert result["success"] is True
    assert result["are_equal"] is False
    assert len(result["differences"]) > 0
    assert result["differences"][0]["type"] in ["file_different", "file_size_different"]
    assert result["differences"][0]["path"] == "file.txt"
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_compare_dirs_single_dir_same():
    """
    Test compare_dirs with single subdirectory in each directory, same content.
    
    Structure:
    dir1/          dir2/
    └── subdir/    └── subdir/
        └── file.txt    └── file.txt
    """
    # Create test directories
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    dir1 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir1")
    dir2 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir2")
    os.makedirs(dir1)
    os.makedirs(dir2)
    
    # Create subdirectories with same file
    subdir1 = os.path.join(dir1, "subdir")
    subdir2 = os.path.join(dir2, "subdir")
    os.makedirs(subdir1)
    os.makedirs(subdir2)
    
    file1 = os.path.join(subdir1, "file.txt")
    file2 = os.path.join(subdir2, "file.txt")
    
    with open(file1, "w") as f:
        f.write("content")
    with open(file2, "w") as f:
        f.write("content")

    result = compare_dirs(dir_path_1=dir1, dir_path_2=dir2)

    assert result["success"] is True
    assert result["are_equal"] is True
    assert len(result["differences"]) == 0
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


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


def test_compare_dirs_empty_directories():
    """Test compare_dirs returns True for two empty directories."""
    # Create test directories
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    dir1 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir1")
    dir2 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir2")
    os.makedirs(dir1)
    os.makedirs(dir2)

    result = compare_dirs(dir_path_1=dir1, dir_path_2=dir2)

    assert result["success"] is True
    assert result["are_equal"] is True
    assert len(result["differences"]) == 0
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_compare_dirs_multiple_files_same():
    """Test compare_dirs with multiple files at same level, all same."""
    # Create test directories
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    dir1 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir1")
    dir2 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir2")
    os.makedirs(dir1)
    os.makedirs(dir2)
    
    # Create multiple files
    for i in range(3):
        file1 = os.path.join(dir1, f"file{i}.txt")
        file2 = os.path.join(dir2, f"file{i}.txt")
        with open(file1, "w") as f:
            f.write(f"content{i}")
        with open(file2, "w") as f:
            f.write(f"content{i}")

    result = compare_dirs(dir_path_1=dir1, dir_path_2=dir2)

    assert result["success"] is True
    assert result["are_equal"] is True
    assert len(result["differences"]) == 0
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_compare_dirs_multiple_files_one_different():
    """
    Test compare_dirs stops at first different file.
    
    Structure:
    dir1/                  dir2/
    ├── file0.txt (same)   ├── file0.txt (same)
    ├── file1.txt (diff)   ├── file1.txt (diff)
    └── file2.txt (same)   └── file2.txt (same)
    """
    # Create test directories
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    dir1 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir1")
    dir2 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir2")
    os.makedirs(dir1)
    os.makedirs(dir2)
    
    # Create multiple files, second one different
    file1_1 = os.path.join(dir1, "file0.txt")
    file2_1 = os.path.join(dir2, "file0.txt")
    with open(file1_1, "w") as f:
        f.write("same")
    with open(file2_1, "w") as f:
        f.write("same")
    
    file1_2 = os.path.join(dir1, "file1.txt")
    file2_2 = os.path.join(dir2, "file1.txt")
    with open(file1_2, "w") as f:
        f.write("different1")
    with open(file2_2, "w") as f:
        f.write("different2")
    
    file1_3 = os.path.join(dir1, "file2.txt")
    file2_3 = os.path.join(dir2, "file2.txt")
    with open(file1_3, "w") as f:
        f.write("same")
    with open(file2_3, "w") as f:
        f.write("same")

    result = compare_dirs(dir_path_1=dir1, dir_path_2=dir2)

    assert result["success"] is True
    assert result["are_equal"] is False
    assert len(result["differences"]) > 0
    # Should stop at first difference (file1.txt)
    assert result["differences"][0]["path"] == "file1.txt"
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_compare_dirs_different_file_name():
    """
    Test compare_dirs detects different file name (one file name differs).
    
    Structure:
    dir1/                  dir2/
    ├── file1.txt         ├── file1.txt
    └── file2.txt         └── file3.txt  (different name)
    """
    # Create test directories
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    dir1 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir1")
    dir2 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir2")
    os.makedirs(dir1)
    os.makedirs(dir2)
    
    # Create files with same content but one has different name
    file1_1 = os.path.join(dir1, "file1.txt")
    file2_1 = os.path.join(dir2, "file1.txt")
    with open(file1_1, "w") as f:
        f.write("content1")
    with open(file2_1, "w") as f:
        f.write("content1")
    
    file1_2 = os.path.join(dir1, "file2.txt")
    file2_3 = os.path.join(dir2, "file3.txt")  # Different name
    with open(file1_2, "w") as f:
        f.write("content2")
    with open(file2_3, "w") as f:
        f.write("content2")

    result = compare_dirs(dir_path_1=dir1, dir_path_2=dir2)

    assert result["success"] is True
    assert result["are_equal"] is False
    assert len(result["differences"]) > 0
    # Should detect missing file2.txt in dir2 and missing file3.txt in dir1
    diff_paths = [d["path"] for d in result["differences"]]
    assert "file2.txt" in diff_paths or "file3.txt" in diff_paths
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_compare_dirs_different_dir_name():
    """
    Test compare_dirs detects different directory name (one dir name differs).
    
    Structure:
    dir1/                  dir2/
    ├── subdir1/          ├── subdir1/
    │   └── file.txt         └── file.txt
    └── subdir2/          └── subdir3/  (different name)
        └── file.txt             └── file.txt
    """
    # Create test directories
    os.makedirs(FILE_SYSTEM_TEST_DIR, exist_ok=True)
    dir1 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir1")
    dir2 = os.path.join(FILE_SYSTEM_TEST_DIR, "dir2")
    os.makedirs(dir1)
    os.makedirs(dir2)
    
    # Create subdirectories with same structure but one has different name
    subdir1_1 = os.path.join(dir1, "subdir1")
    subdir2_1 = os.path.join(dir2, "subdir1")
    os.makedirs(subdir1_1)
    os.makedirs(subdir2_1)
    
    file1_1 = os.path.join(subdir1_1, "file.txt")
    file2_1 = os.path.join(subdir2_1, "file.txt")
    with open(file1_1, "w") as f:
        f.write("content1")
    with open(file2_1, "w") as f:
        f.write("content1")
    
    subdir1_2 = os.path.join(dir1, "subdir2")
    subdir2_3 = os.path.join(dir2, "subdir3")  # Different name
    os.makedirs(subdir1_2)
    os.makedirs(subdir2_3)
    
    file1_2 = os.path.join(subdir1_2, "file.txt")
    file2_2 = os.path.join(subdir2_3, "file.txt")
    with open(file1_2, "w") as f:
        f.write("content2")
    with open(file2_2, "w") as f:
        f.write("content2")

    result = compare_dirs(dir_path_1=dir1, dir_path_2=dir2)

    assert result["success"] is True
    assert result["are_equal"] is False
    assert len(result["differences"]) > 0
    # Should detect missing subdir2 in dir2 and missing subdir3 in dir1
    diff_paths = [d["path"] for d in result["differences"]]
    assert "subdir2" in diff_paths or "subdir3" in diff_paths
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)


def test_compare_dirs_different_file_name_nested():
    """
    Test compare_dirs detects different file name at nested level.
    
    Structure:
    dir1/                  dir2/
    └── subdir/           └── subdir/
        ├── file1.txt         ├── file1.txt
        └── file2.txt         └── file3.txt  (different name)
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
    
    # Same file
    file1_1 = os.path.join(subdir1, "file1.txt")
    file2_1 = os.path.join(subdir2, "file1.txt")
    with open(file1_1, "w") as f:
        f.write("content1")
    with open(file2_1, "w") as f:
        f.write("content1")
    
    # Different file name
    file1_2 = os.path.join(subdir1, "file2.txt")
    file2_3 = os.path.join(subdir2, "file3.txt")  # Different name
    with open(file1_2, "w") as f:
        f.write("content2")
    with open(file2_3, "w") as f:
        f.write("content2")

    result = compare_dirs(dir_path_1=dir1, dir_path_2=dir2)

    assert result["success"] is True
    assert result["are_equal"] is False
    assert len(result["differences"]) > 0
    # Should detect missing file2.txt in dir2 or missing file3.txt in dir1
    diff_paths = [d["path"] for d in result["differences"]]
    assert "subdir/file2.txt" in diff_paths or "subdir/file3.txt" in diff_paths
    
    # Clean up
    empty_dir(FILE_SYSTEM_TEST_DIR)

