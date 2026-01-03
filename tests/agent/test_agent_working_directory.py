"""
Tests for agent working directory functionality.
"""

import os

from tests.conftest import DEFAULT_TEST_MODEL, TEST_DATA_DIR
from tests.api_keys import get_openai_api_key

from ixmachina.llm import LLM
from ixmachina.agent import Agent
from ixmachina.agent.specialists import DatabaseAgent, ToolkitAgent
from ixmachina.utils.persist import get_cache_path
from ixmachina.tools.file_system.delete import delete
from ixmachina.tools.file_system.path_utils import path_exists


def test_agent_creates_working_directory():
    """Test that agent creates working directory lazily when first needed."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    
    # Use real directory in test data folder
    working_dir = os.path.join(TEST_DATA_DIR, "agent_workspace_test")
    
    # Clean up if exists from previous test
    if path_exists(working_dir):
        delete(paths=working_dir)
    
    # Directory shouldn't exist yet
    assert not os.path.exists(working_dir)
    
    # Create agent with working directory (not created yet)
    agent = Agent(llm=llm, working_directory=working_dir)
    
    # Directory should not exist yet (lazy creation)
    assert not os.path.exists(working_dir)
    assert agent.working_directory == working_dir
    
    # Trigger creation by ensuring it exists
    agent._ensure_working_directory()
    
    # Directory should now exist
    assert os.path.exists(working_dir)
    assert os.path.isdir(working_dir)


def test_agent_creates_cache_directory():
    """Test that agent sets cache path and creates directory when cache is used."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL, use_cache=True)
    
    # Use real directory in test data folder
    working_dir = os.path.join(TEST_DATA_DIR, "agent_cache_test")
    
    # Clean up if exists from previous test
    if path_exists(working_dir):
        delete(paths=working_dir)
    
    # Create agent with working directory
    agent = Agent(llm=llm, working_directory=working_dir)
    
    # Global cache path should be set to the cache directory
    cache_dir = os.path.join(working_dir, "cache")
    assert get_cache_path() == cache_dir
    
    # Cache directory should be created lazily when first cache is written
    # Trigger a cache write by making a query
    agent.run("Say hello")
    
    # Now cache directory should exist
    assert os.path.exists(cache_dir)
    assert os.path.isdir(cache_dir)


def test_agent_working_directory_without_path():
    """Test that agent works without working directory."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    
    # Create agent without working directory
    agent = Agent(llm=llm)
    
    # working_directory should be None
    assert agent.working_directory is None


def test_database_agent_uses_working_directory():
    """Test that DatabaseAgent uses working directory for database file."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    
    # Use real directory in test data folder
    working_dir = os.path.join(TEST_DATA_DIR, "database_agent_test")
    
    # Clean up if exists from previous test
    if path_exists(working_dir):
        delete(paths=working_dir)
    
    # Create DatabaseAgent with working directory
    agent = DatabaseAgent(llm=llm, working_directory=working_dir)
    
    # Database file should be created in working directory
    database_file = os.path.join(working_dir, "database.db")
    assert os.path.exists(database_file)
    assert os.path.isfile(database_file)
    
    # Verify database connection works
    result = agent.run("List all tables in the database.")
    assert isinstance(result, str)


def test_toolkit_agent_database_uses_working_directory():
    """Test that ToolkitAgent uses working directory when adding database tools."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    
    # Use real directory in test data folder
    working_dir = os.path.join(TEST_DATA_DIR, "toolkit_agent_test")
    
    # Clean up if exists from previous test
    if path_exists(working_dir):
        delete(paths=working_dir)
    
    # Create ToolkitAgent with working directory
    agent = ToolkitAgent(llm=llm, working_directory=working_dir)
    
    # Add database tools (should use working_directory/database.db)
    agent.add_database_tools()
    
    # Database file should be created in working directory
    database_file = os.path.join(working_dir, "database.db")
    assert os.path.exists(database_file)
    assert os.path.isfile(database_file)
    
    # Verify database connection works
    result = agent.run("List all tables in the database.")
    assert isinstance(result, str)


def test_agent_working_directory_structure():
    """Test that agent creates proper directory structure with lazy creation."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL, use_cache=True)
    
    # Use real directory in test data folder
    working_dir = os.path.join(TEST_DATA_DIR, "agent_structure_test")
    
    # Clean up if exists from previous test
    if path_exists(working_dir):
        delete(paths=working_dir)
    
    # Create agent with working directory (not created yet - lazy)
    agent = Agent(llm=llm, working_directory=working_dir)
    
    # Working directory should not exist yet (lazy creation)
    assert not os.path.exists(working_dir)
    
    # Cache directory path should be set
    cache_dir = os.path.join(working_dir, "cache")
    assert get_cache_path() == cache_dir
    
    # Trigger working directory creation by adding database tools
    from ixmachina.agent.specialists.database_agent import add_database_tools
    add_database_tools(agent=agent)
    
    # Now working directory should exist (created by database connection)
    assert os.path.exists(working_dir)
    assert os.path.isdir(working_dir)
    
    # Database file should exist
    database_file = os.path.join(working_dir, "database.db")
    assert os.path.exists(database_file)
    assert os.path.isfile(database_file)
    
    # Trigger cache creation by making a query
    agent.run("Say hello")
    assert os.path.exists(cache_dir)
    assert os.path.isdir(cache_dir)
    
    # Final structure should be:
    # working_dir/
    #   cache/
    #   database.db
    entries = os.listdir(working_dir)
    assert "cache" in entries
    assert "database.db" in entries

