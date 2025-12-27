"""
Tests for OpenAI API key in environment.
"""

import os
import pytest

from ixmachina.llm import EnvVar


def test_openai_api_key_exists_in_environment():
    """Test that OPENAI_API_KEY environment variable exists."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable is not set")


def test_openai_api_key_can_be_read_with_env_var():
    """Test that OPENAI_API_KEY can be read using EnvVar class."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")
    
    env_var = EnvVar("OPENAI_API_KEY")
    retrieved_key = env_var.get_value()
    
    assert retrieved_key == api_key
    assert len(retrieved_key) > 0


def test_openai_api_key_is_not_empty():
    """Test that OPENAI_API_KEY environment variable is not empty."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")
    
    assert len(api_key.strip()) > 0, "OPENAI_API_KEY should not be empty"

