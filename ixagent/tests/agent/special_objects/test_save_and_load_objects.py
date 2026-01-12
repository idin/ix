"""
Tests for Agent's ability to save and load objects using explicit tools.
"""

from tests.conftest import DEFAULT_TEST_MODEL

from ixmachina.llm import LLM
from ixmachina.agent import Agent
from api_keys import get_openai_api_key
from ixmachina.agent.memory.save_objects import save_as
from ixmachina.llm.tools import prepare_tools_for_provider


def test_agent_save_and_load_conversation_object():
    """Test that agent can save and load conversation-scoped objects using explicit tools."""
    api_key = get_openai_api_key()
    def save_conversation_object(name: str, value: any):
        """
        Save an object scoped to the current conversation.
        
        Args:
            name: Name to save the object under.
            value: The object to save.
            
        Returns:
            ObjectToSave wrapper that will be processed by the agent.
        """
        return save_as(name=name, obj=value, conversation_scoped=True)


    def save_global_object(name: str, value: any):
        """
        Save an object globally (persists across conversations).
        
        Args:
            name: Name to save the object under.
            value: The object to save.
            
        Returns:
            ObjectToSave wrapper that will be processed by the agent.
        """
        return save_as(name=name, obj=value, conversation_scoped=False)


    # Additional tools to make the agent choose from multiple options
    def get_current_time() -> str:
        """Get the current time."""
        return "2024-01-01 12:00:00"

    def calculate_sum(a: int, b: int) -> int:
        """Calculate the sum of two numbers."""
        return a + b

    def format_text(text: str) -> str:
        """Format text by adding exclamation marks."""
        return f"{text}!!!"

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)
    agent.start_conversation()
    conversation_id = agent.current_conversation_id
    
    # Define load functions as closures that capture the agent
    def load_conversation_object(name: str) -> any:
        """Load a conversation-scoped object by name."""
        conversation_id = agent.current_conversation_id
        if conversation_id in agent.memory._conversation_objects:
            if name in agent.memory._conversation_objects[conversation_id]:
                return agent.memory._conversation_objects[conversation_id][name]
        raise KeyError(f"Conversation-scoped object '{name}' not found in conversation '{conversation_id}'")
    
    def load_global_object(name: str) -> any:
        """Load a global object by name."""
        if name in agent.memory._global_objects:
            return agent.memory._global_objects[name]
        raise KeyError(f"Global object '{name}' not found")
    
    # Add tools to agent
    agent.tool_functions = {}
    agent.tools = None
    agent.tool_schemas = {}
    tools = [
        save_conversation_object,
        load_conversation_object,
        save_global_object,
        load_global_object,
        get_current_time,
        calculate_sum,
        format_text,
    ]
    for tool in tools:
        tool_name = tool.__name__
        agent.tool_functions[tool_name] = tool
    
    provider = agent.llm.provider
    prepared = prepare_tools_for_provider(tools, provider)
    agent.tools = prepared["tools"]
    agent.tool_schemas = prepared["schemas"]

    # Test saving and loading a conversation-scoped object
    test_data = {"message": "Hello, world!", "count": 42}
    
    # Verify it's not saved yet
    assert conversation_id not in agent.memory._conversation_objects or "test_data" not in agent.memory._conversation_objects.get(conversation_id, {})
    
    # Save conversation-scoped object - let agent figure out how
    response1 = agent.run(
        f"Save the data {test_data} as a conversation-scoped object with the name 'test_data'. "
        "Use the appropriate tool.",
        return_mode="tool_output_value",
    )
    
    # Verify it was saved in conversation-scoped storage
    assert conversation_id in agent.memory._conversation_objects
    assert "test_data" in agent.memory._conversation_objects[conversation_id]
    saved_data = agent.memory._conversation_objects[conversation_id]["test_data"]
    assert saved_data == test_data
    # Verify it's NOT in global storage
    assert "test_data" not in agent.memory._global_objects

    # Load conversation-scoped object - let agent figure out the reference syntax
    response2 = agent.run(
        "Load the conversation-scoped object named 'test_data' and return its value. "
        "Use the appropriate tool and reference syntax.",
        return_mode="tool_output_value",
    )
    
    # Verify it was loaded correctly
    assert response2 == test_data

    # Test saving and loading a global object
    global_data = {"global_message": "This is global", "value": 100}
    
    # Verify it's not saved yet
    assert "global_data" not in agent.memory._global_objects
    
    # Save global object - let agent figure out how
    response3 = agent.run(
        f"Save the data {global_data} as a global object with the name 'global_data'. "
        "Use the appropriate tool.",
        return_mode="tool_output_value",
    )
    
    # Verify it was saved in global storage
    assert "global_data" in agent.memory._global_objects
    saved_global = agent.memory._global_objects["global_data"]
    assert saved_global == global_data
    # Verify it's NOT in conversation-scoped storage
    assert "global_data" not in agent.memory._conversation_objects.get(conversation_id, {})

    # Load global object - agent just needs to call the tool with name
    response4 = agent.run(
        "Load the global object named 'global_data' and return its value. "
        "Use the load_global_object tool.",
        return_mode="tool_output_value",
    )
    
    # Verify it was loaded correctly
    assert response4 == global_data


