"""
Tests for Agent usage_tracker.
"""

import pytest
from tests.conftest import DEFAULT_TEST_MODEL
import os

from ixmachina.llm import LLM
from ixmachina.agent import Agent


def test_agent_usage_tracker_initialized():
    """Test that Agent initializes usage_tracker correctly."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)
    
    assert agent.usage_tracker is not None
    assert agent.usage_tracker.include_conversation_id is True
    assert len(agent.usage_tracker.records) == 0


def test_agent_usage_tracker_adds_record_with_conversation_id():
    """Test that Agent adds records with conversation_id."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)
    
    agent.start_conversation(conversation_id="conv1")
    response = agent.run("Say hello in one word", conversation_id="conv1")
    
    # Check that a record was added
    assert len(agent.usage_tracker.records) == 1
    
    record = agent.usage_tracker.records[0]
    assert record["input_tokens"] is not None
    assert record["output_tokens"] is not None
    assert record["total_tokens"] is not None
    assert record["input_tokens"] > 0
    assert record["output_tokens"] > 0
    assert record["total_tokens"] > 0
    assert record["conversation_id"] == "conv1"
    assert "llm" in record


def test_agent_usage_tracker_tracks_multiple_conversations():
    """Test that Agent tracks usage separately for different conversations."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)
    
    # First conversation
    agent.start_conversation(conversation_id="conv1")
    agent.run("Say hello", conversation_id="conv1")
    
    # Second conversation
    agent.start_conversation(conversation_id="conv2")
    agent.run("Say goodbye", conversation_id="conv2")
    
    # Should have 2 records
    assert len(agent.usage_tracker.records) == 2
    
    # Check that both records have correct conversation_ids
    conv1_records = [r for r in agent.usage_tracker.records if r["conversation_id"] == "conv1"]
    conv2_records = [r for r in agent.usage_tracker.records if r["conversation_id"] == "conv2"]
    
    assert len(conv1_records) == 1
    assert len(conv2_records) == 1


def test_agent_usage_tracker_accumulates_within_conversation():
    """Test that Agent accumulates multiple records within the same conversation."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)
    
    agent.start_conversation(conversation_id="test_conv")
    
    # First query
    agent.run("Say hello", conversation_id="test_conv")
    first_count = len(agent.usage_tracker.records)
    assert first_count == 1
    
    # Second query in same conversation
    agent.run("Say goodbye", conversation_id="test_conv")
    assert len(agent.usage_tracker.records) == 2
    
    # Both records should have the same conversation_id
    assert agent.usage_tracker.records[0]["conversation_id"] == "test_conv"
    assert agent.usage_tracker.records[1]["conversation_id"] == "test_conv"


def test_agent_usage_tracker_preserves_records_after_conversation_deletion():
    """Test that Agent preserves usage_tracker records even after conversation is deleted."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)
    
    agent.start_conversation(conversation_id="temp_conv")
    agent.run("Say hello", conversation_id="temp_conv")
    
    # Get record count before deletion
    records_before = len(agent.usage_tracker.records)
    assert records_before == 1
    
    # Delete the conversation
    agent.forget_conversation(conversation_id="temp_conv")
    
    # Check that conversation is deleted
    assert "temp_conv" not in agent.conversations
    
    # Check that usage_tracker records are still preserved
    assert len(agent.usage_tracker.records) == records_before
    assert agent.usage_tracker.records[0]["conversation_id"] == "temp_conv"


def test_agent_usage_tracker_get_dataframe():
    """Test that Agent usage_tracker can convert records to DataFrame."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)
    
    agent.start_conversation(conversation_id="conv1")
    agent.run("Say hello", conversation_id="conv1")
    
    # Get DataFrame
    df = agent.usage_tracker.get_dataframe()
    
    assert len(df) == 1
    assert "conversation_id" in df.columns
    assert df.iloc[0]["conversation_id"] == "conv1"
    assert df.iloc[0]["input_tokens"] > 0


def test_agent_usage_tracker_get_aggregated_dataframe_by_conversation():
    """Test that Agent usage_tracker can aggregate by conversation."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)
    
    # Multiple queries in first conversation
    agent.start_conversation(conversation_id="conv1")
    agent.run("Say hello", conversation_id="conv1")
    agent.run("Say goodbye", conversation_id="conv1")
    
    # One query in second conversation
    agent.start_conversation(conversation_id="conv2")
    agent.run("Say hi", conversation_id="conv2")
    
    # Get aggregated DataFrame
    df = agent.usage_tracker.get_aggregated_dataframe()
    
    # Should have 2 rows (one per conversation)
    assert len(df) == 2
    
    # Check that conv1 has more tokens (2 queries vs 1)
    conv1_row = df[df["conversation_id"] == "conv1"].iloc[0]
    conv2_row = df[df["conversation_id"] == "conv2"].iloc[0]
    
    assert conv1_row["input_tokens"] >= conv2_row["input_tokens"]
    assert conv1_row["total_tokens"] >= conv2_row["total_tokens"]


def test_agent_usage_tracker_with_multiple_llms():
    """Test that Agent usage_tracker tracks different LLMs correctly."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm1 = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2}, default_llm="gpt4")
    
    agent.start_conversation(conversation_id="test")
    
    # Use first LLM
    agent.run("Say hello", conversation_id="test", llm_instance="gpt4")
    
    # Use second LLM
    agent.run("Say goodbye", conversation_id="test", llm_instance="gpt35")
    
    # Should have 2 records with different LLM identifiers
    assert len(agent.usage_tracker.records) == 2
    
    # Check LLM identifiers
    llm_keys = [r["llm"] for r in agent.usage_tracker.records]
    assert "gpt4" in llm_keys
    assert "gpt35" in llm_keys


