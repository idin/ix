"""
File system tools for comparing files and directories.
"""

from .compare_files import compare_files
from .compare_dirs import compare_dirs

__all__ = [
    "compare_files",
    "compare_dirs",
]

