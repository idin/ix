"""
File system utilities for listing directory contents.

Simple utility functions that return values directly (not tool format).
"""

from typing import List, Dict
import os

from .path import path_exists, path_is_dir


def list_dir(
    path: str,
    include_hidden: bool = False,
) -> List[Dict[str, str]]:
    """
    List the contents of a directory.

    Simple utility function that returns a list of items directly.
    Raises exceptions on error.

    Args:
        path: Path to the directory to list.
        include_hidden: If True, include hidden files and directories (starting with '.').
            Default: False.

    Returns:
        List of dictionaries, each containing:
            - name: Name of the item (file or directory).
            - type: Type of item ("file" or "directory").
            - path: Full path to the item.

    Raises:
        FileNotFoundError: If the directory does not exist.
        NotADirectoryError: If the path is not a directory.
        PermissionError: If permission is denied.
        OSError: For other file system errors.
    """
    if not path_exists(path):
        raise FileNotFoundError(f"Directory does not exist: {path}")

    if not path_is_dir(path):
        raise NotADirectoryError(f"Path is not a directory: {path}")

    items = []
    for item_name in os.listdir(path):
        # Skip hidden files if include_hidden is False
        if not include_hidden and item_name.startswith("."):
            continue

        item_path = os.path.join(path, item_name)
        item_type = "directory" if path_is_dir(item_path) else "file"

        items.append({
            "name": item_name,
            "type": item_type,
            "path": item_path,
        })

    # Sort items: directories first, then files, both alphabetically
    items.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))

    return items
