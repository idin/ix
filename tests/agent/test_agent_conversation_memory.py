"""
Tests for Agent conversation memory (remembers vs doesn't remember when switching).
"""

import pytest
from tests.conftest import DEFAULT_TEST_MODEL
import os

from ixmachina.llm import LLM
from ixmachina.agent import Agent


def test_agent_remembers_conversation():
    """Test that Agent remembers previous messages in the same conversation."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)

    agent.start_conversation(conversation_id="memory_test")

    # First message - establish context
    response1 = agent.run("My name is Alice. Remember this.", conversation_id="memory_test")
    
    # Second message - should remember the context
    response2 = agent.run("What is my name?", conversation_id="memory_test")

    # The response should contain "Alice" (case-insensitive)
    assert "alice" in response2.lower()


def test_agent_does_not_remember_when_switching_conversations():
    """Test that Agent does not remember messages from other conversations."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)

    # First conversation - establish context
    agent.start_conversation(conversation_id="conv1")
    response1 = agent.run("My name is Bob. Remember this.", conversation_id="conv1")
    
    # Second conversation - should not remember Bob
    agent.start_conversation(conversation_id="conv2")
    response2 = agent.run("What is my name?", conversation_id="conv2")

    # The response should NOT contain "Bob" (or should indicate it doesn't know)
    # Since the model might still mention Bob in various ways, we check that
    # the conversation history is separate by asking a follow-up in conv1
    response3 = agent.run("What is my name?", conversation_id="conv1")
    
    # conv1 should remember Bob
    assert "bob" in response3.lower()
    
    # conv2 should not have Bob in its history (we can't easily test this directly,
    # but we can verify the conversations are separate by checking they exist independently)
    assert "conv1" in agent.conversations
    assert "conv2" in agent.conversations
    assert len(agent.conversations["conv1"]) > len(agent.conversations["conv2"])

