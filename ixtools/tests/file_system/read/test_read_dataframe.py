"""
Tests for DataFrame read tools.
"""

import pytest
import os
import pandas as pd
import pyarrow
import openpyxl

from tests.conftest import TEST_DATA_DIR
from ixtools.file_system import path_exists, empty_dir
from ixtools.file_system.read import (
    read_dataframe_csv,
    read_dataframe_parquet,
    read_dataframe_excel,
)
from ixtools.file_system.write import (
    write_dataframe_csv,
    write_dataframe_parquet,
    write_dataframe_excel,
)


@pytest.fixture
def test_dir():
    """Create a clean test directory in .test_data."""
    test_dir = os.path.join(TEST_DATA_DIR, "read_tests", "dataframe")
    # Clean up any existing files
    if os.path.exists(test_dir):
        empty_dir(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    yield test_dir


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie"],
        "age": [30, 25, 35],
        "city": ["New York", "London", "Tokyo"]
    })


def test_read_dataframe_csv_success(test_dir, sample_dataframe):
    """Test read_dataframe_csv reads DataFrame correctly."""
    test_file = os.path.join(test_dir, "test.csv")
    
    # Write file first
    write_result = write_dataframe_csv(path=test_file, dataframe=sample_dataframe)
    assert write_result["success"] is True
    
    # Read file
    result = read_dataframe_csv(path=test_file)
    
    assert result["success"] is True
    pd.testing.assert_frame_equal(result["result"], sample_dataframe)
    assert result["metadata"]["path"] == test_file
    assert result["error"] is None


def test_read_dataframe_parquet_success(test_dir, sample_dataframe):
    """Test read_dataframe_parquet reads DataFrame correctly."""
    test_file = os.path.join(test_dir, "test.parquet")
    
    # Write file first
    write_result = write_dataframe_parquet(path=test_file, dataframe=sample_dataframe)
    assert write_result["success"] is True
    
    # Read file
    result = read_dataframe_parquet(path=test_file)
    
    assert result["success"] is True
    pd.testing.assert_frame_equal(result["result"], sample_dataframe)
    assert result["metadata"]["path"] == test_file
    assert result["error"] is None


def test_read_dataframe_excel_success(test_dir, sample_dataframe):
    """Test read_dataframe_excel reads DataFrame correctly."""
    test_file = os.path.join(test_dir, "test.xlsx")
    
    # Write file first
    write_result = write_dataframe_excel(path=test_file, dataframe=sample_dataframe, sheet_name="TestSheet")
    assert write_result["success"] is True
    
    # Read file
    result = read_dataframe_excel(path=test_file, sheet_name="TestSheet")
    
    assert result["success"] is True
    pd.testing.assert_frame_equal(result["result"], sample_dataframe)
    assert result["metadata"]["path"] == test_file
    assert result["error"] is None


def test_read_dataframe_excel_default_sheet(test_dir, sample_dataframe):
    """Test read_dataframe_excel reads default sheet correctly."""
    test_file = os.path.join(test_dir, "default.xlsx")
    
    # Write file with default sheet name
    write_result = write_dataframe_excel(path=test_file, dataframe=sample_dataframe)
    assert write_result["success"] is True
    
    # Read file without specifying sheet (should read first sheet)
    result = read_dataframe_excel(path=test_file)
    
    assert result["success"] is True
    # When sheet_name is None, pd.read_excel returns a dict of all sheets
    # Extract the first (and only) sheet
    if isinstance(result["result"], dict):
        dataframe = list(result["result"].values())[0]
    else:
        dataframe = result["result"]
    pd.testing.assert_frame_equal(dataframe, sample_dataframe)



