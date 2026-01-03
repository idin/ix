"""
File system tools for reading serialized Python objects.
"""

from typing import Dict, Any, Optional
import os
import pickle

from ...constants import SUCCESS_KEY, ERROR_KEY, RESULT_KEY, METADATA_KEY
from ..constants import PATH_KEY
from ..path_utils import path_exists


def read_pickle(
    path: str,
) -> Dict[str, Any]:
    """
    Read a Python object from a pickle file.
    
    Args:
        path: Path to the pickle file to read.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - data: Deserialized Python object if successful, None otherwise.
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
        
        # Read pickle file
        with open(path, "rb") as f:
            obj = pickle.load(f)
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: obj,  # Just the file data - what the user needs
            METADATA_KEY: {
                PATH_KEY: path,
            },
            ERROR_KEY: None,
        }
    except pickle.UnpicklingError as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Invalid pickle file: {str(e)}",
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
            ERROR_KEY: f"Error reading pickle file: {str(e)}",
        }

