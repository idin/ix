"""
Tests for unified read_file tool.
"""

import pytest
import os

from tests.conftest import TEST_DATA_DIR
from ixmachina.tools.file_system import path_exists, empty_dir
from ixmachina.tools.file_system import read_file, write_file


@pytest.fixture
def test_dir():
    """Create a clean test directory in .test_data."""
    test_dir = os.path.join(TEST_DATA_DIR, "read_tests", "unified")
    # Clean up any existing files
    if os.path.exists(test_dir):
        empty_dir(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    yield test_dir


def test_read_file_text_auto_detect(test_dir):
    """Test read_file auto-detects text format."""
    test_file = os.path.join(test_dir, "test.txt")
    original_content = "Hello, world!"
    
    # Write file
    write_result = write_file(path=test_file, data=original_content)
    assert write_result["success"] is True
    
    # Read file (auto-detect format)
    result = read_file(path=test_file)
    
    assert result["success"] is True
    assert result["result"] == original_content


def test_read_file_csv_auto_detect(test_dir):
    """Test read_file auto-detects CSV format."""
    test_file = os.path.join(test_dir, "test.csv")
    original_data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
    ]
    
    # Write file
    write_result = write_file(path=test_file, data=original_data)
    assert write_result["success"] is True
    
    # Read file (auto-detect format)
    result = read_file(path=test_file)
    
    assert result["success"] is True
    # CSV files read all values as strings
    expected_data = [
        {"name": "Alice", "age": "30"},
        {"name": "Bob", "age": "25"},
    ]
    assert result["result"] == expected_data


def test_read_file_json_auto_detect(test_dir):
    """Test read_file auto-detects JSON format."""
    test_file = os.path.join(test_dir, "test.json")
    original_data = {"name": "Alice", "age": 30, "cities": ["New York", "London"]}
    
    # Write file
    write_result = write_file(path=test_file, data=original_data)
    assert write_result["success"] is True
    
    # Read file (auto-detect format)
    result = read_file(path=test_file)
    
    assert result["success"] is True
    assert result["result"] == original_data


def test_read_file_yaml_auto_detect(test_dir):
    """Test read_file auto-detects YAML format."""
    try:
        import yaml
    except ImportError:
        pytest.skip("PyYAML not installed")
    
    test_file = os.path.join(test_dir, "test.yaml")
    original_data = {"name": "Alice", "age": 30}
    
    # Write file
    write_result = write_file(path=test_file, data=original_data)
    assert write_result["success"] is True
    
    # Read file (auto-detect format)
    result = read_file(path=test_file)
    
    assert result["success"] is True
    assert result["result"] == original_data


def test_read_file_pickle_auto_detect(test_dir):
    """Test read_file auto-detects pickle format."""
    test_file = os.path.join(test_dir, "test.pkl")
    original_data = {"name": "Alice", "age": 30, "nested": {"key": "value"}}
    
    # Write file
    write_result = write_file(path=test_file, data=original_data, format="pickle")
    assert write_result["success"] is True
    
    # Read file (auto-detect format)
    result = read_file(path=test_file)
    
    assert result["success"] is True
    assert result["result"] == original_data


def test_read_file_explicit_format(test_dir):
    """Test read_file with explicit format parameter."""
    test_file = os.path.join(test_dir, "test.unknown")
    original_content = "Hello, world!"
    
    # Write file as text
    write_result = write_file(path=test_file, data=original_content, format="text")
    assert write_result["success"] is True
    
    # Read file with explicit format
    result = read_file(path=test_file, format="text")
    
    assert result["success"] is True
    assert result["result"] == original_content


def test_read_file_nonexistent(test_dir):
    """Test read_file returns error for nonexistent file."""
    test_file = os.path.join(test_dir, "nonexistent.txt")
    
    result = read_file(path=test_file)
    
    assert result["success"] is False
    assert result["result"] is None
    assert "does not exist" in result["error"].lower()


def test_read_file_unsupported_format(test_dir):
    """Test read_file returns error for unsupported format."""
    test_file = os.path.join(test_dir, "test.xyz")
    
    # Create a dummy file first so it exists
    with open(test_file, "w") as f:
        f.write("dummy content")
    
    result = read_file(path=test_file, format="xyz")
    
    assert result["success"] is False
    assert result["result"] is None
    assert "unsupported format" in result["error"].lower()

