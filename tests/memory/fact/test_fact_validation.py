"""
Tests for Fact validation.
"""

import pytest
from ixmachina.memory import Fact


def test_fact_rejects_non_list_objects():
    """Fact should reject objects that are not a list."""
    with pytest.raises(ValueError, match="objects must be a list"):
        Fact(
            text="Invalid fact",
            relationship_type="invalid",
            objects="not-a-list",
        )


def test_fact_rejects_non_dict_objects():
    """Fact should reject objects that are not dictionaries."""
    with pytest.raises(ValueError, match="Each object must be a dictionary"):
        Fact(
            text="Invalid fact",
            relationship_type="invalid",
            objects=["not-a-dict"],
        )


def test_fact_rejects_objects_without_object_id():
    """Fact should reject objects without object_id key."""
    with pytest.raises(ValueError, match="must have 'object_id' and 'role' keys"):
        Fact(
            text="Invalid fact",
            relationship_type="invalid",
            objects=[{"role": "some_role"}],  # Missing object_id
        )


def test_fact_rejects_objects_without_role():
    """Fact should reject objects without role key."""
    with pytest.raises(ValueError, match="must have 'object_id' and 'role' keys"):
        Fact(
            text="Invalid fact",
            relationship_type="invalid",
            objects=[{"object_id": "some-id"}],  # Missing role
        )


def test_fact_accepts_valid_objects():
    """Fact should accept objects with correct format."""
    fact = Fact(
        text="Valid fact",
        relationship_type="test",
        objects=[
            {"object_id": "id-1", "role": "role-1"},
            {"object_id": "id-2", "role": "role-2"},
        ],
    )
    
    assert len(fact.objects) == 2

