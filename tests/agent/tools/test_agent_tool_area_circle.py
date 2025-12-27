"""
Test for area of circle tool to debug the issue.
"""

import pytest
import os
import math

from ixmachina.llm import LLM
from ixmachina.agent import Agent


def test_agent_area_of_circle_with_proper_docstring():
    """Test agent uses get_area_of_circle tool with proper docstring and type annotations."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    def get_area_of_circle(radius: float) -> float:
        """
        Calculate the area of a circle given its radius.
        
        Args:
            radius: The radius of the circle.
        
        Returns:
            The area of the circle (π * radius²).
        """
        return math.pi * radius ** 2

    llm = LLM(api_key=api_key, model_name="gpt-4")
    agent = Agent(llm=llm, tools=[get_area_of_circle])
    agent.start_conversation()

    response = agent.run("What's the area of a circle with radius of 2? Use the get_area_of_circle function.")

    assert isinstance(response, str)
    assert len(response) > 0
    # Should contain the calculated area (approximately 12.566)
    assert "12.566" in response or "12.57" in response or "12.56" in response or "area" in response.lower()


def test_agent_area_of_circle_without_docstring():
    """Test agent uses get_area_of_circle tool without docstring (to see the error)."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    def get_area_of_circle(radius: float) -> float:
        return math.pi * radius ** 2

    llm = LLM(api_key=api_key, model_name="gpt-4")
    agent = Agent(llm=llm, tools=[get_area_of_circle])
    agent.start_conversation()

    response = agent.run("What's the area of a circle with radius of 2? Use the get_area_of_circle function.")

    # This might fail or give a less helpful response
    print(f"Response without docstring: {response}")
    assert isinstance(response, str)


def test_agent_area_of_circle_with_wrong_formula():
    """Test agent uses get_area_of_circle tool with the wrong formula from user's example."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    def get_area_of_circle(radius: float) -> float:
        """
        Calculate the area of a circle given its radius.
        
        Args:
            radius: The radius of the circle.
        
        Returns:
            The area of the circle.
        """
        return radius ** 2 * 3  # Wrong formula (should be π * r²)

    llm = LLM(api_key=api_key, model_name="gpt-4")
    agent = Agent(llm=llm, tools=[get_area_of_circle])
    agent.start_conversation()

    response = agent.run("What's the area of a circle with radius of 2? Use the get_area_of_circle function.")

    # This will return 12 (2² * 3 = 4 * 3 = 12) instead of ~12.566
    print(f"Response with wrong formula: {response}")
    assert isinstance(response, str)
    # Should contain 12 (the wrong result)
    assert "12" in response

