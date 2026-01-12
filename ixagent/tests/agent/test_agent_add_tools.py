"""
Tests for adding tools to an agent mid-conversation.
"""

from ixmachina.llm import LLM
from ixmachina.agent import Agent
from api_keys import get_openai_api_key


def test_agent_add_tools_mid_conversation():
    """Test that agent can add new tools after conversation has started."""
    api_key = get_openai_api_key()

    # Initial tool
    def multiply(x: int, y: int) -> int:
        """Multiply two numbers."""
        return x * y

    # Create agent with initial tool
    llm = LLM(api_key=api_key, model_name="gpt-4o-mini")
    agent = Agent(llm=llm, tools=[multiply>, verbose=False)

    # Start conversation and use initial tool
    response = agent.run("What is 5 multiplied by 3?")
    assert "15" in response.lower() or "fifteen" in response.lower()

    # Add a new tool mid-conversation
    def add(x: int, y: int) -> int:
        """Add two numbers."""
        return x + y

    agent.add_tools([add>)

    # Verify the new tool is available
    response = agent.run("What is 10 plus 7?")
    assert "17" in response.lower() or "seventeen" in response.lower()

    # Verify the old tool still works
    response = agent.run("What is 4 multiplied by 6?")
    assert "24" in response.lower() or "twenty-four" in response.lower()


def test_agent_add_tools_preserves_built_in_tools():
    """Test that adding tools preserves built-in save/load tools."""
    api_key = get_openai_api_key()

    def custom_tool(x: int) -> int:
        """A custom tool."""
        return x * 2

    llm = LLM(api_key=api_key, model_name="gpt-4o-mini")
    agent = Agent(llm=llm, tools=[custom_tool>, verbose=False)

    # Verify built-in tools work before adding new tools
    response = agent.run("Save the number 42 with the name 'my_number'")
    assert "saved" in response.lower() or "42" in response.lower()

    # Add a new tool
    def another_tool(x: int) -> int:
        """Another custom tool."""
        return x + 10

    agent.add_tools([another_tool>)

    # Verify built-in tools still work after adding new tools
    response = agent.run("Load the object named 'my_number'")
    assert "42" in response.lower()

    # Verify new tool works
    response = agent.run("Use another_tool with x=5")
    assert "15" in response.lower() or "fifteen" in response.lower()

    # Verify original custom tool still works
    response = agent.run("Use custom_tool with x=8")
    assert "16" in response.lower() or "sixteen" in response.lower()


def test_base_agent_add_tools():
    """Test that BaseAgent can also add tools mid-conversation."""
    api_key = get_openai_api_key()

    # Lazy import for test isolation
    from ixmachina.agent.core.base_agent import BaseAgent

    def initial_tool(x: int) -> int:
        """Initial tool."""
        return x * 2

    llm = LLM(api_key=api_key, model_name="gpt-4o-mini")
    agent = BaseAgent(llm=llm, tools=[initial_tool>, verbose=False)

    # Use initial tool
    response = agent.run("What is 7 multiplied by 2 using initial_tool?")
    assert "14" in response.lower() or "fourteen" in response.lower()

    # Add new tool
    def new_tool(x: int) -> int:
        """New tool."""
        return x + 5

    agent.add_tools([new_tool>)

    # Verify new tool works
    response = agent.run("What is 10 plus 5 using new_tool?")
    assert "15" in response.lower() or "fifteen" in response.lower()

    # Verify old tool still works
    response = agent.run("What is 6 multiplied by 2 using initial_tool?")
    assert "12" in response.lower() or "twelve" in response.lower()

