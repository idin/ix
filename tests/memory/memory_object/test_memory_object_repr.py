"""
Tests for MemoryObject string representation.
"""

from ixmachina.memory import MemoryObject


def test_repr():
    """Test string representation of MemoryObject."""
    obj = MemoryObject(
        name="Alice",
        value="test data",
        object_id="alice-uuid-1234567890abcdef",
        tags=["employee", "senior"],
    )
    
    repr_str = repr(obj)
    
    # Should include truncated object ID (first 8 chars)
    assert "alice-uu" in repr_str
    
    # Should include name
    assert "Alice" in repr_str
    
    # Should include tags
    assert "employee" in repr_str
    assert "senior" in repr_str


def test_repr_without_tags():
    """Test string representation when no tags are present."""
    obj = MemoryObject(
        name="Bob",
        value="data",
        object_id="bob-id-123",
    )
    
    repr_str = repr(obj)
    
    assert "Bob" in repr_str
    assert "bob-id-1" in repr_str
    assert "[]" in repr_str  # Empty tags list

