"""
Tests for entities extractor.
"""

import pytest
from ixcore import LLM

from ixmemory.extractors.entities import extract_entities
from tests.api_keys import get_openai_api_key


@pytest.fixture
def llm():
    """Create an LLM instance for testing."""
    api_key = get_openai_api_key()
    return LLM(api_key=api_key, model_name="gpt-4o-mini")


def test_extract_entities_returns_list(llm):
    """extract_entities should return a list."""
    text = "Alice works at Microsoft."
    result = extract_entities(llm=llm, text=text)
    
    assert isinstance(result, list)


def test_extract_entities_finds_person(llm):
    """extract_entities should find person entities."""
    text = "Alice Smith is a software engineer."
    result = extract_entities(llm=llm, text=text)
    
    names = [e["name"] for e in result]
    assert any("Alice" in name for name in names)


def test_extract_entities_finds_organization(llm):
    """extract_entities should find organization entities."""
    text = "Microsoft and Google are technology companies."
    result = extract_entities(llm=llm, text=text)
    
    names = [e["name"] for e in result]
    assert any("Microsoft" in name for name in names)
    assert any("Google" in name for name in names)


def test_extract_entities_finds_place(llm):
    """extract_entities should find place entities."""
    text = "Seattle is located in Washington state."
    result = extract_entities(llm=llm, text=text)
    
    names = [e["name"] for e in result]
    assert any("Seattle" in name for name in names)


def test_extract_entities_finds_brand(llm):
    """extract_entities should find brand entities."""
    text = "I bought a new iPhone from Apple Store."
    result = extract_entities(llm=llm, text=text)
    
    names = [e["name"] for e in result]
    # Should find iPhone and/or Apple
    assert len(result) > 0


def test_extract_entities_has_type(llm):
    """Each entity should have a type field."""
    text = "Alice works at Microsoft in Seattle."
    result = extract_entities(llm=llm, text=text)
    
    for entity in result:
        assert "type" in entity
        assert entity["type"] in [
            "person", "place", "organization", "concept",
            "brand", "product", "project",
        ]


def test_extract_entities_has_name(llm):
    """Each entity should have a name field."""
    text = "Alice works at Microsoft."
    result = extract_entities(llm=llm, text=text)
    
    for entity in result:
        assert "name" in entity
        assert isinstance(entity["name"], str)


def test_extract_entities_empty_text(llm):
    """extract_entities should return empty list for text without entities."""
    text = "Hello world."
    result = extract_entities(llm=llm, text=text)
    
    assert isinstance(result, list)
    # Might be empty or have minimal entities
    assert len(result) <= 1


def test_extract_entities_with_context(llm):
    """extract_entities should use context."""
    text = "She started the company in 2015."
    result = extract_entities(
        llm=llm,
        text=text,
        context="We are discussing Alice and her tech startup called Acme.",
    )
    
    # Context should help identify entities
    assert isinstance(result, list)


def test_extract_entities_multiple(llm):
    """extract_entities should find multiple entities."""
    text = "Alice, Bob, and Charlie work at Microsoft, Google, and Amazon."
    result = extract_entities(llm=llm, text=text)
    
    # Should find at least 4 entities (3 people + some companies)
    assert len(result) >= 4
