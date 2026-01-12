"""
Basic tests for compare_dirs function.
"""

import os

from ixtools.file_system import compare_dirs, empty_dir
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

