"""
Tests that verify brackets are required for special object references.
"""

import pytest
from tests.conftest import DEFAULT_TEST_MODEL
import os

from ixmachina.llm import LLM
from ixmachina.agent import Agent


def test_special_object_without_brackets_not_replaced():
    """Test that special object references without brackets are NOT replaced."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)
    
    # Test that "sys:self" without brackets is NOT replaced - it stays as a string
    result = agent._add_system_objects_to_tool_arguments({"agent": "sys:self"})
    assert "agent" in result
    # Should remain as string, not replaced with agent object
    assert result["agent"] == "sys:self"
    assert not isinstance(result["agent"], Agent)


def test_special_object_with_brackets_is_replaced():
    """Test that special object references WITH brackets ARE replaced."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)
    
    # Test that "[sys:self]" with brackets IS replaced
    result = agent._add_system_objects_to_tool_arguments({"agent": "[sys:self]"})
    assert "agent" in result
    # Should be replaced with agent object
    assert isinstance(result["agent"], Agent)
    assert result["agent"] == agent


def test_special_object_without_brackets_passed_to_tool_fails():
    """Test that using special object without brackets in actual tool call doesn't work."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    def tool_that_expects_agent(agent_instance: Agent) -> str:
        """
        Tool that expects an Agent instance.
        
        Args:
            agent_instance: The agent instance.
            
        Returns:
            A string indicating success.
        """
        if isinstance(agent_instance, Agent):
            return "Agent received successfully"
        else:
            return f"Error: Expected Agent, got {type(agent_instance).__name__}"

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[tool_that_expects_agent])
    agent.start_conversation()
    
    # Try to use tool with special object reference WITHOUT brackets
    # The LLM might pass "sys:self" as a string, which should NOT be replaced
    # and the tool should receive a string instead of the agent object
    response = agent.run(
        "Call tool_that_expects_agent with agent_instance='sys:self' (without brackets). "
        "Report exactly what the tool returns."
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
    # Should indicate an error because it received a string, not an Agent
    assert "error" in response.lower() or "string" in response.lower() or "sys:self" in response.lower()

