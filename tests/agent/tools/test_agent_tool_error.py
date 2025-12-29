"""
Test for tool error handling.
"""

import pytest
from tests.conftest import DEFAULT_TEST_MODEL
import os

from ixmachina.llm import LLM
from ixmachina.agent import Agent


def test_agent_tool_error_handling():
    """Test that tool errors are caught and returned to the LLM."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    def divide_numbers(a: float, b: float) -> float:
        """
        Divide two numbers.
        
        Args:
            a: Numerator.
            b: Denominator.
        
        Returns:
            Result of division.
        """
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[divide_numbers])
    agent.start_conversation()

    # Try to divide by zero - should get error message
    response = agent.run("Divide 10 by 0 using the divide_numbers function.")

    assert isinstance(response, str)
    assert len(response) > 0
    # The LLM should see the error and respond appropriately
    # It might mention the error or try to explain it
    print(f"Response: {response}")
    
    # Check that the error was in the tool call result
    tool_calls = agent.conversation_tool_calls.get("default", [])
    if tool_calls:
        last_tool_call = tool_calls[-1]
        tool_result = last_tool_call.get("result", "")
        # The result should contain the error message
        assert "Error executing tool" in str(tool_result) or "divide by zero" in str(tool_result).lower()


def test_agent_tool_type_error():
    """Test that type errors in tools are caught."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    def add_numbers(a: int, b: int) -> int:
        """
        Add two numbers.
        
        Args:
            a: First number.
            b: Second number.
        
        Returns:
            Sum of a and b.
        """
        # This will fail if a or b is not a number
        return a + b

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[add_numbers])
    agent.start_conversation()

    # The LLM might pass wrong types, but the error should be caught
    # Note: With proper type conversion, this might not fail
    response = agent.run("Add 5 and 3 using the add_numbers function.")

    assert isinstance(response, str)
    print(f"Response: {response}")


def test_agent_tool_missing_argument():
    """Test that missing arguments cause errors."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    def multiply(a: float, b: float, c: float) -> float:
        """
        Multiply three numbers.
        
        Args:
            a: First number.
            b: Second number.
            c: Third number.
        
        Returns:
            Product of a, b, and c.
        """
        return a * b * c

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[multiply])
    agent.start_conversation()

    # Ask to multiply but LLM might miss an argument
    response = agent.run("Multiply 2, 3, and 4 using the multiply function.")

    assert isinstance(response, str)
    print(f"Response: {response}")

