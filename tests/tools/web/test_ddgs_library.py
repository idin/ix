"""
Tests for the ddgs library API to verify it works as expected.
This tests the library directly, not our wrapper.
"""

import pytest


def test_ddgs_import():
    """Test that ddgs can be imported."""
    try:
        from ddgs import DDGS
        assert DDGS is not None
    except ImportError:
        pytest.fail("ddgs package is not installed. Install it with: pip install ddgs")


def test_ddgs_text_method():
    """Test that DDGS.text() method works with correct parameters."""
    from ddgs import DDGS
    
    with DDGS() as ddgs:
        # Test with query parameter (new API)
        results = ddgs.text(query="python programming", max_results=3)
        
        # Verify return type
        assert isinstance(results, list), f"Expected list, got {type(results)}"
        
        # Verify results structure
        if len(results) > 0:
            first_result = results[0]
            assert isinstance(first_result, dict), f"Expected dict, got {type(first_result)}"
            assert "title" in first_result, "Result should have 'title' key"
            assert "href" in first_result, "Result should have 'href' key"
            assert "body" in first_result, "Result should have 'body' key"
            
            # Verify types
            assert isinstance(first_result["title"], str)
            assert isinstance(first_result["href"], str)
            assert isinstance(first_result["body"], str)


def test_ddgs_text_max_results():
    """Test that max_results parameter limits the number of results."""
    from ddgs import DDGS
    
    with DDGS() as ddgs:
        results = ddgs.text(query="test", max_results=5)
        assert isinstance(results, list)
        assert len(results) <= 5, f"Expected at most 5 results, got {len(results)}"


def test_ddgs_text_different_queries():
    """Test that different queries return different results."""
    from ddgs import DDGS
    
    with DDGS() as ddgs:
        results1 = ddgs.text(query="python", max_results=3)
        results2 = ddgs.text(query="javascript", max_results=3)
        
        assert isinstance(results1, list)
        assert isinstance(results2, list)
        
        # Results should be different (at least URLs should differ)
        if len(results1) > 0 and len(results2) > 0:
            urls1 = {r.get("href", "") for r in results1}
            urls2 = {r.get("href", "") for r in results2}
            # They might have some overlap, but shouldn't be identical
            assert urls1 != urls2 or len(urls1) == 0, "Different queries should return different results"

