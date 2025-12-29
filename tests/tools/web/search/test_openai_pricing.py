"""
Test to verify that searching for OpenAI pricing returns results.
"""

from ixmachina.tools.web import search_web


def test_openai_pricing_returns_results():
    """Test that searching for OpenAI pricing returns at least some results."""
    result = search_web(
        query="openai model pricing per million tokens",
        max_results=10,
        search_engine="duckduckgo",
        domain_filter=None,
    )
    
    assert isinstance(result, dict)
    assert result["success"] is True, f"Search failed: {result.get('error')}"
    assert result["count"] > 0, f"No results returned. This indicates the search is not working."
    assert len(result["results"]) > 0
    assert result["search_engine"] == "duckduckgo"
    assert result["error"] is None
    
    # Verify result structure
    for res in result["results"]:
        assert "title" in res
        assert "url" in res
        assert "snippet" in res
        assert isinstance(res["title"], str)
        assert isinstance(res["url"], str)
        assert len(res["title"]) > 0
        assert len(res["url"]) > 0


def test_openai_pricing_with_domain_filter():
    """Test that searching for OpenAI pricing with domain filter returns openai.com results."""
    result = search_web(
        query="openai model pricing per million tokens",
        max_results=10,
        search_engine="duckduckgo",
        domain_filter="openai.com",
    )
    
    assert isinstance(result, dict)
    assert result["success"] is True, f"Search failed: {result.get('error')}"
    assert result["search_engine"] == "duckduckgo"
    assert result["error"] is None
    
    # If we have results, verify they're from openai.com
    if result["count"] > 0:
        from urllib.parse import urlparse
        for res in result["results"]:
            url = res.get("url", "")
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            assert "openai.com" in domain, f"Result URL {url} is not from openai.com domain"
    else:
        # If no results, print info for debugging
        print(f"\nNo results with domain filter 'openai.com'.")
        print(f"This might indicate:")
        print(f"1. Search didn't return any openai.com results")
        print(f"2. Domain filter logic needs adjustment")
        
        # Check if search without filter returns openai.com results
        result_no_filter = search_web(
            query="openai model pricing per million tokens",
            max_results=20,
            search_engine="duckduckgo",
            domain_filter=None,
        )
        
        if result_no_filter["success"] and result_no_filter["count"] > 0:
            from urllib.parse import urlparse
            openai_count = 0
            for res in result_no_filter["results"]:
                url = res.get("url", "")
                parsed_url = urlparse(url)
                domain = parsed_url.netloc.lower()
                if "openai.com" in domain:
                    openai_count += 1
                    print(f"  Found openai.com result: {url[:80]}")
            
            print(f"\nUnfiltered search found {openai_count} openai.com results out of {result_no_filter['count']} total.")
            if openai_count > 0:
                print("WARNING: Unfiltered search found openai.com results but filtered search found none!")
                print("This suggests a domain filtering logic issue.")

