"""
Tests for creating MemoryObject instances.
"""

from ixmachina.memory import MemoryObject


def test_create_memory_object_with_minimal_arguments():
    """Create a memory object with only required arguments."""
    obj = MemoryObject(
        name="Alice",
        value={"age": 30, "role": "Engineer"},
    )
    
    assert obj.name == "Alice"
    assert obj.value == {"age": 30, "role": "Engineer"}
    assert obj.description == ""
    assert obj.object_id is not None  # Auto-generated
    assert obj.tags == []
    assert obj.metadata == {}
    assert obj.embedding is None
    assert obj.created_at is not None
    assert obj.updated_at is not None
    assert obj.access_count == 0
    assert obj.last_accessed is None


def test_create_memory_object_with_description():
    """Create a memory object with a description."""
    obj = MemoryObject(
        name="Bob",
        value={"age": 45},
        description="CEO of Acme Corporation",
    )
    
    assert obj.name == "Bob"
    assert obj.description == "CEO of Acme Corporation"


def test_create_memory_object_with_custom_object_id():
    """Create a memory object with a custom object_id."""
    custom_id = "my-custom-object-id"
    
    obj = MemoryObject(
        name="Charlie",
        value="Some data",
        object_id=custom_id,
    )
    
    assert obj.object_id == custom_id


def test_create_memory_object_with_tags():
    """Create a memory object with tags."""
    obj = MemoryObject(
        name="David",
        value={"department": "Engineering"},
        tags=["employee", "senior", "backend"],
    )
    
    assert obj.tags == ["employee", "senior", "backend"]


def test_create_memory_object_with_metadata():
    """Create a memory object with metadata."""
    metadata = {"source": "hr_database", "verified": True}
    
    obj = MemoryObject(
        name="Eve",
        value={"salary": 120000},
        metadata=metadata,
    )
    
    assert obj.metadata == metadata


def test_create_memory_object_with_embedding():
    """Create a memory object with an embedding vector."""
    embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
    
    obj = MemoryObject(
        name="Frank",
        value="Some text data",
        embedding=embedding,
    )
    
    assert obj.embedding == embedding


def test_create_memory_object_with_all_arguments():
    """Create a memory object with all possible arguments."""
    obj = MemoryObject(
        name="Grace",
        value={"position": "Manager"},
        description="Manager of the sales team",
        object_id="grace-custom-id",
        tags=["manager", "sales"],
        metadata={"team_size": 10},
        embedding=[0.6, 0.7, 0.8],
    )
    
    assert obj.name == "Grace"
    assert obj.value == {"position": "Manager"}
    assert obj.description == "Manager of the sales team"
    assert obj.object_id == "grace-custom-id"
    assert obj.tags == ["manager", "sales"]
    assert obj.metadata == {"team_size": 10}
    assert obj.embedding == [0.6, 0.7, 0.8]


def test_different_value_types():
    """Test that MemoryObject can store different types of values."""
    # String value
    obj1 = MemoryObject(name="test1", value="string value")
    assert obj1.value == "string value"
    
    # Integer value
    obj2 = MemoryObject(name="test2", value=42)
    assert obj2.value == 42
    
    # List value
    obj3 = MemoryObject(name="test3", value=[1, 2, 3])
    assert obj3.value == [1, 2, 3]
    
    # Dict value
    obj4 = MemoryObject(name="test4", value={"key": "value"})
    assert obj4.value == {"key": "value"}
    
    # None value
    obj5 = MemoryObject(name="test5", value=None)
    assert obj5.value is None

