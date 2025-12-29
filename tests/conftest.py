"""
Pytest configuration and fixtures.
Loads environment variables from ~/.zshrc if they're not already set.
"""

import os
import subprocess
import pytest


# Import API key helpers from dedicated module
from tests.api_keys import get_brave_api_key, get_openai_api_key

# Default model for tests (cheaper option)
DEFAULT_TEST_MODEL = "gpt-4o-mini"


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

