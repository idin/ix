"""
Tests for Agent special objects functionality.
"""

import pytest
from tests.conftest import DEFAULT_TEST_MODEL
import os

from ixmachina.llm import LLM
from ixmachina.agent import Agent, SpecialObjectKeyError


def test_agent_add_special_object():
    """Test that special objects can be added to the agent."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)
    
    # Test adding a special object
    test_object = {"test": "value"}
    agent._add_system_object("test_obj", test_object)
    
    # Verify it was added
    assert "test_obj" in agent._system_objects
    assert agent._system_objects["test_obj"] == test_object


def test_agent_add_special_object_with_dict_syntax():
    """Test that special objects can be added using dict-like syntax."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)
    
    # Test adding using dict syntax
    test_object = {"test": "value"}
    agent["test_obj"] = test_object
    
    # Verify it was added
    assert "test_obj" in agent._system_objects
    assert agent._system_objects["test_obj"] == test_object


def test_agent_special_object_retrieval_in_tool():
    """Test that special objects are correctly retrieved and passed to tools."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    def tool_with_agent(agent_instance: Agent) -> str:
        """
        Tool that receives the agent instance.
        
        Args:
            agent_instance: The agent instance.
            
        Returns:
            A string indicating the agent was received.
        """
        assert isinstance(agent_instance, Agent)
        return f"Agent received: {type(agent_instance).__name__}"

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[tool_with_agent])
    agent.start_conversation()
    
    # Ask agent to use the tool with special object reference
    response = agent.run(
        "Use the tool_with_agent tool with agent_instance='[sys:self]'. "
        "Do not repeat the special object syntax in your response."
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
    # The tool should have received the agent instance
    assert "agent" in response.lower() or "received" in response.lower()


def test_agent_special_object_retrieval_with_llm():
    """Test that LLM special object is correctly retrieved and passed to tools."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    def tool_with_llm(llm_instance: LLM) -> str:
        """
        Tool that receives the LLM instance.
        
        Args:
            llm_instance: The LLM instance.
            
        Returns:
            A string indicating the LLM was received.
        """
        assert isinstance(llm_instance, LLM)
        return f"LLM received: {llm_instance.provider}"

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[tool_with_llm])
    agent.start_conversation()
    
    # Ask agent to use the tool with special object reference
    response = agent.run(
        "Use the tool_with_llm tool with llm_instance='[sys:llm]'. "
        "Do not repeat the special object syntax in your response."
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
    # The tool should have received the LLM instance
    assert "llm" in response.lower() or "openai" in response.lower()


def test_agent_special_object_not_found_error():
    """Test that SpecialObjectKeyError is raised when special object is not found."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    def simple_tool(arg: str) -> str:
        """Simple tool."""
        return arg

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[simple_tool])
    
    # Manually call _add_system_objects_to_tool_arguments with non-existent special object
    with pytest.raises(SpecialObjectKeyError) as exc_info:
        agent._add_system_objects_to_tool_arguments({"arg": "[sys:nonexistent]"})
    
    assert "nonexistent" in str(exc_info.value).lower()
    assert "available" in str(exc_info.value).lower()


def test_agent_special_object_with_custom_prefix():
    """Test that custom prefix works for special objects."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    def tool_with_agent(agent_instance: Agent) -> str:
        """Tool that receives the agent instance."""
        assert isinstance(agent_instance, Agent)
        return f"Agent received: {type(agent_instance).__name__}"

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(
        llm=llm,
        tools=[tool_with_agent],
        system_object_prefix="ref:",
    )
    agent.start_conversation()
    
    # Test that custom prefix works
    result = agent._add_system_objects_to_tool_arguments({"agent_instance": "[ref:self]"})
    assert "agent_instance" in result
    assert result["agent_instance"] == agent

def test_agent_use_llm_in_tool():
    """Test the usual LLM test to show how special objects work."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    def tool_with_llm(llm_instance: LLM) -> str:
        """Tool that receives the LLM instance."""
        response = llm_instance.query(user_prompt="In one word, what is the capital of England?")
        return f"LLM response: {response}"

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[tool_with_llm])
    agent.start_conversation()
    response = agent.run(
        "Call the tool_with_llm function with the parameter llm_instance set to '[sys:llm]'. "
        "Return the complete tool result exactly as the tool returns it, without modification."
    )
    assert isinstance(response, str)
    assert len(response) > 0
    
    # London should be in the response
    assert "london" in response.lower()

    # Capital should not be in the response
    assert "capital" not in response.lower()

    # LLM response: should be in the response
    assert "llm response:" in response.lower()
    
