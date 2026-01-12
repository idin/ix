"""
Tests for persist decorator memory caching functionality.
"""

from ixutils import persist


def test_memory_cache():
    """Test in-memory caching."""
    call_count = {"count": 0}
    
    @persist(memory=True)
    def test_function(x: int) -> int:
        call_count["count"] += 1
        return x * 2
    
    # First call
    result1 = test_function(5)
    assert result1 == 10
    assert call_count["count"] == 1
    
    # Second call - should use memory cache
    result2 = test_function(5)
    assert result2 == 10
    assert call_count["count"] == 1

