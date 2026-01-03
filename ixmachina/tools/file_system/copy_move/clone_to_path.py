"""
File system tools for cloning files or directories to exact paths.
"""

from typing import Dict, Any, Optional, List, Union, TYPE_CHECKING
import os
import shutil

from ..path_utils import path_exists, path_is_file, path_is_dir
from ..memory import Action
from ..delete import delete

if TYPE_CHECKING:
    from ..memory import FileSystemMemory


def _clone_single_item(
    source_path: str,
    destination_path: str,
    file_system_memory: Optional["FileSystemMemory"] = None,
) -> Dict[str, Any]:
    """
    Clone a single file or directory to an exact destination path.
    
    Internal helper function.
    """
    try:
        if not path_exists(source_path):
            return {
                "success": False,
                "source_path": source_path,
                "destination_path": None,
                "error": f"Source does not exist: {source_path}",
            }

        # Check if destination exists
        if path_exists(destination_path):
            return {
                "success": False,
                "source_path": source_path,
                "destination_path": destination_path,
                "error": f"Destination already exists: {destination_path}. Overwrite is not allowed.",
            }

        # Create parent directory if it doesn't exist
        parent_dir = os.path.dirname(destination_path)
        if parent_dir and not path_exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        # Copy based on type
        if path_is_file(source_path):
            shutil.copy2(source_path, destination_path)
        elif path_is_dir(source_path):
            shutil.copytree(source_path, destination_path)
        else:
            return {
                "success": False,
                "source_path": source_path,
                "destination_path": None,
                "error": f"Source path is neither a file nor a directory: {source_path}",
            }

        # Track action in memory if provided
        if file_system_memory is not None:
            try:
                undo_action = Action(
                    function_name="delete",
                    function=delete,
                    arguments={"paths": destination_path},
                )

                action = Action(
                    function_name="clone_to_path",
                    function=clone_to_path,
                    arguments={
                        "source_destination_pairs": {
                            "source_path": source_path,
                            "destination_path": destination_path,
                        },
                    },
                )
                file_system_memory.add_action(action=action, undo_action=undo_action)
            except Exception:
                pass

        return {
            "success": True,
            "source_path": source_path,
            "destination_path": destination_path,
            "error": None,
        }
    except PermissionError as e:
        return {
            "success": False,
            "source_path": source_path,
            "destination_path": None,
            "error": f"Permission denied: {str(e)}",
        }
    except Exception as e:
        return {
            "success": False,
            "source_path": source_path,
            "destination_path": None,
            "error": f"Error cloning item: {str(e)}",
        }


def clone_to_path(
    source_destination_pairs: Union[Dict[str, str], List[Dict[str, str]]],
    file_system_memory: Optional["FileSystemMemory"] = None,
) -> Dict[str, Any]:
    """
    Clone files or directories to exact destination paths.

    Automatically detects whether each source is a file or directory and uses
    the appropriate operation. Each source will be copied to its exact destination
    path, and sources remain unchanged.

    Args:
        source_destination_pairs: A single dict with "source_path" and "destination_path" keys,
            or a list of such dicts. Each dict specifies one source-destination pair.
        file_system_memory: Optional FileSystemMemory instance to track actions.
            Default: None.

    Returns:
        Dictionary with:
            - success: Boolean indicating if the overall operation completed
                (True if at least one item was cloned, False if all failed)
            - results: Dictionary mapping each source path to its clone result:
                - success: Boolean indicating if clone was successful
                - source_path: Path to the source item
                - destination_path: Final path where item was cloned (if successful)
                - error: Error message if clone failed (None if successful)
            - successful_paths: List of source paths that were successfully cloned
            - failed_paths: List of source paths that failed to clone
            - total_count: Total number of items attempted
            - success_count: Number of items successfully cloned
            - failure_count: Number of items that failed to clone
            - error: Error message if the overall operation failed (None if successful)
    """
    # Normalize to list
    if isinstance(source_destination_pairs, dict):
        pair_list = [source_destination_pairs]
    else:
        pair_list = source_destination_pairs

    if not pair_list:
        return {
            "success": False,
            "results": {},
            "successful_paths": [],
            "failed_paths": [],
            "total_count": 0,
            "success_count": 0,
            "failure_count": 0,
            "error": "At least one source-destination pair must be provided.",
        }

    results = {}
    successful_paths = []
    failed_paths = []

    # Clone each item
    for pair in pair_list:
        source_path = pair.get("source_path")
        destination_path = pair.get("destination_path")

        if not source_path or not destination_path:
            error_msg = "Each pair must have 'source_path' and 'destination_path' keys."
            results[source_path or "unknown"] = {
                "success": False,
                "source_path": source_path,
                "destination_path": destination_path,
                "error": error_msg,
            }
            if source_path:
                failed_paths.append(source_path)
            continue

        result = _clone_single_item(
            source_path=source_path,
            destination_path=destination_path,
            file_system_memory=file_system_memory,
        )
        results[source_path] = result

        if result["success"]:
            successful_paths.append(source_path)
        else:
            failed_paths.append(source_path)

    success_count = len(successful_paths)
    failure_count = len(failed_paths)
    overall_success = success_count > 0

    return {
        "success": overall_success,
        "results": results,
        "successful_paths": successful_paths,
        "failed_paths": failed_paths,
        "total_count": len(pair_list),
        "success_count": success_count,
        "failure_count": failure_count,
        "error": None if overall_success else "All item clones failed.",
    }
