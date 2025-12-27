"""
Tests for MemoryObject embedding operations.
"""

from ixmachina.memory import MemoryObject


def test_get_embedding_initially_none():
    """Embedding should be None if not provided."""
    obj = MemoryObject(name="Alice", value="data")
    
    assert obj.get_embedding() is None


def test_get_embedding_returns_provided_embedding():
    """Get embedding should return the embedding provided at creation."""
    embedding = [0.1, 0.2, 0.3]
    obj = MemoryObject(name="Bob", value="data", embedding=embedding)
    
    assert obj.get_embedding() == embedding


def test_set_embedding():
    """Set embedding should store the embedding."""
    obj = MemoryObject(name="Charlie", value="data")
    
    embedding = [0.4, 0.5, 0.6, 0.7]
    obj.set_embedding(embedding=embedding)
    
    assert obj.get_embedding() == embedding
    assert obj.embedding == embedding


def test_set_embedding_updates_timestamp():
    """Setting embedding should update the updated_at timestamp."""
    obj = MemoryObject(name="David", value="test")
    
    original_updated_at = obj.updated_at
    
    import time
    time.sleep(0.01)
    
    obj.set_embedding(embedding=[0.8, 0.9])
    
    assert obj.updated_at > original_updated_at


def test_set_embedding_replaces_old_embedding():
    """Setting a new embedding should replace the old one."""
    obj = MemoryObject(
        name="Eve",
        value="data",
        embedding=[1.0, 2.0],
    )
    
    assert obj.get_embedding() == [1.0, 2.0]
    
    obj.set_embedding(embedding=[3.0, 4.0])
    
    assert obj.get_embedding() == [3.0, 4.0]

