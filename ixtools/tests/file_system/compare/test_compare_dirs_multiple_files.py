"""
Tests for compare_dirs with multiple files.
"""

import os

from ixtools.file_system import compare_dirs, empty_dir
from ..tools_file_system_constants import FILE_SYSTEM_TEST_DIR


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

