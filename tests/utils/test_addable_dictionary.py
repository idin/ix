"""
Tests for AddableDictionary class.
"""

import pytest

from ixmachina.utils.addable_dictionary import AddableDictionary


def test_addable_dictionary_creation():
    """Test that AddableDictionary can be created like a regular dict."""
    usage = AddableDictionary({"a": 1, "b": 2})
    
    assert isinstance(usage, dict)
    assert isinstance(usage, AddableDictionary)
    assert usage["a"] == 1
    assert usage["b"] == 2


def test_addable_dictionary_addition():
    """Test that AddableDictionary supports + operator."""
    dict1 = AddableDictionary({"a": 1, "b": 2})
    dict2 = {"b": 3, "c": 4}
    
    result = dict1 + dict2
    
    assert isinstance(result, AddableDictionary)
    assert result["a"] == 1  # From dict1
    assert result["b"] == 5  # Summed: 2 + 3
    assert result["c"] == 4  # From dict2


def test_addable_dictionary_inplace_addition():
    """Test that AddableDictionary supports += operator."""
    dict1 = AddableDictionary({"a": 1, "b": 2})
    dict2 = {"b": 3, "c": 4}
    
    dict1 += dict2
    
    assert isinstance(dict1, AddableDictionary)
    assert dict1["a"] == 1  # From original dict1
    assert dict1["b"] == 5  # Summed: 2 + 3
    assert dict1["c"] == 4  # From dict2


def test_addable_dictionary_addition_with_float():
    """Test that AddableDictionary handles float values."""
    dict1 = AddableDictionary({"a": 1.5, "b": 2.0})
    dict2 = {"b": 3.5, "c": 4.0}
    
    result = dict1 + dict2
    
    assert result["a"] == 1.5
    assert result["b"] == 5.5  # Summed: 2.0 + 3.5
    assert result["c"] == 4.0


def test_addable_dictionary_addition_with_non_numeric():
    """Test that AddableDictionary handles non-numeric values."""
    dict1 = AddableDictionary({"a": 1, "b": "hello"})
    dict2 = {"b": "world", "c": 4}
    
    result = dict1 + dict2
    
    assert result["a"] == 1  # From dict1
    assert result["b"] == "world"  # Non-numeric: overwritten by dict2
    assert result["c"] == 4  # From dict2


def test_addable_dictionary_addition_with_mixed_types():
    """Test that AddableDictionary handles mixed numeric and non-numeric."""
    dict1 = AddableDictionary({"a": 1, "b": 2, "c": "hello"})
    dict2 = {"b": 3, "c": "world", "d": 4}
    
    result = dict1 + dict2
    
    assert result["a"] == 1  # From dict1 only
    assert result["b"] == 5  # Summed: 2 + 3
    assert result["c"] == "world"  # Non-numeric: overwritten
    assert result["d"] == 4  # From dict2


def test_addable_dictionary_empty_addition():
    """Test that AddableDictionary works with empty dictionaries."""
    dict1 = AddableDictionary({"a": 1, "b": 2})
    dict2 = {}
    
    result = dict1 + dict2
    
    assert result["a"] == 1
    assert result["b"] == 2
    assert len(result) == 2


def test_addable_dictionary_chained_addition():
    """Test that AddableDictionary can be chained with multiple additions."""
    dict1 = AddableDictionary({"a": 1, "b": 2})
    dict2 = {"b": 3, "c": 4}
    dict3 = {"c": 5, "d": 6}
    
    result = dict1 + dict2 + dict3
    
    assert result["a"] == 1
    assert result["b"] == 5  # 2 + 3
    assert result["c"] == 9  # 4 + 5
    assert result["d"] == 6

