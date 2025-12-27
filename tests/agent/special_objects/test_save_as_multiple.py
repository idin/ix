"""
Tests for Agent save_as multiple objects functionality.
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


def test_agent_saves_multiple_objects_with_kwargs():
    """Test agent saves multiple objects using kwargs syntax."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    def create_and_save_multiple() -> list:
        """
        Create multiple weird objects and save them all at once.
        
        Returns:
            List of saved objects.
        """
        obj1 = WeirdClass("alpha", 100, {"group": "A"})
        obj2 = WeirdClass("beta", 200, {"group": "B"})
        obj3 = WeirdClass("gamma", 300, {"group": "C"})
        
        return Agent.save_as(
            first_obj=obj1,
            second_obj=obj2,
            third_obj=obj3,
        )

    def use_first_object(obj: WeirdClass) -> str:
        """
        Use the first saved object.
        
        Args:
            obj: The saved object (should be passed as [obj:first_obj]).
        
        Returns:
            String description.
        """
        assert isinstance(obj, WeirdClass)
        return f"First: {obj.name}, {obj.value}"

    def use_second_object(obj: WeirdClass) -> str:
        """
        Use the second saved object.
        
        Args:
            obj: The saved object (should be passed as [obj:second_obj]).
        
        Returns:
            String description.
        """
        assert isinstance(obj, WeirdClass)
        return f"Second: {obj.name}, {obj.value}"

    llm = LLM(api_key=api_key, model_name="gpt-4")
    agent = Agent(
        llm=llm,
        tools=[create_and_save_multiple, use_first_object, use_second_object]
    )
    agent.start_conversation()

    # Create and save multiple objects
    response1 = agent.run(
        "Call create_and_save_multiple. Execute the tool and return only the tool result. Do not show the function call or any other text.",
        return_raw_tool_result=True,
    )
    
    # Should return a list of WeirdClass instances (ObjectsToSave unwrapped)
    assert isinstance(response1, list)
    assert len(response1) == 3
    assert all(isinstance(obj, WeirdClass) for obj in response1)
    assert response1[0].name == "alpha"
    assert response1[1].name == "beta"
    assert response1[2].name == "gamma"
    
    # Verify all objects were saved
    assert "first_obj" in agent._global_objects
    assert "second_obj" in agent._global_objects
    assert "third_obj" in agent._global_objects
    
    saved_first = agent._global_objects["first_obj"]
    saved_second = agent._global_objects["second_obj"]
    saved_third = agent._global_objects["third_obj"]
    
    assert isinstance(saved_first, WeirdClass)
    assert isinstance(saved_second, WeirdClass)
    assert isinstance(saved_third, WeirdClass)
    assert saved_first == response1[0]
    assert saved_second == response1[1]
    assert saved_third == response1[2]
    
    # Use the first saved object
    response2 = agent.run(
        "Call use_first_object with obj set to '[obj:first_obj]'. Execute the tool and return only the tool result. Do not show the function call or any other text.",
        return_raw_tool_result=True,
    )
    
    assert isinstance(response2, str)
    assert "alpha" in response2
    assert "100" in response2
    
    # Use the second saved object
    response3 = agent.run(
        "Call use_second_object with obj set to '[obj:second_obj]'. Execute the tool and return only the tool result. Do not show the function call or any other text.",
        return_raw_tool_result=True,
    )
    
    assert isinstance(response3, str)
    assert "beta" in response3
    assert "200" in response3


def test_agent_saves_multiple_mixed_types():
    """Test agent saves multiple objects of different types using kwargs."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    def create_mixed_objects() -> list:
        """
        Create and save objects of different types.
        
        Returns:
            List of saved objects.
        """
        weird_obj = WeirdClass("test", 42, {"type": "weird"})
        number = 12345
        text = "hello world"
        data_dict = {"key": "value", "nested": {"inner": 999}}
        
        return Agent.save_as(
            weird=weird_obj,
            number=number,
            text=text,
            data=data_dict,
        )

    def use_saved_number(num: int) -> str:
        """
        Use the saved number.
        
        Args:
            num: The saved number (should be passed as [obj:number]).
        
        Returns:
            String with the number.
        """
        return f"Number is: {num}"

    def use_saved_text(text: str) -> str:
        """
        Use the saved text.
        
        Args:
            text: The saved text (should be passed as [obj:text]).
        
        Returns:
            String with the text.
        """
        return f"Text is: {text}"

    llm = LLM(api_key=api_key, model_name="gpt-4")
    agent = Agent(
        llm=llm,
        tools=[create_mixed_objects, use_saved_number, use_saved_text]
    )
    agent.start_conversation()

    # Create and save mixed objects
    response1 = agent.run(
        "Call create_mixed_objects. Execute the tool and return only the tool result. Do not show the function call or any other text.",
        return_raw_tool_result=True,
    )
    
    # Should return a list with different types
    assert isinstance(response1, list)
    assert len(response1) == 4
    assert isinstance(response1[0], WeirdClass)
    assert isinstance(response1[1], int)
    assert isinstance(response1[2], str)
    assert isinstance(response1[3], dict)
    
    # Verify all objects were saved with correct types
    assert "weird" in agent._global_objects
    assert "number" in agent._global_objects
    assert "text" in agent._global_objects
    assert "data" in agent._global_objects
    
    assert isinstance(agent._global_objects["weird"], WeirdClass)
    assert isinstance(agent._global_objects["number"], int)
    assert isinstance(agent._global_objects["text"], str)
    assert isinstance(agent._global_objects["data"], dict)
    assert agent._global_objects["number"] == 12345
    assert agent._global_objects["text"] == "hello world"
    
    # Use the saved number
    response2 = agent.run(
        "Call use_saved_number with num set to '[obj:number]'. Execute the tool and return only the tool result. Do not show the function call or any other text.",
        return_raw_tool_result=True,
    )
    
    assert isinstance(response2, str)
    assert "12345" in response2
    
    # Use the saved text
    response3 = agent.run(
        "Call use_saved_text with text set to '[obj:text]'. Execute the tool and return only the tool result. Do not show the function call or any other text.",
        return_raw_tool_result=True,
    )
    
    assert isinstance(response3, str)
    assert "hello world" in response3

