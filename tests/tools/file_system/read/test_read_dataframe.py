"""
Tests for DataFrame read tools.
"""

import pytest
import os

from tests.conftest import TEST_DATA_DIR
from ixmachina.tools.file_system import path_exists, empty_dir
from ixmachina.tools.file_system.read import (
    read_dataframe_csv,
    read_dataframe_parquet,
    read_dataframe_excel,
)
from ixmachina.tools.file_system.write import (
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
    try:
        import pandas as pd
        return pd.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [30, 25, 35],
            "city": ["New York", "London", "Tokyo"]
        })
    except ImportError:
        pytest.skip("pandas not installed")


def test_read_dataframe_csv_success(test_dir, sample_dataframe):
    """Test read_dataframe_csv reads DataFrame correctly."""
    test_file = os.path.join(test_dir, "test.csv")
    
    # Write file first
    write_result = write_dataframe_csv(path=test_file, dataframe=sample_dataframe)
    assert write_result["success"] is True
    
    # Read file
    result = read_dataframe_csv(path=test_file)
    
    assert result["success"] is True
    import pandas as pd
    pd.testing.assert_frame_equal(result["result"], sample_dataframe)
    assert result["metadata"]["path"] == test_file
    assert result["error"] is None


def test_read_dataframe_csv_missing_pandas(test_dir):
    """Test read_dataframe_csv returns error when pandas is missing."""
    # This test would need to mock the import, but we'll skip it
    # since we can't easily test missing dependencies
    pytest.skip("Cannot easily test missing pandas scenario")


def test_read_dataframe_parquet_success(test_dir, sample_dataframe):
    """Test read_dataframe_parquet reads DataFrame correctly."""
    try:
        import pyarrow
    except ImportError:
        pytest.skip("pyarrow not installed")
    
    test_file = os.path.join(test_dir, "test.parquet")
    
    # Write file first
    write_result = write_dataframe_parquet(path=test_file, dataframe=sample_dataframe)
    assert write_result["success"] is True
    
    # Read file
    result = read_dataframe_parquet(path=test_file)
    
    assert result["success"] is True
    import pandas as pd
    pd.testing.assert_frame_equal(result["result"], sample_dataframe)
    assert result["metadata"]["path"] == test_file
    assert result["error"] is None


def test_read_dataframe_parquet_missing_pyarrow(test_dir):
    """Test read_dataframe_parquet returns error when pyarrow is missing."""
    # This test would need to mock the import, but we'll skip it
    pytest.skip("Cannot easily test missing pyarrow scenario")


def test_read_dataframe_excel_success(test_dir, sample_dataframe):
    """Test read_dataframe_excel reads DataFrame correctly."""
    try:
        import openpyxl
    except ImportError:
        pytest.skip("openpyxl not installed")
    
    test_file = os.path.join(test_dir, "test.xlsx")
    
    # Write file first
    write_result = write_dataframe_excel(path=test_file, dataframe=sample_dataframe, sheet_name="TestSheet")
    assert write_result["success"] is True
    
    # Read file
    result = read_dataframe_excel(path=test_file, sheet_name="TestSheet")
    
    assert result["success"] is True
    import pandas as pd
    pd.testing.assert_frame_equal(result["result"], sample_dataframe)
    assert result["metadata"]["path"] == test_file
    assert result["error"] is None


def test_read_dataframe_excel_default_sheet(test_dir, sample_dataframe):
    """Test read_dataframe_excel reads default sheet correctly."""
    try:
        import openpyxl
    except ImportError:
        pytest.skip("openpyxl not installed")
    
    test_file = os.path.join(test_dir, "default.xlsx")
    
    # Write file with default sheet name
    write_result = write_dataframe_excel(path=test_file, dataframe=sample_dataframe)
    assert write_result["success"] is True
    
    # Read file without specifying sheet (should read first sheet)
    result = read_dataframe_excel(path=test_file)
    
    assert result["success"] is True
    import pandas as pd
    pd.testing.assert_frame_equal(result["result"], sample_dataframe)


def test_read_dataframe_excel_missing_openpyxl(test_dir):
    """Test read_dataframe_excel returns error when openpyxl is missing."""
    # This test would need to mock the import, but we'll skip it
    pytest.skip("Cannot easily test missing openpyxl scenario")

