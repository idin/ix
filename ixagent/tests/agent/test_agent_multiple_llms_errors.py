"""
Tests for Agent class error handling with multiple LLMs.
"""

import pytest

from tests.conftest import DEFAULT_TEST_MODEL

from ixmachina.llm import LLM
from ixmachina.agent import Agent
from api_keys import get_openai_api_key


def test_agent_error_invalid_llm_key_in_run():
    """Test Agent raises KeyError for invalid LLM key in run."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm={"gpt4": llm})
    agent.start_conversation(conversation_id="test")
    
    with pytest.raises(KeyError, match="LLM key 'invalid' not found"):
        agent.run("Say hello", conversation_id="test", llm_instance="invalid")


def test_agent_error_invalid_llm_instance_in_run():
    """Test Agent raises KeyError for invalid LLM instance in run."""
    api_key = get_openai_api_key()

    llm1 = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1})
    agent.start_conversation(conversation_id="test")
    
    # llm2 is not in agent's llms dictionary
    with pytest.raises(KeyError, match="LLM instance not found in llms dictionary"):
        agent.run("Say hello", conversation_id="test", llm_instance=llm2)


def test_agent_error_invalid_default_llm_key():
    """Test Agent raises KeyError for invalid default_llm key in initialization."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    
    with pytest.raises(KeyError, match="Default LLM key 'invalid' not found"):
        Agent(llm={"gpt4": llm}, default_llm="invalid")


def test_agent_error_invalid_default_llm_instance():
    """Test Agent raises KeyError for invalid default_llm instance in initialization."""
    api_key = get_openai_api_key()

    llm1 = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    # llm2 is not in the llms dictionary
    with pytest.raises(KeyError, match="Default LLM instance not found in llms dictionary"):
        Agent(llm={"gpt4": llm1}, default_llm=llm2)


def test_agent_error_invalid_switch_default_llm_key():
    """Test Agent raises KeyError for invalid key in switch_default_llm."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm={"gpt4": llm})
    
    with pytest.raises(KeyError, match="LLM key 'invalid' not found"):
        agent.switch_default_llm("invalid")


def test_agent_error_invalid_switch_default_llm_instance():
    """Test Agent raises KeyError for invalid instance in switch_default_llm."""
    api_key = get_openai_api_key()

    llm1 = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1})
    
    # llm2 is not in agent's llms dictionary
    with pytest.raises(KeyError, match="LLM instance not found in llms dictionary"):
        agent.switch_default_llm(llm2)

