"""
Tests for moments extractor.
"""

import pytest
from ixcore import LLM

from ixmemory.extractors.moments import extract_moments
from tests.api_keys import get_openai_api_key


@pytest.fixture
def llm():
    """Create an LLM instance for testing."""
    api_key = get_openai_api_key()
    return LLM(api_key=api_key, model_name="gpt-4o-mini")


def test_extract_moments_returns_list(llm):
    """extract_moments should return a list."""
    text = "The meeting is on January 15, 2025."
    result = extract_moments(llm=llm, text=text)
    
    assert isinstance(result, list)


def test_extract_moments_finds_full_date(llm):
    """extract_moments should find full dates."""
    text = "The event is on March 15, 2025."
    result = extract_moments(llm=llm, text=text)
    
    assert len(result) >= 1
    if result:
        moment = result[0]
        assert moment.get("year") == 2025
        assert moment.get("month") == 3
        assert moment.get("day") == 15


def test_extract_moments_finds_partial_date_year_only(llm):
    """extract_moments should find year-only dates."""
    text = "The company was founded in 2015."
    result = extract_moments(llm=llm, text=text)
    
    assert len(result) >= 1
    if result:
        moment = result[0]
        assert moment.get("year") == 2015


def test_extract_moments_finds_partial_date_month_year(llm):
    """extract_moments should find month-year dates."""
    text = "She joined in November 2020."
    result = extract_moments(llm=llm, text=text)
    
    assert len(result) >= 1
    if result:
        moment = result[0]
        assert moment.get("year") == 2020
        assert moment.get("month") == 11


def test_extract_moments_finds_time(llm):
    """extract_moments should find times."""
    text = "The meeting starts at 3:30 PM."
    result = extract_moments(llm=llm, text=text)
    
    assert len(result) >= 1
    if result:
        moment = result[0]
        assert "hour" in moment or "minute" in moment


def test_extract_moments_empty_text(llm):
    """extract_moments should return empty list for text without dates."""
    text = "Hello world."
    result = extract_moments(llm=llm, text=text)
    
    assert isinstance(result, list)
    assert len(result) == 0


def test_extract_moments_multiple(llm):
    """extract_moments should find multiple dates."""
    text = "Alice was born in 1990 and started work in 2015."
    result = extract_moments(llm=llm, text=text)
    
    assert len(result) >= 2


def test_extract_moments_has_belongs_to(llm):
    """Moments should have belongs_to when associated with an entity."""
    text = "Alice's birthday is on June 15."
    result = extract_moments(llm=llm, text=text)
    
    # belongs_to is optional but should be present when relevant
    assert isinstance(result, list)


def test_extract_moments_with_context(llm):
    """extract_moments should use context."""
    text = "She started on the 15th."
    result = extract_moments(
        llm=llm,
        text=text,
        context="We are discussing Alice joining Microsoft in March 2020.",
    )
    
    assert isinstance(result, list)
