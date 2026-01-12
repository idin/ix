"""
Tests for attributes extractor.
"""

import pytest
from ixcore import LLM

from ixmemory.extractors.attributes import extract_attributes
from tests.api_keys import get_openai_api_key


@pytest.fixture
def llm():
    """Create an LLM instance for testing."""
    api_key = get_openai_api_key()
    return LLM(api_key=api_key, model_name="gpt-4o-mini")


def test_extract_attributes_returns_list(llm):
    """extract_attributes should return a list."""
    text = "Alice is a software engineer."
    result = extract_attributes(llm=llm, text=text)
    
    assert isinstance(result, list)


def test_extract_attributes_finds_occupation(llm):
    """extract_attributes should find occupation attributes."""
    text = "Alice is a software engineer."
    result = extract_attributes(llm=llm, text=text)
    
    assert len(result) >= 1
    if result:
        attr = result[0]
        assert "Alice" in attr.get("entity", "")
        assert "software engineer" in attr.get("value", "").lower()


def test_extract_attributes_finds_nationality(llm):
    """extract_attributes should find nationality attributes."""
    text = "Bob is Canadian."
    result = extract_attributes(llm=llm, text=text)
    
    assert len(result) >= 1
    if result:
        attr = result[0]
        assert "Bob" in attr.get("entity", "")


def test_extract_attributes_finds_colour(llm):
    """extract_attributes should find colour attributes."""
    text = "The car is red."
    result = extract_attributes(llm=llm, text=text)
    
    assert len(result) >= 1
    if result:
        attr = result[0]
        assert "red" in attr.get("value", "").lower()


def test_extract_attributes_has_entity(llm):
    """Each attribute should have an entity field."""
    text = "Alice is tall."
    result = extract_attributes(llm=llm, text=text)
    
    for attr in result:
        assert "entity" in attr
        assert isinstance(attr["entity"], str)


def test_extract_attributes_has_attribute(llm):
    """Each attribute should have an attribute field."""
    text = "Alice is a doctor."
    result = extract_attributes(llm=llm, text=text)
    
    for attr in result:
        assert "attribute" in attr
        assert isinstance(attr["attribute"], str)


def test_extract_attributes_has_value(llm):
    """Each attribute should have a value field."""
    text = "Alice is Canadian."
    result = extract_attributes(llm=llm, text=text)
    
    for attr in result:
        assert "value" in attr
        assert isinstance(attr["value"], str)


def test_extract_attributes_empty_text(llm):
    """extract_attributes should return empty list for text without attributes."""
    text = "Hello world."
    result = extract_attributes(llm=llm, text=text)
    
    assert isinstance(result, list)
    assert len(result) == 0


def test_extract_attributes_multiple(llm):
    """extract_attributes should find multiple attributes."""
    text = "Alice is a Canadian software engineer. She is tall and friendly."
    result = extract_attributes(llm=llm, text=text)
    
    assert len(result) >= 2


def test_extract_attributes_with_context(llm):
    """extract_attributes should use context."""
    text = "She is very experienced."
    result = extract_attributes(
        llm=llm,
        text=text,
        context="We are discussing Alice, a senior engineer at Microsoft.",
    )
    
    assert isinstance(result, list)


def test_extract_attributes_description(llm):
    """extract_attributes should find descriptive attributes."""
    text = "The project is innovative and groundbreaking."
    result = extract_attributes(llm=llm, text=text)
    
    assert len(result) >= 1
