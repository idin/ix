"""
Tests for WebAgent.
"""

import pytest
from tests.conftest import DEFAULT_TEST_MODEL
from api_keys import get_openai_api_key, get_brave_api_key

from ixmachina.llm import LLM
from ixmachina.agent.specialists import WebAgent


def test_web_agent_initialization():
    """Test WebAgent can be initialized."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = WebAgent(llm=llm)
    
    assert len(agent.tools) > 0


def test_web_agent_has_web_tools():
    """Test WebAgent has web tools available."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = WebAgent(llm=llm)
    
    tool_names = [tool['function'>['name'> for tool in agent.tools>
    assert 'search_web' in tool_names
    assert 'fetch_url' in tool_names
    assert 'parse_html' in tool_names


def test_web_agent_search_web():
    """Test WebAgent can actually search the web."""
    api_key = get_openai_api_key()
    brave_api_key = get_brave_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = WebAgent(llm=llm)
    agent.start_conversation()
    
    response = agent.run(
        "Search the web for 'python programming' using the search_web tool. "
        "Use brave_api_key parameter. "
        "Tell me what you found - mention at least one result."
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
    # Should mention search results
    assert "python" in response.lower() or "result" in response.lower()


def test_web_agent_fetch_url():
    """Test WebAgent can actually fetch a URL."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = WebAgent(llm=llm)
    agent.start_conversation()
    
    response = agent.run(
        "Fetch the URL https://httpbin.org/get using the fetch_url tool. "
        "Tell me what the status code is and if it was successful."
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
    # Should mention success or status code
    assert "200" in response or "success" in response.lower()


def test_web_agent_check_url_status():
    """Test WebAgent can check URL status."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = WebAgent(llm=llm)
    agent.start_conversation()
    
    response = agent.run(
        "Check the status of the URL https://httpbin.org/get using the check_url_status tool. "
        "Tell me if it exists and what the status code is."
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
    # Should mention status or exists
    assert "200" in response or "exist" in response.lower() or "status" in response.lower()


def test_web_agent_parse_html():
    """Test WebAgent can parse HTML from a URL."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = WebAgent(llm=llm)
    agent.start_conversation()
    
    response = agent.run(
        "Fetch and parse the HTML from https://httpbin.org/html using fetch_url and parse_html tools. "
        "Tell me what text content you extracted from the page."
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
    # Should mention extracted content
    assert len(response) > 50  # Should have some content


def test_web_agent_extract_from_page():
    """Test WebAgent can extract information from a page."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = WebAgent(llm=llm)
    agent.start_conversation()
    
    response = agent.run(
        "Use extract_from_page to extract information from https://httpbin.org/html. "
        "Ask: 'What is the title or heading of this page?' "
        "Tell me what you extracted."
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
    # Should have extracted content
    assert len(response) > 20