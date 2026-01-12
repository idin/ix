"""
Tests for NameRegistry basic operations.

Tests name addition, retrieval, and usage tracking.
"""

from ixtools.text import NameRegistry


def test_add_name_basic():
    """Test adding a name to the registry."""
    registry = NameRegistry()
    
    canonical = registry.add_name("John Smith")
    
    assert canonical == "John Smith"
    assert len(registry) == 1


def test_add_name_preserves_case():
    """Test that exact case is preserved when adding names."""
    registry = NameRegistry()
    
    # Test lowercase in middle (like "Chris de Burgh")
    canonical = registry.add_name("Chris de Burgh")
    assert canonical == "Chris de Burgh"
    
    # Test various cases
    registry.add_name("iPhone")
    registry.add_name("eBay")
    
    assert "iPhone" in registry
    assert "eBay" in registry


def test_add_duplicate_name_increments_count():
    """Test that adding the same name twice increments usage count."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    registry.add_name("john_smith")  # Same name, different format
    registry.add_name("JOHN SMITH")  # Same name, uppercase
    
    # Should only have one canonical form
    assert len(registry) == 1
    
    # Usage count should be 3
    assert registry.get_usage_count("John Smith") == 3


def test_get_canonical():
    """Test retrieving canonical form of a name."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    
    # Case-insensitive retrieval
    assert registry.get_canonical("john smith") == "John Smith"
    assert registry.get_canonical("JOHN SMITH") == "John Smith"
    assert registry.get_canonical("john_smith") == "John Smith"
    assert registry.get_canonical("johnsmith") == "John Smith"
    
    # Non-existent name
    assert registry.get_canonical("Jane Doe") is None


def test_get_all_names():
    """Test getting all names with usage counts."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    registry.add_name("john smith")  # Increment count
    registry.add_name("Jane Doe")
    
    names = registry.get_all_names(sort_by_usage=True)
    
    assert len(names) == 2
    assert names[0] == ("John Smith", 2)  # Most used first
    assert names[1] == ("Jane Doe", 1)


def test_get_names_by_letter():
    """Test getting names by first letter."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    registry.add_name("Jane Doe")
    registry.add_name("Alice Wilson")
    
    j_names = registry.get_names_by_letter('j')
    assert set(j_names) == {"John Smith", "Jane Doe"}
    
    a_names = registry.get_names_by_letter('a')
    assert a_names == ["Alice Wilson"]
    
    z_names = registry.get_names_by_letter('z')
    assert z_names == []


def test_contains_operator():
    """Test the 'in' operator for checking name existence."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    
    assert "john smith" in registry
    assert "JOHN SMITH" in registry
    assert "Jane Doe" not in registry


def test_repr():
    """Test string representation of registry."""
    registry = NameRegistry()
    
    registry.add_name("John Smith")
    registry.add_name("Jane Doe")
    
    repr_str = repr(registry)
    
    assert "NameRegistry" in repr_str
    assert "names=2" in repr_str
    assert "tokens=" in repr_str  # Should show token count

