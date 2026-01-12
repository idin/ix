"""
Tests for write_csv tool.
"""

import pytest
import os
import csv

from tests.conftest import TEST_DATA_DIR
from ixtools.file_system import path_exists, empty_dir
from ixtools.file_system.write import write_csv
from ixtools.file_system.memory import FileSystemMemory


@pytest.fixture
def test_dir():
    """Create a clean test directory in .test_data."""
    test_dir = os.path.join(TEST_DATA_DIR, "write_tests", "csv")
    # Clean up any existing files
    if os.path.exists(test_dir):
        empty_dir(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    yield test_dir


def test_write_csv_exclusive_create(test_dir):
    """Test write_csv with exclusive create mode (default)."""
    test_file = os.path.join(test_dir, "test.csv")
    data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
    ]
    
    result = write_csv(path=test_file, data=data)
    
    assert result["success"] is True
    assert result["metadata"]["path"] == test_file
    assert result["error"] is None
    assert path_exists(test_file)
    
    # Verify content
    with open(test_file, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["name"] == "Alice"
        assert rows[0]["age"] == "30"
        assert rows[1]["name"] == "Bob"
        assert rows[1]["age"] == "25"


def test_write_csv_fails_if_exists(test_dir):
    """Test write_csv fails if file exists with mode 'x'."""
    test_file = os.path.join(test_dir, "test.csv")
    
    # Create file first
    with open(test_file, "w") as f:
        f.write("existing")
    
    result = write_csv(path=test_file, data=[{"col": "val"}], mode="x")
    
    assert result["success"] is False
    assert "already exists" in result["error"].lower()


def test_write_csv_overwrite_mode(test_dir):
    """Test write_csv with overwrite mode."""
    test_file = os.path.join(test_dir, "test.csv")
    original_data = [{"col": "old"}]
    new_data = [{"col": "new"}]
    
    # Create file first
    result = write_csv(path=test_file, data=original_data)
    assert result["success"] is True
    
    result = write_csv(path=test_file, data=new_data, mode="w")
    assert result["success"] is True
    
    # Verify new content
    with open(test_file, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert rows[0]["col"] == "new"


def test_write_csv_empty_data(test_dir):
    """Test write_csv fails with empty data."""
    test_file = os.path.join(test_dir, "test.csv")
    
    result = write_csv(path=test_file, data=[])
    
    assert result["success"] is False
    assert "empty" in result["error"].lower()


def test_write_csv_invalid_data_type(test_dir):
    """Test write_csv fails with invalid data type."""
    test_file = os.path.join(test_dir, "test.csv")
    
    result = write_csv(path=test_file, data="not a list")
    
    assert result["success"] is False
    assert "list of dictionaries" in result["error"].lower()


def test_write_csv_with_memory_tracking(test_dir):
    """Test write_csv tracks action in FileSystemMemory."""
    test_file = os.path.join(test_dir, "test.csv")
    data = [{"col": "val"}]
    memory = FileSystemMemory()
    
    result = write_csv(path=test_file, data=data, file_system_memory=memory)
    
    assert result["success"] is True
    assert memory.size() == 1
    last_action, _ = memory.get_last_action()
    assert last_action.function_name == "write_csv"

