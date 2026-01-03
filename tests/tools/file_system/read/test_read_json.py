"""
Tests for read_json tool.
"""

import pytest
import os

from tests.conftest import TEST_DATA_DIR
from ixmachina.tools.file_system import path_exists, empty_dir
from ixmachina.tools.file_system.read import read_json
from ixmachina.tools.file_system.write import write_json


@pytest.fixture
def test_dir():
    """Create a clean test directory in .test_data."""
    test_dir = os.path.join(TEST_DATA_DIR, "read_tests", "json")
    # Clean up any existing files
    if os.path.exists(test_dir):
        empty_dir(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    yield test_dir


def test_read_json_success(test_dir):
    """Test read_json reads data correctly."""
    test_file = os.path.join(test_dir, "test.json")
    original_data = {
        "name": "Alice",
        "age": 30,
        "cities": ["New York", "London", "Tokyo"],
        "metadata": {"active": True, "score": 95.5}
    }
    
    # Write file first
    write_result = write_json(path=test_file, data=original_data)
    assert write_result["success"] is True
    
    # Read file
    result = read_json(path=test_file)
    
    assert result["success"] is True
    assert result["result"] == original_data
    assert result["metadata"]["path"] == test_file
    assert result["error"] is None


def test_read_json_list(test_dir):
    """Test read_json reads list data correctly."""
    test_file = os.path.join(test_dir, "list.json")
    original_data = [1, 2, 3, {"nested": "value"}]
    
    # Write file
    write_result = write_json(path=test_file, data=original_data)
    assert write_result["success"] is True
    
    # Read file
    result = read_json(path=test_file)
    
    assert result["success"] is True
    assert result["result"] == original_data


def test_read_json_nonexistent(test_dir):
    """Test read_json returns error for nonexistent file."""
    test_file = os.path.join(test_dir, "nonexistent.json")
    
    result = read_json(path=test_file)
    
    assert result["success"] is False
    assert result["result"] is None
    assert "does not exist" in result["error"].lower()


def test_read_json_invalid_json(test_dir):
    """Test read_json returns error for invalid JSON."""
    test_file = os.path.join(test_dir, "invalid.json")
    
    # Write invalid JSON
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("{ invalid json }")
    
    result = read_json(path=test_file)
    
    assert result["success"] is False
    assert result["result"] is None
    assert "invalid json" in result["error"].lower()


def test_read_json_empty_object(test_dir):
    """Test read_json reads empty object correctly."""
    test_file = os.path.join(test_dir, "empty.json")
    original_data = {}
    
    # Write file
    write_result = write_json(path=test_file, data=original_data)
    assert write_result["success"] is True
    
    # Read file
    result = read_json(path=test_file)
    
    assert result["success"] is True
    assert result["result"] == original_data


def test_read_json_custom_indent(test_dir):
    """Test read_json reads file with custom indent correctly."""
    test_file = os.path.join(test_dir, "indent.json")
    original_data = {"key": "value", "nested": {"a": 1, "b": 2}}
    
    # Write file with custom indent
    write_result = write_json(path=test_file, data=original_data, indent=4)
    assert write_result["success"] is True
    
    # Read file
    result = read_json(path=test_file)
    
    assert result["success"] is True
    assert result["result"] == original_data

