"""
Utilities for moving files to Trash on macOS.
"""

import os
import shutil
from pathlib import Path
from typing import Union


def _get_trash_path(file_path: Path) -> Path:
    """
    Determine the appropriate Trash path for a given file path.
    
    Args:
        file_path: Resolved path to the file.
    
    Returns:
        Path to the Trash directory where the file should be moved.
    """
    home_path = Path.home().resolve()
    
    try:
        # Check if path is on the same volume as home directory
        if str(file_path).startswith(str(home_path)) or os.path.samefile(file_path, home_path):
            # Boot volume - use ~/.Trash
            return Path.home() / ".Trash"
        else:
            # External volume - use /.Trashes/{uid}/ at volume root
            # Get the mount point (volume root)
            volume_root = Path(file_path.parts[0]) if file_path.is_absolute() else Path("/")
            uid = os.getuid()
            return volume_root / ".Trashes" / str(uid)
    except (OSError, ValueError):
        # Fallback to home Trash if we can't determine volume
        return Path.home() / ".Trash"


def move_to_trash(path: Union[str, Path]) -> None:
    """
    Move a file or directory to the macOS Trash.
    
    Moves items to the appropriate Trash location based on the file's volume:
    - Boot volume: ~/.Trash
    - External volumes: /.Trashes/{uid}/ at the root of that volume
    
    This allows files to be recovered from Trash if needed.
    
    Args:
        path: Path to file or directory to move to Trash.
    """
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")
    
    # Get the real path to determine which volume it's on
    real_path = path_obj.resolve()
    
    # Determine the appropriate Trash path
    trash_path = _get_trash_path(real_path)
    
    trash_path.mkdir(parents=True, exist_ok=True)
    
    # Get the name of the item to move
    item_name = path_obj.name
    
    # Handle name conflicts by appending a number if needed
    dest_path = trash_path / item_name
    counter = 1
    while dest_path.exists():
        stem = path_obj.stem
        suffix = path_obj.suffix
        dest_path = trash_path / f"{stem} {counter}{suffix}"
        counter += 1
    
    # Move the file or directory
    shutil.move(str(path_obj), str(dest_path))
