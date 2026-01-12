"""
File system tools for writing structured data files (CSV, JSON, YAML).
"""

from typing import Dict, Any, Optional, List, Literal, TYPE_CHECKING
import json
import csv
import yaml

from ...constants import SUCCESS_KEY, ERROR_KEY, RESULT_KEY, METADATA_KEY
from ..constants import PATH_KEY
from ixutils.file_system import path_exists
from ixutils.file_system.write import write_text_file as _write_text_file
from ..memory import Action
from ..delete import delete

if TYPE_CHECKING:
    from ..memory import FileSystemMemory


def write_csv(
    path: str,
    data: List[Dict[str, Any]],
    mode: Literal["x", "w"] = "x",
    encoding: str = "utf-8",
    file_system_memory: Optional["FileSystemMemory"] = None,
) -> Dict[str, Any]:
    """
    Write data to a CSV file.
    
    Args:
        path: Path where the CSV file should be written.
        data: List of dictionaries to write as CSV rows.
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
        
        # Validate data
        if not isinstance(data, list):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: "Data must be a list of dictionaries.",
            }
        
        if len(data) == 0:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: "Data list is empty. Cannot write CSV with no rows.",
            }
        
        if not all(isinstance(row, dict) for row in data):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: "All items in data must be dictionaries.",
            }
        
        # Get fieldnames from first row
        fieldnames = list(data[0].keys())
        
        # Convert CSV data to string format
        from io import StringIO
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        csv_content = output.getvalue()
        
        # Write CSV file using ixutils
        try:
            _write_text_file(path=path, content=csv_content, mode=mode, encoding=encoding)
        except ValueError as e:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: str(e),
            }
        except FileExistsError as e:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: str(e),
            }
        except Exception as e:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Error writing CSV file: {str(e)}",
            }
        
        # Track action in memory if provided
        if file_system_memory is not None:
            try:
                undo_action = Action(
                    function_name="delete",
                    function=delete,
                    arguments={"paths": path},
                )
                
                action = Action(
                    function_name="write_csv",
                    function=write_csv,
                    arguments={
                        "path": path,
                        "data": data,
                        "mode": mode,
                        "encoding": encoding,
                    },
                )
                file_system_memory.add_action(action=action, undo_action=undo_action)
            except Exception:
                pass
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: data,  # Just the written data - what the user needs
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
            ERROR_KEY: f"Error writing CSV file: {str(e)}",
        }


def write_json(
    path: str,
    data: Any,
    mode: Literal["x", "w"] = "x",
    encoding: str = "utf-8",
    indent: int = 2,
    file_system_memory: Optional["FileSystemMemory"] = None,
) -> Dict[str, Any]:
    """
    Write data to a JSON file.
    
    Args:
        path: Path where the JSON file should be written.
        data: Data to write as JSON (must be JSON-serializable).
        mode: File write mode:
            - "x" (default): Exclusive create - fails if file exists
            - "w": Overwrite - creates or overwrites existing file
        encoding: Text encoding to use (default: "utf-8").
        indent: Number of spaces for indentation (default: 2).
        file_system_memory: Optional FileSystemMemory instance to track actions.
            Default: None.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - path: Path where the file was written.
            - error: Error message if operation failed (None if successful).
    """
    try:
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
        
        # Convert JSON data to string format
        json_content = json.dumps(data, indent=indent, ensure_ascii=False)
        
        # Write JSON file using ixutils
        try:
            _write_text_file(path=path, content=json_content, mode=mode, encoding=encoding)
        except ValueError as e:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: str(e),
            }
        except FileExistsError as e:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: str(e),
            }
        except Exception as e:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Error writing JSON file: {str(e)}",
            }
        
        # Track action in memory if provided
        if file_system_memory is not None:
            try:
                undo_action = Action(
                    function_name="delete",
                    function=delete,
                    arguments={"paths": path},
                )
                
                action = Action(
                    function_name="write_json",
                    function=write_json,
                    arguments={
                        "path": path,
                        "data": data,
                        "mode": mode,
                        "encoding": encoding,
                        "indent": indent,
                    },
                )
                file_system_memory.add_action(action=action, undo_action=undo_action)
            except Exception:
                pass
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: data,  # Just the written data - what the user needs
            METADATA_KEY: {
                PATH_KEY: path,
            },
            ERROR_KEY: None,
        }
    except (TypeError, ValueError) as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Data is not JSON-serializable: {str(e)}",
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
            ERROR_KEY: f"Error writing JSON file: {str(e)}",
        }


def write_yaml(
    path: str,
    data: Any,
    mode: Literal["x", "w"] = "x",
    encoding: str = "utf-8",
    file_system_memory: Optional["FileSystemMemory"] = None,
) -> Dict[str, Any]:
    """
    Write data to a YAML file.
    
    Args:
        path: Path where the YAML file should be written.
        data: Data to write as YAML.
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
        
        # Convert YAML data to string format
        yaml_content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
        
        # Write YAML file using ixutils
        try:
            _write_text_file(path=path, content=yaml_content, mode=mode, encoding=encoding)
        except ValueError as e:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: str(e),
            }
        except FileExistsError as e:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: str(e),
            }
        except Exception as e:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Error writing YAML file: {str(e)}",
            }
        
        # Track action in memory if provided
        if file_system_memory is not None:
            try:
                undo_action = Action(
                    function_name="delete",
                    function=delete,
                    arguments={"paths": path},
                )
                
                action = Action(
                    function_name="write_yaml",
                    function=write_yaml,
                    arguments={
                        "path": path,
                        "data": data,
                        "mode": mode,
                        "encoding": encoding,
                    },
                )
                file_system_memory.add_action(action=action, undo_action=undo_action)
            except Exception:
                pass
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: data,  # Just the written data - what the user needs
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
            ERROR_KEY: f"Error writing YAML file: {str(e)}",
        }

