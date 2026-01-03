"""
File system tools for deleting files or directories.
"""

from typing import Dict, Any, Optional, List, Union, TYPE_CHECKING
import os
import shutil
from datetime import datetime

from ..path_utils import path_exists, path_is_file, path_is_dir
from ..memory import Action
from .recycle_bin import (
    ensure_recycle_bin_exists,
    generate_hash_folder_name,
    create_metadata,
    save_metadata,
    add_to_recycle_bin_index,
)

if TYPE_CHECKING:
    from ..memory import FileSystemMemory


def _delete_single_item(
    path: str,
    file_system_memory: Optional["FileSystemMemory"] = None,
) -> Dict[str, Any]:
    """
    Delete a single file or directory by moving it to the recycle bin.
    
    Internal helper function.
    """
    try:
        if not path_exists(path):
            return {
                "success": False,
                "path": path,
                "recycle_bin_path": None,
                "error": f"Path does not exist: {path}",
            }

        # Determine if it's a file or directory
        is_file = path_is_file(path)
        is_dir = path_is_dir(path)

        if not is_file and not is_dir:
            return {
                "success": False,
                "path": path,
                "recycle_bin_path": None,
                "error": f"Path is neither a file nor a directory: {path}",
            }

        item_type = "file" if is_file else "directory"

        # Ensure recycle bin exists
        recycle_bin = ensure_recycle_bin_exists()

        # Generate unique hash folder
        timestamp = datetime.now().isoformat()
        hash_folder_name = generate_hash_folder_name(path, timestamp)
        hash_folder = os.path.join(recycle_bin, hash_folder_name)
        os.makedirs(hash_folder, exist_ok=True)

        # Move item to recycle bin
        if is_file:
            item_name = os.path.basename(path)
        else:
            item_name = os.path.basename(path.rstrip(os.sep))
        
        recycle_bin_path = os.path.join(hash_folder, item_name)
        shutil.move(path, recycle_bin_path)

        # Save metadata
        metadata = create_metadata(
            original_path=path,
            recycle_bin_path=recycle_bin_path,
            item_type=item_type,
        )
        save_metadata(hash_folder, metadata)

        # Add to index for lookup
        add_to_recycle_bin_index(path, recycle_bin_path)

        # Track action in memory if provided
        if file_system_memory is not None:
            try:
                from .undelete import undelete

                undo_action = Action(
                    function_name="undelete",
                    function=undelete,
                    arguments={"recycle_bin_paths": recycle_bin_path},
                )

                action = Action(
                    function_name="delete",
                    function=delete,
                    arguments={"paths": path},
                )
                file_system_memory.add_action(action=action, undo_action=undo_action)
            except Exception:
                pass

        return {
            "success": True,
            "path": path,
            "recycle_bin_path": recycle_bin_path,
            "item_type": item_type,
            "error": None,
        }
    except PermissionError as e:
        return {
            "success": False,
            "path": path,
            "recycle_bin_path": None,
            "error": f"Permission denied: {str(e)}",
        }
    except Exception as e:
        return {
            "success": False,
            "path": path,
            "recycle_bin_path": None,
            "error": f"Error deleting item: {str(e)}",
        }


def delete(
    paths: Union[str, List[str]],
    file_system_memory: Optional["FileSystemMemory"] = None,
) -> Dict[str, Any]:
    """
    Delete files or directories by moving them to the recycle bin.

    Automatically detects whether each path is a file or directory and uses
    the appropriate operation. Each item will be moved to the recycle bin
    where it can be recovered later.

    Args:
        paths: A single path (string) or list of paths to delete.
        file_system_memory: Optional FileSystemMemory instance to track actions.
            Default: None.

    Returns:
        Dictionary with:
            - success: Boolean indicating if the overall operation completed
                (True if at least one item was deleted, False if all failed)
            - results: Dictionary mapping each path to its deletion result:
                - success: Boolean indicating if deletion was successful
                - path: Path to the item
                - recycle_bin_path: Path where item was moved in recycle bin (if successful)
                - item_type: "file" or "directory" (if successful)
                - error: Error message if deletion failed (None if successful)
            - successful_paths: List of paths that were successfully deleted
            - failed_paths: List of paths that failed to delete
            - total_count: Total number of items attempted
            - success_count: Number of items successfully deleted
            - failure_count: Number of items that failed to delete
            - error: Error message if the overall operation failed (None if successful)
    """
    # Normalize paths to list
    if isinstance(paths, str):
        path_list = [paths]
    else:
        path_list = paths

    if not path_list:
        return {
            "success": False,
            "results": {},
            "successful_paths": [],
            "failed_paths": [],
            "total_count": 0,
            "success_count": 0,
            "failure_count": 0,
            "error": "At least one path must be provided.",
        }

    results = {}
    successful_paths = []
    failed_paths = []

    # Delete each item
    for path in path_list:
        result = _delete_single_item(
            path=path,
            file_system_memory=file_system_memory,
        )
        results[path] = result

        if result["success"]:
            successful_paths.append(path)
        else:
            failed_paths.append(path)

    success_count = len(successful_paths)
    failure_count = len(failed_paths)
    overall_success = success_count > 0

    return {
        "success": overall_success,
        "results": results,
        "successful_paths": successful_paths,
        "failed_paths": failed_paths,
        "total_count": len(path_list),
        "success_count": success_count,
        "failure_count": failure_count,
        "error": None if overall_success else "All item deletions failed.",
    }

