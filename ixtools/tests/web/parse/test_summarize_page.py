"""
Tests for summarize_page function.
"""

import pytest
from tests.conftest import DEFAULT_TEST_MODEL

from ixcore import LLM
from ixtools.web import summarize_page
from tests.api_keys import get_openai_api_key


def test_summarize_page_basic():
    """Test summarizing a web page."""
    api_key = get_openai_api_key()
    
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    
    result = summarize_page(
        url="https://httpbin.org/html",
        llm=llm,
    )
    
    assert result["success"] is True
    assert result["summary"] is not None
    assert len(result["summary"]) > 0
    assert result["url"] == "https://httpbin.org/html"


def test_summarize_page_with_max_length():
    """Test summarizing with max_length specified."""
    api_key = get_openai_api_key()
    
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    
    result = summarize_page(
        url="https://httpbin.org/html",
        llm=llm,
        max_length=50,
    )
    
    assert result["success"] is True
    assert result["summary"] is not None
    assert len(result["summary"]) > 0


def test_summarize_page_invalid_url():
    """Test summarizing invalid URL."""
    api_key = get_openai_api_key()
    
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    
    result = summarize_page(
        url="https://this-domain-definitely-does-not-exist-12345.com",
        llm=llm,
    )
    
    assert result["success"] is False
    assert result["summary"] is None
    assert result["error"] is not None

