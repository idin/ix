"""
Tests for OpenAI API key in environment.
"""

from ixmachina.llm import EnvVar
from tests.api_keys import get_openai_api_key


def test_openai_api_key_exists_in_environment():
    """Test that OPENAI_API_KEY environment variable exists."""
    api_key = get_openai_api_key()
    assert api_key is not None
    assert len(api_key) > 0


def test_openai_api_key_can_be_read_with_env_var():
    """Test that OPENAI_API_KEY can be read using EnvVar class."""
    api_key = get_openai_api_key()
    
    env_var = EnvVar("OPENAI_API_KEY")
    retrieved_key = env_var.get_value()
    
    assert retrieved_key == api_key
    assert len(retrieved_key) > 0


def test_openai_api_key_is_not_empty():
    """Test that OPENAI_API_KEY environment variable is not empty."""
    api_key = get_openai_api_key()
    assert len(api_key.strip()) > 0, "OPENAI_API_KEY should not be empty"

