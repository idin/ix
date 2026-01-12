"""
Shared constants for media tests.

This module contains constants used across all media test files.
"""

import os

# Protected source directory where manually added media files are stored
# Tests read directly from here - no copying or symlinks needed
# Path is relative to ixtools package root
PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
MEDIA_SOURCE_DIR = os.path.join(PACKAGE_ROOT, ".test_source_protected", "media_tools")