def test_agent_saves_and_loads_multiple_objects():
    """Test that agent can save and load multiple objects of different types."""
    api_key = get_openai_api_key()
    def save_conversation_object(name: str, value: any):
        """Save a conversation-scoped object."""
        return save_as(name=name, obj=value, conversation_scoped=True)

    def save_global_object(name: str, value: any):
        """Save a global object."""
        return save_as(name=name, obj=value, conversation_scoped=False)

    def multiply_numbers(a: int, b: int) -> int:
        """Multiply two numbers."""
        return a * b

    def reverse_string(text: str) -> str:
        """Reverse a string."""
        return text[::-1]

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)
    agent.start_conversation()
    conversation_id = agent.current_conversation_id
    
    # Define load functions as closures that capture the agent
    def load_conversation_object(name: str) -> any:
        """Load a conversation-scoped object."""
        conversation_id = agent.current_conversation_id
        if conversation_id in agent.memory._conversation_objects and name in agent.memory._conversation_objects[conversation_id]:
            return agent.memory._conversation_objects[conversation_id][name]
        raise KeyError(f"Conversation-scoped object '{name}' not found")
    
    def load_global_object(name: str) -> any:
        """Load a global object."""
        if name in agent.memory._global_objects:
            return agent.memory._global_objects[name]
        raise KeyError(f"Global object '{name}' not found")
    
    # Add tools to agent
    agent.tool_functions = {}
    agent.tools = None
    agent.tool_schemas = {}
    tools = [
        save_conversation_object,
        load_conversation_object,
        save_global_object,
        load_global_object,
        multiply_numbers,
        reverse_string,
    ]
    for tool in tools:
        tool_name = tool.__name__
        agent.tool_functions[tool_name] = tool
    
    provider = agent.llm.provider
    prepared = prepare_tools_for_provider(tools, provider)
    agent.tools = prepared["tools"]
    agent.tool_schemas = prepared["schemas"]

    # Save multiple conversation-scoped objects - let agent figure out how
    agent.run("Save the number 42 as a conversation-scoped object named 'number'.")
    # Verify it was saved
    assert conversation_id in agent.memory._conversation_objects
    assert "number" in agent.memory._conversation_objects[conversation_id]
    assert agent.memory._conversation_objects[conversation_id]["number"] == 42
    assert "number" not in agent.memory._global_objects
    
    agent.run("Save the text 'hello' as a conversation-scoped object named 'text'.")
    # Verify it was saved
    assert "text" in agent.memory._conversation_objects[conversation_id]
    assert agent.memory._conversation_objects[conversation_id]["text"] == "hello"
    assert "text" not in agent.memory._global_objects
    
    agent.run("Save the list [1, 2, 3] as a conversation-scoped object named 'list_data'.")
    # Verify it was saved
    assert "list_data" in agent.memory._conversation_objects[conversation_id]
    assert agent.memory._conversation_objects[conversation_id]["list_data"] == [1, 2, 3]
    assert "list_data" not in agent.memory._global_objects

    # Save multiple global objects - let agent figure out how
    agent.run("Save the number 100 as a global object named 'global_number'.")
    # Verify it was saved
    assert "global_number" in agent.memory._global_objects
    assert agent.memory._global_objects["global_number"] == 100
    assert "global_number" not in agent.memory._conversation_objects.get(conversation_id, {})
    
    agent.run("Save the text 'world' as a global object named 'global_text'.")
    # Verify it was saved
    assert "global_text" in agent.memory._global_objects
    assert agent.memory._global_objects["global_text"] == "world"
    assert "global_text" not in agent.memory._conversation_objects.get(conversation_id, {})

    # Load conversation-scoped objects - agent just needs to call the tool with name
    result1 = agent.run(
        "Load the conversation-scoped object named 'number' and return its value.",
        return_mode="tool_output_value",
    )
    assert result1 == 42

    result2 = agent.run(
        "Load the conversation-scoped object named 'text' and return its value.",
        return_mode="tool_output_value",
    )
    assert result2 == "hello"

    # Load global objects - agent just needs to call the tool with name
    result3 = agent.run(
        "Load the global object named 'global_number' and return its value.",
        return_mode="tool_output_value",
    )
    assert result3 == 100

    result4 = agent.run(
        "Load the global object named 'global_text' and return its value.",
        return_mode="tool_output_value",
    )
    assert result4 == "world"


