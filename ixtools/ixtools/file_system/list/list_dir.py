"""
File system tools for listing directory contents.
"""

from typing import Dict, Any

from ...constants import SUCCESS_KEY, ERROR_KEY, RESULT_KEY

# Import the simple utility function from ixutils
from ixutils.file_system.list import list_dir as _list_dir


def list_dir(
    path: str,
    include_hidden: bool = False,
) -> Dict[str, Any]:
    """
    List the contents of a directory.

    Tool format wrapper around ixutils.file_system.list.list_dir.

    Args:
        path: Path to the directory to list.
        include_hidden: If True, include hidden files and directories (starting with '.').
            Default: False.

    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - result: List of dictionaries, each containing:
                - name: Name of the item (file or directory).
                - type: Type of item ("file" or "directory").
                - path: Full path to the item.
            - error: Error message if operation failed (None if successful).
    """
    try:
        # Call the simple utility function from ixutils
        items = _list_dir(path=path, include_hidden=include_hidden)
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: items,
            ERROR_KEY: None,
        }
    except FileNotFoundError as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: [],
            ERROR_KEY: str(e),
        }
    except NotADirectoryError as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: [],
            ERROR_KEY: str(e),
        }
    except PermissionError as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: [],
            ERROR_KEY: f"Permission denied: {str(e)}",
        }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: [],
            ERROR_KEY: f"Error listing directory: {str(e)}",
        }

