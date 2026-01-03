"""
File system tools for writing text files.
"""

from typing import Dict, Any, Optional, Literal, TYPE_CHECKING
import os

from ...constants import SUCCESS_KEY, ERROR_KEY, RESULT_KEY, METADATA_KEY
from ..constants import PATH_KEY
from ..path_utils import path_exists
from ..memory import Action
from ..delete import delete

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
            - path: Path where the file was written.
            - error: Error message if operation failed (None if successful).
    """
    try:
        # Validate mode
        if mode not in ("x", "w", "a"):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Invalid mode '{mode}'. Must be 'x' (exclusive create), 'w' (overwrite), or 'a' (append).",
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
        
        # Store original content for undo (only for overwrite mode)
        original_content = None
        if mode == "w" and path_exists(path):
            try:
                with open(path, "r", encoding=encoding) as f:
                    original_content = f.read()
            except Exception:
                # If we can't read original, we'll just delete on undo
                original_content = None
        
        # Write the file
        with open(path, mode, encoding=encoding) as f:
            f.write(content)
        
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