def test_agent_loads_from_storage_not_conversation():
    """Test that agent loads objects from storage, not from conversation text."""
    api_key = get_openai_api_key()

    def save_conversation_object(name: str, value: any):
        """Save a conversation-scoped object."""
        return save_as(name=name, obj=value, conversation_scoped=True)

    def save_global_object(name: str, value: any):
        """Save a global object."""
        return save_as(name=name, obj=value, conversation_scoped=False)

    def get_current_time() -> str:
        """Get the current time."""
        return "2024-01-01 12:00:00"

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)
    agent.start_conversation()
    conversation_id = agent.current_conversation_id

    # Define load functions as closures that capture the agent
    def load_conversation_object(name: str) -> any:
        """Load a conversation-scoped object."""
        conversation_id = agent.current_conversation_id
        if conversation_id in agent.memory._conversation_objects and name in agent.memory._conversation_objects[conversation_id]:
            return agent.memory._conversation_objects[conversation_id][name]
        raise KeyError(f"Conversation-scoped object '{name}' not found")

    def load_global_object(name: str) -> any:
        """Load a global object."""
        if name in agent.memory._global_objects:
            return agent.memory._global_objects[name]
        raise KeyError(f"Global object '{name}' not found")

    # Add tools to agent
    agent.tool_functions = {}
    agent.tools = None
    agent.tool_schemas = {}
    tools = [
        save_conversation_object,
        load_conversation_object,
        save_global_object,
        load_global_object,
        get_current_time,
    ]
    for tool in tools:
        tool_name = tool.__name__
        agent.tool_functions[tool_name] = tool

    provider = agent.llm.provider
    prepared = prepare_tools_for_provider(tools, provider)
    agent.tools = prepared["tools"]
    agent.tool_schemas = prepared["schemas"]

    # Save a conversation-scoped object
    test_data = {"original": "value", "count": 100}
    agent.run(
        f"Save the data {test_data} as a conversation-scoped object with the name 'test_data'.",
        return_mode="tool_output_value",
    )

    # Verify it was saved
    assert conversation_id in agent.memory._conversation_objects
    assert "test_data" in agent.memory._conversation_objects[conversation_id]
    original_saved = agent.memory._conversation_objects[conversation_id]["test_data"]
    assert original_saved == test_data

    # Now MODIFY the saved object directly in storage (not through conversation)
    agent.memory._conversation_objects[conversation_id]["test_data"] = {"modified": "value", "count": 999}

    # Load it - should get the MODIFIED value, not the original
    result = agent.run(
        "Load the conversation-scoped object named 'test_data' and return its value.",
        return_mode="tool_output_value",
    )

    # Verify it loaded the MODIFIED value, proving it's loading from storage
    assert result == {"modified": "value", "count": 999}
    assert result != test_data  # Should NOT be the original value

    # Test the same for global objects
    global_data = {"global_original": "value", "number": 50}
    agent.run(
        f"Save the data {global_data} as a global object with the name 'global_test'.",
        return_mode="tool_output_value",
    )

    # Verify it was saved
    assert "global_test" in agent.memory._global_objects
    original_global = agent.memory._global_objects["global_test"]
    assert original_global == global_data

    # Modify the global object directly in storage
    agent.memory._global_objects["global_test"] = {"global_modified": "value", "number": 999}

    # Load it - should get the MODIFIED value
    result2 = agent.run(
        "Load the global object named 'global_test' and return its value.",
        return_mode="tool_output_value",
    )

    # Verify it loaded the MODIFIED value
    assert result2 == {"global_modified": "value", "number": 999}
    assert result2 != global_data  # Should NOT be the original value

