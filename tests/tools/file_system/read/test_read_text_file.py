"""
Tests for read_text_file tool.
"""

import pytest
import os

from tests.conftest import TEST_DATA_DIR
from ixmachina.tools.file_system import path_exists, empty_dir
from ixmachina.tools.file_system.read import read_text_file
from ixmachina.tools.file_system.write import write_text_file


@pytest.fixture
def test_dir():
    """Create a clean test directory in .test_data."""
    test_dir = os.path.join(TEST_DATA_DIR, "read_tests", "text_file")
    # Clean up any existing files
    if os.path.exists(test_dir):
        empty_dir(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    yield test_dir


def test_read_text_file_success(test_dir):
    """Test read_text_file reads content correctly."""
    test_file = os.path.join(test_dir, "test.txt")
    original_content = "Hello, world!\nThis is a test file."
    
    # Write file first
    write_result = write_text_file(path=test_file, content=original_content)
    assert write_result["success"] is True
    
    # Read file
    result = read_text_file(path=test_file)
    
    assert result["success"] is True
    assert result["result"] == original_content  # RESULT_KEY contains just the data
    assert result["metadata"]["path"] == test_file  # Path is in metadata
    assert result["error"] is None


def test_read_text_file_nonexistent(test_dir):
    """Test read_text_file returns error for nonexistent file."""
    test_file = os.path.join(test_dir, "nonexistent.txt")
    
    result = read_text_file(path=test_file)
    
    assert result["success"] is False
    assert result["result"] is None
    assert "does not exist" in result["error"].lower()


def test_read_text_file_directory(test_dir):
    """Test read_text_file returns error when path is a directory."""
    result = read_text_file(path=test_dir)
    
    assert result["success"] is False
    assert result["result"] is None
    assert "not a file" in result["error"].lower()


def test_read_text_file_encoding(test_dir):
    """Test read_text_file with different encoding."""
    test_file = os.path.join(test_dir, "test_utf8.txt")
    original_content = "Hello, 世界! 🌍"
    
    # Write file with UTF-8
    write_result = write_text_file(path=test_file, content=original_content, encoding="utf-8")
    assert write_result["success"] is True
    
    # Read file with UTF-8
    result = read_text_file(path=test_file, encoding="utf-8")
    
    assert result["success"] is True
    assert result["result"] == original_content


def test_read_text_file_empty_file(test_dir):
    """Test read_text_file reads empty file correctly."""
    test_file = os.path.join(test_dir, "empty.txt")
    original_content = ""
    
    # Write empty file
    write_result = write_text_file(path=test_file, content=original_content)
    assert write_result["success"] is True
    
    # Read file
    result = read_text_file(path=test_file)
    
    assert result["success"] is True
    assert result["result"] == original_content


def test_read_text_file_multiline(test_dir):
    """Test read_text_file reads multiline content correctly."""
    test_file = os.path.join(test_dir, "multiline.txt")
    original_content = "Line 1\nLine 2\nLine 3\n\nLine 5"
    
    # Write file
    write_result = write_text_file(path=test_file, content=original_content)
    assert write_result["success"] is True
    
    # Read file
    result = read_text_file(path=test_file)
    
    assert result["success"] is True
    assert result["result"] == original_content

