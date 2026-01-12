"""
Tests for moment_ranges extractor.
"""

import pytest
from ixcore import LLM

from ixmemory.extractors.moment_ranges import extract_moment_ranges
from tests.api_keys import get_openai_api_key


@pytest.fixture
def llm():
    """Create an LLM instance for testing."""
    api_key = get_openai_api_key()
    return LLM(api_key=api_key, model_name="gpt-4o-mini")


def test_extract_moment_ranges_returns_list(llm):
    """extract_moment_ranges should return a list."""
    text = "The event runs from March to June 2025."
    result = extract_moment_ranges(llm=llm, text=text)
    
    assert isinstance(result, list)


def test_extract_moment_ranges_finds_bounded_range(llm):
    """extract_moment_ranges should find ranges with both bounds."""
    text = "The conference is from March 1 to March 5, 2025."
    result = extract_moment_ranges(llm=llm, text=text)
    
    assert len(result) >= 1
    if result:
        range_item = result[0]
        assert "start" in range_item
        assert "end" in range_item


def test_extract_moment_ranges_finds_since(llm):
    """extract_moment_ranges should find 'since' ranges."""
    text = "She has been working here since 2019."
    result = extract_moment_ranges(llm=llm, text=text)
    
    assert len(result) >= 1
    if result:
        range_item = result[0]
        assert "start" in range_item
        assert range_item.get("end") is None


def test_extract_moment_ranges_finds_until(llm):
    """extract_moment_ranges should find 'until' ranges."""
    text = "The offer is valid until December 31, 2025."
    result = extract_moment_ranges(llm=llm, text=text)
    
    assert len(result) >= 1
    if result:
        range_item = result[0]
        assert range_item.get("start") is None
        assert "end" in range_item


def test_extract_moment_ranges_finds_before(llm):
    """extract_moment_ranges should find 'before' ranges."""
    text = "Submit applications before January 15."
    result = extract_moment_ranges(llm=llm, text=text)
    
    assert len(result) >= 1
    if result:
        range_item = result[0]
        assert range_item.get("start") is None
        assert "end" in range_item


def test_extract_moment_ranges_finds_after(llm):
    """extract_moment_ranges should find 'after' ranges."""
    text = "The new policy takes effect after March 1, 2025."
    result = extract_moment_ranges(llm=llm, text=text)
    
    assert len(result) >= 1
    if result:
        range_item = result[0]
        assert "start" in range_item
        assert range_item.get("end") is None


def test_extract_moment_ranges_empty_text(llm):
    """extract_moment_ranges should return empty list for text without ranges."""
    text = "The meeting is on January 15."  # Single date, not a range
    result = extract_moment_ranges(llm=llm, text=text)
    
    assert isinstance(result, list)
    # Should not find ranges in single dates
    assert len(result) == 0


def test_extract_moment_ranges_has_record_type(llm):
    """Moment ranges should have record_type field."""
    text = "The project runs from Q1 to Q3 2025."
    result = extract_moment_ranges(llm=llm, text=text)
    
    if result:
        range_item = result[0]
        assert "record_type" in range_item


def test_extract_moment_ranges_multiple(llm):
    """extract_moment_ranges should find multiple ranges."""
    text = "Phase 1 is from Jan to Mar. Phase 2 is from Apr to Jun."
    result = extract_moment_ranges(llm=llm, text=text)
    
    assert len(result) >= 2


def test_extract_moment_ranges_with_context(llm):
    """extract_moment_ranges should use context."""
    text = "It runs from the 1st to the 15th."
    result = extract_moment_ranges(
        llm=llm,
        text=text,
        context="We are discussing the March 2025 sprint schedule.",
    )
    
    assert isinstance(result, list)


def test_extract_moment_ranges_partial_dates(llm):
    """extract_moment_ranges should handle partial date ranges."""
    text = "The fiscal year runs from April to March."
    result = extract_moment_ranges(llm=llm, text=text)
    
    assert len(result) >= 1
    if result:
        range_item = result[0]
        # Should have start and end with at least month
        if range_item.get("start"):
            assert range_item["start"].get("month") is not None
