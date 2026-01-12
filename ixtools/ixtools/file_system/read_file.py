"""
Unified read function for all file formats.
"""

from typing import Dict, Any, Optional, Literal
import os

from ..constants import SUCCESS_KEY, ERROR_KEY, RESULT_KEY, METADATA_KEY
from .constants import PATH_KEY
from ixutils.file_system import path_exists
from ixutils.file_system.read import read_text_file as _read_text_file


def read_file(
    path: str,
    format: Optional[Literal["text", "csv", "json", "yaml", "pickle", "parquet", "excel"]] = None,
    encoding: str = "utf-8",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Read data from a file in various formats.
    
    Automatically detects format from file extension if format is not specified.
    Supports: text, csv, json, yaml, pickle, parquet, excel (xlsx).
    
    Args:
        path: Path to the file to read.
        format: File format. If None, detected from file extension.
            Options: "text", "csv", "json", "yaml", "pickle", "parquet", "excel"
        encoding: Text encoding to use (default: "utf-8"). Only used for text-based formats.
        **kwargs: Additional format-specific arguments:
            - For Excel: sheet_name (default: None, reads first sheet)
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - data: Read data (type depends on format) if successful, None otherwise.
            - path: Path to the file that was read.
            - error: Error message if operation failed (None if successful).
    """
    # Check if file exists
    if not path_exists(path):
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"File does not exist: {path}",
        }
    
    # Detect format from extension if not provided
    if format is None:
        ext = os.path.splitext(path)[1].lower()
        format_map = {
            ".txt": "text",
            ".md": "text",
            ".csv": "csv",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".pkl": "pickle",
            ".pickle": "pickle",
            ".parquet": "parquet",
            ".xlsx": "excel",
            ".xls": "excel",
        }
        format = format_map.get(ext, "text")  # Default to text if unknown extension
    
    # Route to appropriate read function
    if format == "text":
        return _read_text(path, encoding)
    elif format == "csv":
        # Check if we should read as DataFrame or list of dicts
        # For now, default to list of dicts (CSV format)
        # User can use read_dataframe_csv directly if they want DataFrame
        return _read_csv(path, encoding)
    elif format == "json":
        return _read_json(path, encoding)
    elif format == "yaml":
        return _read_yaml(path, encoding)
    elif format == "pickle":
        return _read_pickle(path)
    elif format == "parquet":
        return _read_dataframe_parquet(path)
    elif format == "excel":
        sheet_name = kwargs.get("sheet_name", None)
        return _read_dataframe_excel(path, sheet_name)
    else:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Unsupported format: {format}. Supported formats: text, csv, json, yaml, pickle, parquet, excel",
        }


def _read_text(
    path: str,
    encoding: str,
) -> Dict[str, Any]:
    """Internal function to read text files."""
    # Use ixutils read_text_file and wrap in tool format
    
    
    try:
        content = _read_text_file(path=path, encoding=encoding)
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: content,
            METADATA_KEY: {
                PATH_KEY: path,
            },
            ERROR_KEY: None,
        }
    except FileNotFoundError as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"File does not exist: {path}",
        }
    except IsADirectoryError as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Path is a directory, not a file: {path}",
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
            ERROR_KEY: f"Error reading file: {str(e)}",
        }


def _read_csv(
    path: str,
    encoding: str,
) -> Dict[str, Any]:
    """Internal function to read CSV files."""
    # Lazy import to avoid circular dependencies
    from .read.structured import read_csv
    return read_csv(path, encoding)


def _read_json(
    path: str,
    encoding: str,
) -> Dict[str, Any]:
    """Internal function to read JSON files."""
    # Lazy import to avoid circular dependencies
    from .read.structured import read_json
    return read_json(path, encoding)


def _read_yaml(
    path: str,
    encoding: str,
) -> Dict[str, Any]:
    """Internal function to read YAML files."""
    # Lazy import to avoid circular dependencies
    from .read.structured import read_yaml
    return read_yaml(path, encoding)


def _read_pickle(
    path: str,
) -> Dict[str, Any]:
    """Internal function to read pickle files."""
    # Lazy import to avoid circular dependencies
    from .read.serialization import read_pickle
    return read_pickle(path)


def _read_dataframe_csv(
    path: str,
    encoding: str,
) -> Dict[str, Any]:
    """Internal function to read DataFrame from CSV."""
    # Lazy import to avoid circular dependencies
    from .read.dataframe import read_dataframe_csv
    return read_dataframe_csv(path, encoding)


def _read_dataframe_parquet(
    path: str,
) -> Dict[str, Any]:
    """Internal function to read Parquet files."""
    # Lazy import to avoid circular dependencies
    from .read.dataframe import read_dataframe_parquet
    return read_dataframe_parquet(path)


def _read_dataframe_excel(
    path: str,
    sheet_name: Optional[str],
) -> Dict[str, Any]:
    """Internal function to read Excel files."""
    # Lazy import to avoid circular dependencies
    from .read.dataframe import read_dataframe_excel
    return read_dataframe_excel(path, sheet_name)

