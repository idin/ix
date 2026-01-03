"""
File system tools for emptying directories.
"""

from typing import Dict, Any, Optional, TYPE_CHECKING
import os

from ..path_utils import path_exists, path_is_dir
from ..list.list_dir_contents import list_dir_contents
from .delete import delete

if TYPE_CHECKING:
    from ..memory import FileSystemMemory


def empty_dir(
    path: str,
    file_system_memory: Optional["FileSystemMemory"] = None,
) -> Dict[str, Any]:
    """
    Delete all contents inside a directory by moving them to the recycle bin.

    This function uses delete_file and delete_dir to move all contents to the
    recycle bin. The directory itself remains empty after this operation.

    Args:
        path: Path to the directory to empty.
        file_system_memory: Optional FileSystemMemory instance to track actions.
            Default: None.

    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - dir_path: Path to the directory that was emptied.
            - deleted_items: List of paths that were deleted.
            - error: Error message if operation failed (None if successful).
    """
    try:
        if not path_exists(path):
            return {
                "success": False,
                "dir_path": path,
                "deleted_items": [],
                "error": f"Directory does not exist: {path}",
            }

        if not path_is_dir(path):
            return {
                "success": False,
                "dir_path": path,
                "deleted_items": [],
                "error": f"Path is not a directory: {path}",
            }

        # Get all items to delete using list_dir_contents (separates files and directories)
        list_result = list_dir_contents(path=path, include_hidden=True)
        if not list_result["success"]:
            return {
                "success": False,
                "dir_path": path,
                "deleted_items": [],
                "error": f"Error listing directory: {list_result['error']}",
            }

        deleted_items = []
        errors = []

        # Collect all paths to delete
        paths_to_delete = []
        for file_item in list_result["files"]:
            paths_to_delete.append(file_item["path"])
        for dir_item in list_result["directories"]:
            paths_to_delete.append(dir_item["path"])

        # Delete all items using the unified delete function
        if paths_to_delete:
            delete_result = delete(paths=paths_to_delete, file_system_memory=file_system_memory)
            deleted_items = delete_result["successful_paths"]
            for failed_path in delete_result["failed_paths"]:
                error_msg = delete_result["results"].get(failed_path, {}).get("error", "Unknown error")
                errors.append(f"{failed_path}: {error_msg}")

        if errors:
            return {
                "success": False,
                "dir_path": path,
                "deleted_items": deleted_items,
                "error": f"Some items could not be deleted: {'; '.join(errors)}",
            }

        return {
            "success": True,
            "dir_path": path,
            "deleted_items": deleted_items,
            "error": None,
        }
    except PermissionError as e:
        return {
            "success": False,
            "dir_path": path,
            "deleted_items": [],
            "error": f"Permission denied: {str(e)}",
        }
    except Exception as e:
        return {
            "success": False,
            "dir_path": path,
            "deleted_items": [],
            "error": f"Error emptying directory: {str(e)}",
        }

