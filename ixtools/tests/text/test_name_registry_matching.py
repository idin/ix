"""
Tests for NameRegistry matching operations.

Tests finding names in text with fuzzy matching.
"""

from ixtools.text import NameRegistry


def test_find_name_in_text_exact_match():
    """Test finding a name with exact token matches."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    
    result = registry.find_name_in_text("john_smith_report.pdf")
    
    assert result is not None
    canonical, score, details = result
    assert canonical == "John Smith"
    assert score == 100  # Perfect match


def test_find_name_in_text_fuzzy_match():
    """Test finding a name with fuzzy token matching (Smiths -> Smith)."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    
    # "smiths" should fuzzy match to "smith"
    result = registry.find_name_in_text("john_smiths_report.pdf")
    
    assert result is not None
    canonical, score, details = result
    assert canonical == "John Smith"
    assert score >= 70  # Should pass threshold


def test_find_name_in_text_no_match():
    """Test that non-matching text returns None."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    
    result = registry.find_name_in_text("alice_wilson_report.pdf")
    
    assert result is None


def test_find_name_in_text_partial_match_below_threshold():
    """Test that partial matches below threshold return None."""
    registry = NameRegistry()
    
    registry.add_name("John Smith Wilson")  # 3 tokens
    
    # Only 1 token matches
    result = registry.find_name_in_text("john_report.pdf", threshold=80)
    
    # Should not match because coverage is only 1/3 = 33%
    # Coverage * avg_score + bonus would be ~33, below threshold 80
    assert result is None


def test_find_all_names_in_text():
    """Test finding multiple names in one text."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    registry.add_name("Jane Doe")
    
    results = registry.find_all_names_in_text("john_smith_and_jane_doe_report.pdf")
    
    assert len(results) >= 2
    found_names = [name for name, score, details in results]
    assert "John Smith" in found_names
    assert "Jane Doe" in found_names


def test_find_name_case_insensitive():
    """Test that matching is case-insensitive."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    
    # All case variations should match
    assert registry.find_name_in_text("JOHN_SMITH_report.pdf") is not None
    assert registry.find_name_in_text("john_smith_report.pdf") is not None
    assert registry.find_name_in_text("John_Smith_report.pdf") is not None


def test_find_name_with_special_characters():
    """Test finding names when text has special characters."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    
    # Various separators - all should create separate tokens
    assert registry.find_name_in_text("john-smith_report.pdf") is not None
    assert registry.find_name_in_text("john.smith.report.pdf") is not None  # Dots now split tokens
    assert registry.find_name_in_text("john smith report.pdf") is not None


def test_find_concatenated_tokens():
    """Test finding names when tokens are concatenated (no separator)."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    
    # "johnsmith" should be split into "john" + "smith"
    result = registry.find_name_in_text("johnsmith_report.pdf")
    
    assert result is not None
    canonical, score, details = result
    assert canonical == "John Smith"
    # Score will be lower than perfect match due to splitting penalty
    assert score >= 70


def test_adjacency_bonus():
    """Test that adjacent tokens get a scoring bonus."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    
    # Adjacent tokens: john_smith
    result_adjacent = registry.find_name_in_text("john_smith_report.pdf")
    
    # Non-adjacent would be: john_xyz_smith (if we tested it)
    # Adjacent should have higher score due to adjacency bonus
    
    assert result_adjacent is not None
    _, score_adjacent, details_adjacent = result_adjacent
    
    # Should have adjacency bonus
    assert details_adjacent['adjacency_bonus'] > 0


def test_multi_word_name_matching():
    """Test matching names with more than 2 words."""
    registry = NameRegistry()
    
    registry.add_name("Mary Jane Watson")
    
    result = registry.find_name_in_text("mary_jane_watson_photos.jpg")
    
    assert result is not None
    canonical, score, details = result
    assert canonical == "Mary Jane Watson"
    assert score >= 95  # Should be high score


def test_token_threshold():
    """Test that token_threshold parameter works."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    
    # With high token threshold, "smiths" might not match "smith"
    result_strict = registry.find_name_in_text(
        "john_smiths_report.pdf",
        token_threshold=95  # Very strict
    )
    
    # With normal threshold, it should match
    result_normal = registry.find_name_in_text(
        "john_smiths_report.pdf",
        token_threshold=80  # Normal
    )
    
    # Normal threshold should find it
    assert result_normal is not None

