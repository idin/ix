"""
Shared constants for file system tests.

This module contains constants used across all file system test files.
"""

import os

# Test directory for file system tests - located in tests/tools/file_system/
FILE_SYSTEM_TEST_DIR = os.path.join(
    os.path.dirname(__file__),
    "ixmachina_tools_file_system_test_directory"
)

