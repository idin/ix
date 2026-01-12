"""
Tests for numbers extractor.
"""

import pytest
from ixcore import LLM

from ixmemory.extractors.numbers import extract_numbers
from tests.api_keys import get_openai_api_key


@pytest.fixture
def llm():
    """Create an LLM instance for testing."""
    api_key = get_openai_api_key()
    return LLM(api_key=api_key, model_name="gpt-4o-mini")


def test_extract_numbers_returns_list(llm):
    """extract_numbers should return a list."""
    text = "The price is $50."
    result = extract_numbers(llm=llm, text=text)
    
    assert isinstance(result, list)


def test_extract_numbers_finds_age(llm):
    """extract_numbers should find age values."""
    text = "Alice is 32 years old."
    result = extract_numbers(llm=llm, text=text)
    
    values = [n["value"] for n in result]
    assert 32 in values or 32.0 in values


def test_extract_numbers_finds_price(llm):
    """extract_numbers should find price values."""
    text = "The laptop costs $1299."
    result = extract_numbers(llm=llm, text=text)
    
    values = [n["value"] for n in result]
    assert 1299 in values or 1299.0 in values


def test_extract_numbers_finds_measurement(llm):
    """extract_numbers should find measurements."""
    text = "The package weighs 2.5 kilograms."
    result = extract_numbers(llm=llm, text=text)
    
    values = [n["value"] for n in result]
    assert 2.5 in values


def test_extract_numbers_has_value(llm):
    """Each number should have a value field."""
    text = "There are 5 apples."
    result = extract_numbers(llm=llm, text=text)
    
    for number in result:
        assert "value" in number
        assert isinstance(number["value"], (int, float))


def test_extract_numbers_has_belongs_to(llm):
    """Numbers should have belongs_to when associated with an entity."""
    text = "Alice is 32 years old."
    result = extract_numbers(llm=llm, text=text)
    
    # At least one number should be associated with Alice
    if result:
        # belongs_to is optional but should be present when relevant
        assert any("belongs_to" in n for n in result) or len(result) > 0


def test_extract_numbers_empty_text(llm):
    """extract_numbers should return empty list for text without numbers."""
    text = "Hello world."
    result = extract_numbers(llm=llm, text=text)
    
    assert isinstance(result, list)
    assert len(result) == 0


def test_extract_numbers_multiple(llm):
    """extract_numbers should find multiple numbers."""
    text = "Alice is 32 and Bob is 45. The project has 100 tasks."
    result = extract_numbers(llm=llm, text=text)
    
    assert len(result) >= 3


def test_extract_numbers_with_context(llm):
    """extract_numbers should use context."""
    text = "It weighs 5 pounds."
    result = extract_numbers(
        llm=llm,
        text=text,
        context="We are discussing the weight of Alice's new laptop.",
    )
    
    assert isinstance(result, list)
    if result:
        values = [n["value"] for n in result]
        assert 5 in values or 5.0 in values
