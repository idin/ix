"""
File system tools for reading text files.
"""

from typing import Dict, Any, Optional
import os

from ...constants import SUCCESS_KEY, ERROR_KEY, RESULT_KEY, METADATA_KEY
from ..constants import PATH_KEY
from ..path_utils import path_exists


def read_text_file(
    path: str,
    encoding: str = "utf-8",
) -> Dict[str, Any]:
    """
    Read text content from a file.
    
    Args:
        path: Path to the file to read.
        encoding: Text encoding to use (default: "utf-8").
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - data: Text content of the file (str) if successful, None otherwise.
            - path: Path to the file that was read.
            - error: Error message if operation failed (None if successful).
    """
    try:
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
        
        # Read the file
        with open(path, "r", encoding=encoding) as f:
            content = f.read()
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: content,  # Just the file data - what the user needs
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
            ERROR_KEY: f"Error reading file: {str(e)}",
        }

