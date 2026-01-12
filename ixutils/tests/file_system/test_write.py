"""
Tests for file_system write utilities.
"""

import os
from ixutils.file_system import write_text_file, read_text_file
from tests.file_system.test_paths import FILE_SYSTEM_TEST_DIR


def test_write_text_file_mode_x_success():
    """Test that write_text_file with mode 'x' creates new file."""
    file_path = os.path.join(FILE_SYSTEM_TEST_DIR, "write_test_x.txt")
    content = "Hello, world!"
    
    write_text_file(file_path, content, mode="x")
    
    assert os.path.exists(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        assert f.read() == content
    os.unlink(file_path)


def test_write_text_file_mode_x_file_exists():
    """Test that write_text_file with mode 'x' raises FileExistsError if file exists."""
    import pytest
    file_path = os.path.join(FILE_SYSTEM_TEST_DIR, "write_test_exists.txt")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        f.write("existing")
    with pytest.raises(FileExistsError):
        write_text_file(file_path, "content", mode="x")
    os.unlink(file_path)


def test_write_text_file_mode_w_overwrites():
    """Test that write_text_file with mode 'w' overwrites existing file."""
    file_path = os.path.join(FILE_SYSTEM_TEST_DIR, "write_test_w.txt")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        f.write("Original content")
    
    write_text_file(file_path, "New content", mode="w")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        assert f.read() == "New content"
    os.unlink(file_path)


def test_write_text_file_mode_w_creates_new():
    """Test that write_text_file with mode 'w' creates new file if it doesn't exist."""
    file_path = os.path.join(FILE_SYSTEM_TEST_DIR, "write_test_w_new.txt")
    content = "New file content"
    
    write_text_file(file_path, content, mode="w")
    
    assert os.path.exists(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        assert f.read() == content
    os.unlink(file_path)


def test_write_text_file_mode_a_appends():
    """Test that write_text_file with mode 'a' appends to existing file."""
    file_path = os.path.join(FILE_SYSTEM_TEST_DIR, "write_test_a.txt")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        f.write("Original content\n")
    
    write_text_file(file_path, "Appended content\n", mode="a")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "Original content" in content
        assert "Appended content" in content
    os.unlink(file_path)


def test_write_text_file_mode_a_creates_new():
    """Test that write_text_file with mode 'a' creates new file if it doesn't exist."""
    file_path = os.path.join(FILE_SYSTEM_TEST_DIR, "write_test_a_new.txt")
    content = "Appended content"
    
    write_text_file(file_path, content, mode="a")
    
    assert os.path.exists(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        assert f.read() == content
    os.unlink(file_path)


def test_write_text_file_creates_parent_directories():
    """Test that write_text_file creates parent directories if they don't exist."""
    file_path = os.path.join(FILE_SYSTEM_TEST_DIR, "subdir", "nested", "file.txt")
    content = "Nested file content"
    
    write_text_file(file_path, content, mode="x")
    
    assert os.path.exists(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        assert f.read() == content
    os.unlink(file_path)
    os.rmdir(os.path.join(FILE_SYSTEM_TEST_DIR, "subdir", "nested"))
    os.rmdir(os.path.join(FILE_SYSTEM_TEST_DIR, "subdir"))


def test_write_text_file_invalid_mode():
    """Test that write_text_file raises ValueError for invalid mode."""
    import pytest
    file_path = os.path.join(FILE_SYSTEM_TEST_DIR, "write_test_invalid.txt")
    with pytest.raises(ValueError):
        write_text_file(file_path, "content", mode="invalid")


def test_write_text_file_with_utf8_content():
    """Test that write_text_file handles UTF-8 content correctly."""
    file_path = os.path.join(FILE_SYSTEM_TEST_DIR, "write_test_utf8.txt")
    content = "Hello, 世界! 🌍"
    
    write_text_file(file_path, content, mode="x", encoding='utf-8')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        assert f.read() == content
    os.unlink(file_path)


def test_write_text_file_multiline_content():
    """Test that write_text_file writes multiline content correctly."""
    file_path = os.path.join(FILE_SYSTEM_TEST_DIR, "write_test_multiline.txt")
    content = "Line 1\nLine 2\nLine 3"
    
    write_text_file(file_path, content, mode="x")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        assert f.read() == content
    os.unlink(file_path)
