"""
Tests for relationships extractor.
"""

import pytest
from ixcore import LLM

from ixmemory.extractors.relationships import extract_relationships
from tests.api_keys import get_openai_api_key


@pytest.fixture
def llm():
    """Create an LLM instance for testing."""
    api_key = get_openai_api_key()
    return LLM(api_key=api_key, model_name="gpt-4o-mini")


def test_extract_relationships_returns_list(llm):
    """extract_relationships should return a list."""
    text = "Alice works at Microsoft."
    result = extract_relationships(llm=llm, text=text)
    
    assert isinstance(result, list)


def test_extract_relationships_finds_works_at(llm):
    """extract_relationships should find employment relationships."""
    text = "Alice works at Microsoft."
    result = extract_relationships(llm=llm, text=text)
    
    assert len(result) >= 1
    if result:
        rel = result[0]
        assert "Alice" in rel.get("source", "")
        assert "Microsoft" in rel.get("target", "")


def test_extract_relationships_finds_lives_in(llm):
    """extract_relationships should find location relationships."""
    text = "Bob lives in Seattle."
    result = extract_relationships(llm=llm, text=text)
    
    assert len(result) >= 1
    if result:
        rel = result[0]
        assert "Bob" in rel.get("source", "")
        assert "Seattle" in rel.get("target", "")


def test_extract_relationships_finds_knows(llm):
    """extract_relationships should find social relationships."""
    text = "Alice knows Bob."
    result = extract_relationships(llm=llm, text=text)
    
    assert len(result) >= 1
    if result:
        rel = result[0]
        assert "Alice" in rel.get("source", "")
        assert "Bob" in rel.get("target", "")


def test_extract_relationships_has_source(llm):
    """Each relationship should have a source field."""
    text = "Alice works at Microsoft."
    result = extract_relationships(llm=llm, text=text)
    
    for rel in result:
        assert "source" in rel
        assert isinstance(rel["source"], str)


def test_extract_relationships_has_relationship(llm):
    """Each relationship should have a relationship field."""
    text = "Alice works at Microsoft."
    result = extract_relationships(llm=llm, text=text)
    
    for rel in result:
        assert "relationship" in rel
        assert isinstance(rel["relationship"], str)


def test_extract_relationships_has_target(llm):
    """Each relationship should have a target field."""
    text = "Alice works at Microsoft."
    result = extract_relationships(llm=llm, text=text)
    
    for rel in result:
        assert "target" in rel
        assert isinstance(rel["target"], str)


def test_extract_relationships_empty_text(llm):
    """extract_relationships should return empty list for text without relationships."""
    text = "Hello world."
    result = extract_relationships(llm=llm, text=text)
    
    assert isinstance(result, list)
    assert len(result) == 0


def test_extract_relationships_multiple(llm):
    """extract_relationships should find multiple relationships."""
    text = "Alice works at Microsoft. Bob lives in Seattle. Alice knows Bob."
    result = extract_relationships(llm=llm, text=text)
    
    assert len(result) >= 3


def test_extract_relationships_with_context(llm):
    """extract_relationships should use context."""
    text = "She started there in 2020."
    result = extract_relationships(
        llm=llm,
        text=text,
        context="We are discussing Alice's employment at Microsoft.",
    )
    
    assert isinstance(result, list)


def test_extract_relationships_ownership(llm):
    """extract_relationships should find ownership relationships."""
    text = "Alice owns a Tesla Model 3."
    result = extract_relationships(llm=llm, text=text)
    
    assert len(result) >= 1
    if result:
        rel = result[0]
        assert "Alice" in rel.get("source", "")
