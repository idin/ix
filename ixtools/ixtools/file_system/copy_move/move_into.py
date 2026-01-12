"""
File system tools for moving files or directories into directories.
"""

from typing import Dict, Any, Optional, List, Union, TYPE_CHECKING
import os
import shutil

from ixutils.file_system import path_exists, path_is_file, path_is_dir
from ..memory import Action
from .change_path import change_path

if TYPE_CHECKING:
    from ..memory import FileSystemMemory


def _move_single_item(
    source_path: str,
    destination_dir: str,
    file_system_memory: Optional["FileSystemMemory"] = None,
) -> Dict[str, Any]:
    """
    Move a single file or directory into a destination directory.
    
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

        if not path_exists(destination_dir):
            return {
                "success": False,
                "source_path": source_path,
                "destination_path": None,
                "error": f"Destination directory does not exist: {destination_dir}",
            }

        if not path_is_dir(destination_dir):
            return {
                "success": False,
                "source_path": source_path,
                "destination_path": None,
                "error": f"Destination path is not a directory: {destination_dir}",
            }

        # Determine final destination path
        if path_is_file(source_path):
            source_name = os.path.basename(source_path)
            final_destination = os.path.join(destination_dir, source_name)
        elif path_is_dir(source_path):
            source_dirname = os.path.basename(source_path.rstrip(os.sep))
            final_destination = os.path.join(destination_dir, source_dirname)
        else:
            return {
                "success": False,
                "source_path": source_path,
                "destination_path": None,
                "error": f"Source path is neither a file nor a directory: {source_path}",
            }

        # Check if destination exists
        if path_exists(final_destination):
            return {
                "success": False,
                "source_path": source_path,
                "destination_path": final_destination,
                "error": f"Destination already exists: {final_destination}. Overwrite is not allowed.",
            }

        # Move the item (works for both files and directories)
        shutil.move(source_path, final_destination)

        # Track action in memory if provided
        if file_system_memory is not None:
            try:
                undo_action = Action(
                    function_name="change_path",
                    function=change_path,
                    arguments={
                        "source_destination_pairs": {
                            "source_path": final_destination,
                            "destination_path": source_path,
                        },
                    },
                )

                action = Action(
                    function_name="move_into",
                    function=move_into,
                    arguments={
                        "source_paths": source_path,
                        "destination_dir": destination_dir,
                    },
                )
                file_system_memory.add_action(action=action, undo_action=undo_action)
            except Exception:
                pass

        return {
            "success": True,
            "source_path": source_path,
            "destination_path": final_destination,
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
            "error": f"Error moving item: {str(e)}",
        }


def move_into(
    source_paths: Union[str, List[str]],
    destination_dir: str,
    file_system_memory: Optional["FileSystemMemory"] = None,
) -> Dict[str, Any]:
    """
    Move files or directories into a destination directory.

    Automatically detects whether each source is a file or directory and uses
    the appropriate operation. Each source will be moved inside the destination
    directory, keeping its original name.

    Args:
        source_paths: A single path (string) or list of paths to move.
        destination_dir: Path to the destination directory (must exist).
        file_system_memory: Optional FileSystemMemory instance to track actions.
            Default: None.

    Returns:
        Dictionary with:
            - success: Boolean indicating if the overall operation completed
                (True if at least one item was moved, False if all failed)
            - destination_dir: Path to the destination directory
            - results: Dictionary mapping each source path to its move result:
                - success: Boolean indicating if move was successful
                - source_path: Path to the source item
                - destination_path: Final path where item was moved (if successful)
                - error: Error message if move failed (None if successful)
            - successful_paths: List of source paths that were successfully moved
            - failed_paths: List of source paths that failed to move
            - total_count: Total number of items attempted
            - success_count: Number of items successfully moved
            - failure_count: Number of items that failed to move
            - error: Error message if the overall operation failed (None if successful)
    """
    # Normalize source_paths to list
    if isinstance(source_paths, str):
        path_list = [source_paths]
    else:
        path_list = source_paths

    if not path_list:
        return {
            "success": False,
            "destination_dir": destination_dir,
            "results": {},
            "successful_paths": [],
            "failed_paths": [],
            "total_count": 0,
            "success_count": 0,
            "failure_count": 0,
            "error": "At least one source path must be provided.",
        }

    results = {}
    successful_paths = []
    failed_paths = []

    # Move each item
    for source_path in path_list:
        result = _move_single_item(
            source_path=source_path,
            destination_dir=destination_dir,
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
        "destination_dir": destination_dir,
        "results": results,
        "successful_paths": successful_paths,
        "failed_paths": failed_paths,
        "total_count": len(path_list),
        "success_count": success_count,
        "failure_count": failure_count,
        "error": None if overall_success else "All item moves failed.",
    }

