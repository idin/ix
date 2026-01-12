"""
Tests for Agent class switch_default_llm method with multiple LLMs.
"""

from tests.conftest import DEFAULT_TEST_MODEL

from ixmachina.llm import LLM
from ixmachina.agent import Agent
from api_keys import get_openai_api_key


def test_agent_switch_default_llm_by_key():
    """Test Agent can switch default LLM using key."""
    api_key = get_openai_api_key()

    llm1 = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2}, default_llm="gpt4")
    assert agent.llm is llm1
    
    # Switch to gpt35
    agent.switch_default_llm("gpt35")
    assert agent.llm is llm2
    
    # Switch back to gpt4
    agent.switch_default_llm("gpt4")
    assert agent.llm is llm1


def test_agent_switch_default_llm_by_instance():
    """Test Agent can switch default LLM using instance."""
    api_key = get_openai_api_key()

    llm1 = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2}, default_llm="gpt4")
    assert agent.llm is llm1
    
    # Switch to llm2
    agent.switch_default_llm(llm2)
    assert agent.llm is llm2


def test_agent_switch_default_llm_updates_special_objects():
    """Test switching default LLM updates special objects."""
    api_key = get_openai_api_key()

    llm1 = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2}, default_llm="gpt4")
    
    # Check initial special objects
    assert agent._system_objects["llm"> is llm1
    assert agent._system_objects["llm:gpt4"> is llm1
    assert agent._system_objects["llm:gpt35"> is llm2
    
    # Switch default
    agent.switch_default_llm("gpt35")
    
    # Check updated special objects
    assert agent._system_objects["llm"> is llm2
    assert agent._system_objects["llm:gpt4"> is llm1
    assert agent._system_objects["llm:gpt35"> is llm2

