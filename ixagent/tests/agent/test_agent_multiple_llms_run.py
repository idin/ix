"""
Tests for Agent class run method with multiple LLMs.
"""

from tests.conftest import DEFAULT_TEST_MODEL

from ixmachina.llm import LLM
from ixmachina.agent import Agent
from api_keys import get_openai_api_key


def test_agent_run_with_different_llm_by_key():
    """Test Agent can use different LLMs for different runs using key."""
    api_key = get_openai_api_key()

    llm1 = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2}, default_llm="gpt4")
    agent.start_conversation(conversation_id="test")
    
    # Use first LLM
    response1 = agent.run("Say hello", conversation_id="test", llm_instance="gpt4")
    assert isinstance(response1, str)
    assert len(response1) > 0
    
    # Use second LLM
    response2 = agent.run("Say goodbye", conversation_id="test", llm_instance="gpt35")
    assert isinstance(response2, str)
    assert len(response2) > 0
    
    # Default LLM should still be gpt4
    assert agent.llm is llm1


def test_agent_run_with_different_llm_by_instance():
    """Test Agent can use different LLMs for different runs using instance."""
    api_key = get_openai_api_key()

    llm1 = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2}, default_llm="gpt4")
    agent.start_conversation(conversation_id="test")
    
    # Use first LLM by instance
    response1 = agent.run("Say hello", conversation_id="test", llm_instance=llm1)
    assert isinstance(response1, str)
    
    # Use second LLM by instance
    response2 = agent.run("Say goodbye", conversation_id="test", llm_instance=llm2)
    assert isinstance(response2, str)


def test_agent_run_with_default_llm():
    """Test Agent uses default LLM when llm_instance is 'default'."""
    api_key = get_openai_api_key()

    llm1 = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2}, default_llm="gpt4")
    agent.start_conversation(conversation_id="test")
    
    # Use default LLM
    response = agent.run("Say hello", conversation_id="test", llm_instance="default")
    assert isinstance(response, str)
    
    # Should use gpt4 (the default)
    assert agent.llm is llm1

