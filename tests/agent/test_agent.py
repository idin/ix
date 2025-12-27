"""
Tests for Agent class.
"""

import pytest
import os

from ixmachina.llm import LLM
from ixmachina.agent import Agent


def test_agent_asks_what_is_capital_of_germany():
    """Test agent can answer question about capital of Germany."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name="gpt-4")
    agent = Agent(llm=llm)
    agent.start_conversation()

    response = agent.run("What is the capital of Germany?")

    assert isinstance(response, str)
    assert len(response) > 0
    # The response should contain "Berlin" (case-insensitive)
    assert "berlin" in response.lower()

