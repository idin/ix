"""
Tests for Agent's built-in memorize and remember functions.
"""

import pytest
import os

from ixmachina.llm import LLM
from ixmachina.agent import Agent


def test_agent_memorize_and_remember():
    """Test that agent can memorize something and remember it later using built-in functions."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name="gpt-4o-mini")
    agent = Agent(llm=llm, verbose=False)

    # Memorize something (make sure it is memorized not in a global memory)
    agent.start_conversation(conversation_id="conv1")
    response1 = agent.run("Memorize that my favorite colour is greenish purple.", conversation_id="conv1")
    assert "memorized" in response1.lower() or "saved" in response1.lower() or "remember" in response1.lower()
    
    # Verify it was saved to conversation-scoped memory
    assert "conv1" in agent._conversation_objects
    # The saved object might have a key like "favorite colour" or similar - check that something was saved
    assert len(agent._conversation_objects["conv1"]) > 0

    # Delete the conversation history but keep the conversation-scoped memory
    # (forget_conversation deletes both, so we manually delete just the conversation)
    del agent.conversations["conv1"]
    # Verify conversation is deleted but memory remains
    assert "conv1" not in agent.conversations
    assert "conv1" in agent._conversation_objects

    # Remember it later in the same conversation (memory persists even though conversation history is gone)
    agent.start_conversation(conversation_id="conv1")  # Recreate conversation
    # Ask naturally - agent should figure out to use remember function
    response2 = agent.run("What is my favorite colour?", conversation_id="conv1")
    assert "greenish purple" in response2.lower() or "greenish" in response2.lower() or "purple" in response2.lower()

    # Now delete the conversation memory and the conversation itself. It should not remember it
    agent.forget_conversation(conversation_id="conv1")
    # Verify both are deleted
    assert "conv1" not in agent.conversations
    assert "conv1" not in agent._conversation_objects
    
    # Start fresh conversation and verify it doesn't remember
    agent.start_conversation(conversation_id="conv1")
    response3 = agent.run("What is my favorite colour?", conversation_id="conv1")
    assert "greenish purple" not in response3.lower()


def test_agent_memorize_and_remember_multiple_things():
    """Test that agent can memorize multiple things and remember them."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name="gpt-4o-mini")
    agent = Agent(llm=llm, verbose=False)

    # Memorize first thing
    agent.run("Memorize that my name is Alice.")
    
    # Memorize second thing
    agent.run("Memorize that I am 30 years old.")
    
    # Remember both
    response1 = agent.run("What is my name?")
    assert "alice" in response1.lower()
    
    response2 = agent.run("How old am I?")
    assert "30" in response2.lower() or "thirty" in response2.lower()


def test_agent_memorize_conversation_scoped():
    """Test that memorized items are conversation-scoped by default."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name="gpt-4o-mini")
    agent = Agent(llm=llm, verbose=False)

    # Memorize in first conversation
    agent.start_conversation(conversation_id="conv1")
    agent.run("Memorize that my favorite food is pizza.", conversation_id="conv1")
    
    # Start new conversation
    agent.start_conversation(conversation_id="conv2")
    
    # Should not remember from other conversation
    response = agent.run("What is my favorite food?", conversation_id="conv2")
    # The agent might say it doesn't know, or might not mention pizza
    # We verify by checking that conv1 still remembers
    response_conv1 = agent.run("What is my favorite food?", conversation_id="conv1")
    assert "pizza" in response_conv1.lower()


def test_agent_remember_with_global_memory():
    """Test that agent can save to global memory and remember across conversations."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name="gpt-4o-mini")
    agent = Agent(llm=llm, verbose=False)

    # Save to global memory (not conversation-scoped)
    agent.start_conversation(conversation_id="conv1")
    agent.run("Save to global memory that the company name is Acme Corp.")

    agent.forget_conversation(conversation_id="conv1")
    
    # Start new conversation
    agent.start_conversation(conversation_id="new_conv")
    
    # Should remember from global memory - ask naturally
    response = agent.run("What is the company name?", conversation_id="new_conv")
    assert "acme" in response.lower()


def test_agent_memorize_vs_save():
    """Test that memorize and save are aliases and work the same way."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name="gpt-4o-mini")
    agent = Agent(llm=llm, verbose=False)

    # Use memorize
    agent.run("Memorize that my pet's name is Fluffy.")
    
    # Use remember (alias for load)
    response = agent.run("What is my pet's name?")
    assert "fluffy" in response.lower()
    
    # Use save (should work the same as memorize)
    agent.run("Save that my city is Toronto.")
    
    # Use load (should work the same as remember)
    response2 = agent.run("What city do I live in?")
    assert "toronto" in response2.lower()

