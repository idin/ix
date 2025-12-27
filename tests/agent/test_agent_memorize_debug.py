"""
Debug test to investigate memorize/remember failures.

Tests the save/load/memorize/remember built-in functions to understand
why the agent isn't successfully storing or retrieving objects.
"""

import os
import pytest
from ixmachina.llm import LLM
from ixmachina.agent import Agent


def test_memorize_saves_to_conversation_objects():
    """Test that memorize actually saves to _conversation_objects."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name="gpt-4o-mini")
    agent = Agent(llm=llm, verbose=False)

    # Start conversation
    agent.start_conversation(conversation_id="conv1")
    
    # Check initial state
    assert "conv1" not in agent._conversation_objects or len(agent._conversation_objects["conv1"]) == 0
    
    # Memorize something
    response = agent.run("Memorize that my favorite food is pizza.", conversation_id="conv1")
    
    # Check if something was saved
    print(f"\nResponse: {response}")
    print(f"Conversation objects in conv1: {agent._conversation_objects.get('conv1', {})}")
    print(f"Global objects: {agent._global_objects}")
    
    # Assert that something was saved
    has_conv_objects = "conv1" in agent._conversation_objects and len(agent._conversation_objects["conv1"]) > 0
    has_global_objects = len(agent._global_objects) > 0
    
    assert has_conv_objects or has_global_objects, (
        f"No objects were saved after memorize. "
        f"Conv objects: {agent._conversation_objects.get('conv1', {})}, "
        f"Global objects: {agent._global_objects}"
    )


def test_save_to_global_memory():
    """Test that 'save to global memory' works."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name="gpt-4o-mini")
    agent = Agent(llm=llm, verbose=False)

    # Start conversation
    agent.start_conversation(conversation_id="conv1")
    
    # Check initial state
    assert len(agent._global_objects) == 0
    
    # Save to global memory
    response = agent.run("Save to global memory that the company name is Acme Corp.", conversation_id="conv1")
    
    # Check if something was saved
    print(f"\nResponse: {response}")
    print(f"Global objects: {agent._global_objects}")
    print(f"Conversation objects in conv1: {agent._conversation_objects.get('conv1', {})}")
    
    # Assert that something was saved to global
    assert len(agent._global_objects) > 0, (
        f"No objects were saved to global memory. "
        f"Global objects: {agent._global_objects}"
    )


def test_list_objects_after_memorize():
    """Test that list_objects shows memorized items."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name="gpt-4o-mini")
    agent = Agent(llm=llm, verbose=False)

    # Start conversation
    agent.start_conversation(conversation_id="conv1")
    
    # Memorize something
    agent.run("Memorize that my favorite colour is blue.", conversation_id="conv1")
    
    # List objects
    response = agent.run("List all memorized objects.", conversation_id="conv1")
    
    print(f"\nList objects response: {response}")
    print(f"Conversation objects in conv1: {agent._conversation_objects.get('conv1', {})}")
    print(f"Global objects: {agent._global_objects}")
    
    # The response should mention at least one object
    # or the storage should have objects
    has_objects = (
        ("conv1" in agent._conversation_objects and len(agent._conversation_objects["conv1"]) > 0) or
        len(agent._global_objects) > 0
    )
    
    assert has_objects, f"No objects found after memorize. Response: {response}"


def test_remember_after_memorize():
    """Test the full memorize -> remember cycle."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name="gpt-4o-mini")
    agent = Agent(llm=llm, verbose=False)

    # Start conversation
    agent.start_conversation(conversation_id="conv1")
    
    # Memorize
    response1 = agent.run("Memorize this: my lucky number is 42.", conversation_id="conv1")
    print(f"\nMemorize response: {response1}")
    
    # Check storage
    print(f"After memorize - Conv objects: {agent._conversation_objects.get('conv1', {})}")
    print(f"After memorize - Global objects: {agent._global_objects}")
    
    # List to see what's available
    response2 = agent.run("List all saved objects.", conversation_id="conv1")
    print(f"\nList response: {response2}")
    
    # Try to remember
    response3 = agent.run("Remember what my lucky number is.", conversation_id="conv1")
    print(f"\nRemember response: {response3}")
    
    # Check if it found the number
    assert "42" in response3 or "forty-two" in response3.lower(), (
        f"Agent couldn't remember the lucky number. "
        f"Storage: {agent._conversation_objects.get('conv1', {})} / {agent._global_objects}"
    )

