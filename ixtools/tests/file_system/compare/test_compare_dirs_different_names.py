"""
Tests for compare_dirs detecting different file/directory names.
"""

import os

from ixtools.file_system import compare_dirs, empty_dir
from ..tools_file_system_constants import FILE_SYSTEM_TEST_DIR


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

