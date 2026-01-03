"""
Tests for write_yaml tool.
"""

import pytest
import os

from tests.conftest import TEST_DATA_DIR
from ixmachina.tools.file_system import path_exists, empty_dir
from ixmachina.tools.file_system.write import write_yaml


@pytest.fixture
def test_dir():
    """Create a clean test directory in .test_data."""
    test_dir = os.path.join(TEST_DATA_DIR, "write_tests", "yaml")
    # Clean up any existing files
    if os.path.exists(test_dir):
        empty_dir(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    yield test_dir


def test_write_yaml_exclusive_create(test_dir):
    """Test write_yaml with exclusive create mode (default)."""
    try:
        import yaml
    except ImportError:
        pytest.skip("PyYAML not installed")
    
    test_file = os.path.join(test_dir, "test.yaml")
    data = {"name": "Alice", "age": 30, "cities": ["New York", "London"]}
    
    result = write_yaml(path=test_file, data=data)
    
    assert result["success"] is True
    assert result["metadata"]["path"] == test_file
    assert result["error"] is None
    assert path_exists(test_file)
    
    # Verify content
    import yaml
    with open(test_file, "r", encoding="utf-8") as f:
        loaded_data = yaml.safe_load(f)
        assert loaded_data == data


def test_write_yaml_missing_pyyaml(test_dir):
    """Test write_yaml returns error if PyYAML is not installed."""
    # Skip this test if PyYAML is installed (can't easily test missing dependency)
    try:
        import yaml
        pytest.skip("PyYAML is installed, cannot test missing dependency scenario")
    except ImportError:
        pass
    
    test_file = os.path.join(test_dir, "test.yaml")
    data = {"key": "value"}
    
    result = write_yaml(path=test_file, data=data)
    assert result["success"] is False
    assert "pyyaml" in result["error"].lower()

