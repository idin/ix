"""
File system tools for reading text files.
"""

from typing import Dict, Any

from ...constants import SUCCESS_KEY, ERROR_KEY, RESULT_KEY, METADATA_KEY
from ..constants import PATH_KEY

# Import the simple utility function from ixutils
from ixutils.file_system.read import read_text_file as _read_text_file


def read_text_file(
    path: str,
    encoding: str = "utf-8",
) -> Dict[str, Any]:
    """
    Read text content from a file.
    
    Tool format wrapper around ixutils.file_system.read.read_text_file.
    
    Args:
        path: Path to the file to read.
        encoding: Text encoding to use (default: "utf-8").
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - result: Text content of the file (str) if successful, None otherwise.
            - metadata: Dictionary with:
                - path: Path to the file that was read.
            - error: Error message if operation failed (None if successful).
    """
    try:
        # Call the simple utility function from ixutils
        content = _read_text_file(path=path, encoding=encoding)
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: content,  # Just the file data - what the user needs
            METADATA_KEY: {
                PATH_KEY: path,
            },
            ERROR_KEY: None,
        }
    except FileNotFoundError as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: str(e),
        }
    except IsADirectoryError as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: str(e),
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

