"""
Tests for conversation-scoped saved objects: [conv_obj:conversation_id:object_name].
"""

import pytest
from tests.conftest import DEFAULT_TEST_MODEL
import os

from ixmachina.llm import LLM
from ixmachina.agent import Agent, SpecialObjectKeyError
from ixmachina.agent.save_objects import save_as


class TestData:
    """Test data class."""
    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value
    
    def __eq__(self, other):
        if not isinstance(other, TestData):
            return False
        return self.name == other.name and self.value == other.value


def test_conversation_scoped_saved_object():
    """Test that conversation-scoped saved objects work correctly."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    def save_conversation_data(name: str, value: int):
        """
        Save data scoped to the conversation.
        
        Args:
            name: Name for the data.
            value: Value for the data.
            
        Returns:
            TestData instance.
        """
        data = TestData(name=name, value=value)
        return save_as(name="conversation_data", obj=data, conversation_scoped=True)

    def use_conversation_data(data: TestData) -> str:
        """
        Use the conversation-scoped saved data.
        
        Args:
            data: The saved data (should be passed as [conv_obj:conversation_id:conversation_data]).
            
        Returns:
            String description of the data.
        """
        assert isinstance(data, TestData)
        return f"Data: {data.name}, value: {data.value}"

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[save_conversation_data, use_conversation_data])
    agent.start_conversation()
    conversation_id = agent.current_conversation_id

    # Save conversation-scoped data
    response1 = agent.run(
        "Call save_conversation_data with name='test' and value=100. Save the result.",
        return_mode="tool_output_value",
    )
    
    # Verify it was saved in conversation-scoped storage
    assert conversation_id in agent._conversation_objects
    assert "conversation_data" in agent._conversation_objects[conversation_id]
    saved_data = agent._conversation_objects[conversation_id]["conversation_data"]
    assert isinstance(saved_data, TestData)
    assert saved_data.name == "test"
    assert saved_data.value == 100
    
    # Verify it's NOT in global storage
    assert "conversation_data" not in agent._global_objects
    
    # Use the conversation-scoped saved object
    response2 = agent.run(
        f"Call use_conversation_data with data='[conv_obj:{conversation_id}:conversation_data]'. "
        "Return only the tool result.",
        return_mode="tool_output_value",
    )
    
    assert isinstance(response2, str)
    assert "test" in response2
    assert "100" in response2


def test_conversation_scoped_saved_object_deleted_on_conversation_reset():
    """Test that conversation-scoped saved objects are cleared when conversation is reset."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    def save_data(value: int):
        """Save conversation-scoped data."""
        return save_as(name="data", obj=value, conversation_scoped=True)

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[save_data])
    agent.start_conversation()
    conversation_id = agent.current_conversation_id

    # Save conversation-scoped data
    agent.run("Call save_data with value=42. Save the result.")
    
    # Verify it's saved
    assert conversation_id in agent._conversation_objects
    assert "data" in agent._conversation_objects[conversation_id]
    assert agent._conversation_objects[conversation_id]["data"] == 42
    
    # Reset conversation
    agent.reset_conversation(conversation_id=conversation_id)
    
    # Verify conversation-scoped data is cleared
    assert conversation_id in agent._conversation_objects
    assert len(agent._conversation_objects[conversation_id]) == 0


def test_conversation_scoped_saved_object_deleted_on_conversation_forget():
    """Test that conversation-scoped saved objects are deleted when conversation is forgotten."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    def save_data(value: int):
        """Save conversation-scoped data."""
        return save_as(name="data", obj=value, conversation_scoped=True)

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[save_data])
    agent.start_conversation(conversation_id="test_conv")

    # Save conversation-scoped data
    agent.run("Call save_data with value=42. Save the result.")
    
    # Verify it's saved
    assert "test_conv" in agent._conversation_objects
    assert "data" in agent._conversation_objects["test_conv"]
    
    # Forget conversation
    agent.forget_conversation(conversation_id="test_conv")
    
    # Verify conversation-scoped data is deleted
    assert "test_conv" not in agent._conversation_objects


def test_conversation_scoped_saved_object_not_found():
    """Test that error occurs when conversation-scoped saved object is not found."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    def use_data(data: TestData) -> str:
        """
        Use the saved data.
        
        Args:
            data: The saved data (should be passed as [conv_obj:conversation_id:data]).
            
        Returns:
            String description of the data.
        """
        return str(data)

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[use_data])
    agent.start_conversation()
    conversation_id = agent.current_conversation_id

    # Try to reference a non-existent conversation-scoped saved object
    response = agent.run(
        f"Call use_data with data='[conv_obj:{conversation_id}:nonexistent]'. "
        "Report exactly what happens."
    )
    
    # Should indicate an error
    assert isinstance(response, str)
    assert len(response) > 0
    assert "error" in response.lower() or "not found" in response.lower() or "nonexistent" in response.lower()


