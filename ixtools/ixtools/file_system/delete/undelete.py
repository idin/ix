"""
File system tools for undeleting files and directories from recycle bin.
"""

from typing import Dict, Any, Optional, List, Union, TYPE_CHECKING
import os
import shutil

from ixutils.file_system import path_exists
from ..memory import Action
from .recycle_bin import (
    load_metadata,
    find_in_recycle_bin_index,
    remove_from_recycle_bin_index,
)
from .delete import delete

if TYPE_CHECKING:
    from ..memory import FileSystemMemory


def _undelete_single_item(
    recycle_bin_path: Optional[str] = None,
    original_path: Optional[str] = None,
    file_system_memory: Optional["FileSystemMemory"] = None,
) -> Dict[str, Any]:
    """
    Restore a single file or directory from the recycle bin to its original location.
    
    Internal helper function.
    """
    try:
        # If original_path is provided, look it up in the index
        if original_path and not recycle_bin_path:
            recycle_bin_path = find_in_recycle_bin_index(original_path)
            if not recycle_bin_path:
                return {
                    "success": False,
                    "original_path": original_path,
                    "recycle_bin_path": None,
                    "error": f"Item not found in recycle bin index: {original_path}",
                }

        if not recycle_bin_path:
            return {
                "success": False,
                "original_path": original_path,
                "recycle_bin_path": None,
                "error": "Either recycle_bin_path or original_path must be provided.",
            }

        if not path_exists(recycle_bin_path):
            return {
                "success": False,
                "original_path": original_path,
                "recycle_bin_path": recycle_bin_path,
                "error": f"Item does not exist in recycle bin: {recycle_bin_path}",
            }

        # Find metadata - check parent directory (hash folder)
        parent_dir = os.path.dirname(recycle_bin_path)
        metadata = load_metadata(parent_dir)

        if not metadata:
            return {
                "success": False,
                "original_path": None,
                "recycle_bin_path": recycle_bin_path,
                "error": f"Metadata not found for item: {recycle_bin_path}",
            }

        original_path = metadata["original_path"]

        # Check if original location already exists
        if path_exists(original_path):
            return {
                "success": False,
                "original_path": original_path,
                "recycle_bin_path": recycle_bin_path,
                "error": f"Original location already exists: {original_path}. Delete it first if you want to restore.",
            }

        # Create parent directory if it doesn't exist
        parent_dir = os.path.dirname(original_path)
        if parent_dir and not path_exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        # Move item back to original location
        shutil.move(recycle_bin_path, original_path)

        # Remove from index
        remove_from_recycle_bin_index(original_path)

        # Track action in memory if provided
        if file_system_memory is not None:
            try:
                undo_action = Action(
                    function_name="delete",
                    function=delete,
                    arguments={"paths": original_path},
                )

                action = Action(
                    function_name="undelete",
                    function=undelete,
                    arguments={
                        "recycle_bin_paths": recycle_bin_path,
                    },
                )
                file_system_memory.add_action(action=action, undo_action=undo_action)
            except Exception:
                pass

        return {
            "success": True,
            "original_path": original_path,
            "recycle_bin_path": recycle_bin_path,
            "error": None,
        }
    except PermissionError as e:
        return {
            "success": False,
            "original_path": None,
            "recycle_bin_path": recycle_bin_path,
            "error": f"Permission denied: {str(e)}",
        }
    except Exception as e:
        return {
            "success": False,
            "original_path": None,
            "recycle_bin_path": recycle_bin_path,
            "error": f"Error undeleting item: {str(e)}",
        }


