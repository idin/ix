"""
Tests for file_system read utilities.
"""

import os
from ixutils.file_system import read_text_file
from tests.file_system.test_paths import FILE_SYSTEM_TEST_DIR


def test_read_text_file_success():
    """Test that read_text_file reads file content correctly."""
    test_file = os.path.join(FILE_SYSTEM_TEST_DIR, "read_test.txt")
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    content = "Hello, world!\nThis is a test file."
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(content)
    result = read_text_file(test_file)
    assert result == content
    os.unlink(test_file)


def test_read_text_file_with_utf8_encoding():
    """Test that read_text_file handles UTF-8 encoding correctly."""
    test_file = os.path.join(FILE_SYSTEM_TEST_DIR, "read_utf8.txt")
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    content = "Hello, 世界! 🌍"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(content)
    result = read_text_file(test_file, encoding='utf-8')
    assert result == content
    os.unlink(test_file)


def test_read_text_file_with_custom_encoding():
    """Test that read_text_file works with custom encoding."""
    test_file = os.path.join(FILE_SYSTEM_TEST_DIR, "read_latin1.txt")
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    content = "Test content"
    with open(test_file, 'w', encoding='latin-1') as f:
        f.write(content)
    result = read_text_file(test_file, encoding='latin-1')
    assert result == content
    os.unlink(test_file)


def test_read_text_file_nonexistent_file():
    """Test that read_text_file raises FileNotFoundError for nonexistent files."""
    import pytest
    with pytest.raises(FileNotFoundError):
        read_text_file(os.path.join(FILE_SYSTEM_TEST_DIR, "nonexistent_file.txt"))


def test_read_text_file_with_directory():
    """Test that read_text_file raises IsADirectoryError for directories."""
    import pytest
    test_dir = os.path.join(FILE_SYSTEM_TEST_DIR, "read_test_dir")
    os.makedirs(test_dir, exist_ok=True)
    with pytest.raises(IsADirectoryError):
        read_text_file(test_dir)
    os.rmdir(test_dir)


def test_read_text_file_multiline_content():
    """Test that read_text_file reads multiline content correctly."""
    test_file = os.path.join(FILE_SYSTEM_TEST_DIR, "read_multiline.txt")
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    content = "Line 1\nLine 2\nLine 3"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(content)
    result = read_text_file(test_file)
    assert result == content
    assert len(result.split('\n')) == 3
    os.unlink(test_file)


def test_read_text_file_empty_file():
    """Test that read_text_file reads empty files correctly."""
    test_file = os.path.join(FILE_SYSTEM_TEST_DIR, "read_empty.txt")
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    with open(test_file, 'w', encoding='utf-8') as f:
        pass
    result = read_text_file(test_file)
    assert result == ""
    os.unlink(test_file)
