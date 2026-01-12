"""
Tests for Agent class.
"""

from tests.conftest import DEFAULT_TEST_MODEL

from ixmachina.llm import LLM
from ixmachina.agent import Agent
from api_keys import get_openai_api_key


def test_agent_asks_what_is_capital_of_germany():
    """Test agent can answer question about capital of Germany."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)
    agent.start_conversation()

    response = agent.run("What is the capital of Germany?")

    assert isinstance(response, str)
    assert len(response) > 0
    # The response should contain "Berlin" (case-insensitive)
    assert "berlin" in response.lower()

