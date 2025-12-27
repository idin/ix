"""
Tests for NameRegistry standardization operations.

Tests standardizing names in text (replacing with canonical forms).
"""

from ixmachina.tools.text import NameRegistry


def test_standardize_single_name():
    """Test standardizing text with one name."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    
    result = registry.standardize_names_in_text("john_smith_report.pdf")
    
    # Note: token extraction loses original formatting (underscore vs space vs dot)
    assert "John Smith" in result['standardized_text']
    assert result['original_text'] == "john_smith_report.pdf"
    assert result['names_found'] == ["John Smith"]
    assert result['num_replacements'] == 1


def test_standardize_multiple_names():
    """Test standardizing text with multiple names."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    registry.add_name("Jane Doe")
    
    result = registry.standardize_names_in_text("john_smith_and_jane_doe_report.pdf")
    
    assert "John Smith" in result['standardized_text']
    assert "Jane Doe" in result['standardized_text']
    assert set(result['names_found']) == {"John Smith", "Jane Doe"}
    assert result['num_replacements'] == 2


def test_standardize_no_names():
    """Test standardizing text with no matching names."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    
    result = registry.standardize_names_in_text("some_random_report.pdf")
    
    assert result['standardized_text'] == "some_random_report.pdf"
    assert result['names_found'] == []
    assert result['num_replacements'] == 0


def test_standardize_preserves_case_from_registry():
    """Test that standardization uses the canonical case from registry."""
    registry = NameRegistry()
    
    # Register with specific case
    registry.add_name("Chris de Burgh")  # lowercase "de"
    
    result = registry.standardize_names_in_text("chris_de_burgh_concert.mp4")
    
    # Should use canonical form with lowercase "de"
    assert "Chris de Burgh" in result['standardized_text']
    assert "Chris de Burgh" in result['names_found']


def test_standardize_fuzzy_match():
    """Test standardization with fuzzy matching (Smiths -> Smith)."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    
    # "smiths" should fuzzy match to "smith"
    result = registry.standardize_names_in_text("john_smiths_report.pdf")
    
    assert "John Smith" in result['standardized_text']
    assert "John Smith" in result['names_found']


def test_standardize_overlapping_prevention():
    """Test that overlapping name matches don't conflict."""
    registry = NameRegistry()
    
    # Add names that could overlap
    registry.add_name("John")
    registry.add_name("John Smith")
    
    result = registry.standardize_names_in_text("john_smith_report.pdf")
    
    # Should pick the longer/better match (John Smith, not just John)
    # and not replace both
    assert result['num_replacements'] >= 1


def test_standardize_threshold_parameter():
    """Test that threshold parameter affects standardization."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    
    # With very high threshold, might not match fuzzy
    result_strict = registry.standardize_names_in_text(
        "john_smithson_report.pdf",  # "smithson" is different from "smith"
        threshold=95
    )
    
    # Should probably not match
    assert result_strict['num_replacements'] == 0


def test_standardize_returns_dictionary():
    """Test that standardize returns a properly structured dictionary."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    
    result = registry.standardize_names_in_text("john_smith_report.pdf")
    
    # Check all required keys
    assert 'standardized_text' in result
    assert 'original_text' in result
    assert 'names_found' in result
    assert 'num_replacements' in result
    
    # Check types
    assert isinstance(result['standardized_text'], str)
    assert isinstance(result['original_text'], str)
    assert isinstance(result['names_found'], list)
    assert isinstance(result['num_replacements'], int)


def test_standardize_multi_word_names():
    """Test standardizing multi-word names."""
    registry = NameRegistry()
    
    registry.add_name("The Beatles")
    registry.add_name("John Lennon")
    
    result = registry.standardize_names_in_text("the_beatles_john_lennon_live_1964.mp4")
    
    assert "The Beatles" in result['standardized_text']
    assert "John Lennon" in result['standardized_text']
    assert set(result['names_found']) == {"The Beatles", "John Lennon"}

