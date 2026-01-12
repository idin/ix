"""
File system tools for writing serialized Python objects.
"""

from typing import Dict, Any, Optional, Literal, TYPE_CHECKING
import os
import pickle

from ...constants import SUCCESS_KEY, ERROR_KEY, RESULT_KEY, METADATA_KEY
from ..constants import PATH_KEY
from ixutils.file_system import path_exists
from ..memory import Action
from ..delete import delete

if TYPE_CHECKING:
    from ..memory import FileSystemMemory


def write_pickle(
    path: str,
    obj: Any,
    mode: Literal["x", "w"] = "x",
    file_system_memory: Optional["FileSystemMemory"] = None,
) -> Dict[str, Any]:
    """
    Write a Python object to a pickle file.
    
    Args:
        path: Path where the pickle file should be written.
        obj: Python object to serialize and write.
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
        
        # Write pickle file
        with open(path, "wb") as f:
            pickle.dump(obj, f)
        
        # Track action in memory if provided
        if file_system_memory is not None:
            try:
                undo_action = Action(
                    function_name="delete",
                    function=delete,
                    arguments={"paths": path},
                )
                
                action = Action(
                    function_name="write_pickle",
                    function=write_pickle,
                    arguments={
                        "path": path,
                        "obj": obj,
                        "mode": mode,
                    },
                )
                file_system_memory.add_action(action=action, undo_action=undo_action)
            except Exception:
                pass
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: obj,  # Just the written object - what the user needs
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
            ERROR_KEY: f"Error writing pickle file: {str(e)}",
        }

