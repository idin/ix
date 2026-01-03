"""
Tests for write_json tool.
"""

import pytest
import os
import json

from tests.conftest import TEST_DATA_DIR
from ixmachina.tools.file_system import path_exists, empty_dir
from ixmachina.tools.file_system.write import write_json
from ixmachina.tools.file_system.memory import FileSystemMemory


@pytest.fixture
def test_dir():
    """Create a clean test directory in .test_data."""
    test_dir = os.path.join(TEST_DATA_DIR, "write_tests", "json")
    # Clean up any existing files
    if os.path.exists(test_dir):
        empty_dir(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    yield test_dir


def test_write_json_exclusive_create(test_dir):
    """Test write_json with exclusive create mode (default)."""
    test_file = os.path.join(test_dir, "test.json")
    data = {"name": "Alice", "age": 30, "cities": ["New York", "London"]}
    
    result = write_json(path=test_file, data=data)
    
    assert result["success"] is True
    assert result["metadata"]["path"] == test_file
    assert result["error"] is None
    assert path_exists(test_file)
    
    # Verify content
    with open(test_file, "r", encoding="utf-8") as f:
        loaded_data = json.load(f)
        assert loaded_data == data


def test_write_json_fails_if_exists(test_dir):
    """Test write_json fails if file exists with mode 'x'."""
    test_file = os.path.join(test_dir, "test.json")
    
    # Create file first
    with open(test_file, "w") as f:
        f.write('{"existing": true}')
    
    result = write_json(path=test_file, data={"new": "data"}, mode="x")
    
    assert result["success"] is False
    assert "already exists" in result["error"].lower()


def test_write_json_overwrite_mode(test_dir):
    """Test write_json with overwrite mode."""
    test_file = os.path.join(test_dir, "test.json")
    original_data = {"old": "data"}
    new_data = {"new": "data"}
    
    # Create file first
    result = write_json(path=test_file, data=original_data)
    assert result["success"] is True
    
    result = write_json(path=test_file, data=new_data, mode="w")
    assert result["success"] is True
    
    # Verify new content
    with open(test_file, "r", encoding="utf-8") as f:
        loaded_data = json.load(f)
        assert loaded_data == new_data


def test_write_json_custom_indent(test_dir):
    """Test write_json with custom indent."""
    test_file = os.path.join(test_dir, "test.json")
    data = {"key": "value"}
    
    result = write_json(path=test_file, data=data, indent=4)
    
    assert result["success"] is True
    
    # Verify indent
    with open(test_file, "r", encoding="utf-8") as f:
        content = f.read()
        # Should have 4-space indentation
        assert "    " in content


def test_write_json_non_serializable(test_dir):
    """Test write_json fails with non-serializable data."""
    test_file = os.path.join(test_dir, "test.json")
    
    # Function is not JSON-serializable
    def func():
        pass
    
    result = write_json(path=test_file, data={"func": func})
    
    assert result["success"] is False
    assert "json-serializable" in result["error"].lower()


def test_write_json_with_memory_tracking(test_dir):
    """Test write_json tracks action in FileSystemMemory."""
    test_file = os.path.join(test_dir, "test.json")
    data = {"key": "value"}
    memory = FileSystemMemory()
    
    result = write_json(path=test_file, data=data, file_system_memory=memory)
    
    assert result["success"] is True
    assert memory.size() == 1
    last_action, _ = memory.get_last_action()
    assert last_action.function_name == "write_json"

