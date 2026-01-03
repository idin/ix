"""
Tests for read_pickle tool.
"""

import pytest
import os
import pickle

from tests.conftest import TEST_DATA_DIR
from ixmachina.tools.file_system import path_exists, empty_dir
from ixmachina.tools.file_system.read import read_pickle
from ixmachina.tools.file_system.write import write_pickle


# Custom class for testing pickle serialization (must be at module level for pickle)
class CustomClass:
    """Test class for pickle serialization."""
    def __init__(self, value):
        self.value = value
    
    def __eq__(self, other):
        return isinstance(other, CustomClass) and self.value == other.value


@pytest.fixture
def test_dir():
    """Create a clean test directory in .test_data."""
    test_dir = os.path.join(TEST_DATA_DIR, "read_tests", "pickle")
    # Clean up any existing files
    if os.path.exists(test_dir):
        empty_dir(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    yield test_dir


def test_read_pickle_success(test_dir):
    """Test read_pickle reads data correctly."""
    test_file = os.path.join(test_dir, "test.pkl")
    original_data = {"name": "Alice", "age": 30, "nested": {"key": "value"}}
    
    # Write file first
    write_result = write_pickle(path=test_file, obj=original_data)
    assert write_result["success"] is True
    
    # Read file
    result = read_pickle(path=test_file)
    
    assert result["success"] is True
    assert result["result"] == original_data
    assert result["metadata"]["path"] == test_file
    assert result["error"] is None


def test_read_pickle_complex_object(test_dir):
    """Test read_pickle reads complex object correctly."""
    test_file = os.path.join(test_dir, "complex.pkl")
    obj = CustomClass("test")
    
    # Write file
    write_result = write_pickle(path=test_file, obj=obj)
    assert write_result["success"] is True
    
    # Read file
    result = read_pickle(path=test_file)
    
    assert result["success"] is True
    assert isinstance(result["result"], CustomClass)
    assert result["result"] == obj


def test_read_pickle_list(test_dir):
    """Test read_pickle reads list correctly."""
    test_file = os.path.join(test_dir, "list.pkl")
    original_data = [1, 2, 3, {"nested": "value"}]
    
    # Write file
    write_result = write_pickle(path=test_file, obj=original_data)
    assert write_result["success"] is True
    
    # Read file
    result = read_pickle(path=test_file)
    
    assert result["success"] is True
    assert result["result"] == original_data


def test_read_pickle_nonexistent(test_dir):
    """Test read_pickle returns error for nonexistent file."""
    test_file = os.path.join(test_dir, "nonexistent.pkl")
    
    result = read_pickle(path=test_file)
    
    assert result["success"] is False
    assert result["result"] is None
    assert "does not exist" in result["error"].lower()


def test_read_pickle_invalid_file(test_dir):
    """Test read_pickle returns error for invalid pickle file."""
    test_file = os.path.join(test_dir, "invalid.pkl")
    
    # Write invalid pickle data
    with open(test_file, "wb") as f:
        f.write(b"invalid pickle data")
    
    result = read_pickle(path=test_file)
    
    assert result["success"] is False
    assert result["result"] is None
    assert "invalid pickle" in result["error"].lower()

