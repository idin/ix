"""
Tests for Fact metadata operations.
"""

from datetime import datetime
from ixmachina.memory import Fact


def test_update_metadata():
    """Update fact metadata."""
    fact = Fact(
        text="Alice works at Acme",
        relationship_type="employment",
        objects=[
            {"object_id": "alice-id", "role": "employee"},
            {"object_id": "acme-id", "role": "employer"},
        ],
        metadata={"confidence": 0.9},
    )
    
    original_updated_at = fact.updated_at
    
    # Wait a tiny bit to ensure timestamp changes
    import time
    time.sleep(0.01)
    
    fact.update_metadata(metadata={"source": "hr_database"})
    
    assert fact.metadata["confidence"] == 0.9  # Original metadata preserved
    assert fact.metadata["source"] == "hr_database"  # New metadata added
    assert fact.updated_at > original_updated_at  # Timestamp updated


def test_set_and_get_embedding():
    """Set and get embedding vector."""
    fact = Fact(
        text="Bob is father of Charlie",
        relationship_type="father_of",
        objects=[
            {"object_id": "bob-id", "role": "father"},
            {"object_id": "charlie-id", "role": "child"},
        ],
    )
    
    assert fact.get_embedding() is None
    
    embedding = [0.1, 0.2, 0.3]
    fact.set_embedding(embedding=embedding)
    
    assert fact.get_embedding() == embedding


def test_set_embedding_updates_timestamp():
    """Setting embedding should update the timestamp."""
    fact = Fact(
        text="David works at Initech",
        relationship_type="employment",
        objects=[
            {"object_id": "david-id", "role": "employee"},
            {"object_id": "initech-id", "role": "employer"},
        ],
    )
    
    original_updated_at = fact.updated_at
    
    import time
    time.sleep(0.01)
    
    fact.set_embedding(embedding=[0.5, 0.6])
    
    assert fact.updated_at > original_updated_at

