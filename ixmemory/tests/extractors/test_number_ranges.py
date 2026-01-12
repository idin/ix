"""
Tests for number_ranges extractor.
"""

import pytest
from ixcore import LLM

from ixmemory.extractors.number_ranges import extract_number_ranges
from tests.api_keys import get_openai_api_key


@pytest.fixture
def llm():
    """Create an LLM instance for testing."""
    api_key = get_openai_api_key()
    return LLM(api_key=api_key, model_name="gpt-4o-mini")


def test_extract_number_ranges_returns_list(llm):
    """extract_number_ranges should return a list."""
    text = "The price is between $50 and $100."
    result = extract_number_ranges(llm=llm, text=text)
    
    assert isinstance(result, list)


def test_extract_number_ranges_finds_bounded_range(llm):
    """extract_number_ranges should find ranges with both bounds."""
    text = "Temperature should be between 20 and 30 degrees."
    result = extract_number_ranges(llm=llm, text=text)
    
    assert len(result) >= 1
    if result:
        range_item = result[0]
        assert range_item.get("min") == 20 or range_item.get("min") == 20.0
        assert range_item.get("max") == 30 or range_item.get("max") == 30.0


def test_extract_number_ranges_finds_at_least(llm):
    """extract_number_ranges should find 'at least' ranges."""
    text = "Candidates must have at least 5 years of experience."
    result = extract_number_ranges(llm=llm, text=text)
    
    assert len(result) >= 1
    if result:
        range_item = result[0]
        assert range_item.get("min") == 5 or range_item.get("min") == 5.0
        assert range_item.get("max") is None


def test_extract_number_ranges_finds_at_most(llm):
    """extract_number_ranges should find 'at most' ranges."""
    text = "The weight should be at most 10 kilograms."
    result = extract_number_ranges(llm=llm, text=text)
    
    assert len(result) >= 1
    if result:
        range_item = result[0]
        assert range_item.get("min") is None
        assert range_item.get("max") == 10 or range_item.get("max") == 10.0


def test_extract_number_ranges_finds_greater_than(llm):
    """extract_number_ranges should find 'greater than' ranges."""
    text = "Salary must be greater than $50,000."
    result = extract_number_ranges(llm=llm, text=text)
    
    assert len(result) >= 1
    if result:
        range_item = result[0]
        assert range_item.get("min") is not None
        assert range_item.get("max") is None


def test_extract_number_ranges_finds_less_than(llm):
    """extract_number_ranges should find 'less than' ranges."""
    text = "The score should be less than 100."
    result = extract_number_ranges(llm=llm, text=text)
    
    assert len(result) >= 1
    if result:
        range_item = result[0]
        assert range_item.get("min") is None
        assert range_item.get("max") is not None


def test_extract_number_ranges_empty_text(llm):
    """extract_number_ranges should return empty list for text without ranges."""
    text = "The price is $50."  # Single value, not a range
    result = extract_number_ranges(llm=llm, text=text)
    
    assert isinstance(result, list)
    # Should not find ranges in single values
    assert len(result) == 0


def test_extract_number_ranges_has_record_type(llm):
    """Number ranges should have record_type field."""
    text = "Age requirement is between 18 and 65."
    result = extract_number_ranges(llm=llm, text=text)
    
    if result:
        range_item = result[0]
        assert "record_type" in range_item


def test_extract_number_ranges_multiple(llm):
    """extract_number_ranges should find multiple ranges."""
    text = "Age must be between 18 and 65. Salary is $50k to $100k."
    result = extract_number_ranges(llm=llm, text=text)
    
    assert len(result) >= 2


def test_extract_number_ranges_with_context(llm):
    """extract_number_ranges should use context."""
    text = "It should be between 5 and 10."
    result = extract_number_ranges(
        llm=llm,
        text=text,
        context="We are discussing the acceptable weight range for packages.",
    )
    
    assert isinstance(result, list)
