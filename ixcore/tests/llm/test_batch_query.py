"""
Tests for batch_query function.
"""

import pytest

from conftest import DEFAULT_TEST_MODEL
from ixcore.llm.single_query import batch_query
from openai import OpenAI
from api_keys import get_openai_api_key


def test_batch_query_executes_multiple_queries_in_parallel():
    """Test that batch_query executes multiple queries in parallel."""
    api_key = get_openai_api_key()
    client = OpenAI(api_key=api_key)
    
    queries = [
        [{"role": "user", "content": "What is 2+2? Answer with just the number."}],
        [{"role": "user", "content": "What is 3+3? Answer with just the number."}],
        [{"role": "user", "content": "What is 4+4? Answer with just the number."}],
    ]
    
    results = batch_query(
        client=client,
        model_name=DEFAULT_TEST_MODEL,
        queries=queries,
    )
    
    assert len(results) == 3
    # Results can be strings or dicts with 'content' key
    result_0 = results[0]["content"] if isinstance(results[0], dict) else results[0]
    result_1 = results[1]["content"] if isinstance(results[1], dict) else results[1]
    result_2 = results[2]["content"] if isinstance(results[2], dict) else results[2]
    assert "4" in result_0 or "four" in result_0.lower()
    assert "6" in result_1 or "six" in result_1.lower()
    assert "8" in result_2 or "eight" in result_2.lower()


def test_batch_query_returns_results_in_same_order():
    """Test that batch_query returns results in the same order as input queries."""
    api_key = get_openai_api_key()
    client = OpenAI(api_key=api_key)
    
    queries = [
        [{"role": "user", "content": "Say 'first'"}],
        [{"role": "user", "content": "Say 'second'"}],
        [{"role": "user", "content": "Say 'third'"}],
    ]
    
    results = batch_query(
        client=client,
        model_name=DEFAULT_TEST_MODEL,
        queries=queries,
    )
    
    assert len(results) == 3
    # Results can be strings or dicts with 'content' key
    result_0 = results[0]["content"] if isinstance(results[0], dict) else results[0]
    result_1 = results[1]["content"] if isinstance(results[1], dict) else results[1]
    result_2 = results[2]["content"] if isinstance(results[2], dict) else results[2]
    assert "first" in result_0.lower()
    assert "second" in result_1.lower()
    assert "third" in result_2.lower()


def test_batch_query_handles_empty_list():
    """Test that batch_query handles empty list of queries."""
    api_key = get_openai_api_key()
    client = OpenAI(api_key=api_key)
    
    results = batch_query(
        client=client,
        model_name=DEFAULT_TEST_MODEL,
        queries=[],
    )
    
    assert results == []


def test_batch_query_with_single_query():
    """Test that batch_query works with a single query."""
    api_key = get_openai_api_key()
    client = OpenAI(api_key=api_key)
    
    queries = [
        [{"role": "user", "content": "What is 5+5? Answer with just the number."}],
    ]
    
    results = batch_query(
        client=client,
        model_name=DEFAULT_TEST_MODEL,
        queries=queries,
    )
    
    assert len(results) == 1
    # Results can be strings or dicts with 'content' key
    result = results[0]["content"] if isinstance(results[0], dict) else results[0]
    assert "10" in result or "ten" in result.lower()


def test_batch_query_with_multiple_messages_per_query():
    """Test that batch_query works with queries that have multiple messages."""
    api_key = get_openai_api_key()
    client = OpenAI(api_key=api_key)
    
    queries = [
        [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is 1+1?"},
        ],
        [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is 2+2?"},
        ],
    ]
    
    results = batch_query(
        client=client,
        model_name=DEFAULT_TEST_MODEL,
        queries=queries,
    )
    
    assert len(results) == 2
    # Results can be strings or dicts with 'content' key
    result_0 = results[0]["content"] if isinstance(results[0], dict) else results[0]
    result_1 = results[1]["content"] if isinstance(results[1], dict) else results[1]
    assert "2" in result_0 or "two" in result_0.lower()
    assert "4" in result_1 or "four" in result_1.lower()


def test_batch_query_uses_cached_results():
    """Test that batch_query uses cached results when use_cache=True."""
    api_key = get_openai_api_key()
    client = OpenAI(api_key=api_key)
    
    queries = [
        [{"role": "user", "content": "What is 7+7? Answer with just the number."}],
        [{"role": "user", "content": "What is 8+8? Answer with just the number."}],
    ]
    
    # First call - should make API requests
    results_1 = batch_query(
        client=client,
        model_name=DEFAULT_TEST_MODEL,
        queries=queries,
        use_cache=True,
    )
    
    assert len(results_1) == 2
    # Check that results are dicts with from_cache flag
    assert isinstance(results_1[0], dict)
    assert isinstance(results_1[1], dict)
    assert results_1[0]["from_cache"] is False
    assert results_1[1]["from_cache"] is False
    
    result_1_0 = results_1[0]["content"] if "content" in results_1[0] else str(results_1[0])
    result_1_1 = results_1[1]["content"] if "content" in results_1[1] else str(results_1[1])
    assert "14" in result_1_0 or "fourteen" in result_1_0.lower()
    assert "16" in result_1_1 or "sixteen" in result_1_1.lower()
    
    # Second call with same queries - should use cache
    results_2 = batch_query(
        client=client,
        model_name=DEFAULT_TEST_MODEL,
        queries=queries,
        use_cache=True,
    )
    
    assert len(results_2) == 2
    # Check that results are from cache
    assert isinstance(results_2[0], dict)
    assert isinstance(results_2[1], dict)
    assert results_2[0]["from_cache"] is True
    assert results_2[1]["from_cache"] is True
    
    # Results should be the same (from cache)
    result_2_0 = results_2[0]["content"] if "content" in results_2[0] else str(results_2[0])
    result_2_1 = results_2[1]["content"] if "content" in results_2[1] else str(results_2[1])
    assert result_1_0 == result_2_0
    assert result_1_1 == result_2_1
