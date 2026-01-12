"""
File system utilities.
"""

from .trash import move_to_trash
from .path import path_exists, path_is_dir, path_is_file
from .read import read_text_file
from .write import write_text_file
from .list import list_dir

__all__ = [
    "move_to_trash",
    "path_exists",
    "path_is_dir",
    "path_is_file",
    "read_text_file",
    "write_text_file",
    "list_dir",
]