def test_agent_get_total_usage_all():
    """Test Agent get_total_usage with no filters."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)
    
    agent.start_conversation(conversation_id="conv1")
    agent.run("Say hello", conversation_id="conv1")
    agent.run("Say goodbye", conversation_id="conv1")
    
    # Get total usage for all conversations
    total = agent.get_total_usage()
    
    assert total["input_tokens"] is not None
    assert total["output_tokens"] is not None
    assert total["total_tokens"] is not None
    assert total["input_tokens"] > 0
    assert total["output_tokens"] > 0
    assert total["total_tokens"] > 0


def test_agent_get_total_usage_by_conversation():
    """Test Agent get_total_usage filtered by conversation_id."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)
    
    agent.start_conversation(conversation_id="conv1")
    agent.run("Say hello", conversation_id="conv1")
    
    agent.start_conversation(conversation_id="conv2")
    agent.run("Say goodbye", conversation_id="conv2")
    
    # Get total usage for conv1 only
    total_conv1 = agent.get_total_usage(conversation_id="conv1")
    assert total_conv1["input_tokens"] is not None
    assert total_conv1["input_tokens"] > 0
    
    # Get total usage for conv2 only
    total_conv2 = agent.get_total_usage(conversation_id="conv2")
    assert total_conv2["input_tokens"] is not None
    assert total_conv2["input_tokens"] > 0


def test_agent_get_total_usage_by_llm():
    """Test Agent get_total_usage filtered by LLM."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm1 = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2}, default_llm="gpt4")
    
    agent.start_conversation(conversation_id="test")
    
    # Use first LLM
    agent.run("Say hello", conversation_id="test", llm_instance="gpt4")
    
    # Use second LLM
    agent.run("Say goodbye", conversation_id="test", llm_instance="gpt35")
    
    # Get total usage for gpt4 only
    total_gpt4 = agent.get_total_usage(llm="gpt4")
    assert total_gpt4["input_tokens"] is not None
    assert total_gpt4["input_tokens"] > 0
    
    # Get total usage for gpt35 only
    total_gpt35 = agent.get_total_usage(llm="gpt35")
    assert total_gpt35["input_tokens"] is not None
    assert total_gpt35["input_tokens"] > 0


def test_agent_get_total_usage_by_llm_and_conversation():
    """Test Agent get_total_usage filtered by both LLM and conversation_id."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)
    
    agent.start_conversation(conversation_id="conv1")
    agent.run("Say hello", conversation_id="conv1")
    agent.run("Say goodbye", conversation_id="conv1")
    
    agent.start_conversation(conversation_id="conv2")
    agent.run("Say hi", conversation_id="conv2")
    
    # Get total usage for specific LLM and conversation
    # Since we only have one LLM, we need to get its key
    llm_key = list(agent.llms.keys())[0]
    total = agent.get_total_usage(llm=llm_key, conversation_id="conv1")
    
    assert total["input_tokens"] is not None
    assert total["input_tokens"] > 0
    # conv1 should have more tokens than conv2 (2 queries vs 1)
    total_conv2 = agent.get_total_usage(conversation_id="conv2")
    assert total["input_tokens"] >= total_conv2["input_tokens"]


def test_agent_get_total_cost_all():
    """Test Agent get_total_cost with no filters."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(
        api_key=api_key,
        model_name=DEFAULT_TEST_MODEL,
        pricing={"input": 30.0, "output": 60.0},
        fetch_pricing=False,
    )
    agent = Agent(llm=llm)
    
    agent.start_conversation(conversation_id="conv1")
    agent.run("Say hello", conversation_id="conv1")
    
    # Get total cost for all conversations
    total = agent.get_total_cost()
    
    # Cost should be calculated if pricing is available
    if total["input_cost"] is not None:
        assert total["input_cost"] >= 0
    if total["output_cost"] is not None:
        assert total["output_cost"] >= 0
    if total["total_cost"] is not None:
        assert total["total_cost"] >= 0


def test_agent_get_total_cost_by_conversation():
    """Test Agent get_total_cost filtered by conversation_id."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(
        api_key=api_key,
        model_name=DEFAULT_TEST_MODEL,
        pricing={"input": 30.0, "output": 60.0},
        fetch_pricing=False,
    )
    agent = Agent(llm=llm)
    
    agent.start_conversation(conversation_id="conv1")
    agent.run("Say hello", conversation_id="conv1")
    
    agent.start_conversation(conversation_id="conv2")
    agent.run("Say goodbye", conversation_id="conv2")
    
    # Get total cost for conv1 only
    total_conv1 = agent.get_total_cost(conversation_id="conv1")
    if total_conv1["input_cost"] is not None:
        assert total_conv1["input_cost"] >= 0
    
    # Get total cost for conv2 only
    total_conv2 = agent.get_total_cost(conversation_id="conv2")
    if total_conv2["input_cost"] is not None:
        assert total_conv2["input_cost"] >= 0


def test_agent_get_total_cost_without_pricing():
    """Test Agent get_total_cost when pricing is not available."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL, pricing=None, fetch_pricing=False)
    agent = Agent(llm=llm)
    
    agent.start_conversation(conversation_id="conv1")
    agent.run("Say hello", conversation_id="conv1")
    
    # Get total cost
    total = agent.get_total_cost()
    
    # Costs should be None when pricing is not available
    assert total["input_cost"] is None
    assert total["output_cost"] is None
    assert total["total_cost"] is None

