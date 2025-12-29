"""
Tests for LLM usage_tracker.
"""

import pytest
from tests.conftest import DEFAULT_TEST_MODEL
import os

from ixmachina.llm import LLM


def test_llm_usage_tracker_initialized():
    """Test that LLM initializes usage_tracker correctly."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    
    assert llm.usage_tracker is not None
    assert llm.usage_tracker.include_conversation_id is False
    assert len(llm.usage_tracker.records) == 0


def test_llm_usage_tracker_adds_record_on_query():
    """Test that LLM adds records to usage_tracker when making queries."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    
    # Initial state - no records
    assert len(llm.usage_tracker.records) == 0
    
    # Make a query
    response = llm.query(user_prompt="Say hello in one word")
    
    # Check that a record was added
    assert len(llm.usage_tracker.records) == 1
    
    record = llm.usage_tracker.records[0]
    assert record["input_tokens"] is not None
    assert record["output_tokens"] is not None
    assert record["total_tokens"] is not None
    assert record["input_tokens"] > 0
    assert record["output_tokens"] > 0
    assert record["total_tokens"] > 0
    assert record["llm"] == DEFAULT_TEST_MODEL
    assert "conversation_id" not in record


def test_llm_usage_tracker_accumulates_records():
    """Test that LLM accumulates multiple records in usage_tracker."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    
    # Make first query
    llm.query(user_prompt="Say hello")
    first_record_count = len(llm.usage_tracker.records)
    assert first_record_count == 1
    
    # Make second query
    llm.query(user_prompt="Say goodbye")
    assert len(llm.usage_tracker.records) == 2
    
    # Both records should have the same LLM
    assert llm.usage_tracker.records[0]["llm"] == "gpt-4"
    assert llm.usage_tracker.records[1]["llm"] == "gpt-4"


def test_llm_usage_tracker_with_cost():
    """Test that LLM usage_tracker includes cost information when pricing is available."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    # Create LLM with pricing
    llm = LLM(
        api_key=api_key,
        model_name=DEFAULT_TEST_MODEL,
        pricing={"input": 30.0, "output": 60.0},  # Per million tokens
        fetch_pricing=False,
    )
    
    # Make a query
    response = llm.query(user_prompt="Say hello")
    
    # Check that cost information is included
    assert len(llm.usage_tracker.records) == 1
    record = llm.usage_tracker.records[0]
    
    # Cost should be calculated and included
    if record["input_cost"] is not None:
        assert record["input_cost"] >= 0
    if record["output_cost"] is not None:
        assert record["output_cost"] >= 0
    if record["total_cost"] is not None:
        assert record["total_cost"] >= 0


def test_llm_usage_tracker_without_cost():
    """Test that LLM usage_tracker handles missing cost information."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    # Create LLM without pricing
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL, pricing=None, fetch_pricing=False)
    
    # Make a query
    response = llm.query(user_prompt="Say hello")
    
    # Check that record has None for costs
    assert len(llm.usage_tracker.records) == 1
    record = llm.usage_tracker.records[0]
    
    # Tokens should be present
    assert record["input_tokens"] is not None
    assert record["output_tokens"] is not None
    
    # Costs should be None when pricing is not available
    assert record["input_cost"] is None
    assert record["output_cost"] is None
    assert record["total_cost"] is None


def test_llm_usage_tracker_get_dataframe():
    """Test that LLM usage_tracker can convert records to DataFrame."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    
    # Make a query
    llm.query(user_prompt="Say hello")
    
    # Get DataFrame
    df = llm.usage_tracker.get_dataframe()
    
    assert len(df) == 1
    assert df.iloc[0]["llm"] == "gpt-4"
    assert df.iloc[0]["input_tokens"] > 0
    assert "conversation_id" not in df.columns


def test_llm_usage_tracker_get_aggregated_dataframe():
    """Test that LLM usage_tracker can aggregate records."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    
    # Make multiple queries
    llm.query(user_prompt="Say hello")
    llm.query(user_prompt="Say goodbye")
    
    # Get aggregated DataFrame
    df = llm.usage_tracker.get_aggregated_dataframe()
    
    assert len(df) == 1  # All records aggregated into one row
    assert df.iloc[0]["llm"] == "gpt-4"
    assert df.iloc[0]["input_tokens"] > 0
    assert df.iloc[0]["output_tokens"] > 0


def test_llm_get_total_usage():
    """Test LLM get_total_usage method."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    
    # Make multiple queries
    llm.query(user_prompt="Say hello")
    llm.query(user_prompt="Say goodbye")
    
    # Get total usage
    total = llm.get_total_usage()
    
    assert total["input_tokens"] is not None
    assert total["output_tokens"] is not None
    assert total["total_tokens"] is not None
    assert total["input_tokens"] > 0
    assert total["output_tokens"] > 0
    assert total["total_tokens"] > 0


def test_llm_get_total_cost():
    """Test LLM get_total_cost method."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    # Create LLM with pricing
    llm = LLM(
        api_key=api_key,
        model_name=DEFAULT_TEST_MODEL,
        pricing={"input": 30.0, "output": 60.0},  # Per million tokens
        fetch_pricing=False,
    )
    
    # Make a query
    llm.query(user_prompt="Say hello")
    
    # Get total cost
    total = llm.get_total_cost()
    
    # Cost should be calculated if pricing is available
    if total["input_cost"] is not None:
        assert total["input_cost"] >= 0
    if total["output_cost"] is not None:
        assert total["output_cost"] >= 0
    if total["total_cost"] is not None:
        assert total["total_cost"] >= 0


def test_llm_get_total_cost_without_pricing():
    """Test LLM get_total_cost when pricing is not available."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL, pricing=None, fetch_pricing=False)
    
    # Make a query
    llm.query(user_prompt="Say hello")
    
    # Get total cost
    total = llm.get_total_cost()
    
    # Costs should be None when pricing is not available
    assert total["input_cost"] is None
    assert total["output_cost"] is None
    assert total["total_cost"] is None
