"""
File system utilities for writing text files.

Simple utility functions that return values directly (not tool format).
"""

from typing import Literal
import os

from .path import path_exists


def write_text_file(
    path: str,
    content: str,
    mode: Literal["x", "w", "a"] = "x",
    encoding: str = "utf-8",
) -> None:
    """
    Write text content to a file.
    
    Simple utility function that writes the file directly.
    Raises exceptions on error.
    
    Args:
        path: Path where the file should be written.
        content: Text content to write to the file.
        mode: File write mode:
            - "x" (default): Exclusive create - fails if file exists
            - "w": Overwrite - creates or overwrites existing file
            - "a": Append - appends to existing file or creates if doesn't exist
        encoding: Text encoding to use (default: "utf-8").
    
    Returns:
        None (raises exception on error).
    
    Raises:
        ValueError: If mode is invalid.
        FileExistsError: If mode is "x" and file already exists.
        PermissionError: If permission is denied.
        OSError: For other file system errors.
    """
    # Validate mode
    if mode not in ("x", "w", "a"):
        raise ValueError(f"Invalid mode '{mode}'. Must be 'x' (exclusive create), 'w' (overwrite), or 'a' (append).")
    
    # Check if file exists (for mode "x")
    if mode == "x" and path_exists(path):
        raise FileExistsError(f"File already exists: {path}. Overwrite is not allowed with mode 'x'.")
    
    # Create parent directory if it doesn't exist
    parent_dir = os.path.dirname(path)
    if parent_dir and not path_exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)
    
    # Write the file
    with open(path, mode, encoding=encoding) as f:
        f.write(content)
