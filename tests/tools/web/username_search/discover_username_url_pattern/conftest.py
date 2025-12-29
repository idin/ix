"""
Shared fixtures and utilities for discover_username_url_pattern tests.
"""

import os


def get_brave_api_key():
    """Get Brave API key from environment, raising RuntimeError if not set."""
    api_key = os.getenv("BRAVE_API_KEY")
    if api_key is None:
        raise RuntimeError("BRAVE_API_KEY environment variable not set")
    return api_key

