"""
Tests for persist decorator behavior.
"""

from ixutils import persist


def test_persist_preserves_docstring():
    """Test that persist decorator preserves function docstring."""
    @persist()
    def documented_function(x: int) -> int:
        """This is a test function with a docstring.
        
        Args:
            x: An integer input.
        
        Returns:
            The input multiplied by 2.
        """
        return x * 2
    
    # Check that docstring is preserved
    assert documented_function.__doc__ is not None
    assert "This is a test function with a docstring" in documented_function.__doc__
    assert "Args:" in documented_function.__doc__
    assert "Returns:" in documented_function.__doc__
    
    # Also test with memory cache
    @persist(memory=True)
    def memory_documented_function(x: int) -> int:
        """Memory cached function with docstring."""
        return x * 3
    
    assert memory_documented_function.__doc__ is not None
    assert "Memory cached function with docstring" in memory_documented_function.__doc__

