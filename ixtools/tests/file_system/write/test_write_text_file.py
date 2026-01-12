"""
Tests for write_text_file tool.
"""

import pytest
import os

from tests.conftest import TEST_DATA_DIR
from ixtools.file_system import path_exists, empty_dir
from ixtools.file_system.write import write_text_file
from ixtools.file_system.memory import FileSystemMemory


@pytest.fixture
def test_dir():
    """Create a clean test directory in .test_data."""
    test_dir = os.path.join(TEST_DATA_DIR, "write_tests", "text_file")
    # Clean up any existing files
    if os.path.exists(test_dir):
        empty_dir(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    yield test_dir


def test_write_text_file_exclusive_create(test_dir):
    """Test write_text_file with exclusive create mode (default)."""
    test_file = os.path.join(test_dir, "test.txt")
    content = "Hello, world!"
    
    result = write_text_file(path=test_file, content=content)
    
    assert result["success"] is True
    assert result["result"] == content  # RESULT_KEY contains the written content
    assert result["metadata"]["path"] == test_file  # Path is in metadata
    assert result["error"] is None
    assert path_exists(test_file)["result"] is True
    
    # Verify content
    with open(test_file, "r", encoding="utf-8") as f:
        assert f.read() == content


def test_write_text_file_exclusive_create_fails_if_exists(test_dir):
    """Test write_text_file fails if file exists with mode 'x'."""
    test_file = os.path.join(test_dir, "test.txt")
    content = "Hello, world!"
    
    # Create file first
    with open(test_file, "w") as f:
        f.write("existing content")
    
    result = write_text_file(path=test_file, content=content, mode="x")
    
    assert result["success"] is False
    assert "already exists" in result["error"].lower()
    assert "overwrite is not allowed" in result["error"].lower()


def test_write_text_file_overwrite_mode(test_dir):
    """Test write_text_file with overwrite mode."""
    test_file = os.path.join(test_dir, "test.txt")
    original_content = "original content"
    new_content = "new content"
    
    # Create file first
    with open(test_file, "w") as f:
        f.write(original_content)
    
    result = write_text_file(path=test_file, content=new_content, mode="w")
    
    assert result["success"] is True
    assert result["error"] is None
    
    # Verify new content
    with open(test_file, "r", encoding="utf-8") as f:
        assert f.read() == new_content


def test_write_text_file_append_mode(test_dir):
    """Test write_text_file with append mode."""
    test_file = os.path.join(test_dir, "test.txt")
    original_content = "original"
    appended_content = " appended"
    
    # Create file first
    with open(test_file, "w") as f:
        f.write(original_content)
    
    result = write_text_file(path=test_file, content=appended_content, mode="a")
    
    assert result["success"] is True
    assert result["error"] is None
    
    # Verify appended content
    with open(test_file, "r", encoding="utf-8") as f:
        assert f.read() == original_content + appended_content


def test_write_text_file_append_creates_if_not_exists(test_dir):
    """Test write_text_file append mode creates file if it doesn't exist."""
    test_file = os.path.join(test_dir, "new_file.txt")
    content = "new content"
    
    result = write_text_file(path=test_file, content=content, mode="a")
    
    assert result["success"] is True
    assert path_exists(test_file)["result"] is True
    
    with open(test_file, "r", encoding="utf-8") as f:
        assert f.read() == content


def test_write_text_file_creates_parent_directories(test_dir):
    """Test write_text_file creates parent directories if they don't exist."""
    test_file = os.path.join(test_dir, "subdir", "nested", "test.txt")
    content = "nested content"
    
    result = write_text_file(path=test_file, content=content)
    
    assert result["success"] is True
    assert path_exists(test_file)["result"] is True
    
    with open(test_file, "r", encoding="utf-8") as f:
        assert f.read() == content


def test_write_text_file_invalid_mode(test_dir):
    """Test write_text_file with invalid mode."""
    test_file = os.path.join(test_dir, "test.txt")
    
    result = write_text_file(path=test_file, content="test", mode="invalid")
    
    assert result["success"] is False
    assert "invalid mode" in result["error"].lower()


def test_write_text_file_with_memory_tracking(test_dir):
    """Test write_text_file tracks action in FileSystemMemory."""
    test_file = os.path.join(test_dir, "test.txt")
    content = "test content"
    memory = FileSystemMemory()
    
    result = write_text_file(path=test_file, content=content, file_system_memory=memory)
    
    assert result["success"] is True
    assert memory.size() == 1
    last_action, _ = memory.get_last_action()
    assert last_action.function_name == "write_text_file"


def test_write_text_file_undo(test_dir):
    """Test write_text_file undo functionality."""
    test_file = os.path.join(test_dir, "test.txt")
    content = "test content"
    memory = FileSystemMemory()
    
    # Write file
    result = write_text_file(path=test_file, content=content, file_system_memory=memory)
    assert result["success"] is True
    assert path_exists(test_file)["result"] is True
    
    # Undo
    undo_result = memory.undo()
    assert undo_result["success"] is True
    assert path_exists(test_file)["result"] is False

