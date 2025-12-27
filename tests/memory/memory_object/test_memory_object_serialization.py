"""
Tests for MemoryObject serialization (to_dict/from_dict).
"""

from ixmachina.memory import MemoryObject


def test_to_dict():
    """Convert memory object to dictionary."""
    obj = MemoryObject(
        name="Alice",
        value={"age": 30, "role": "Engineer"},
        description="Software engineer at Acme",
        object_id="alice-id",
        tags=["employee", "senior"],
        metadata={"department": "Engineering"},
        embedding=[0.1, 0.2, 0.3],
    )
    
    obj.record_access()
    
    data = obj.to_dict()
    
    assert data["object_id"] == "alice-id"
    assert data["name"] == "Alice"
    assert data["description"] == "Software engineer at Acme"
    assert data["value"] == {"age": 30, "role": "Engineer"}
    assert data["tags"] == ["employee", "senior"]
    assert data["metadata"] == {"department": "Engineering"}
    assert data["embedding"] == [0.1, 0.2, 0.3]
    assert "created_at" in data
    assert "updated_at" in data
    assert data["access_count"] == 1
    assert data["last_accessed"] is not None


def test_from_dict():
    """Create memory object from dictionary."""
    data = {
        "object_id": "bob-id",
        "name": "Bob",
        "description": "CEO of Initech",
        "value": {"title": "CEO"},
        "tags": ["executive"],
        "metadata": {"tenure_years": 10},
        "embedding": [0.4, 0.5],
        "created_at": "2024-01-01T10:00:00",
        "updated_at": "2024-01-01T11:00:00",
        "access_count": 5,
        "last_accessed": "2024-01-01T11:30:00",
    }
    
    obj = MemoryObject.from_dict(data=data)
    
    assert obj.object_id == "bob-id"
    assert obj.name == "Bob"
    assert obj.description == "CEO of Initech"
    assert obj.value == {"title": "CEO"}
    assert obj.tags == ["executive"]
    assert obj.metadata == {"tenure_years": 10}
    assert obj.embedding == [0.4, 0.5]
    assert obj.created_at.isoformat() == "2024-01-01T10:00:00"
    assert obj.updated_at.isoformat() == "2024-01-01T11:00:00"
    assert obj.access_count == 5
    assert obj.last_accessed.isoformat() == "2024-01-01T11:30:00"


def test_round_trip_serialization():
    """Test to_dict followed by from_dict preserves all data."""
    original_obj = MemoryObject(
        name="Charlie",
        value=[1, 2, 3],
        description="Test object",
        object_id="charlie-id",
        tags=["test", "demo"],
        metadata={"source": "test"},
        embedding=[0.6, 0.7, 0.8],
    )
    
    original_obj.record_access()
    
    # Convert to dict and back
    data = original_obj.to_dict()
    restored_obj = MemoryObject.from_dict(data=data)
    
    assert restored_obj.object_id == original_obj.object_id
    assert restored_obj.name == original_obj.name
    assert restored_obj.description == original_obj.description
    assert restored_obj.value == original_obj.value
    assert restored_obj.tags == original_obj.tags
    assert restored_obj.metadata == original_obj.metadata
    assert restored_obj.embedding == original_obj.embedding
    assert restored_obj.created_at == original_obj.created_at
    assert restored_obj.updated_at == original_obj.updated_at
    assert restored_obj.access_count == original_obj.access_count
    assert restored_obj.last_accessed == original_obj.last_accessed


def test_from_dict_with_minimal_data():
    """Create memory object from dictionary with minimal required fields."""
    data = {
        "name": "David",
        "value": "minimal data",
    }
    
    obj = MemoryObject.from_dict(data=data)
    
    assert obj.name == "David"
    assert obj.value == "minimal data"
    assert obj.description == ""
    assert obj.tags == []
    assert obj.metadata == {}
    assert obj.embedding is None
    assert obj.object_id is not None  # Auto-generated


def test_from_dict_without_last_accessed():
    """Create memory object from dict when last_accessed is None."""
    data = {
        "name": "Eve",
        "value": "test",
        "created_at": "2024-01-01T10:00:00",
        "updated_at": "2024-01-01T11:00:00",
        "access_count": 0,
        "last_accessed": None,
    }
    
    obj = MemoryObject.from_dict(data=data)
    
    assert obj.access_count == 0
    assert obj.last_accessed is None

