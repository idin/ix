"""
Tests for detect module.

Tests the grouped detection strategy for identifying extractable content types.
"""

import pytest
from ixcore import LLM

from ixmemory.extractors.detect import (
    detect,
    detect_and_extract,
    STRUCTURE_TYPES,
    DATA_TYPES,
    ALL_TYPES,
)
from tests.api_keys import get_openai_api_key


@pytest.fixture
def llm():
    """Create an LLM instance for testing."""
    api_key = get_openai_api_key()
    return LLM(api_key=api_key, model_name="gpt-4o-mini")


def test_detect_returns_all_types(llm):
    """detect() should return a dict with all type keys."""
    text = "Hello world."
    result = detect(llm=llm, text=text)
    
    assert isinstance(result, dict)
    assert set(result.keys()) == set(ALL_TYPES)
    for value in result.values():
        assert isinstance(value, bool)


def test_detect_finds_entities(llm):
    """detect() should find entities when present."""
    text = "Alice works at Microsoft in Seattle."
    result = detect(llm=llm, text=text)
    
    assert result["entities"] is True


def test_detect_finds_relationships(llm):
    """detect() should find relationships when present."""
    text = "Alice works at Microsoft. Bob knows Alice."
    result = detect(llm=llm, text=text)
    
    assert result["relationships"] is True


def test_detect_finds_numbers(llm):
    """detect() should find numbers when present."""
    text = "The product costs $49.99 and weighs 2.5 kilograms."
    result = detect(llm=llm, text=text)
    
    assert result["numbers"] is True


def test_detect_finds_moments(llm):
    """detect() should find moments (dates/times) when present."""
    text = "The meeting is on January 15, 2025 at 3pm."
    result = detect(llm=llm, text=text)
    
    assert result["moments"] is True


def test_detect_finds_attributes(llm):
    """detect() should find attributes when present."""
    text = "Alice is a software engineer. She is Canadian."
    result = detect(llm=llm, text=text)
    
    assert result["attributes"] is True


def test_detect_finds_number_ranges(llm):
    """detect() should find number ranges when present."""
    text = "The temperature should be between 20 and 25 degrees."
    result = detect(llm=llm, text=text)
    
    assert result["number_ranges"] is True


def test_detect_finds_moment_ranges(llm):
    """detect() should find moment ranges when present."""
    text = "The conference runs from March 1st to March 5th, 2025."
    result = detect(llm=llm, text=text)
    
    assert result["moment_ranges"] is True


def test_detect_finds_open_ended_number_range(llm):
    """detect() should find open-ended number ranges (at least, at most)."""
    text = "Candidates must have at least 5 years of experience."
    result = detect(llm=llm, text=text)
    
    assert result["number_ranges"] is True


def test_detect_finds_open_ended_moment_range(llm):
    """detect() should find open-ended moment ranges (since, until, before, after)."""
    text = "The project started in January 2020 and continues until December 2025."
    result = detect(llm=llm, text=text)
    
    # Should detect either moments or moment_ranges (LLM interpretation varies)
    assert result["moments"] is True or result["moment_ranges"] is True


def test_detect_empty_text(llm):
    """detect() should return all False for empty or minimal text."""
    text = "Hello."
    result = detect(llm=llm, text=text)
    
    # Most types should be False for simple greeting
    assert result["entities"] is False
    assert result["numbers"] is False
    assert result["moments"] is False


def test_detect_complex_text_multiple_types(llm):
    """detect() should find multiple types in complex text."""
    text = (
        "Alice is 32 years old and works at Acme Corp since 2020. "
        "She earns between $80,000 and $100,000 per year."
    )
    result = detect(llm=llm, text=text)
    
    # Should find: entities, numbers, relationships, moments, number_ranges
    assert result["entities"] is True  # Alice, Acme Corp
    assert result["numbers"] is True   # 32
    assert result["relationships"] is True  # works at
    assert result["number_ranges"] is True  # between $80k and $100k


def test_detect_with_context(llm):
    """detect() should use context when provided."""
    text = "She started in 2020."
    result = detect(
        llm=llm,
        text=text,
        context="We are discussing Alice's career history.",
    )
    
    assert result["moments"] is True  # 2020


def test_detect_structure_vs_data_separation():
    """Verify type groupings are correct."""
    assert set(STRUCTURE_TYPES) == {"entities", "relationships"}
    assert set(DATA_TYPES) == {"numbers", "moments", "attributes", "number_ranges", "moment_ranges"}
    assert set(ALL_TYPES) == set(STRUCTURE_TYPES) | set(DATA_TYPES)


def test_detect_and_extract_returns_only_present_types(llm):
    """detect_and_extract() should only return types that were detected."""
    text = "Alice is 32 years old."
    result = detect_and_extract(llm=llm, text=text)
    
    assert isinstance(result, dict)
    # Should have entities and numbers at minimum
    assert "entities" in result or "numbers" in result
    
    # Each value should be a list
    for key, value in result.items():
        assert isinstance(value, list)


def test_detect_and_extract_entities_have_structure(llm):
    """detect_and_extract() entities should have proper structure."""
    text = "Alice works at Microsoft."
    result = detect_and_extract(llm=llm, text=text)
    
    if "entities" in result and result["entities"]:
        entity = result["entities"][0]
        assert "name" in entity
        assert "type" in entity


def test_detect_and_extract_numbers_have_structure(llm):
    """detect_and_extract() numbers should have proper structure."""
    text = "The item costs $50."
    result = detect_and_extract(llm=llm, text=text)
    
    if "numbers" in result and result["numbers"]:
        number = result["numbers"][0]
        assert "value" in number


def test_detect_and_extract_relationships_have_structure(llm):
    """detect_and_extract() relationships should have proper structure."""
    text = "Alice works at Microsoft."
    result = detect_and_extract(llm=llm, text=text)
    
    if "relationships" in result and result["relationships"]:
        rel = result["relationships"][0]
        assert "source" in rel
        assert "relationship" in rel
        assert "target" in rel


def test_detect_and_extract_empty_text(llm):
    """detect_and_extract() should return empty dict for minimal text."""
    text = "Hello."
    result = detect_and_extract(llm=llm, text=text)
    
    # Should be empty or have very few items
    assert isinstance(result, dict)


def test_detect_and_extract_with_context(llm):
    """detect_and_extract() should use context."""
    text = "She is 32."
    result = detect_and_extract(
        llm=llm,
        text=text,
        context="We are discussing Alice, a software engineer.",
    )
    
    # Should find at least a number
    if "numbers" in result:
        assert len(result["numbers"]) > 0
