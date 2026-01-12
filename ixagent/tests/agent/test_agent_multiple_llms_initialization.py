"""
Tests for Agent class initialization with multiple LLMs.
"""

from tests.conftest import DEFAULT_TEST_MODEL

from ixmachina.llm import LLM
from ixmachina.agent import Agent
from api_keys import get_openai_api_key


def test_agent_initialization_with_multiple_llms_dict():
    """Test Agent can be initialized with a dictionary of LLMs."""
    api_key = get_openai_api_key()

    llm1 = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2})
    
    assert len(agent.llms) == 2
    assert "gpt4" in agent.llms
    assert "gpt35" in agent.llms
    assert agent.llms["gpt4"> is llm1
    assert agent.llms["gpt35"> is llm2
    # Default should be first LLM in dict
    assert agent.llm is llm1


def test_agent_initialization_with_multiple_llms_and_default_key():
    """Test Agent can be initialized with multiple LLMs and default_llm as key."""
    api_key = get_openai_api_key()

    llm1 = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2}, default_llm="gpt35")
    
    assert agent.llm is llm2
    assert agent.llms["gpt35"> is llm2


def test_agent_initialization_with_multiple_llms_and_default_instance():
    """Test Agent can be initialized with multiple LLMs and default_llm as instance."""
    api_key = get_openai_api_key()

    llm1 = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2}, default_llm=llm2)
    
    assert agent.llm is llm2


def test_agent_initialization_with_single_llm():
    """Test Agent can still be initialized with a single LLM."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)
    
    assert len(agent.llms) == 1
    assert "default" in agent.llms
    assert agent.llms["default"> is llm
    assert agent.llm is llm

