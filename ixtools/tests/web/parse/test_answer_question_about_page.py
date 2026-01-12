"""
Tests for answer_question_about_page function.
"""

import pytest
from tests.conftest import DEFAULT_TEST_MODEL

from ixcore import LLM
from ixtools.web import answer_question_about_page
from tests.api_keys import get_openai_api_key


def test_answer_question_about_page_basic():
    """Test answering a question about a web page."""
    api_key = get_openai_api_key()
    
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    
    result = answer_question_about_page(
        url="https://httpbin.org/html",
        question="What is the title of this page?",
        llm=llm,
    )
    
    assert result["success"] is True
    assert result["answer"] is not None
    assert len(result["answer"]) > 0
    assert result["url"] == "https://httpbin.org/html"
    assert result["question"] == "What is the title of this page?"


def test_answer_question_about_page_invalid_url():
    """Test answering question about invalid URL."""
    api_key = get_openai_api_key()
    
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    
    result = answer_question_about_page(
        url="https://this-domain-definitely-does-not-exist-12345.com",
        question="What is this page about?",
        llm=llm,
    )
    
    assert result["success"] is False
    assert result["answer"] is None
    assert result["error"] is not None

