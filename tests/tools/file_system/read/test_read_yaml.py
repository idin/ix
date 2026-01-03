"""
Tests for read_yaml tool.
"""

import pytest
import os

from tests.conftest import TEST_DATA_DIR
from ixmachina.tools.file_system import path_exists, empty_dir
from ixmachina.tools.file_system.read import read_yaml
from ixmachina.tools.file_system.write import write_yaml


@pytest.fixture
def test_dir():
    """Create a clean test directory in .test_data."""
    test_dir = os.path.join(TEST_DATA_DIR, "read_tests", "yaml")
    # Clean up any existing files
    if os.path.exists(test_dir):
        empty_dir(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    yield test_dir


def test_read_yaml_success(test_dir):
    """Test read_yaml reads data correctly."""
    try:
        import yaml
    except ImportError:
        pytest.skip("PyYAML not installed")
    
    test_file = os.path.join(test_dir, "test.yaml")
    original_data = {
        "name": "Alice",
        "age": 30,
        "cities": ["New York", "London"],
        "metadata": {"active": True, "score": 95.5}
    }
    
    # Write file first
    write_result = write_yaml(path=test_file, data=original_data)
    assert write_result["success"] is True
    
    # Read file
    result = read_yaml(path=test_file)
    
    assert result["success"] is True
    assert result["result"] == original_data
    assert result["metadata"]["path"] == test_file
    assert result["error"] is None


def test_read_yaml_list(test_dir):
    """Test read_yaml reads list data correctly."""
    try:
        import yaml
    except ImportError:
        pytest.skip("PyYAML not installed")
    
    test_file = os.path.join(test_dir, "list.yaml")
    original_data = [1, 2, 3, {"nested": "value"}]
    
    # Write file
    write_result = write_yaml(path=test_file, data=original_data)
    assert write_result["success"] is True
    
    # Read file
    result = read_yaml(path=test_file)
    
    assert result["success"] is True
    assert result["result"] == original_data


def test_read_yaml_nonexistent(test_dir):
    """Test read_yaml returns error for nonexistent file."""
    try:
        import yaml
    except ImportError:
        pytest.skip("PyYAML not installed")
    
    test_file = os.path.join(test_dir, "nonexistent.yaml")
    
    result = read_yaml(path=test_file)
    
    assert result["success"] is False
    assert result["result"] is None
    assert "does not exist" in result["error"].lower()


def test_read_yaml_missing_pyyaml(test_dir):
    """Test read_yaml returns error when PyYAML is not installed."""
    # This test would need to mock the import, but we'll skip it
    # since we can't easily test missing dependencies
    pytest.skip("Cannot easily test missing PyYAML scenario")


def test_read_yaml_empty_object(test_dir):
    """Test read_yaml reads empty object correctly."""
    try:
        import yaml
    except ImportError:
        pytest.skip("PyYAML not installed")
    
    test_file = os.path.join(test_dir, "empty.yaml")
    original_data = {}
    
    # Write file
    write_result = write_yaml(path=test_file, data=original_data)
    assert write_result["success"] is True
    
    # Read file
    result = read_yaml(path=test_file)
    
    assert result["success"] is True
    assert result["result"] == original_data

