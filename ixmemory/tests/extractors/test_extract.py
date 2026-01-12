"""
Tests for extract module.

Tests the combined extraction functionality.
"""

import pytest
from ixcore import LLM

from ixmemory.extractors.extract import extract, SPECS
from tests.api_keys import get_openai_api_key


@pytest.fixture
def llm():
    """Create an LLM instance for testing."""
    api_key = get_openai_api_key()
    return LLM(api_key=api_key, model_name="gpt-4o-mini")


def test_specs_contains_all_types():
    """SPECS should contain all expected extraction types."""
    expected_types = [
        "entities", "numbers", "moments", "attributes",
        "relationships", "number_ranges", "moment_ranges",
    ]
    for t in expected_types:
        assert t in SPECS


def test_specs_have_required_keys():
    """Each spec should have key, description, fields, and examples."""
    for name, spec in SPECS.items():
        assert "key" in spec, f"{name} missing key"
        assert "description" in spec, f"{name} missing description"
        assert "fields" in spec, f"{name} missing fields"
        assert "examples" in spec, f"{name} missing examples"


def test_extract_single_type_entities(llm):
    """extract() with single type should return that type only."""
    text = "Alice works at Microsoft."
    result = extract(llm=llm, text=text, types=["entities"])
    
    assert isinstance(result, dict)
    assert "entities" in result
    assert isinstance(result["entities"], list)


def test_extract_single_type_numbers(llm):
    """extract() should extract numbers when requested."""
    text = "The product costs $49.99."
    result = extract(llm=llm, text=text, types=["numbers"])
    
    assert "numbers" in result
    assert isinstance(result["numbers"], list)
    if result["numbers"]:
        assert "value" in result["numbers"][0]


def test_extract_single_type_moments(llm):
    """extract() should extract moments when requested."""
    text = "The meeting is on January 15, 2025."
    result = extract(llm=llm, text=text, types=["moments"])
    
    assert "moments" in result
    assert isinstance(result["moments"], list)


def test_extract_single_type_relationships(llm):
    """extract() should extract relationships when requested."""
    text = "Alice works at Microsoft. Bob knows Alice."
    result = extract(llm=llm, text=text, types=["relationships"])
    
    assert "relationships" in result
    assert isinstance(result["relationships"], list)


def test_extract_single_type_attributes(llm):
    """extract() should extract attributes when requested."""
    text = "Alice is a software engineer. She is Canadian."
    result = extract(llm=llm, text=text, types=["attributes"])
    
    assert "attributes" in result
    assert isinstance(result["attributes"], list)


def test_extract_single_type_number_ranges(llm):
    """extract() should extract number ranges when requested."""
    text = "The salary is between $80,000 and $120,000."
    result = extract(llm=llm, text=text, types=["number_ranges"])
    
    assert "number_ranges" in result
    assert isinstance(result["number_ranges"], list)


def test_extract_single_type_moment_ranges(llm):
    """extract() should extract moment ranges when requested."""
    text = "The project runs from March to June 2025."
    result = extract(llm=llm, text=text, types=["moment_ranges"])
    
    assert "moment_ranges" in result
    assert isinstance(result["moment_ranges"], list)


def test_extract_multiple_types(llm):
    """extract() should handle multiple types in one call."""
    text = "Alice is 32 years old and works at Microsoft."
    result = extract(llm=llm, text=text, types=["entities", "numbers", "relationships"])
    
    assert "entities" in result
    assert "numbers" in result
    assert "relationships" in result


def test_extract_all_types(llm):
    """extract() should handle all types at once."""
    text = (
        "Alice is a 32-year-old Canadian engineer at Microsoft since 2020. "
        "The salary is between $100k and $150k. The contract runs until 2025."
    )
    all_types = list(SPECS.keys())
    result = extract(llm=llm, text=text, types=all_types)
    
    # Should have all requested types as keys
    for t in all_types:
        assert t in result


def test_extract_empty_types_raises(llm):
    """extract() with empty types should raise ValueError."""
    text = "Some text."
    with pytest.raises(ValueError):
        extract(llm=llm, text=text, types=[])


def test_extract_invalid_type_raises(llm):
    """extract() with invalid type should raise ValueError."""
    text = "Some text."
    with pytest.raises(ValueError):
        extract(llm=llm, text=text, types=["invalid_type"])


def test_extract_with_context(llm):
    """extract() should use context when provided."""
    text = "She started in 2020 and earns $100k."
    result = extract(
        llm=llm,
        text=text,
        types=["numbers", "moments"],
        context="We are discussing Alice's career.",
    )
    
    assert "numbers" in result
    assert "moments" in result


def test_extract_entities_structure(llm):
    """Extracted entities should have name and type."""
    text = "Alice works at Microsoft in Seattle."
    result = extract(llm=llm, text=text, types=["entities"])
    
    if result["entities"]:
        entity = result["entities"][0]
        assert "name" in entity
        assert "type" in entity


def test_extract_numbers_structure(llm):
    """Extracted numbers should have value."""
    text = "Alice is 32 years old."
    result = extract(llm=llm, text=text, types=["numbers"])
    
    if result["numbers"]:
        number = result["numbers"][0]
        assert "value" in number


def test_extract_relationships_structure(llm):
    """Extracted relationships should have source, relationship, target."""
    text = "Alice works at Microsoft."
    result = extract(llm=llm, text=text, types=["relationships"])
    
    if result["relationships"]:
        rel = result["relationships"][0]
        assert "source" in rel
        assert "relationship" in rel
        assert "target" in rel


def test_extract_number_ranges_structure(llm):
    """Extracted number ranges should have min/max bounds."""
    text = "Temperature should be between 20 and 30 degrees."
    result = extract(llm=llm, text=text, types=["number_ranges"])
    
    if result["number_ranges"]:
        range_item = result["number_ranges"][0]
        # Should have min and/or max keys (as per NUMBER_RANGES_SPEC)
        assert "min" in range_item or "max" in range_item


def test_extract_moment_ranges_structure(llm):
    """Extracted moment ranges should have start and/or end."""
    text = "The event runs from January to March 2025."
    result = extract(llm=llm, text=text, types=["moment_ranges"])
    
    if result["moment_ranges"]:
        range_item = result["moment_ranges"][0]
        # Should have at least one bound
        assert "start" in range_item or "end" in range_item
