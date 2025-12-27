"""
Test conversation-scoped memory isolation.

Replicates the exact scenario from the failing test to diagnose the issue.
"""

import os
import pytest
from ixmachina.llm import LLM
from ixmachina.agent import Agent


def test_memorize_conversation_scoped_exact_replica():
    """Exact replica of the failing test with added diagnostics."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name="gpt-4o-mini")
    agent = Agent(llm=llm, verbose=False)

    # Memorize in first conversation
    agent.start_conversation(conversation_id="conv1")
    agent.run("Memorize that my favorite food is pizza.", conversation_id="conv1")
    
    print(f"\nAfter memorize in conv1:")
    print(f"  Conv1 objects: {agent._conversation_objects.get('conv1', {})}")
    print(f"  Conv1 history length: {len(agent.conversations['conv1'])}")
    
    # Start new conversation
    agent.start_conversation(conversation_id="conv2")
    
    print(f"\nAfter starting conv2:")
    print(f"  Conv1 objects: {agent._conversation_objects.get('conv1', {})}")
    print(f"  Conv2 objects: {agent._conversation_objects.get('conv2', {})}")
    print(f"  Conv1 history length: {len(agent.conversations['conv1'])}")
    print(f"  Conv2 history length: {len(agent.conversations['conv2'])}")
    
    # Should not remember from other conversation
    response = agent.run("What is my favorite food?", conversation_id="conv2")
    print(f"\nConv2 response: {response}")
    
    # We verify by checking that conv1 still remembers
    response_conv1 = agent.run("What is my favorite food?", conversation_id="conv1")
    print(f"\nConv1 response: {response_conv1}")
    print(f"\nFinal state:")
    print(f"  Conv1 objects: {agent._conversation_objects.get('conv1', {})}")
    print(f"  Conv1 history length: {len(agent.conversations['conv1'])}")
    
    # The issue: conv1 should remember pizza
    assert "pizza" in response_conv1.lower(), (
        f"Conv1 couldn't remember pizza. "
        f"Objects: {agent._conversation_objects.get('conv1', {})}"
    )


def test_global_memory_after_forget_exact_replica():
    """Exact replica of the second failing test with added diagnostics."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name="gpt-4o-mini")
    agent = Agent(llm=llm, verbose=False)

    # Save to global memory (not conversation-scoped)
    agent.start_conversation(conversation_id="conv1")
    agent.run("Save to global memory that the company name is Acme Corp.", conversation_id="conv1")

    print(f"\nAfter save in conv1:")
    print(f"  Global objects: {agent._global_objects}")
    print(f"  Conv1 objects: {agent._conversation_objects.get('conv1', {})}")
    
    agent.forget_conversation(conversation_id="conv1")

    print(f"\nAfter forget conv1:")
    print(f"  Global objects: {agent._global_objects}")
    print(f"  Conversations: {list(agent.conversations.keys())}")
    
    # Start new conversation
    agent.start_conversation(conversation_id="new_conv")
    
    print(f"\nAfter starting new_conv:")
    print(f"  Global objects: {agent._global_objects}")
    print(f"  New_conv objects: {agent._conversation_objects.get('new_conv', {})}")
    
    # Should remember from global memory - ask naturally
    response = agent.run("What is the company name?", conversation_id="new_conv")
    print(f"\nNew_conv response: {response}")
    
    assert "acme" in response.lower(), (
        f"Couldn't remember from global memory. "
        f"Global objects: {agent._global_objects}"
    )

