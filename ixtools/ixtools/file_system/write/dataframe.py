"""
File system tools for writing pandas DataFrame files.
"""

from typing import Dict, Any, Optional, Literal, TYPE_CHECKING
import os
import pandas as pd
import pyarrow
import openpyxl

from ...constants import SUCCESS_KEY, ERROR_KEY, RESULT_KEY, METADATA_KEY
from ..constants import PATH_KEY
from ixutils.file_system import path_exists
from ..memory import Action
from ..delete import delete

if TYPE_CHECKING:
    from ..memory import FileSystemMemory


def write_dataframe_csv(
    path: str,
    dataframe: Any,
    mode: Literal["x", "w"] = "x",
    encoding: str = "utf-8",
    file_system_memory: Optional["FileSystemMemory"] = None,
) -> Dict[str, Any]:
    """
    Write a pandas DataFrame to a CSV file.
    
    Args:
        path: Path where the CSV file should be written.
        dataframe: pandas DataFrame to write.
        mode: File write mode:
            - "x" (default): Exclusive create - fails if file exists
            - "w": Overwrite - creates or overwrites existing file
        encoding: Text encoding to use (default: "utf-8").
        file_system_memory: Optional FileSystemMemory instance to track actions.
            Default: None.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - path: Path where the file was written.
            - error: Error message if operation failed (None if successful).
    """
    try:
        # Validate that dataframe is a DataFrame
        if not isinstance(dataframe, pd.DataFrame):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: "dataframe must be a pandas DataFrame.",
            }
        
        # Validate mode
        if mode not in ("x", "w"):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Invalid mode '{mode}'. Must be 'x' (exclusive create) or 'w' (overwrite).",
            }
        
        # Check if file exists (for mode "x")
        if mode == "x" and path_exists(path):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"File already exists: {path}. Overwrite is not allowed with mode 'x'.",
            }
        
        # Create parent directory if it doesn't exist
        parent_dir = os.path.dirname(path)
        if parent_dir and not path_exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        
        # Write DataFrame to CSV
        dataframe.to_csv(path, index=False, encoding=encoding)
        
        # Track action in memory if provided
        if file_system_memory is not None:
            try:
                undo_action = Action(
                    function_name="delete",
                    function=delete,
                    arguments={"paths": path},
                )
                
                action = Action(
                    function_name="write_dataframe_csv",
                    function=write_dataframe_csv,
                    arguments={
                        "path": path,
                        "dataframe": dataframe,
                        "mode": mode,
                        "encoding": encoding,
                    },
                )
                file_system_memory.add_action(action=action, undo_action=undo_action)
            except Exception:
                pass
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: dataframe,  # Just the written DataFrame - what the user needs
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
            ERROR_KEY: f"Error writing DataFrame to CSV: {str(e)}",
        }


def write_dataframe_parquet(
    path: str,
    dataframe: Any,
    mode: Literal["x", "w"] = "x",
    file_system_memory: Optional["FileSystemMemory"] = None,
) -> Dict[str, Any]:
    """
    Write a pandas DataFrame to a Parquet file.
    
    Parquet is a columnar storage format that is more efficient than CSV for large datasets.
    
    Args:
        path: Path where the Parquet file should be written.
        dataframe: pandas DataFrame to write.
        mode: File write mode:
            - "x" (default): Exclusive create - fails if file exists
            - "w": Overwrite - creates or overwrites existing file
        file_system_memory: Optional FileSystemMemory instance to track actions.
            Default: None.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - path: Path where the file was written.
            - error: Error message if operation failed (None if successful).
    """
    try:
        # Validate that dataframe is a DataFrame
        if not isinstance(dataframe, pd.DataFrame):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: "dataframe must be a pandas DataFrame.",
            }
        
        # Validate mode
        if mode not in ("x", "w"):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Invalid mode '{mode}'. Must be 'x' (exclusive create) or 'w' (overwrite).",
            }
        
        # Check if file exists (for mode "x")
        if mode == "x" and path_exists(path):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"File already exists: {path}. Overwrite is not allowed with mode 'x'.",
            }
        
        # Create parent directory if it doesn't exist
        parent_dir = os.path.dirname(path)
        if parent_dir and not path_exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        
        # Write DataFrame to Parquet
        dataframe.to_parquet(path, index=False)
        
        # Track action in memory if provided
        if file_system_memory is not None:
            try:
                undo_action = Action(
                    function_name="delete",
                    function=delete,
                    arguments={"paths": path},
                )
                
                action = Action(
                    function_name="write_dataframe_parquet",
                    function=write_dataframe_parquet,
                    arguments={
                        "path": path,
                        "dataframe": dataframe,
                        "mode": mode,
                    },
                )
                file_system_memory.add_action(action=action, undo_action=undo_action)
            except Exception:
                pass
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: dataframe,  # Just the written DataFrame - what the user needs
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
            ERROR_KEY: f"Error writing DataFrame to Parquet: {str(e)}",
        }


def write_dataframe_excel(
    path: str,
    dataframe: Any,
    mode: Literal["x", "w"] = "x",
    sheet_name: str = "Sheet1",
    file_system_memory: Optional["FileSystemMemory"] = None,
) -> Dict[str, Any]:
    """
    Write a pandas DataFrame to an Excel file.
    
    Args:
        path: Path where the Excel file should be written.
        dataframe: pandas DataFrame to write.
        mode: File write mode:
            - "x" (default): Exclusive create - fails if file exists
            - "w": Overwrite - creates or overwrites existing file
        sheet_name: Name of the Excel sheet (default: "Sheet1").
        file_system_memory: Optional FileSystemMemory instance to track actions.
            Default: None.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - path: Path where the file was written.
            - error: Error message if operation failed (None if successful).
    """
    try:
        # Validate that dataframe is a DataFrame
        if not isinstance(dataframe, pd.DataFrame):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: "dataframe must be a pandas DataFrame.",
            }
        
        # Validate mode
        if mode not in ("x", "w"):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Invalid mode '{mode}'. Must be 'x' (exclusive create) or 'w' (overwrite).",
            }
        
        # Check if file exists (for mode "x")
        if mode == "x" and path_exists(path):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"File already exists: {path}. Overwrite is not allowed with mode 'x'.",
            }
        
        # Create parent directory if it doesn't exist
        parent_dir = os.path.dirname(path)
        if parent_dir and not path_exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        
        # Write DataFrame to Excel
        dataframe.to_excel(path, index=False, sheet_name=sheet_name, engine="openpyxl")
        
        # Track action in memory if provided
        if file_system_memory is not None:
            undo_action = Action(
                function_name="delete",
                function=delete,
                arguments={"paths": path},
            )
            
            action = Action(
                function_name="write_dataframe_excel",
                function=write_dataframe_excel,
                arguments={
                    "path": path,
                    "dataframe": dataframe,
                    "mode": mode,
                    "sheet_name": sheet_name,
                },
            )
            file_system_memory.add_action(action=action, undo_action=undo_action)
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: dataframe,  # Just the written DataFrame - what the user needs
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
            ERROR_KEY: f"Error writing DataFrame to Excel: {str(e)}",
        }

