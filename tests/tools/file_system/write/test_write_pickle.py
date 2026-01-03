"""
Tests for write_pickle tool.
"""

import pytest
import os
import pickle

from tests.conftest import TEST_DATA_DIR
from ixmachina.tools.file_system import path_exists, empty_dir
from ixmachina.tools.file_system.write import write_pickle
from ixmachina.tools.file_system.memory import FileSystemMemory


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
    test_dir = os.path.join(TEST_DATA_DIR, "write_tests", "pickle")
    # Clean up any existing files
    if os.path.exists(test_dir):
        empty_dir(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    yield test_dir


def test_write_pickle_exclusive_create(test_dir):
    """Test write_pickle with exclusive create mode (default)."""
    test_file = os.path.join(test_dir, "test.pkl")
    data = {"name": "Alice", "age": 30, "nested": {"key": "value"}}
    
    result = write_pickle(path=test_file, obj=data)
    
    assert result["success"] is True
    assert result["metadata"]["path"] == test_file
    assert result["error"] is None
    assert path_exists(test_file)
    
    # Verify content
    with open(test_file, "rb") as f:
        loaded_data = pickle.load(f)
        assert loaded_data == data


def test_write_pickle_complex_object(test_dir):
    """Test write_pickle with complex object."""
    test_file = os.path.join(test_dir, "test.pkl")
    
    obj = CustomClass("test")
    
    result = write_pickle(path=test_file, obj=obj)
    
    assert result["success"] is True
    
    # Verify content
    with open(test_file, "rb") as f:
        loaded_obj = pickle.load(f)
        assert loaded_obj == obj
        assert isinstance(loaded_obj, CustomClass)


def test_write_pickle_fails_if_exists(test_dir):
    """Test write_pickle fails if file exists with mode 'x'."""
    test_file = os.path.join(test_dir, "test.pkl")
    
    # Create file first
    with open(test_file, "wb") as f:
        pickle.dump({"existing": True}, f)
    
    result = write_pickle(path=test_file, obj={"new": "data"}, mode="x")
    
    assert result["success"] is False
    assert "already exists" in result["error"].lower()


def test_write_pickle_overwrite_mode(test_dir):
    """Test write_pickle with overwrite mode."""
    test_file = os.path.join(test_dir, "test.pkl")
    original_obj = {"old": "data"}
    new_obj = {"new": "data"}
    
    # Create file first
    result = write_pickle(path=test_file, obj=original_obj)
    assert result["success"] is True
    
    result = write_pickle(path=test_file, obj=new_obj, mode="w")
    assert result["success"] is True
    
    # Verify new content
    with open(test_file, "rb") as f:
        loaded_obj = pickle.load(f)
        assert loaded_obj == new_obj


def test_write_pickle_with_memory_tracking(test_dir):
    """Test write_pickle tracks action in FileSystemMemory."""
    test_file = os.path.join(test_dir, "test.pkl")
    obj = {"key": "value"}
    memory = FileSystemMemory()
    
    result = write_pickle(path=test_file, obj=obj, file_system_memory=memory)
    
    assert result["success"] is True
    assert memory.size() == 1
    last_action, _ = memory.get_last_action()
    assert last_action.function_name == "write_pickle"

