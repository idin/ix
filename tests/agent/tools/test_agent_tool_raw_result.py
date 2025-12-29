"""
Tests for Agent class raw tool result functionality.
"""

import pytest
from tests.conftest import DEFAULT_TEST_MODEL
import os

from ixmachina.llm import LLM
from ixmachina.agent import Agent


def test_agent_returns_raw_tool_result_single():
    """Test agent returns raw tool result for single tool call."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    def add_numbers(a: int, b: int) -> int:
        """
        Add two numbers together.
        
        Args:
            a: First number.
            b: Second number.
        
        Returns:
            Sum of a and b.
        """
        return a + b

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[add_numbers])
    agent.start_conversation()

    # Ask to add numbers - should return raw integer result
    result = agent.run(
        "Add 5 and 3 together. Call the tool and return only the result.",
        return_mode="tool_output_value",
    )

    # Should return the raw integer result, not a string
    assert isinstance(result, int)
    assert result == 8


def test_agent_returns_raw_tool_result_multiple():
    """Test agent returns list of raw tool results for multiple tool calls."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    def multiply(a: int, b: int) -> int:
        """
        Multiply two numbers.
        
        Args:
            a: First number.
            b: Second number.
        
        Returns:
            Product of a and b.
        """
        return a * b

    def subtract(a: int, b: int) -> int:
        """
        Subtract second number from first.
        
        Args:
            a: First number.
            b: Second number.
        
        Returns:
            Difference of a and b.
        """
        return a - b

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[multiply, subtract])
    agent.start_conversation()

    # Ask to perform multiple operations - should return list of raw results
    result = agent.run(
        "Multiply 4 by 3, then subtract 2 from 10. Call both tools and return only the results.",
        return_mode="tool_output_value",
    )

    # Should return a list of raw integer results
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(r, int) for r in result)
    # Results could be in any order, so check both possibilities
    assert set(result) == {12, 8}


def test_agent_returns_string_when_no_tool_called():
    """Test agent returns string response when return_mode is tool_output_value but no tool is called."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[])
    agent.start_conversation()

    # Ask a simple question that doesn't require tools
    result = agent.run(
        "What is the capital of France?",
        return_mode="tool_output_value",
    )

    # Should return string response since no tool was called
    assert isinstance(result, str)
    assert "paris" in result.lower()

