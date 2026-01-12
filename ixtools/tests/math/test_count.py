"""
Tests for count functions.
"""

import pytest

from ixtools.math.count import (
    count_characters,
    count_words,
    count_items,
    count,
    count_occurrences,
)


def test_count_characters_basic():
    """Test basic character counting."""
    result = count_characters("hello")
    assert result["success"] is True
    assert result["result"]["total"] == 5
    assert result["result"]["total_unique"] == 4
    assert result["error"] is None


def test_count_characters_with_spaces():
    """Test character counting with spaces."""
    result = count_characters("hello world")
    assert result["success"] is True
    assert result["result"]["total"] == 11
    assert " " in result["result"]["unique_elements"]
    assert result["result"]["unique_elements"][" "] == 1
    assert result["error"] is None


def test_count_characters_strawberry():
    """Test character counting with strawberry (has 3 r's)."""
    result = count_characters("strawberry")
    assert result["success"] is True
    assert result["result"]["total"] == 10
    assert result["result"]["unique_elements"]["r"] == 3
    assert result["result"]["total_unique"] == 8
    assert result["error"] is None


def test_count_characters_case_sensitive_false():
    """Test character counting case insensitive (default)."""
    result = count_characters("Hello", case_sensitive=False)
    assert result["success"] is True
    assert result["result"]["unique_elements"]["h"] == 1
    assert result["result"]["unique_elements"]["e"] == 1
    assert result["result"]["unique_elements"]["l"] == 2
    assert result["result"]["unique_elements"]["o"] == 1
    assert "H" not in result["result"]["unique_elements"]
    assert result["error"] is None


def test_count_characters_case_sensitive_true():
    """Test character counting case sensitive."""
    result = count_characters("Hello", case_sensitive=True)
    assert result["success"] is True
    assert result["result"]["unique_elements"]["H"] == 1
    assert result["result"]["unique_elements"]["e"] == 1
    assert result["result"]["unique_elements"]["l"] == 2
    assert result["result"]["unique_elements"]["o"] == 1
    assert result["result"]["total_unique"] == 4
    assert result["error"] is None


def test_count_characters_empty_string():
    """Test character counting with empty string."""
    result = count_characters("")
    assert result["success"] is True
    assert result["result"]["total"] == 0
    assert result["result"]["total_unique"] == 0
    assert result["result"]["unique_elements"] == {}
    assert result["error"] is None


def test_count_characters_invalid_type():
    """Test character counting with invalid type."""
    result = count_characters(123)
    assert result["success"] is False
    assert result["result"] is None
    assert "Expected string" in result["error"]


def test_count_words_basic():
    """Test basic word counting."""
    result = count_words("hello world")
    assert result["success"] is True
    assert result["result"]["total"] == 2
    assert result["result"]["total_unique"] == 2
    assert result["error"] is None


def test_count_words_repeated():
    """Test word counting with repeated words."""
    result = count_words("hello world hello")
    assert result["success"] is True
    assert result["result"]["total"] == 3
    assert result["result"]["total_unique"] == 2
    assert result["result"]["unique_elements"]["hello"] == 2
    assert result["result"]["unique_elements"]["world"] == 1
    assert result["error"] is None


def test_count_words_case_sensitive_false():
    """Test word counting case insensitive (default)."""
    result = count_words("Hello hello HELLO", case_sensitive=False)
    assert result["success"] is True
    assert result["result"]["total"] == 3
    assert result["result"]["total_unique"] == 1
    assert result["result"]["unique_elements"]["hello"] == 3
    assert result["error"] is None


def test_count_words_case_sensitive_true():
    """Test word counting case sensitive."""
    result = count_words("Hello hello HELLO", case_sensitive=True)
    assert result["success"] is True
    assert result["result"]["total"] == 3
    assert result["result"]["total_unique"] == 3
    assert result["result"]["unique_elements"]["Hello"] == 1
    assert result["result"]["unique_elements"]["hello"] == 1
    assert result["result"]["unique_elements"]["HELLO"] == 1
    assert result["error"] is None


def test_count_words_empty_string():
    """Test word counting with empty string."""
    result = count_words("")
    assert result["success"] is True
    assert result["result"]["total"] == 0
    assert result["result"]["total_unique"] == 0
    assert result["result"]["unique_elements"] == {}
    assert result["error"] is None


def test_count_words_multiple_spaces():
    """Test word counting with multiple spaces."""
    result = count_words("hello    world")
    assert result["success"] is True
    assert result["result"]["total"] == 2
    assert result["result"]["total_unique"] == 2
    assert result["error"] is None


def test_count_words_invalid_type():
    """Test word counting with invalid type."""
    result = count_words(123)
    assert result["success"] is False
    assert result["result"] is None
    assert "Expected string" in result["error"]


def test_count_items_list():
    """Test item counting with list."""
    result = count_items([1, 2, 2, 3, 3, 3])
    assert result["success"] is True
    assert result["result"]["total"] == 6
    assert result["result"]["total_unique"] == 3
    assert result["result"]["unique_elements"][1] == 1
    assert result["result"]["unique_elements"][2] == 2
    assert result["result"]["unique_elements"][3] == 3
    assert result["error"] is None


def test_count_items_tuple():
    """Test item counting with tuple."""
    result = count_items((1, 2, 2, 3))
    assert result["success"] is True
    assert result["result"]["total"] == 4
    assert result["result"]["total_unique"] == 3
    assert result["error"] is None


def test_count_items_set():
    """Test item counting with set."""
    result = count_items({1, 2, 3})
    assert result["success"] is True
    assert result["result"]["total"] == 3
    assert result["result"]["total_unique"] == 3
    assert result["error"] is None


