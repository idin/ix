"""
Tests for LLM usage tracking.
"""

import pytest
from tests.conftest import DEFAULT_TEST_MODEL
import os

from ixmachina.llm import LLM


def test_llm_captures_usage():
    """Test that LLM captures usage information from API responses."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)

    # Initial state - no usage yet
    assert llm.last_usage is None
    assert llm.total_usage["input_tokens"] == 0
    assert llm.total_usage["output_tokens"] == 0
    assert llm.total_usage["total_tokens"] == 0

    # Make a query
    response = llm.query(user_prompt="Say hello in one word")

    # Check that usage was captured
    assert llm.last_usage is not None
    assert "input_tokens" in llm.last_usage
    assert "output_tokens" in llm.last_usage
    assert "total_tokens" in llm.last_usage
    assert llm.last_usage["input_tokens"] > 0
    assert llm.last_usage["output_tokens"] > 0
    assert llm.last_usage["total_tokens"] > 0

    # Check that total_usage was updated
    assert llm.total_usage["input_tokens"] == llm.last_usage["input_tokens"]
    assert llm.total_usage["output_tokens"] == llm.last_usage["output_tokens"]
    assert llm.total_usage["total_tokens"] == llm.last_usage["total_tokens"]


def test_llm_accumulates_usage():
    """Test that LLM accumulates usage across multiple queries."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)

    # Make first query
    first_response = llm.query(user_prompt="Say hello")
    first_usage = llm.last_usage.copy()
    first_total = llm.total_usage.copy()

    # Make second query
    second_response = llm.query(user_prompt="Say goodbye")
    second_usage = llm.last_usage.copy()
    second_total = llm.total_usage.copy()

    # Check that last_usage reflects the second query
    assert llm.last_usage == second_usage

    # Check that total_usage accumulated both queries
    assert second_total["input_tokens"] >= first_total["input_tokens"]
    assert second_total["output_tokens"] >= first_total["output_tokens"]
    assert second_total["total_tokens"] >= first_total["total_tokens"]

    # Total should be approximately the sum (allowing for some variance)
    expected_input = first_usage["input_tokens"] + second_usage["input_tokens"]
    expected_output = first_usage["output_tokens"] + second_usage["output_tokens"]
    expected_total = first_usage["total_tokens"] + second_usage["total_tokens"]

    # Allow small variance due to system messages, etc.
    assert abs(second_total["input_tokens"] - expected_input) < 50
    assert abs(second_total["output_tokens"] - expected_output) < 50
    assert abs(second_total["total_tokens"] - expected_total) < 50

