"""
File system tools for deleting files and directories.
"""

from .delete import delete
from .empty_dir import empty_dir
from .empty_recycle_bin import empty_recycle_bin
from .recycle_bin import (
    get_recycle_bin_path,
    get_recycle_bin_index_path,
    set_recycle_bin_path,
    ensure_recycle_bin_exists,
    generate_hash_folder_name,
    create_metadata,
)
from .undelete import undelete

# Backward compatibility aliases
def delete_file(path: str, file_system_memory=None):
    """Backward compatibility alias for delete()."""
    result = delete(paths=path, file_system_memory=file_system_memory)
    if result["success"]:
        # Extract single result
        single_result = result["results"][path]
        return {
            "success": single_result["success"],
            "file_path": single_result["path"],
            "recycle_bin_path": single_result.get("recycle_bin_path"),
            "error": single_result.get("error"),
        }
    return result["results"].get(path, result)

def delete_dir(path: str, file_system_memory=None):
    """Backward compatibility alias for delete()."""
    result = delete(paths=path, file_system_memory=file_system_memory)
    if result["success"]:
        # Extract single result
        single_result = result["results"][path]
        return {
            "success": single_result["success"],
            "dir_path": single_result["path"],
            "recycle_bin_path": single_result.get("recycle_bin_path"),
            "error": single_result.get("error"),
        }
    return result["results"].get(path, result)

def delete_files(paths, file_system_memory=None):
    """Backward compatibility alias for delete()."""
    return delete(paths=paths, file_system_memory=file_system_memory)

def delete_dirs(paths, file_system_memory=None):
    """Backward compatibility alias for delete()."""
    return delete(paths=paths, file_system_memory=file_system_memory)

__all__ = [
    "delete",
    "delete_file",
    "delete_dir",
    "delete_files",
    "delete_dirs",
    "empty_dir",
    "empty_recycle_bin",
    "get_recycle_bin_path",
    "get_recycle_bin_index_path",
    "set_recycle_bin_path",
    "ensure_recycle_bin_exists",
    "generate_hash_folder_name",
    "create_metadata",
    "undelete",
]

