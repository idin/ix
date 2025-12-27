"""
Tests for MemoryObject access tracking.
"""

from ixmachina.memory import MemoryObject


def test_initial_access_count_is_zero():
    """Newly created object should have access_count of 0."""
    obj = MemoryObject(name="Alice", value={"data": 123})
    
    assert obj.access_count == 0
    assert obj.last_accessed is None


def test_record_access_increments_count():
    """Recording access should increment access_count."""
    obj = MemoryObject(name="Bob", value="test data")
    
    obj.record_access()
    assert obj.access_count == 1
    assert obj.last_accessed is not None
    
    first_access = obj.last_accessed
    
    import time
    time.sleep(0.01)
    
    obj.record_access()
    assert obj.access_count == 2
    assert obj.last_accessed > first_access


def test_record_access_multiple_times():
    """Recording access multiple times should keep incrementing."""
    obj = MemoryObject(name="Charlie", value=[1, 2, 3])
    
    for i in range(1, 6):
        obj.record_access()
        assert obj.access_count == i


def test_last_accessed_timestamp():
    """last_accessed should be set to current time when access is recorded."""
    obj = MemoryObject(name="David", value="data")
    
    assert obj.last_accessed is None
    
    obj.record_access()
    
    from datetime import datetime
    now = datetime.now()
    
    assert obj.last_accessed is not None
    # Should be very recent (within 1 second)
    assert (now - obj.last_accessed).total_seconds() < 1

