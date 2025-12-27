"""
Tests for Agent class tool functionality.
"""

import pytest
import os

from ixmachina.llm import LLM
from ixmachina.agent import Agent


def test_agent_tool():
    """Test agent uses word_pingpong tool to look up dictionary values."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    # Dictionary for word_pingpong tool
    word_dictionary = {
        "xylophone": "A musical instrument with wooden bars",
        "quasar": "A massive celestial object emitting energy",
        "zephyr": "A gentle breeze from the west",
        "nebula": "A cloud of gas and dust in space",
    }

    def word_pingpong(word: str) -> str:
        """
        Look up the definition of a word from the dictionary.
        
        Args:
            word: The word to look up.
        
        Returns:
            The definition of the word, or a message if not found.
        """
        return word_dictionary.get(
            word.lower(), f"Word '{word}' not found in dictionary"
        )

    llm = LLM(api_key=api_key, model_name="gpt-4")
    agent = Agent(llm=llm, tools=[word_pingpong])
    agent.start_conversation()

    # Ask about a word that requires using the tool
    # Using "xylophone" which is in the dictionary
    response = agent.run("What is a xylophone?")

    assert isinstance(response, str)
    assert len(response) > 0
    # The response should contain the dictionary definition
    assert "musical instrument" in response.lower() or "wooden bars" in response.lower()

