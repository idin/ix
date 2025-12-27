"""
Tests for smart_truncate_text with real web page content.
"""

import os

from ixmachina.tools.string import smart_truncate_text
from ixmachina.tools.web import fetch_url, search_web
from ixmachina.tools.web.parse_html import extract_text
from ixmachina.tools.web.constants import BROWSER_USER_AGENT


def test_smart_truncate_text_with_pricing_page():
    """Test that smart truncation works with a real pricing page."""
    # First, try to find a pricing page via search (like get_model_prices does)
    search_result = search_web(
        query="openai model pricing per million tokens",
        max_results=5,
        search_engine="duckduckgo",
        domain_filter="openai.com",
    )
    
    # If search fails, we can't test with real data
    if not search_result["success"] or search_result["count"] == 0:
        # Use a fallback URL that should work
        url = "https://platform.openai.com/docs/pricing"
    else:
        # Use the first search result
        url = search_result["results"][0]["url"]
    
    headers = {"User-Agent": BROWSER_USER_AGENT}
    page = fetch_url(url=url, headers=headers)
    
    # If page fetch fails, provide useful debugging info
    if not page["success"]:
        error_msg = (
            f"Failed to fetch page: {page.get('error')}\n"
            f"URL: {url}\n"
            f"Status code: {page.get('status_code')}\n"
            f"This may indicate the page requires authentication or blocks automated requests."
        )
        # Fail the test but with helpful message
        assert False, error_msg
    
    text = extract_text(page["content"])
    assert len(text) > 0, "Page text should not be empty"
    
    # Test smart truncation with search terms
    search_terms = [
        "gpt-4",
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-3.5",
        "gpt-4-turbo",
        "ada",
        "babbage",
        "curie",
        "davinci",
        "pricing",
        "price",
        "token",
        "per million",
    ]
    
    truncated = smart_truncate_text(
        text=text,
        search_terms=search_terms,
        max_length=8000,
    )
    
    # Verify truncation worked
    assert len(truncated) <= 8000, "Truncated text should be within max_length"
    assert len(truncated) < len(text), "Truncated text should be shorter than original"
    
    # Verify relevant models are in truncated text
    models_found = []
    for model in ["gpt-4", "gpt-4o", "gpt-4o-mini", "gpt-3.5", "ada"]:
        if model.lower() in truncated.lower():
            models_found.append(model)
    
    assert len(models_found) > 0, (
        f"Should find at least one model in truncated text. Found: {models_found}\n"
        f"Truncated text length: {len(truncated)}\n"
        f"Original text length: {len(text)}\n"
        f"URL: {url}"
    )
    
    # Verify pricing-related terms are present
    pricing_terms_found = []
    for term in ["pricing", "price", "token"]:
        if term.lower() in truncated.lower():
            pricing_terms_found.append(term)
    
    assert len(pricing_terms_found) > 0, (
        f"Should find pricing terms in truncated text. Found: {pricing_terms_found}\n"
        f"URL: {url}"
    )

