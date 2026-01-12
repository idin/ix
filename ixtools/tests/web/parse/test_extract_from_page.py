"""
Tests for extract_from_page tool.
"""

from tests.conftest import DEFAULT_TEST_MODEL

from ixcore import LLM
from ixtools.web import extract_from_page
from tests.api_keys import get_openai_api_key


def test_extract_from_page_success():
    """Test extract_from_page successfully extracts information from a web page."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    
    # Use a simple, stable page for testing (httpbin.org)
    result = extract_from_page(
        url="https://httpbin.org/html",
        query="What is the title or heading of this page?",
        llm=llm,
    )
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert result["url"] == "https://httpbin.org/html"
    assert result["query"] == "What is the title or heading of this page?"
    assert "extracted" in result
    assert isinstance(result["extracted"], str)
    assert len(result["extracted"]) > 0
    assert result["error"] is None


def test_extract_from_page_fetch_error():
    """Test extract_from_page handles fetch errors."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    
    # Use an invalid URL
    result = extract_from_page(
        url="https://this-domain-does-not-exist-12345.com",
        query="Find something",
        llm=llm,
    )
    
    assert isinstance(result, dict)
    assert result["success"] is False
    assert result["extracted"] is None
    assert result["error"] is not None
    assert "failed to fetch" in result["error"].lower()


def test_extract_from_page_extracts_specific_info():
    """Test extract_from_page can extract specific information like prices."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    
    # Create a simple HTML page with price information
    # We'll use httpbin.org/html which returns a simple HTML page
    result = extract_from_page(
        url="https://httpbin.org/html",
        query="What text or content is on this page?",
        llm=llm,
    )
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert "extracted" in result
    assert isinstance(result["extracted"], str)
    # The extracted content should not be empty
    assert len(result["extracted"].strip()) > 0


def test_extract_from_page_with_special_characters_in_query():
    """Test extract_from_page handles special characters in query."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    
    result = extract_from_page(
        url="https://httpbin.org/html",
        query="Find the price in $ or €",
        llm=llm,
    )
    
    assert isinstance(result, dict)
    assert result["query"] == "Find the price in $ or €"
    assert "success" in result

