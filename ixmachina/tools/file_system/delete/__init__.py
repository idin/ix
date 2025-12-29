"""
File system tools for deleting files and directories.
"""

from .delete_file import delete_file
from .delete_dir import delete_dir
from .empty_dir import empty_dir
from .empty_recycle_bin import empty_recycle_bin
from .recycle_bin import (
    get_recycle_bin_path,
    get_recycle_bin_index_path,
    ensure_recycle_bin_exists,
    generate_hash_folder_name,
    create_metadata,
)
from .undelete import undelete

__all__ = [
    "delete_file",
    "delete_dir",
    "empty_dir",
    "empty_recycle_bin",
    "get_recycle_bin_path",
    "get_recycle_bin_index_path",
    "ensure_recycle_bin_exists",
    "generate_hash_folder_name",
    "create_metadata",
    "undelete",
]

