"""
Tests for MemoryObject metadata operations.
"""

from ixmachina.memory import MemoryObject


def test_update_metadata_adds_tags():
    """Update metadata should append tags to existing tags."""
    obj = MemoryObject(
        name="Alice",
        value={"data": 1},
        tags=["tag1", "tag2"],
    )
    
    obj.update_metadata(tags=["tag3", "tag4"])
    
    assert obj.tags == ["tag1", "tag2", "tag3", "tag4"]


def test_update_metadata_merges_metadata_dict():
    """Update metadata should merge with existing metadata."""
    obj = MemoryObject(
        name="Bob",
        value="test",
        metadata={"key1": "value1", "key2": "value2"},
    )
    
    obj.update_metadata(metadata={"key2": "updated", "key3": "value3"})
    
    assert obj.metadata["key1"] == "value1"  # Original preserved
    assert obj.metadata["key2"] == "updated"  # Updated
    assert obj.metadata["key3"] == "value3"  # New added


def test_update_metadata_updates_timestamp():
    """Update metadata should update the updated_at timestamp."""
    obj = MemoryObject(name="Charlie", value="data")
    
    original_updated_at = obj.updated_at
    
    import time
    time.sleep(0.01)
    
    obj.update_metadata(tags=["new_tag"])
    
    assert obj.updated_at > original_updated_at


def test_update_metadata_with_none_values():
    """Update metadata with None values should not change anything."""
    obj = MemoryObject(
        name="David",
        value="test",
        tags=["original"],
        metadata={"original": "value"},
    )
    
    obj.update_metadata(tags=None, metadata=None)
    
    assert obj.tags == ["original"]
    assert obj.metadata == {"original": "value"}


def test_get_metadata():
    """Get metadata should return all metadata fields."""
    obj = MemoryObject(
        name="Eve",
        value="test value",
        description="Test object",
        object_id="custom-id",
        tags=["tag1"],
        metadata={"custom": "data"},
    )
    
    obj.record_access()  # Set last_accessed
    
    meta = obj.get_metadata()
    
    assert meta["object_id"] == "custom-id"
    assert meta["name"] == "Eve"
    assert meta["description"] == "Test object"
    assert meta["tags"] == ["tag1"]
    assert meta["metadata"] == {"custom": "data"}
    assert "created_at" in meta
    assert "updated_at" in meta
    assert meta["access_count"] == 1
    assert meta["last_accessed"] is not None

