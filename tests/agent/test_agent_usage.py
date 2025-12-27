"""
Tests for Agent usage tracking by conversation.
"""

import pytest
import os

from ixmachina.llm import LLM
from ixmachina.agent import Agent


def test_agent_tracks_usage_by_conversation():
    """Test that Agent tracks usage separately for each conversation."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name="gpt-4")
    agent = Agent(llm=llm)

    # Start first conversation
    agent.start_conversation(conversation_id="conv1")
    response1 = agent.run("Say hello in one word", conversation_id="conv1")

    # Check that usage was tracked for conv1
    conv1_records = [r for r in agent.usage_tracker.records if r["conversation_id"] == "conv1"]
    assert len(conv1_records) == 1
    conv1_usage = conv1_records[0]
    assert conv1_usage["input_tokens"] is not None
    assert conv1_usage["input_tokens"] > 0
    assert conv1_usage["output_tokens"] is not None
    assert conv1_usage["output_tokens"] > 0
    assert conv1_usage["total_tokens"] is not None
    assert conv1_usage["total_tokens"] > 0

    # Start second conversation
    agent.start_conversation(conversation_id="conv2")
    response2 = agent.run("Say goodbye in one word", conversation_id="conv2")

    # Check that usage was tracked for conv2
    conv2_records = [r for r in agent.usage_tracker.records if r["conversation_id"] == "conv2"]
    assert len(conv2_records) == 1
    conv2_usage = conv2_records[0]
    assert conv2_usage["input_tokens"] is not None
    assert conv2_usage["input_tokens"] > 0
    assert conv2_usage["output_tokens"] is not None
    assert conv2_usage["output_tokens"] > 0
    assert conv2_usage["total_tokens"] is not None
    assert conv2_usage["total_tokens"] > 0

    # Check that conv1 usage is still there and unchanged
    conv1_records_after = [r for r in agent.usage_tracker.records if r["conversation_id"] == "conv1"]
    assert len(conv1_records_after) == 1
    assert conv1_records_after[0]["total_tokens"] == conv1_usage["total_tokens"]

    # Both conversations should have independent usage tracking
    assert conv1_usage["total_tokens"] > 0
    assert conv2_usage["total_tokens"] > 0


def test_agent_accumulates_usage_within_conversation():
    """Test that Agent accumulates usage across multiple queries in the same conversation."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name="gpt-4")
    agent = Agent(llm=llm)

    agent.start_conversation(conversation_id="test_conv")

    # First query
    response1 = agent.run("Say hello", conversation_id="test_conv")
    first_records = [r for r in agent.usage_tracker.records if r["conversation_id"] == "test_conv"]
    assert len(first_records) == 1
    first_usage = first_records[0]

    # Second query in same conversation
    response2 = agent.run("Say goodbye", conversation_id="test_conv")
    second_records = [r for r in agent.usage_tracker.records if r["conversation_id"] == "test_conv"]
    assert len(second_records) == 2
    
    # Calculate totals for the conversation
    total_input = sum(r["input_tokens"] for r in second_records if r["input_tokens"] is not None)
    total_output = sum(r["output_tokens"] for r in second_records if r["output_tokens"] is not None)
    total_tokens = sum(r["total_tokens"] for r in second_records if r["total_tokens"] is not None)

    # Usage should have accumulated (total should be greater than first record)
    assert total_input >= first_usage["input_tokens"]
    assert total_output >= first_usage["output_tokens"]
    assert total_tokens >= first_usage["total_tokens"]


def test_agent_preserves_usage_after_conversation_deletion():
    """Test that Agent preserves usage tracking even after conversation is deleted."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name="gpt-4")
    agent = Agent(llm=llm)

    agent.start_conversation(conversation_id="temp_conv")
    response = agent.run("Say hello", conversation_id="temp_conv")

    # Get usage before deletion
    records_before = [r for r in agent.usage_tracker.records if r["conversation_id"] == "temp_conv"]
    assert len(records_before) == 1
    usage_before = records_before[0].copy()
    assert usage_before["total_tokens"] is not None
    assert usage_before["total_tokens"] > 0

    # Delete the conversation
    agent.forget_conversation(conversation_id="temp_conv")

    # Check that conversation is deleted
    assert "temp_conv" not in agent.conversations

    # Check that usage_tracker records are still preserved
    records_after = [r for r in agent.usage_tracker.records if r["conversation_id"] == "temp_conv"]
    assert len(records_after) == 1
    assert records_after[0]["total_tokens"] == usage_before["total_tokens"]

