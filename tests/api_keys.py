"""
API key helper functions for tests.

These functions retrieve API keys from the environment for use in tests.
ALWAYS use these functions in tests to get API keys - DO NOT load environment
variables inside the functions being tested.

Environment variables are stored in ~/.zshrc:
- BRAVE_API_KEY="BSA7kX4M5x1AO4GlrlXFVfHPOeuoIGL"
- OPENAI_API_KEY="sk-proj-..."

The root tests/conftest.py automatically loads these from ~/.zshrc when pytest runs.
"""

import os


def get_brave_api_key():
    """
    Get Brave API key from environment, raising RuntimeError if not set.
    
    Use this function in tests to get the Brave API key. Pass it as a parameter
    to functions that require it. DO NOT load environment variables inside functions.
    
    Returns:
        The Brave API key string.
    
    Raises:
        RuntimeError: If BRAVE_API_KEY environment variable is not set.
    """
    api_key = os.getenv("BRAVE_API_KEY")
    if api_key is None:
        raise RuntimeError("BRAVE_API_KEY environment variable not set")
    return api_key


def get_openai_api_key():
    """
    Get OpenAI API key from environment, raising RuntimeError if not set.
    
    Use this function in tests to get the OpenAI API key. Pass it as a parameter
    to functions that require it. DO NOT load environment variables inside functions.
    
    Returns:
        The OpenAI API key string.
    
    Raises:
        RuntimeError: If OPENAI_API_KEY environment variable is not set.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key is None:
        raise RuntimeError("OPENAI_API_KEY environment variable not set")
    return api_key