def test_conversation_scoped_vs_global_saved_objects():
    """Test that conversation-scoped and global saved objects are stored separately."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    def save_both(conv_value: int, global_value: int):
        """Save both conversation-scoped and global objects."""
        conv_data = save_as(name="data", obj=conv_value, conversation_scoped=True)
        global_data = save_as(name="data", obj=global_value, conversation_scoped=False)
        return {"conv": conv_data, "global": global_data}

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[save_both])
    agent.start_conversation()
    conversation_id = agent.current_conversation_id

    # Save both types
    agent.run("Call save_both with conv_value=100 and global_value=200. Save the results.")
    
    # Verify they're stored separately
    assert conversation_id in agent._conversation_objects
    assert "data" in agent._conversation_objects[conversation_id]
    assert agent._conversation_objects[conversation_id]["data"] == 100
    
    assert "data" in agent._global_objects
    assert agent._global_objects["data"] == 200


def test_conversation_scoped_saved_object_brackets_required():
    """Test that brackets are required for conversation-scoped saved object references."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    def save_data():
        """Save conversation-scoped data."""
        return save_as(name="test_data", obj=TestData(name="test", value=42), conversation_scoped=True)

    def use_data(data: TestData) -> str:
        """
        Use the saved data.
        
        Args:
            data: The saved data (should be passed as [conv_obj:conversation_id:test_data]).
            
        Returns:
            String description of the data.
        """
        assert isinstance(data, TestData)
        return f"Data: {data.name}, value: {data.value}"

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[save_data, use_data])
    agent.start_conversation()
    conversation_id = agent.current_conversation_id

    # Save conversation-scoped data
    agent.run("Call save_data. Save the result.")
    
    # Verify it was saved correctly
    assert conversation_id in agent._conversation_objects
    assert "test_data" in agent._conversation_objects[conversation_id]
    assert isinstance(agent._conversation_objects[conversation_id]["test_data"], TestData)

    # Try to use WITHOUT brackets - should fail or receive string
    response = agent.run(
        f"Call use_data with data='conv_obj:{conversation_id}:test_data' (without brackets). "
        "Report exactly what happens or what the tool returns."
    )
    
    # Should indicate an error because it received a string, not TestData
    assert isinstance(response, str)
    assert len(response) > 0
    assert "error" in response.lower() or "string" in response.lower() or "test_data" in response.lower()


def test_save_as_conversation_scoped_parameter():
    """Test that save_as(conversation_scoped=True) actually saves to conversation-scoped storage."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    def save_conv_data():
        """Save conversation-scoped data."""
        return save_as(name="conv_data", obj=100, conversation_scoped=True)

    def save_global_data():
        """Save global data."""
        return save_as(name="global_data", obj=200, conversation_scoped=False)

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[save_conv_data, save_global_data])
    agent.start_conversation()
    conversation_id = agent.current_conversation_id

    # Save conversation-scoped data
    result1 = agent.run("Call save_conv_data. Save the result.", return_mode="tool_output_value")
    assert result1 == 100
    
    # Verify it's in conversation-scoped storage, NOT global
    assert conversation_id in agent._conversation_objects
    assert "conv_data" in agent._conversation_objects[conversation_id]
    assert agent._conversation_objects[conversation_id]["conv_data"] == 100
    assert "conv_data" not in agent._global_objects

    # Save global data
    result2 = agent.run("Call save_global_data. Save the result.", return_mode="tool_output_value")
    assert result2 == 200
    
    # Verify it's in global storage, NOT conversation-scoped
    assert "global_data" in agent._global_objects
    assert agent._global_objects["global_data"] == 200
    assert "global_data" not in agent._conversation_objects[conversation_id]