def undelete(
    recycle_bin_paths: Optional[Union[str, List[str]]] = None,
    original_paths: Optional[Union[str, List[str]]] = None,
    recycle_bin_path: Optional[str] = None,  # Backward compatibility
    original_path: Optional[str] = None,  # Backward compatibility
    file_system_memory: Optional["FileSystemMemory"] = None,
) -> Dict[str, Any]:
    """
    Restore files or directories from the recycle bin to their original locations.

    Either recycle_bin_paths or original_paths must be provided. Automatically
    detects whether each item is a file or directory and restores it appropriately.

    Args:
        recycle_bin_paths: A single path (string) or list of paths to items in the recycle bin.
            Optional if original_paths is provided.
        original_paths: A single path (string) or list of original paths of deleted items.
            Optional if recycle_bin_paths is provided.
        recycle_bin_path: (Backward compatibility) Single path to item in recycle bin.
            If provided, takes precedence over recycle_bin_paths for single-item operations.
        original_path: (Backward compatibility) Single original path of deleted item.
            If provided, takes precedence over original_paths for single-item operations.
        file_system_memory: Optional FileSystemMemory instance to track actions.
            Default: None.

    Returns:
        Dictionary with:
            - success: Boolean indicating if the overall operation completed
                (True if at least one item was restored, False if all failed)
            - results: Dictionary mapping each path to its undelete result:
                - success: Boolean indicating if undelete was successful
                - original_path: Path where item was restored (if successful)
                - recycle_bin_path: Path where item was in recycle bin
                - error: Error message if undelete failed (None if successful)
            - successful_paths: List of paths that were successfully restored
            - failed_paths: List of paths that failed to restore
            - total_count: Total number of items attempted
            - success_count: Number of items successfully restored
            - failure_count: Number of items that failed to restore
            - error: Error message if the overall operation failed (None if successful)
    """
    # Handle backward compatibility: if old singular names are used, convert to new format
    if recycle_bin_path is not None:
        recycle_bin_paths = recycle_bin_path
    if original_path is not None:
        original_paths = original_path

    # Normalize paths to lists
    if recycle_bin_paths is not None:
        if isinstance(recycle_bin_paths, str):
            recycle_bin_list = [recycle_bin_paths]
        else:
            recycle_bin_list = recycle_bin_paths
    else:
        recycle_bin_list = []

    if original_paths is not None:
        if isinstance(original_paths, str):
            original_list = [original_paths]
        else:
            original_list = original_paths
    else:
        original_list = []

    # Ensure we have at least one set of paths
    if not recycle_bin_list and not original_list:
        return {
            "success": False,
            "results": {},
            "successful_paths": [],
            "failed_paths": [],
            "total_count": 0,
            "success_count": 0,
            "failure_count": 0,
            "error": "Either recycle_bin_paths or original_paths must be provided.",
        }

    # If both are provided, they must have the same length
    if recycle_bin_list and original_list:
        if len(recycle_bin_list) != len(original_list):
            return {
                "success": False,
                "results": {},
                "successful_paths": [],
                "failed_paths": [],
                "total_count": 0,
                "success_count": 0,
                "failure_count": 0,
                "error": "recycle_bin_paths and original_paths must have the same length if both are provided.",
            }

    # Process each item
    results = {}
    successful_paths = []
    failed_paths = []

    # Determine which list to iterate over
    if recycle_bin_list:
        for i, recycle_bin_path in enumerate(recycle_bin_list):
            original_path = original_list[i] if original_list else None
            result = _undelete_single_item(
                recycle_bin_path=recycle_bin_path,
                original_path=original_path,
                file_system_memory=file_system_memory,
            )
            # Use original_path from result if available, otherwise use recycle_bin_path as key
            key = result.get("original_path") or recycle_bin_path
            results[key] = result

            if result["success"]:
                successful_paths.append(key)
            else:
                failed_paths.append(key)
    else:
        # Only original_paths provided
        for original_path in original_list:
            result = _undelete_single_item(
                recycle_bin_path=None,
                original_path=original_path,
                file_system_memory=file_system_memory,
            )
            results[original_path] = result

            if result["success"]:
                successful_paths.append(original_path)
            else:
                failed_paths.append(original_path)

    success_count = len(successful_paths)
    failure_count = len(failed_paths)
    overall_success = success_count > 0

    return {
        "success": overall_success,
        "results": results,
        "successful_paths": successful_paths,
        "failed_paths": failed_paths,
        "total_count": len(results),
        "success_count": success_count,
        "failure_count": failure_count,
        "error": None if overall_success else "All item undeletes failed.",
    }
