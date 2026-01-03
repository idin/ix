"""
Shared constants for file system tests.

This module contains constants used across all file system test files.
"""

import os
from tests.conftest import TEST_DATA_DIR

# Test directory for file system tests - located in centralized test data directory
FILE_SYSTEM_TEST_DIR = os.path.join(TEST_DATA_DIR, "file_system_tools")

