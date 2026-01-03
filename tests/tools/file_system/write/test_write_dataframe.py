"""
Tests for DataFrame write tools.
"""

import pytest
import os

from tests.conftest import TEST_DATA_DIR
from ixmachina.tools.file_system import path_exists, empty_dir
from ixmachina.tools.file_system.write import (
    write_dataframe_csv,
    write_dataframe_parquet,
    write_dataframe_excel,
)


@pytest.fixture
def test_dir():
    """Create a clean test directory in .test_data."""
    test_dir = os.path.join(TEST_DATA_DIR, "write_tests", "dataframe")
    # Clean up any existing files
    if os.path.exists(test_dir):
        empty_dir(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    yield test_dir


@pytest.fixture
def sample_dataframe():
    """Create a sample pandas DataFrame."""
    try:
        import pandas as pd
        return pd.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [30, 25, 35],
            "city": ["New York", "London", "Tokyo"],
        })
    except ImportError:
        pytest.skip("pandas not installed")


def test_write_dataframe_csv_exclusive_create(test_dir, sample_dataframe):
    """Test write_dataframe_csv with exclusive create mode."""
    test_file = os.path.join(test_dir, "test.csv")
    
    result = write_dataframe_csv(path=test_file, dataframe=sample_dataframe)
    
    assert result["success"] is True
    assert result["metadata"]["path"] == test_file
    assert result["error"] is None
    assert path_exists(test_file)
    
    # Verify content
    import pandas as pd
    loaded_df = pd.read_csv(test_file)
    assert len(loaded_df) == 3
    assert list(loaded_df.columns) == ["name", "age", "city"]


def test_write_dataframe_csv_missing_pandas(test_dir):
    """Test write_dataframe_csv returns error if pandas is not installed."""
    test_file = os.path.join(test_dir, "test.csv")
    
    # Pass a non-DataFrame object
    result = write_dataframe_csv(path=test_file, dataframe="not a dataframe")
    
    assert result["success"] is False
    assert "pandas" in result["error"].lower() or "dataframe" in result["error"].lower()


def test_write_dataframe_parquet_exclusive_create(test_dir, sample_dataframe):
    """Test write_dataframe_parquet with exclusive create mode."""
    try:
        import pyarrow
    except ImportError:
        pytest.skip("pyarrow not installed")
    
    test_file = os.path.join(test_dir, "test.parquet")
    
    result = write_dataframe_parquet(path=test_file, dataframe=sample_dataframe)
    
    assert result["success"] is True
    assert result["metadata"]["path"] == test_file
    assert result["error"] is None
    assert path_exists(test_file)
    
    # Verify content
    import pandas as pd
    loaded_df = pd.read_parquet(test_file)
    assert len(loaded_df) == 3
    assert list(loaded_df.columns) == ["name", "age", "city"]


def test_write_dataframe_parquet_missing_pyarrow(test_dir, sample_dataframe):
    """Test write_dataframe_parquet returns error if pyarrow is not installed."""
    test_file = os.path.join(test_dir, "test.parquet")
    
    # Temporarily remove pyarrow module if it exists
    import sys
    pyarrow_backup = sys.modules.get("pyarrow")
    if "pyarrow" in sys.modules:
        del sys.modules["pyarrow"]
    
    try:
        result = write_dataframe_parquet(path=test_file, dataframe=sample_dataframe)
        assert result["success"] is False
        assert "pyarrow" in result["error"].lower()
    finally:
        # Restore pyarrow module if it was there
        if pyarrow_backup:
            sys.modules["pyarrow"] = pyarrow_backup


def test_write_dataframe_excel_exclusive_create(test_dir, sample_dataframe):
    """Test write_dataframe_excel with exclusive create mode."""
    try:
        import openpyxl
    except ImportError:
        pytest.skip("openpyxl not installed")
    
    test_file = os.path.join(test_dir, "test.xlsx")
    
    result = write_dataframe_excel(path=test_file, dataframe=sample_dataframe)
    
    assert result["success"] is True
    assert result["metadata"]["path"] == test_file
    assert result["error"] is None
    assert path_exists(test_file)
    
    # Verify content
    import pandas as pd
    loaded_df = pd.read_excel(test_file, engine="openpyxl")
    assert len(loaded_df) == 3
    assert list(loaded_df.columns) == ["name", "age", "city"]


def test_write_dataframe_excel_custom_sheet_name(test_dir, sample_dataframe):
    """Test write_dataframe_excel with custom sheet name."""
    try:
        import openpyxl
    except ImportError:
        pytest.skip("openpyxl not installed")
    
    test_file = os.path.join(test_dir, "test.xlsx")
    sheet_name = "MySheet"
    
    result = write_dataframe_excel(path=test_file, dataframe=sample_dataframe, sheet_name=sheet_name)
    
    assert result["success"] is True
    
    # Verify sheet name
    import openpyxl
    wb = openpyxl.load_workbook(test_file)
    assert sheet_name in wb.sheetnames


def test_write_dataframe_excel_missing_openpyxl(test_dir, sample_dataframe):
    """Test write_dataframe_excel returns error if openpyxl is not installed."""
    test_file = os.path.join(test_dir, "test.xlsx")
    
    # Temporarily remove openpyxl module if it exists
    import sys
    openpyxl_backup = sys.modules.get("openpyxl")
    if "openpyxl" in sys.modules:
        del sys.modules["openpyxl"]
    
    try:
        result = write_dataframe_excel(path=test_file, dataframe=sample_dataframe)
        assert result["success"] is False
        assert "openpyxl" in result["error"].lower()
    finally:
        # Restore openpyxl module if it was there
        if openpyxl_backup:
            sys.modules["openpyxl"] = openpyxl_backup

