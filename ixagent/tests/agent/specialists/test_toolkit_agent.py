"""
Tests for ToolkitAgent.
"""

import pytest
import os
from tests.conftest import DEFAULT_TEST_MODEL, TEST_DATA_DIR
from api_keys import get_openai_api_key

from ixmachina.llm import LLM
from ixmachina.agent.specialists import ToolkitAgent
from ixmachina.tools.file_system import empty_dir, path_exists


def test_toolkit_agent_initialization():
    """Test ToolkitAgent can be initialized."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = ToolkitAgent(llm=llm)
    
    # Agent starts with built-in tools (memorize, remember, list_objects, etc.)
    # but no file system or web tools yet
    assert len(agent.tools) > 0  # Has built-in tools
    tool_names = [tool['function'>['name'> for tool in agent.tools>
    # Should not have file system or web tools yet
    assert 'list_dir' not in tool_names
    assert 'search_web' not in tool_names


def test_toolkit_agent_add_file_system_tools():
    """Test ToolkitAgent can add file system tools."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = ToolkitAgent(llm=llm)
    
    agent.add_file_system_tools()
    
    assert hasattr(agent, '_file_system_memory')
    tool_names = [tool['function'>['name'> for tool in agent.tools>
    assert 'list_dir' in tool_names
    assert 'delete' in tool_names


def test_toolkit_agent_add_web_tools():
    """Test ToolkitAgent can add web tools."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = ToolkitAgent(llm=llm)
    
    agent.add_web_tools()
    
    tool_names = [tool['function'>['name'> for tool in agent.tools>
    assert 'search_web' in tool_names
    assert 'fetch_url' in tool_names


def test_toolkit_agent_add_multiple_tool_sets():
    """Test ToolkitAgent can add multiple tool sets."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = ToolkitAgent(llm=llm)
    
    agent.add_file_system_tools()
    agent.add_web_tools()
    
    assert hasattr(agent, '_file_system_memory')
    tool_names = [tool['function'>['name'> for tool in agent.tools>
    assert 'list_dir' in tool_names
    assert 'search_web' in tool_names


def test_toolkit_agent_add_text_tools_raises_not_implemented():
    """Test ToolkitAgent.add_text_tools raises NotImplementedError."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = ToolkitAgent(llm=llm)
    
    with pytest.raises(NotImplementedError):
        agent.add_text_tools()


def test_toolkit_agent_file_system_tools_work():
    """Test ToolkitAgent can actually use file system tools."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = ToolkitAgent(llm=llm)
    agent.add_file_system_tools()
    agent.start_conversation()
    
    test_dir = os.path.join(TEST_DATA_DIR, "toolkit_agent", "test_dir")
    test_file = os.path.join(test_dir, "test.txt")
    
    # Clean up first
    if path_exists(test_dir):
        empty_dir(path=test_dir)
    
    os.makedirs(test_dir, exist_ok=True)
    
    response = agent.run(
        f"List the contents of the directory {test_dir} using list_dir. "
        "Tell me what you found."
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
    
    # Clean up
    if path_exists(test_dir):
        empty_dir(path=test_dir)


def test_toolkit_agent_file_system_undo_works():
    """Test ToolkitAgent can use file system undo functionality."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = ToolkitAgent(llm=llm)
    agent.add_file_system_tools()
    agent.start_conversation()
    
    test_dir = os.path.join(TEST_DATA_DIR, "toolkit_agent", "undo_test_dir")
    source_file = os.path.join(test_dir, "source.txt")
    dest_file = os.path.join(test_dir, "moved.txt")
    
    # Clean up first
    if path_exists(test_dir):
        empty_dir(path=test_dir)
    
    os.makedirs(test_dir, exist_ok=True)
    with open(source_file, "w") as f:
        f.write("original content")
    
    response = agent.run(
        f"Move the file at {source_file} to {dest_file}. "
        "Then undo that operation. "
        "Verify the file is back at the original location."
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
    # Verify file is back at original location
    assert path_exists(source_file)
    assert not path_exists(dest_file)
    
    # Clean up
    if path_exists(test_dir):
        empty_dir(path=test_dir)


def test_toolkit_agent_web_tools_work():
    """Test ToolkitAgent can actually use web tools."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = ToolkitAgent(llm=llm)
    agent.add_web_tools()
    agent.start_conversation()
    
    response = agent.run(
        "Fetch the URL https://httpbin.org/get using the fetch_url tool. "
        "Tell me what the status code is."
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
    # Should mention status code
    assert "200" in response or "success" in response.lower()


def test_toolkit_agent_combined_tools_work():
    """Test ToolkitAgent can use both file system and web tools together."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = ToolkitAgent(llm=llm)
    agent.add_file_system_tools()
    agent.add_web_tools()
    agent.start_conversation()
    
    test_dir = os.path.join(TEST_DATA_DIR, "toolkit_agent", "combined_test_dir")
    
    # Clean up first
    if path_exists(test_dir):
        empty_dir(path=test_dir)
    
    os.makedirs(test_dir, exist_ok=True)
    
    response = agent.run(
        f"First, fetch the URL https://httpbin.org/get and tell me the status code. "
        f"Then, list the contents of the directory {test_dir}."
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
    # Should mention both operations
    assert "200" in response or "status" in response.lower()
    
    # Clean up
    if path_exists(test_dir):
        empty_dir(path=test_dir)


def test_toolkit_agent_undo_delete_operation():
    """Test ToolkitAgent can undo a delete operation."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = ToolkitAgent(llm=llm)
    agent.add_file_system_tools()
    agent.start_conversation()
    
    test_dir = os.path.join(TEST_DATA_DIR, "toolkit_agent", "undo_delete_test_dir")
    test_file = os.path.join(test_dir, "file_to_delete.txt")
    
    # Clean up first
    if path_exists(test_dir):
        empty_dir(path=test_dir)
    
    os.makedirs(test_dir, exist_ok=True)
    with open(test_file, "w") as f:
        f.write("content")
    
    response = agent.run(
        f"Delete the file at {test_file}. "
        "Then undo that operation. "
        "Verify the file is restored."
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
    # Verify file is restored
    assert path_exists(test_file)
    
    # Clean up
    if path_exists(test_dir):
        empty_dir(path=test_dir)