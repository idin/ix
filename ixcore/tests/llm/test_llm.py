"""
Tests for LLM class.
"""

import pytest

from conftest import DEFAULT_TEST_MODEL
from ixcore.llm import LLM
from ixutils import EnvVar
from api_keys import get_openai_api_key


def test_initialization_with_openai_provider():
    """Test LLM initialization with OpenAI provider."""
    api_key = get_openai_api_key()

    llm = LLM(
        api_key=api_key,
        model_name=DEFAULT_TEST_MODEL,
        provider="openai",
    )

    assert llm.api_key == api_key
    assert llm.model_name == DEFAULT_TEST_MODEL
    assert llm.provider == "openai"
    assert llm.client is not None


def test_auto_detects_openai_provider_from_gpt_model_name():
    """Test LLM auto-detects OpenAI provider from GPT model name."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)

    assert llm.provider == "openai"


def test_auto_detects_openai_provider_from_o1_model_name():
    """Test LLM auto-detects OpenAI provider from O1 model name."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name="o1-preview")

    assert llm.provider == "openai"


def test_initialization_with_env_var_reads_from_environment():
    """Test LLM initialization with EnvVar reads value from environment."""
    api_key = get_openai_api_key()

    env_var = EnvVar("OPENAI_API_KEY")
    llm = LLM(api_key=env_var, model_name=DEFAULT_TEST_MODEL)

    assert llm.api_key == api_key
    assert llm.provider == "openai"


def test_query_with_user_prompt():
    """Test LLM query method with user prompt."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    response = llm.query(user_prompt="Say hello in one word")

    assert isinstance(response, str)
    assert len(response) > 0


def test_query_with_system_and_user_prompt():
    """Test LLM query method with system and user prompts."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    response = llm.query(
        user_prompt="Say hello",
        system_prompt="You are a helpful assistant",
    )

    assert isinstance(response, str)
    assert len(response) > 0


def test_query_with_messages_as_string():
    """Test LLM query method with messages parameter as string."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    response = llm.query(messages="Say hello in one word")

    assert isinstance(response, str)
    assert len(response) > 0


def test_query_with_messages_as_single_dictionary():
    """Test LLM query method with messages parameter as single dictionary."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    response = llm.query(messages={"role": "user", "content": "Say hello in one word"})

    assert isinstance(response, str)
    assert len(response) > 0


def test_query_with_messages_as_list():
    """Test LLM query method with messages parameter as list."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    messages = [
        {"role": "user", "content": "Say hello"},
        {"role": "assistant", "content": "Hello!"},
        {"role": "user", "content": "Say it again"},
    ]
    response = llm.query(messages=messages)

    assert isinstance(response, str)
    assert len(response) > 0


def test_query_with_max_tokens_parameter():
    """Test LLM query method with max_tokens parameter."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    response = llm.query(
        user_prompt="Count from 1 to 5",
        max_tokens=10,
    )

    assert isinstance(response, str)
    assert len(response) > 0


def test_query_with_temperature_parameter():
    """Test LLM query method with temperature parameter."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    response = llm.query(
        user_prompt="Say hello",
        temperature=0.7,
    )

    assert isinstance(response, str)
    assert len(response) > 0


def test_query_with_max_tokens_and_temperature_parameters():
    """Test LLM query method with both max_tokens and temperature parameters."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    response = llm.query(
        user_prompt="Say hello",
        max_tokens=10,
        temperature=0.7,
    )

    assert isinstance(response, str)
    assert len(response) > 0


def test_query_raises_error_when_no_prompt_provided():
    """Test LLM query method raises ValueError when no prompt is provided."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)

    with pytest.raises(ValueError, match="Either user_prompt or messages must be provided"):
        llm.query()


def test_query_raises_error_for_invalid_message_dictionary():
    """Test LLM query method raises ValueError for invalid message dictionary."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)

    with pytest.raises(
        ValueError, match="Message dictionary must contain 'role' and 'content' keys"
    ):
        llm.query(messages={"invalid": "dict"})


def test_query_raises_error_for_invalid_messages_type():
    """Test LLM query method raises ValueError for invalid messages type."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)

    with pytest.raises(
        ValueError, match="messages must be a string, dictionary, or list of dictionaries"
    ):
        llm.query(messages=123)


def test_query_what_is_capital_of_france():
    """Test LLM query with question about capital of France."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    response = llm.query(user_prompt="What is the capital of France?")

    assert isinstance(response, str)
    assert len(response) > 0
    # The response should contain "Paris" (case-insensitive)
    assert "paris" in response.lower()
