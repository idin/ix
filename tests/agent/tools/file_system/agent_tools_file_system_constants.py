"""
Shared constants for agent file system tests.

This module contains constants used across all agent file system test files.
"""

import os
from tests.conftest import TEST_DATA_DIR

# Test directory for agent file system tests - located in centralized test data directory
AGENT_FILE_SYSTEM_TEST_DIR = os.path.join(TEST_DATA_DIR, "agent_file_system_tools")


