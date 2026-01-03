"""
File system tools for reading pandas DataFrame files.
"""

from typing import Dict, Any, Optional
import os

from ...constants import SUCCESS_KEY, ERROR_KEY, RESULT_KEY, METADATA_KEY
from ..constants import PATH_KEY
from ..path_utils import path_exists


def read_dataframe_csv(
    path: str,
    encoding: str = "utf-8",
) -> Dict[str, Any]:
    """
    Read a pandas DataFrame from a CSV file.
    
    Args:
        path: Path to the CSV file to read.
        encoding: Text encoding to use (default: "utf-8").
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - data: pandas DataFrame if successful, None otherwise.
            - path: Path to the file that was read.
            - error: Error message if operation failed (None if successful).
    """
    try:
        # Try to import pandas
        try:
            import pandas as pd
        except ImportError:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: "pandas is required for DataFrame operations. Install it with: pip install pandas",
            }
        
        # Check if file exists
        if not path_exists(path):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"File does not exist: {path}",
            }
        
        # Check if it's a file (not a directory)
        if not os.path.isfile(path):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Path is not a file: {path}",
            }
        
        # Read DataFrame from CSV
        dataframe = pd.read_csv(path, encoding=encoding)
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: dataframe,  # Just the file data - what the user needs
            METADATA_KEY: {
                PATH_KEY: path,
            },
            ERROR_KEY: None,
        }
    except UnicodeDecodeError as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Encoding error: {str(e)}. Try a different encoding.",
        }
    except PermissionError as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Permission denied: {str(e)}",
        }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error reading DataFrame from CSV: {str(e)}",
        }


def read_dataframe_parquet(
    path: str,
) -> Dict[str, Any]:
    """
    Read a pandas DataFrame from a Parquet file.
    
    Parquet is a columnar storage format that is more efficient than CSV for large datasets.
    
    Args:
        path: Path to the Parquet file to read.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - data: pandas DataFrame if successful, None otherwise.
            - path: Path to the file that was read.
            - error: Error message if operation failed (None if successful).
    """
    try:
        # Try to import pandas and pyarrow
        try:
            import pandas as pd
            import pyarrow
        except ImportError:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: "pandas and pyarrow are required for Parquet support. Install with: pip install pandas pyarrow",
            }
        
        # Check if file exists
        if not path_exists(path):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"File does not exist: {path}",
            }
        
        # Check if it's a file (not a directory)
        if not os.path.isfile(path):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Path is not a file: {path}",
            }
        
        # Read DataFrame from Parquet
        dataframe = pd.read_parquet(path)
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: dataframe,  # Just the file data - what the user needs
            METADATA_KEY: {
                PATH_KEY: path,
            },
            ERROR_KEY: None,
        }
    except PermissionError as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Permission denied: {str(e)}",
        }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error reading DataFrame from Parquet: {str(e)}",
        }


def read_dataframe_excel(
    path: str,
    sheet_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Read a pandas DataFrame from an Excel file.
    
    Args:
        path: Path to the Excel file to read.
        sheet_name: Name of the Excel sheet to read. If None, reads the first sheet.
            Default: None.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - data: pandas DataFrame if successful, None otherwise.
            - path: Path to the file that was read.
            - error: Error message if operation failed (None if successful).
    """
    try:
        # Try to import pandas and openpyxl
        try:
            import pandas as pd
            import openpyxl
        except ImportError:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: "pandas and openpyxl are required for Excel support. Install with: pip install pandas openpyxl",
            }
        
        # Check if file exists
        if not path_exists(path):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"File does not exist: {path}",
            }
        
        # Check if it's a file (not a directory)
        if not os.path.isfile(path):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Path is not a file: {path}",
            }
        
        # Read DataFrame from Excel
        dataframe = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: dataframe,  # Just the file data - what the user needs
            METADATA_KEY: {
                PATH_KEY: path,
            },
            ERROR_KEY: None,
        }
    except PermissionError as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Permission denied: {str(e)}",
        }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error reading DataFrame from Excel: {str(e)}",
        }