def test_count_items_string():
    """Test item counting with string."""
    result = count_items("hello")
    assert result["success"] is True
    assert result["result"]["total"] == 5
    assert result["result"]["total_unique"] == 4
    assert result["result"]["unique_elements"]["l"] == 2
    assert result["error"] is None


def test_count_items_empty():
    """Test item counting with empty iterable."""
    result = count_items([])
    assert result["success"] is True
    assert result["result"]["total"] == 0
    assert result["result"]["total_unique"] == 0
    assert result["result"]["unique_elements"] == {}
    assert result["error"] is None


def test_count_items_invalid_type():
    """Test item counting with invalid type."""
    result = count_items(123)
    assert result["success"] is False
    assert result["result"] is None
    assert "Expected list, tuple, set, or string" in result["error"]


def test_count_list():
    """Test count function with list."""
    result = count([1, 2, 3, 4, 5])
    assert result["success"] is True
    assert result["result"] == 5
    assert result["error"] is None


def test_count_tuple():
    """Test count function with tuple."""
    result = count((1, 2, 3))
    assert result["success"] is True
    assert result["result"] == 3
    assert result["error"] is None


def test_count_set():
    """Test count function with set."""
    result = count({1, 2, 3, 4})
    assert result["success"] is True
    assert result["result"] == 4
    assert result["error"] is None


def test_count_string():
    """Test count function with string."""
    result = count("hello")
    assert result["success"] is True
    assert result["result"] == 5
    assert result["error"] is None


def test_count_empty():
    """Test count function with empty iterable."""
    result = count([])
    assert result["success"] is True
    assert result["result"] == 0
    assert result["error"] is None


def test_count_invalid_type():
    """Test count function with invalid type."""
    result = count(123)
    assert result["success"] is False
    assert result["result"] is None
    assert "Expected list, tuple, set, or string" in result["error"]


def test_count_occurrences_list_no_elements():
    """Test count_occurrences with list and no elements specified."""
    result = count_occurrences([1, 2, 2, 3, 3, 3])
    assert result["success"] is True
    assert result["result"]["total_elements"] == 6
    assert result["result"]["total_unique"] == 3
    assert result["result"]["unique_elements"][1] == 1
    assert result["result"]["unique_elements"][2] == 2
    assert result["result"]["unique_elements"][3] == 3
    assert result["error"] is None


def test_count_occurrences_list_with_elements():
    """Test count_occurrences with list and specific elements."""
    result = count_occurrences([1, 2, 2, 3, 3, 3], [2, 3, 4])
    assert result["success"] is True
    assert result["result"]["counts"][2] == 2
    assert result["result"]["counts"][3] == 3
    assert result["result"]["counts"][4] == 0
    assert result["result"]["total_occurrences"] == 5
    assert 2 in result["result"]["elements_found"]
    assert 3 in result["result"]["elements_found"]
    assert 4 not in result["result"]["elements_found"]
    assert result["error"] is None


def test_count_occurrences_list_single_element():
    """Test count_occurrences with list and single element."""
    result = count_occurrences([1, 2, 2, 3], 2)
    assert result["success"] is True
    assert result["result"]["counts"][2] == 2
    assert result["result"]["total_occurrences"] == 2
    assert result["error"] is None


def test_count_occurrences_string_no_elements():
    """Test count_occurrences with string and no elements (should count words and characters)."""
    result = count_occurrences("hello world")
    assert result["success"] is True
    assert "words" in result["result"]
    assert "characters" in result["result"]
    assert result["result"]["words"]["total_elements"] == 2
    assert result["result"]["characters"]["total_elements"] == 11
    assert result["error"] is None


def test_count_occurrences_string_with_characters():
    """Test count_occurrences with string and specific characters."""
    result = count_occurrences("strawberry", ["r", "s", "t"])
    assert result["success"] is True
    assert result["result"]["counts"]["r"] == 3
    assert result["result"]["counts"]["s"] == 1
    assert result["result"]["counts"]["t"] == 1
    assert result["result"]["total_occurrences"] == 5
    assert result["error"] is None


def test_count_occurrences_string_single_character():
    """Test count_occurrences with string and single character."""
    result = count_occurrences("strawberry", "r")
    assert result["success"] is True
    assert result["result"]["counts"]["r"] == 3
    assert result["result"]["total_occurrences"] == 3
    assert result["error"] is None


def test_count_occurrences_tuple():
    """Test count_occurrences with tuple."""
    result = count_occurrences((1, 2, 2, 3), [2, 3])
    assert result["success"] is True
    assert result["result"]["counts"][2] == 2
    assert result["result"]["counts"][3] == 1
    assert result["error"] is None


def test_count_occurrences_set():
    """Test count_occurrences with set."""
    result = count_occurrences({1, 2, 3}, [2, 3, 4])
    assert result["success"] is True
    assert result["result"]["counts"][2] == 1
    assert result["result"]["counts"][3] == 1
    assert result["result"]["counts"][4] == 0
    assert result["error"] is None


def test_count_occurrences_empty_iterable():
    """Test count_occurrences with empty iterable."""
    result = count_occurrences([])
    assert result["success"] is True
    assert result["result"]["total_elements"] == 0
    assert result["result"]["total_unique"] == 0
    assert result["result"]["unique_elements"] == {}
    assert result["error"] is None


def test_count_occurrences_empty_string():
    """Test count_occurrences with empty string."""
    result = count_occurrences("")
    assert result["success"] is True
    assert result["result"]["words"]["total_elements"] == 0
    assert result["result"]["characters"]["total_elements"] == 0
    assert result["error"] is None


def test_count_occurrences_invalid_type():
    """Test count_occurrences with invalid type."""
    result = count_occurrences(123)
    assert result["success"] is False
    assert result["result"] is None
    assert "Expected list, tuple, set, or string" in result["error"]
