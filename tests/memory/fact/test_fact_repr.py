"""
Tests for Fact string representation.
"""

from ixmachina.memory import Fact


def test_repr():
    """Test string representation of Fact."""
    fact = Fact(
        text="Alice works at Acme",
        relationship_type="employment",
        objects=[
            {"object_id": "alice-uuid-1234567890", "role": "employee"},
            {"object_id": "acme-uuid-9876543210", "role": "employer"},
        ],
    )
    
    repr_str = repr(fact)
    
    # Should include relationship type
    assert "employment" in repr_str
    
    # Should include truncated object IDs (first 8 chars)
    assert "alice-uu" in repr_str
    assert "acme-uui" in repr_str
    
    # Should include roles
    assert "employee" in repr_str
    assert "employer" in repr_str

