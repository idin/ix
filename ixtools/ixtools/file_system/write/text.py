"""
File system tools for writing text files.
"""

from typing import Dict, Any, Optional, Literal, TYPE_CHECKING
import os

from ...constants import SUCCESS_KEY, ERROR_KEY, RESULT_KEY, METADATA_KEY
from ..constants import PATH_KEY
from ixutils.file_system import path_exists
from ..memory import Action
from ..delete import delete

# Import the simple utility function from ixutils
from ixutils.file_system.write import write_text_file as _write_text_file

if TYPE_CHECKING:
    from ..memory import FileSystemMemory


def write_text_file(
    path: str,
    content: str,
    mode: Literal["x", "w", "a"] = "x",  # Runtime validation still needed for dynamic calls
    encoding: str = "utf-8",
    file_system_memory: Optional["FileSystemMemory"] = None,
) -> Dict[str, Any]:
    """
    Write text content to a file.
    
    Tool format wrapper around ixutils.file_system.write.write_text_file
    with optional file system memory tracking.
    
    Args:
        path: Path where the file should be written.
        content: Text content to write to the file.
        mode: File write mode:
            - "x" (default): Exclusive create - fails if file exists
            - "w": Overwrite - creates or overwrites existing file
            - "a": Append - appends to existing file or creates if doesn't exist
        encoding: Text encoding to use (default: "utf-8").
        file_system_memory: Optional FileSystemMemory instance to track actions.
            Default: None.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - result: Written content (str) if successful, None otherwise.
            - metadata: Dictionary with:
                - path: Path where the file was written.
            - error: Error message if operation failed (None if successful).
    """
    try:
        # Store original content for undo (only for overwrite mode)
        original_content = None
        if mode == "w" and path_exists(path):
            try:
                with open(path, "r", encoding=encoding) as f:
                    original_content = f.read()
            except Exception:
                # If we can't read original, we'll just delete on undo
                original_content = None
        
        # Call the simple utility function from ixutils
        _write_text_file(path=path, content=content, mode=mode, encoding=encoding)
        
        # Track action in memory if provided (only after operation succeeds)
        if file_system_memory is not None:
            try:
                # For mode "x" and "w", undo is delete_file
                # For mode "a", undo would need to restore original content (complex, so we'll just delete)
                if mode in ("x", "w"):
                    undo_action = Action(
                    function_name="delete",
                    function=delete,
                    arguments={"paths": path},
                    )
                else:  # mode "a"
                    # For append, we delete the file (simple undo)
                    undo_action = Action(
                    function_name="delete",
                    function=delete,
                    arguments={"paths": path},
                    )
                
                action = Action(
                    function_name="write_text_file",
                    function=write_text_file,
                    arguments={
                        "path": path,
                        "content": content,
                        "mode": mode,
                        "encoding": encoding,
                    },
                )
                file_system_memory.add_action(action=action, undo_action=undo_action)
            except Exception:
                # If memory tracking fails, don't affect the operation result
                pass
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: content,  # Just the written content - what the user needs
            METADATA_KEY: {
                PATH_KEY: path,
            },
            ERROR_KEY: None,
        }
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
            ERROR_KEY: f"Error writing file: {str(e)}",
        }

