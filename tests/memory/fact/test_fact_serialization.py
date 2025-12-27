"""
Tests for Fact serialization (to_dict/from_dict).
"""

from ixmachina.memory import Fact


def test_to_dict():
    """Convert fact to dictionary."""
    fact = Fact(
        text="Alice works at Acme",
        relationship_type="employment",
        objects=[
            {"object_id": "alice-id", "role": "employee"},
            {"object_id": "acme-id", "role": "employer"},
        ],
        fact_id="custom-fact-id",
        metadata={"confidence": 0.95},
        embedding=[0.1, 0.2, 0.3],
    )
    
    data = fact.to_dict()
    
    assert data["fact_id"] == "custom-fact-id"
    assert data["text"] == "Alice works at Acme"
    assert data["relationship_type"] == "employment"
    assert len(data["objects"]) == 2
    assert data["metadata"] == {"confidence": 0.95}
    assert data["embedding"] == [0.1, 0.2, 0.3]
    assert "created_at" in data
    assert "updated_at" in data


def test_from_dict():
    """Create fact from dictionary."""
    data = {
        "fact_id": "test-fact-id",
        "text": "Bob is father of Charlie",
        "relationship_type": "father_of",
        "objects": [
            {"object_id": "bob-id", "role": "father"},
            {"object_id": "charlie-id", "role": "child"},
        ],
        "metadata": {"source": "family_tree"},
        "embedding": [0.4, 0.5],
        "created_at": "2024-01-01T10:00:00",
        "updated_at": "2024-01-01T11:00:00",
    }
    
    fact = Fact.from_dict(data=data)
    
    assert fact.fact_id == "test-fact-id"
    assert fact.text == "Bob is father of Charlie"
    assert fact.relationship_type == "father_of"
    assert len(fact.objects) == 2
    assert fact.metadata == {"source": "family_tree"}
    assert fact.embedding == [0.4, 0.5]
    assert fact.created_at.isoformat() == "2024-01-01T10:00:00"
    assert fact.updated_at.isoformat() == "2024-01-01T11:00:00"


def test_round_trip_serialization():
    """Test to_dict followed by from_dict preserves all data."""
    original_fact = Fact(
        text="David manages Eve",
        relationship_type="manager_of",
        objects=[
            {"object_id": "david-id", "role": "manager"},
            {"object_id": "eve-id", "role": "subordinate"},
        ],
        fact_id="round-trip-id",
        metadata={"team": "engineering"},
        embedding=[0.7, 0.8, 0.9],
    )
    
    # Convert to dict and back
    data = original_fact.to_dict()
    restored_fact = Fact.from_dict(data=data)
    
    assert restored_fact.fact_id == original_fact.fact_id
    assert restored_fact.text == original_fact.text
    assert restored_fact.relationship_type == original_fact.relationship_type
    assert restored_fact.objects == original_fact.objects
    assert restored_fact.metadata == original_fact.metadata
    assert restored_fact.embedding == original_fact.embedding
    assert restored_fact.created_at == original_fact.created_at
    assert restored_fact.updated_at == original_fact.updated_at


def test_from_dict_with_minimal_data():
    """Create fact from dictionary with minimal required fields."""
    data = {
        "text": "Frank works at Globex",
        "relationship_type": "employment",
        "objects": [
            {"object_id": "frank-id", "role": "employee"},
            {"object_id": "globex-id", "role": "employer"},
        ],
    }
    
    fact = Fact.from_dict(data=data)
    
    assert fact.text == "Frank works at Globex"
    assert fact.relationship_type == "employment"
    assert len(fact.objects) == 2
    assert fact.metadata == {}
    assert fact.embedding is None
    assert fact.fact_id is not None  # Auto-generated

