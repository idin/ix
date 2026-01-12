"""
Tests for smart_truncate_text function.
"""

from ixtools.string import smart_truncate_text


def test_smart_truncate_text_no_truncation_needed():
    """Test that text shorter than max_length is returned unchanged."""
    text = "Short text"
    result = smart_truncate_text(text=text, max_length=100)
    assert result == text
    assert len(result) == len(text)


def test_smart_truncate_text_no_search_terms():
    """Test that without search terms, it falls back to simple truncation."""
    text = "A" * 10000
    result = smart_truncate_text(text=text, max_length=100)
    assert len(result) == 100
    assert result == "A" * 100


def test_smart_truncate_text_single_term_string():
    """Test that single term can be passed as string."""
    text = "This is a test with keyword in the middle and more text after keyword"
    result = smart_truncate_text(text=text, search_terms="keyword", max_length=50)
    assert "keyword" in result.lower()
    assert len(result) <= 50


def test_smart_truncate_text_single_term_list():
    """Test that single term can be passed as list."""
    text = "This is a test with keyword in the middle and more text after keyword"
    result = smart_truncate_text(text=text, search_terms=["keyword"], max_length=50)
    assert "keyword" in result.lower()
    assert len(result) <= 50


def test_smart_truncate_text_multiple_terms():
    """Test that multiple terms are found and truncation includes all."""
    text = (
        "Prefix text before. "
        "First term appears here. "
        "Middle text between terms. "
        "Second term appears here. "
        "More text after both terms."
    )
    result = smart_truncate_text(
        text=text,
        search_terms=["first term", "second term"],
        max_length=100,
    )
    assert "first term" in result.lower()
    assert "second term" in result.lower()
    assert len(result) <= 100


def test_smart_truncate_text_finds_min_max_indices():
    """Test that truncation correctly finds min and max indices of all terms."""
    text = "A" * 500 + "keyword1" + "B" * 1000 + "keyword2" + "C" * 500
    result = smart_truncate_text(
        text=text,
        search_terms=["keyword1", "keyword2"],
        max_length=2000,
    )
    assert "keyword1" in result.lower()
    assert "keyword2" in result.lower()
    # Should include text around both keywords
    assert len(result) > 100
    assert len(result) < len(text)
    # Should remove majority of garbage text (A's at start and C's at end)
    # Original has 500 A's + 500 C's = 1000 chars of garbage
    # Result should be significantly shorter, removing most of this garbage
    garbage_removed = len(text) - len(result)
    assert garbage_removed >= 400, f"Expected at least 400 chars of garbage removed, got {garbage_removed}"


def test_smart_truncate_text_five_percent_buffer():
    """Test that 5% buffer is added on each side."""
    text = "A" * 10000 + "keyword" + "B" * 10000
    result = smart_truncate_text(
        text=text,
        search_terms=["keyword"],
        max_length=5000,
    )
    # Should include buffer before and after keyword
    assert "keyword" in result.lower()
    # Buffer should be approximately 5% of 20000 = 1000 on each side
    # So result should be longer than just the keyword
    assert len(result) > len("keyword")


def test_smart_truncate_text_special_regex_characters():
    """Test that terms with special regex characters work correctly."""
    text = "Text with gpt.4 and gpt$4 and gpt*4 models"
    result = smart_truncate_text(
        text=text,
        search_terms=["gpt.4", "gpt$4", "gpt*4"],
        max_length=100,
    )
    assert "gpt.4" in result.lower() or "gpt$4" in result.lower() or "gpt*4" in result.lower()


def test_smart_truncate_text_no_matches():
    """Test that when no terms are found, it falls back to simple truncation."""
    text = "A" * 10000
    result = smart_truncate_text(
        text=text,
        search_terms=["nonexistent"],
        max_length=100,
    )
    assert len(result) == 100
    assert result == "A" * 100


def test_smart_truncate_text_empty_text():
    """Test that empty text is handled correctly."""
    result = smart_truncate_text(text="", search_terms=["keyword"], max_length=100)
    assert result == ""


def test_smart_truncate_text_case_insensitive():
    """Test that search is case-insensitive."""
    text = "This text has KEYWORD in uppercase"
    result = smart_truncate_text(
        text=text,
        search_terms=["keyword"],
        max_length=50,
    )
    assert "KEYWORD" in result or "keyword" in result.lower()


def test_smart_truncate_text_multiple_occurrences():
    """Test that all occurrences of terms are considered for min/max."""
    text = "First keyword here. Middle text. Second keyword here. More text."
    result = smart_truncate_text(
        text=text,
        search_terms=["keyword"],
        max_length=100,
    )
    # Should include text from first to last occurrence
    assert "keyword" in result.lower()
    # Should include some of the middle text
    assert len(result) > len("keyword")


def test_smart_truncate_text_long_result_truncated():
    """Test that if result is still too long after smart truncation, it's truncated from end."""
    text = "A" * 5000 + "keyword" + "B" * 5000
    result = smart_truncate_text(
        text=text,
        search_terms=["keyword"],
        max_length=100,
    )
    assert len(result) == 100
    assert "keyword" in result.lower() or "A" in result or "B" in result

