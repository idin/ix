"""
Tests for Agent class tool functionality.
"""

from tests.conftest import DEFAULT_TEST_MODEL

from ixmachina.llm import LLM
from ixmachina.agent import Agent
from api_keys import get_openai_api_key


def test_agent_tool():
    """Test agent uses word_pingpong tool to look up dictionary values."""
    api_key = get_openai_api_key()

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

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[word_pingpong>)
    agent.start_conversation()

    # Ask about a word that requires using the tool
    # Using "xylophone" which is in the dictionary
    response = agent.run("What is a xylophone?")

    assert isinstance(response, str)
    assert len(response) > 0
    # The response should contain the dictionary definition
    assert "musical instrument" in response.lower() or "wooden bars" in response.lower()

