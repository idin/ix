"""
Path utility tools for file system operations.

These are AI agent tools that wrap ixutils.file_system functions
and return standard tool format responses.
"""

from typing import Dict, Any

from ixutils.file_system import path_exists as _path_exists, path_is_dir as _path_is_dir, path_is_file as _path_is_file

from ..constants import SUCCESS_KEY, RESULT_KEY, ERROR_KEY


def path_exists(path: str) -> Dict[str, Any]:
    """
    Check if a path exists.
    
    Args:
        path: Path to check.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - result: Boolean indicating if the path exists.
            - error: Error message if operation failed (None if successful).
    """
    try:
        exists = _path_exists(path)
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: exists,
            ERROR_KEY: None,
        }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error checking if path exists: {str(e)}",
        }


def path_is_dir(path: str) -> Dict[str, Any]:
    """
    Check if a path is a directory.
    
    Args:
        path: Path to check.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - result: Boolean indicating if the path exists and is a directory.
            - error: Error message if operation failed (None if successful).
    """
    try:
        is_dir = _path_is_dir(path)
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: is_dir,
            ERROR_KEY: None,
        }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error checking if path is directory: {str(e)}",
        }


def path_is_file(path: str) -> Dict[str, Any]:
    """
    Check if a path is a file.
    
    Args:
        path: Path to check.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - result: Boolean indicating if the path exists and is a file.
            - error: Error message if operation failed (None if successful).
    """
    try:
        is_file = _path_is_file(path)
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: is_file,
            ERROR_KEY: None,
        }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error checking if path is file: {str(e)}",
        }
