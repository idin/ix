"""
Tests for read_csv tool.
"""

import pytest
import os

from tests.conftest import TEST_DATA_DIR
from ixmachina.tools.file_system import path_exists, empty_dir
from ixmachina.tools.file_system.read import read_csv
from ixmachina.tools.file_system.write import write_csv


@pytest.fixture
def test_dir():
    """Create a clean test directory in .test_data."""
    test_dir = os.path.join(TEST_DATA_DIR, "read_tests", "csv")
    # Clean up any existing files
    if os.path.exists(test_dir):
        empty_dir(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    yield test_dir


def test_read_csv_success(test_dir):
    """Test read_csv reads data correctly."""
    test_file = os.path.join(test_dir, "test.csv")
    original_data = [
        {"name": "Alice", "age": 30, "city": "New York"},
        {"name": "Bob", "age": 25, "city": "London"},
        {"name": "Charlie", "age": 35, "city": "Tokyo"},
    ]
    
    # Write file first
    write_result = write_csv(path=test_file, data=original_data)
    assert write_result["success"] is True
    
    # Read file
    result = read_csv(path=test_file)
    
    assert result["success"] is True
    # CSV files read all values as strings, so convert expected values
    expected_data = [
        {"name": "Alice", "age": "30", "city": "New York"},
        {"name": "Bob", "age": "25", "city": "London"},
        {"name": "Charlie", "age": "35", "city": "Tokyo"},
    ]
    assert result["result"] == expected_data
    assert result["metadata"]["path"] == test_file
    assert result["error"] is None


def test_read_csv_nonexistent(test_dir):
    """Test read_csv returns error for nonexistent file."""
    test_file = os.path.join(test_dir, "nonexistent.csv")
    
    result = read_csv(path=test_file)
    
    assert result["success"] is False
    assert result["result"] is None
    assert "does not exist" in result["error"].lower()


def test_read_csv_empty_file(test_dir):
    """Test read_csv handles empty CSV file."""
    test_file = os.path.join(test_dir, "empty.csv")
    
    # Create empty CSV file (just header)
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("name,age\n")
    
    result = read_csv(path=test_file)
    
    assert result["success"] is True
    assert result["result"] == []  # Empty list when only header exists


def test_read_csv_single_row(test_dir):
    """Test read_csv reads single row correctly."""
    test_file = os.path.join(test_dir, "single.csv")
    original_data = [{"name": "Alice", "age": 30}]
    
    # Write file
    write_result = write_csv(path=test_file, data=original_data)
    assert write_result["success"] is True
    
    # Read file
    result = read_csv(path=test_file)
    
    assert result["success"] is True
    # CSV files read all values as strings
    expected_data = [{"name": "Alice", "age": "30"}]
    assert result["result"] == expected_data


def test_read_csv_encoding(test_dir):
    """Test read_csv with different encoding."""
    test_file = os.path.join(test_dir, "test_utf8.csv")
    original_data = [{"name": "José", "city": "São Paulo"}]
    
    # Write file
    write_result = write_csv(path=test_file, data=original_data, encoding="utf-8")
    assert write_result["success"] is True
    
    # Read file
    result = read_csv(path=test_file, encoding="utf-8")
    
    assert result["success"] is True
    assert result["result"] == original_data

