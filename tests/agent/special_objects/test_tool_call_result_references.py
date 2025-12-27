"""
Tests for tool call result references: [tool_obj:conversation_id:tool_call_id].
"""

import pytest
import os

from ixmachina.llm import LLM
from ixmachina.agent import Agent, SpecialObjectKeyError


def test_tool_call_result_reference_resolution():
    """Test that tool call results can be referenced using [tool_obj:conversation_id:tool_call_id]."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    def first_tool() -> dict:
        """First tool that returns a dictionary."""
        return {"result": "first_tool_data", "value": 42}

    def second_tool(data: dict) -> str:
        """
        Second tool that receives the result from first_tool.
        
        Args:
            data: The result from first_tool.
            
        Returns:
            String description of the data.
        """
        assert isinstance(data, dict)
        assert data["result"] == "first_tool_data"
        return f"Received: {data['result']}, value: {data['value']}"

    llm = LLM(api_key=api_key, model_name="gpt-4")
    agent = Agent(llm=llm, tools=[first_tool, second_tool])
    agent.start_conversation()

    # First, call first_tool to get a result
    response1 = agent.run(
        "Call first_tool and remember the tool_call_id from the result.",
        return_raw_tool_result=True,
    )
    
    # Get the tool_call_id from the conversation
    conversation_id = agent.current_conversation_id
    tool_calls = agent.conversation_tool_calls[conversation_id]
    assert len(tool_calls) > 0
    first_tool_call_id = tool_calls[0]["tool_call_id"]
    
    # Verify the result is stored in _tool_call_objects
    assert conversation_id in agent._tool_call_objects
    assert first_tool_call_id in agent._tool_call_objects[conversation_id]
    stored_result = agent._tool_call_objects[conversation_id][first_tool_call_id]
    assert stored_result == {"result": "first_tool_data", "value": 42}
    
    # Now use the tool call result reference in second_tool
    response2 = agent.run(
        f"Call second_tool with data='[tool_obj:{conversation_id}:{first_tool_call_id}]'. "
        "Return only the tool result.",
        return_raw_tool_result=True,
    )
    
    assert isinstance(response2, str)
    assert "first_tool_data" in response2
    assert "42" in response2


def test_tool_call_result_reference_brackets_required():
    """Test that brackets are required for tool call result references."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    def first_tool() -> dict:
        """First tool that returns a dictionary."""
        return {"result": "test_data", "value": 42}

    def second_tool(data: dict) -> str:
        """
        Second tool that receives the result from first_tool.
        
        Args:
            data: The result from first_tool (should be passed as [tool_obj:conversation_id:tool_call_id]).
            
        Returns:
            String description of the data.
        """
        assert isinstance(data, dict)
        return f"Received: {data['result']}, value: {data['value']}"

    llm = LLM(api_key=api_key, model_name="gpt-4")
    agent = Agent(llm=llm, tools=[first_tool, second_tool])
    agent.start_conversation()
    conversation_id = agent.current_conversation_id

    # Call first_tool to create a tool call result
    agent.run("Call first_tool.", return_raw_tool_result=True)
    
    # Get the tool_call_id
    assert conversation_id in agent.conversation_tool_calls
    tool_calls = agent.conversation_tool_calls[conversation_id]
    assert len(tool_calls) > 0
    first_tool_call_id = tool_calls[0]["tool_call_id"]
    
    # Verify it's stored correctly
    assert conversation_id in agent._tool_call_objects
    assert first_tool_call_id in agent._tool_call_objects[conversation_id]

    # Try to use WITHOUT brackets - should fail or receive string
    response = agent.run(
        f"Call second_tool with data='tool_obj:{conversation_id}:{first_tool_call_id}' (without brackets). "
        "Report exactly what happens or what the tool returns."
    )
    
    # Should indicate an error because it received a string, not a dict
    assert isinstance(response, str)
    assert len(response) > 0
    assert "error" in response.lower() or "string" in response.lower()

