"""
Unified write function for all file formats.
"""

from typing import Dict, Any, Optional, List, Literal, TYPE_CHECKING
import os

if TYPE_CHECKING:
    from .memory import FileSystemMemory


# Dictionary mapping data types to allowed formats
FORMAT_BY_DATA_TYPE: Dict[str, List[str]] = {
    "str": ["text"],
    "list": ["csv", "json", "yaml", "pickle"],
    "dict": ["json", "yaml", "pickle"],
    "dataframe": ["csv", "parquet", "excel", "json", "pickle"],
    "any": ["pickle"],  # Pickle can handle any Python object
}

# Dictionary mapping formats to expected data types
DATA_TYPE_BY_FORMAT: Dict[str, List[str]] = {
    "text": ["str"],
    "csv": ["list", "dataframe"],
    "json": ["list", "dict", "dataframe", "any"],
    "yaml": ["list", "dict", "any"],
    "pickle": ["any"],
    "parquet": ["dataframe"],
    "excel": ["dataframe"],
}


def write_file(
    path: str,
    data: Any,
    format: Optional[Literal["text", "csv", "json", "yaml", "pickle", "parquet", "excel"]] = None,
    mode: Literal["x", "w", "a"] = "x",
    encoding: str = "utf-8",
    file_system_memory: Optional["FileSystemMemory"] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Write data to a file in various formats.
    
    Automatically detects format from file extension if format is not specified.
    Supports: text, csv, json, yaml, pickle, parquet, excel (xlsx).
    
    See FORMAT_BY_DATA_TYPE and DATA_TYPE_BY_FORMAT dictionaries for format compatibility.
    
    Args:
        path: Path where the file should be written.
        data: Data to write. Type depends on format:
            - text: str
            - csv: List[Dict[str, Any]] or pandas DataFrame
            - json: Any JSON-serializable object (dict, list, etc.)
            - yaml: Any YAML-serializable object (dict, list, etc.)
            - pickle: Any Python object
            - parquet/excel: pandas DataFrame
        format: File format. If None, detected from file extension.
            Options: "text", "csv", "json", "yaml", "pickle", "parquet", "excel"
        mode: File write mode:
            - "x" (default): Exclusive create - fails if file exists
            - "w": Overwrite - creates or overwrites existing file
            - "a": Append - only for text files
        encoding: Text encoding to use (default: "utf-8").
        file_system_memory: Optional FileSystemMemory instance to track actions.
            Default: None.
        **kwargs: Additional format-specific arguments:
            - For JSON: indent (default: 2)
            - For Excel: sheet_name (default: "Sheet1")
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - path: Path where the file was written.
            - error: Error message if operation failed (None if successful).
    """
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
    
    # Route to appropriate write function
    if format == "text":
        return _write_text(path, data, mode, encoding, file_system_memory)
    elif format == "csv":
        # Check if data is a DataFrame
        try:
            import pandas as pd
            if isinstance(data, pd.DataFrame):
                return _write_dataframe_csv(path, data, mode, encoding, file_system_memory)
        except ImportError:
            pass
        # Otherwise treat as list of dicts
        return _write_csv(path, data, mode, encoding, file_system_memory)
    elif format == "json":
        indent = kwargs.get("indent", 2)
        return _write_json(path, data, mode, encoding, indent, file_system_memory)
    elif format == "yaml":
        return _write_yaml(path, data, mode, encoding, file_system_memory)
    elif format == "pickle":
        return _write_pickle(path, data, mode, file_system_memory)
    elif format == "parquet":
        return _write_dataframe_parquet(path, data, mode, file_system_memory)
    elif format == "excel":
        sheet_name = kwargs.get("sheet_name", "Sheet1")
        return _write_dataframe_excel(path, data, mode, sheet_name, file_system_memory)
    else:
        return {
            "success": False,
            "path": path,
            "error": f"Unsupported format: {format}. Supported formats: text, csv, json, yaml, pickle, parquet, excel",
        }


def _write_text(
    path: str,
    content: str,
    mode: str,
    encoding: str,
    file_system_memory: Optional["FileSystemMemory"],
) -> Dict[str, Any]:
    """Internal function to write text files."""
    from .write.text import write_text_file
    return write_text_file(path, content, mode, encoding, file_system_memory)


def _write_csv(
    path: str,
    data: List[Dict[str, Any]],
    mode: str,
    encoding: str,
    file_system_memory: Optional["FileSystemMemory"],
) -> Dict[str, Any]:
    """Internal function to write CSV files."""
    from .write.structured import write_csv
    return write_csv(path, data, mode, encoding, file_system_memory)


def _write_json(
    path: str,
    data: Any,
    mode: str,
    encoding: str,
    indent: int,
    file_system_memory: Optional["FileSystemMemory"],
) -> Dict[str, Any]:
    """Internal function to write JSON files."""
    from .write.structured import write_json
    return write_json(path, data, mode, encoding, indent, file_system_memory)


def _write_yaml(
    path: str,
    data: Any,
    mode: str,
    encoding: str,
    file_system_memory: Optional["FileSystemMemory"],
) -> Dict[str, Any]:
    """Internal function to write YAML files."""
    from .write.structured import write_yaml
    return write_yaml(path, data, mode, encoding, file_system_memory)


def _write_pickle(
    path: str,
    obj: Any,
    mode: str,
    file_system_memory: Optional["FileSystemMemory"],
) -> Dict[str, Any]:
    """Internal function to write pickle files."""
    from .write.serialization import write_pickle
    return write_pickle(path, obj, mode, file_system_memory)


def _write_dataframe_csv(
    path: str,
    dataframe: Any,
    mode: str,
    encoding: str,
    file_system_memory: Optional["FileSystemMemory"],
) -> Dict[str, Any]:
    """Internal function to write DataFrame to CSV."""
    from .write.dataframe import write_dataframe_csv
    return write_dataframe_csv(path, dataframe, mode, encoding, file_system_memory)


def _write_dataframe_parquet(
    path: str,
    dataframe: Any,
    mode: str,
    file_system_memory: Optional["FileSystemMemory"],
) -> Dict[str, Any]:
    """Internal function to write Parquet files."""
    from .write.dataframe import write_dataframe_parquet
    return write_dataframe_parquet(path, dataframe, mode, file_system_memory)


def _write_dataframe_excel(
    path: str,
    dataframe: Any,
    mode: str,
    sheet_name: str,
    file_system_memory: Optional["FileSystemMemory"],
) -> Dict[str, Any]:
    """Internal function to write Excel files."""
    from .write.dataframe import write_dataframe_excel
    return write_dataframe_excel(path, dataframe, mode, sheet_name, file_system_memory)

