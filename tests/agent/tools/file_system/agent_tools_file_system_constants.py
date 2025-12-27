"""
Shared constants for agent file system tests.

This module contains constants used across all agent file system test files.
"""

import os

# Test directory for agent file system tests - located in tests/agent/tools/file_system/
AGENT_FILE_SYSTEM_TEST_DIR = os.path.join(
    os.path.dirname(__file__),
    "ixmachina_agent_file_system_test_directory"
)


