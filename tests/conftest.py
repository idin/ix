"""
Pytest configuration and fixtures.
Loads environment variables from ~/.zshrc if they're not already set.
"""

import os
import pytest

from ixmachina.tools.file_system.delete import delete
from ixmachina.tools.file_system.path_utils import path_exists, path_is_file, path_is_dir

# Default model for tests (cheaper option)
DEFAULT_TEST_MODEL = "gpt-4o-mini"

# Test data directory at project root - all tests should use this for file operations
TEST_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    ".test_data"
)


def _load_env_from_zshrc():
    """Load environment variables from ~/.zshrc if they exist."""
    if not os.path.exists(os.path.expanduser("~/.zshrc")):
        return
    
    # Extract export statements from .zshrc
    try:
        with open(os.path.expanduser("~/.zshrc"), "r") as f:
            for line in f:
                line = line.strip()
                # Look for export statements for API keys
                if line.startswith("export ") and ("API_KEY" in line or "BRAVE_API_KEY" in line or "OPENAI_API_KEY" in line):
                    # Parse the export statement
                    # Format: export KEY="value"
                    if "=" in line:
                        key_part = line.split("=", 1)[0].replace("export", "").strip()
                        value_part = line.split("=", 1)[1].strip()
                        # Remove quotes if present
                        if value_part.startswith('"') and value_part.endswith('"'):
                            value_part = value_part[1:-1]
                        elif value_part.startswith("'") and value_part.endswith("'"):
                            value_part = value_part[1:-1]
                        
                        # Only set if not already in environment
                        if key_part and key_part not in os.environ:
                            os.environ[key_part] = value_part
    except Exception:
        # If we can't read .zshrc, just continue
        pass


# Load environment variables when pytest starts
_load_env_from_zshrc()


@pytest.fixture(scope="session", autouse=True)
def ensure_api_keys():
    """Ensure API keys are loaded from ~/.zshrc if not in environment."""
    _load_env_from_zshrc()


@pytest.fixture(autouse=True)
def cleanup_test_data():
    """
    Clean up test data directory before and after each test.
    
    Ensures test data directory exists and cleans up test files after each test.
    Preserves symlinks to .test_source_protected/ (where manually added files like media are stored).
    """
    # Ensure test data directory exists
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    yield
    # Clean up after test
    if os.path.exists(TEST_DATA_DIR):
        _cleanup_test_data_directory(TEST_DATA_DIR)


def _cleanup_test_data_directory(directory_path):
    """
    Recursively clean up test data directory.
    
    Preserves symlinks pointing to .test_source_protected/ (where manually added files are stored).
    Uses recycle bin deletion functions to ensure deleted items can be recovered.
    
    Args:
        directory_path: Path to directory to clean.
    """
    if not path_exists(directory_path):
        return
    
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        
        if path_is_dir(item_path):
            # Recursively clean directories
            _cleanup_test_data_directory(item_path)
            
            # Remove empty directories using recycle bin
            try:
                if not os.listdir(item_path):
                    delete(paths=item_path)
            except Exception:
                pass
        else:
            # Preserve symlinks to .test_source_protected/
            if os.path.islink(item_path):
                try:
                    link_target = os.readlink(item_path)
                    # Resolve relative symlinks
                    if not os.path.isabs(link_target):
                        link_target = os.path.normpath(os.path.join(os.path.dirname(item_path), link_target))
                    # Check if symlink points to .test_source_protected/
                    if ".test_source_protected" in link_target:
                        # Preserve symlinks to protected source directory
                        continue
                except Exception:
                    pass
            
            # Delete files using recycle bin (symlinks to protected directories are skipped above)
            if path_is_file(item_path):
                try:
                    delete(paths=item_path)
                except Exception:
                    pass

