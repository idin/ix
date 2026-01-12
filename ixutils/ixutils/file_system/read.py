"""
File system utilities for reading text files.

Simple utility functions that return values directly (not tool format).
"""

import os

from .path import path_exists


def read_text_file(
    path: str,
    encoding: str = "utf-8",
) -> str:
    """
    Read text content from a file.
    
    Simple utility function that returns the file content directly.
    Raises exceptions on error.
    
    Args:
        path: Path to the file to read.
        encoding: Text encoding to use (default: "utf-8").
    
    Returns:
        Text content of the file as a string.
    
    Raises:
        FileNotFoundError: If the file does not exist.
        IsADirectoryError: If the path is a directory, not a file.
        UnicodeDecodeError: If the file cannot be decoded with the specified encoding.
        PermissionError: If permission is denied.
        OSError: For other file system errors.
    """
    # Check if file exists
    if not path_exists(path):
        raise FileNotFoundError(f"File does not exist: {path}")
    
    # Check if it's a file (not a directory)
    if not os.path.isfile(path):
        raise IsADirectoryError(f"Path is a directory, not a file: {path}")
    
    # Read the file
    with open(path, "r", encoding=encoding) as f:
        content = f.read()
    
    return content
