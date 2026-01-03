"""
File system tools for copying and moving files and directories.
"""

# Main API functions (handle both files and directories, accept single item or list)
from .change_path import change_path
from .copy_into import copy_into
from .move_into import move_into
from .clone_to_path import clone_to_path

__all__ = [
    "change_path",
    "copy_into",
    "move_into",
    "clone_to_path",
]

