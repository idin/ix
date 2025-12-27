"""
Tests for NameRegistry token operations.

Tests token indexing, retrieval, and token-based lookups.
"""

from ixmachina.tools.text import NameRegistry


def test_tokens_are_indexed():
    """Test that tokens are automatically indexed when adding names."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    
    # Check tokens were indexed
    stats = registry.get_statistics()
    assert stats['total_tokens'] == 2  # "john" and "smith"


def test_get_names_containing_token():
    """Test finding names that contain a specific token."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    registry.add_name("John Doe")
    registry.add_name("Jane Smith")
    
    # Names with "john"
    john_names = registry.get_names_containing_token("john")
    assert set(john_names) == {"John Smith", "John Doe"}
    
    # Names with "smith"
    smith_names = registry.get_names_containing_token("smith")
    assert set(smith_names) == {"John Smith", "Jane Smith"}
    
    # Names with "doe"
    doe_names = registry.get_names_containing_token("doe")
    assert doe_names == ["John Doe"]
    
    # Non-existent token
    xyz_names = registry.get_names_containing_token("xyz")
    assert xyz_names == []


def test_get_all_tokens():
    """Test getting all tokens with frequency counts."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    registry.add_name("John Doe")
    registry.add_name("Jane Smith")
    
    tokens = registry.get_all_tokens(sort_by_frequency=True)
    
    # "john" appears in 2 names, "smith" appears in 2 names
    # "jane" and "doe" appear in 1 name each
    assert len(tokens) == 4
    
    # Most frequent tokens first
    token_dict = dict(tokens)
    assert token_dict['john'] == 2
    assert token_dict['smith'] == 2
    assert token_dict['jane'] == 1
    assert token_dict['doe'] == 1


def test_get_name_tokens():
    """Test getting tokens that make up a name."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    registry.add_name("Mary Jane Watson")
    
    john_tokens = registry.get_name_tokens("John Smith")
    assert john_tokens == ["john", "smith"]
    
    mary_tokens = registry.get_name_tokens("Mary Jane Watson")
    assert mary_tokens == ["mary", "jane", "watson"]
    
    # Non-existent name
    none_tokens = registry.get_name_tokens("Unknown Person")
    assert none_tokens is None


def test_multi_word_names():
    """Test that multi-word names are tokenized correctly."""
    registry = NameRegistry()
    
    registry.add_name("Mary Jane Watson")
    
    # All three tokens should be indexed
    assert "Mary Jane Watson" in registry.get_names_containing_token("mary")
    assert "Mary Jane Watson" in registry.get_names_containing_token("jane")
    assert "Mary Jane Watson" in registry.get_names_containing_token("watson")


def test_tokens_case_insensitive():
    """Test that token lookups are case-insensitive."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    
    # All variations should find the name
    assert "John Smith" in registry.get_names_containing_token("john")
    assert "John Smith" in registry.get_names_containing_token("JOHN")
    assert "John Smith" in registry.get_names_containing_token("John")
    assert "John Smith" in registry.get_names_containing_token("smith")
    assert "John Smith" in registry.get_names_containing_token("SMITH")

