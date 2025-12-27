"""
Tests for Agent save_as functionality.
"""

import pytest
import os

from ixmachina.llm import LLM
from ixmachina.agent import Agent


class WeirdClass:
    """
    A weird custom class for testing save_as functionality.
    """
    def __init__(self, name: str, value: int, metadata: dict):
        self.name = name
        self.value = value
        self.metadata = metadata
    
    def __str__(self) -> str:
        return f"WeirdClass(name={self.name}, value={self.value}, metadata={self.metadata})"
    
    def __eq__(self, other):
        if not isinstance(other, WeirdClass):
            return False
        return (
            self.name == other.name and
            self.value == other.value and
            self.metadata == other.metadata
        )


def test_agent_saves_and_retrieves_weird_class():
    """Test agent saves a weird class instance and retrieves it in another tool."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    def create_weird_object(name: str, value: int) -> WeirdClass:
        """
        Create a weird class instance and save it.
        
        Args:
            name: Name for the object.
            value: Numeric value for the object.
        
        Returns:
            WeirdClass instance wrapped in save_as.
        """
        weird_obj = WeirdClass(
            name=name,
            value=value,
            metadata={"created_by": "test", "version": 1}
        )
        return Agent.save_as(name="my_weird_object", value=weird_obj)

    def use_saved_object(weird_object: WeirdClass) -> str:
        """
        Use the saved weird object.
        
        Args:
            weird_object: The saved weird object (should be passed as [obj:my_weird_object]).
        
        Returns:
            String description of the object.
        """
        assert isinstance(weird_object, WeirdClass)
        return f"Object name: {weird_object.name}, value: {weird_object.value}, metadata: {weird_object.metadata}"

    llm = LLM(api_key=api_key, model_name="gpt-4")
    agent = Agent(llm=llm, tools=[create_weird_object, use_saved_object])
    agent.start_conversation()

    # First, create and save the weird object
    response1 = agent.run(
        "Call create_weird_object with name='test_obj' and value=42. Save the result.",
        return_raw_tool_result=True,
    )
    
    # The result should be the WeirdClass instance (not wrapped in ObjectToSave)
    assert isinstance(response1, WeirdClass)
    assert response1.name == "test_obj"
    assert response1.value == 42
    assert response1.metadata == {"created_by": "test", "version": 1}
    
    # Verify it was saved in the agent
    assert "my_weird_object" in agent._global_objects
    saved_obj = agent._global_objects["my_weird_object"]
    assert isinstance(saved_obj, WeirdClass)
    assert saved_obj == response1
    
    # Now use the saved object in another tool
    response2 = agent.run(
        "Call use_saved_object with weird_object set to '[obj:my_weird_object]'. Return only the tool result.",
        return_raw_tool_result=True,
    )
    
    # Should return the string description
    assert isinstance(response2, str)
    assert "test_obj" in response2
    assert "42" in response2
    assert "created_by" in response2 or "test" in response2


def test_agent_saves_object_in_list():
    """Test agent saves an object that's inside a list."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    def create_multiple_objects() -> list:
        """
        Create multiple weird objects, some saved, some not.
        
        Returns:
            List containing saved and unsaved objects.
        """
        obj1 = WeirdClass("first", 10, {"type": "saved"})
        obj2 = WeirdClass("second", 20, {"type": "unsaved"})
        obj3 = WeirdClass("third", 30, {"type": "saved"})
        
        return [
            Agent.save_as(name="first_obj", value=obj1),
            obj2,  # Not saved
            Agent.save_as(name="third_obj", value=obj3),
        ]

    def use_first_object(obj: WeirdClass) -> str:
        """
        Use the first saved object.
        
        Args:
            obj: The saved object (should be passed as [obj:first_obj]).
        
        Returns:
            String description.
        """
        return f"First object: {obj.name}, value: {obj.value}"

    llm = LLM(api_key=api_key, model_name="gpt-4")
    agent = Agent(llm=llm, tools=[create_multiple_objects, use_first_object])
    agent.start_conversation()

    # Create and save objects
    response1 = agent.run(
        "Call create_multiple_objects. Return only the tool result.",
        return_raw_tool_result=True,
    )
    
    # Should return a list with WeirdClass instances (ObjectToSave unwrapped)
    assert isinstance(response1, list)
    assert len(response1) == 3
    assert all(isinstance(obj, WeirdClass) for obj in response1)
    assert response1[0].name == "first"
    assert response1[1].name == "second"
    assert response1[2].name == "third"
    
    # Verify saved objects
    assert "first_obj" in agent._global_objects
    assert "third_obj" in agent._global_objects
    assert response1[1] not in agent._global_objects.values()  # Second object not saved
    
    # Use the first saved object
    response2 = agent.run(
        "Call use_first_object with obj set to '[obj:first_obj]'. Return only the tool result.",
        return_raw_tool_result=True,
    )
    
    assert isinstance(response2, str)
    assert "first" in response2
    assert "10" in response2


def test_agent_saves_object_in_dict():
    """Test agent saves an object that's inside a dictionary."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    def create_object_dict() -> dict:
        """
        Create a dictionary containing saved objects.
        
        Returns:
            Dictionary with saved objects.
        """
        obj1 = WeirdClass("alpha", 100, {"group": "A"})
        obj2 = WeirdClass("beta", 200, {"group": "B"})
        
        return {
            "saved": Agent.save_as(name="alpha_obj", value=obj1),
            "unsaved": obj2,
            "nested": {
                "deep": Agent.save_as(name="beta_obj", value=obj2),
            }
        }

    def use_alpha_object(obj: WeirdClass) -> str:
        """
        Use the alpha saved object.
        
        Args:
            obj: The saved object (should be passed as [obj:alpha_obj]).
        
        Returns:
            String description.
        """
        return f"Alpha: {obj.name}, {obj.value}"

    llm = LLM(api_key=api_key, model_name="gpt-4")
    agent = Agent(llm=llm, tools=[create_object_dict, use_alpha_object])
    agent.start_conversation()

    # Create and save objects
    response1 = agent.run(
        "Call the create_object_dict function. Execute the tool and return only the tool result. Do not show the function call or any other text.",
        return_raw_tool_result=True,
    )
    
    # Should return a dict with WeirdClass instances (ObjectToSave unwrapped)
    assert isinstance(response1, dict)
    assert isinstance(response1["saved"], WeirdClass)
    assert isinstance(response1["unsaved"], WeirdClass)
    assert isinstance(response1["nested"]["deep"], WeirdClass)
    assert response1["saved"].name == "alpha"
    assert response1["nested"]["deep"].name == "beta"
    
    # Verify saved objects
    assert "alpha_obj" in agent._global_objects
    assert "beta_obj" in agent._global_objects
    
    # Use the alpha saved object
    response2 = agent.run(
        "Call use_alpha_object with obj set to '[obj:alpha_obj]'. Return only the tool result.",
        return_raw_tool_result=True,
    )
    
    assert isinstance(response2, str)
    assert "alpha" in response2
    assert "100" in response2

