"""
Tests for Agent class tool functionality with dictionary input.
"""

from tests.conftest import DEFAULT_TEST_MODEL

from ixmachina.llm import LLM
from ixmachina.agent import Agent
from api_keys import get_openai_api_key


def test_agent_tool_with_dictionary_input():
    """Test agent uses a tool that takes a dictionary and returns list of values."""
    api_key = get_openai_api_key()

    def get_dict_values(data: dict) -> list:
        """
        Get all values from a dictionary.
        
        Args:
            data: A dictionary to extract values from.
        
        Returns:
            A list of all values in the dictionary.
        """
        return list(data.values())

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[get_dict_values>)
    agent.start_conversation()

    # Ask the agent to use the tool with a dictionary
    # The agent should call the tool with a dictionary and get back the values

    dictionary = {'name': 'Alice', 'age': 30, 'city': 'Paris'}

    response = agent.run(
        f"Use the get_dict_values tool with this dictionary: {dictionary}. "
        "Do not repeat the dictionary structure in your response, only report the output of the tool."
    )

    assert isinstance(response, str)
    assert len(response) > 0
    # The response should mention the values from the dictionary
    # The tool should return ['Alice', 30, 'Paris'> or similar
    response_lower = response.lower()
    # ALL OF THE VALUES SHOULD BE MENTIONED IN THE RESPONSE
    for value in dictionary.values():
        assert str(value).lower() in response_lower

    # NO KEYS SHOULD BE MENTIONED IN THE RESPONSE
    for key in dictionary.keys():
        assert str(key).lower() not in response_lower

