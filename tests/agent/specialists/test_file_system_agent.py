"""
Tests for FileSystemAgent.
"""

import pytest
from tests.conftest import DEFAULT_TEST_MODEL
from tests.api_keys import get_openai_api_key
import os

from ixmachina.llm import LLM
from ixmachina.agent.specialists import FileSystemAgent
from ixmachina.tools.file_system import path_exists, empty_dir


from tests.conftest import TEST_DATA_DIR

# Test directory for specialist agent tests - located in centralized test data directory
SPECIALIST_TEST_DIR = os.path.join(TEST_DATA_DIR, "specialist_agents")


def test_file_system_agent_initialization():
    """Test FileSystemAgent can be initialized."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = FileSystemAgent(llm=llm)
    
    assert hasattr(agent, '_file_system_memory')
    assert 'file_system_memory' in agent._system_objects
    assert len(agent.tools) > 0


def test_file_system_agent_has_file_system_tools():
    """Test FileSystemAgent has file system tools available."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = FileSystemAgent(llm=llm)
    
    tool_names = [tool['function']['name'] for tool in agent.tools]
    assert 'list_dir' in tool_names
    assert 'delete' in tool_names
    assert 'move_into' in tool_names


def test_file_system_agent_create_directory_and_undo():
    """Test FileSystemAgent can create a directory and then undo it."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = FileSystemAgent(llm=llm)
    agent.start_conversation()
    
    os.makedirs(SPECIALIST_TEST_DIR, exist_ok=True)
    test_dir = os.path.join(SPECIALIST_TEST_DIR, "test_dir")
    
    # Create directory using Python, then delete it with agent and undo
    os.makedirs(test_dir, exist_ok=True)
    
    response = agent.run(
        f"Delete the directory at {test_dir}. "
        "Then undo that operation. "
        "Verify the directory is restored."
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
    # Verify directory is restored
    assert path_exists(test_dir)
    
    # Clean up
    empty_dir(path=SPECIALIST_TEST_DIR)


def test_file_system_agent_create_file_and_undo():
    """Test FileSystemAgent can create a file and then undo it."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = FileSystemAgent(llm=llm)
    agent.start_conversation()
    
    os.makedirs(SPECIALIST_TEST_DIR, exist_ok=True)
    source_file = os.path.join(SPECIALIST_TEST_DIR, "source.txt")
    cloned_file = os.path.join(SPECIALIST_TEST_DIR, "cloned.txt")
    
    # Create source file
    with open(source_file, "w") as f:
        f.write("original content")
    
    response = agent.run(
        f"Clone the file at {source_file} to {cloned_file}. "
        "Then undo that operation. "
        "Verify the cloned file is removed but the source file remains."
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
    # Verify source still exists
    assert path_exists(source_file)
    # Verify cloned file is gone
    assert not path_exists(cloned_file)
    
    # Clean up
    empty_dir(path=SPECIALIST_TEST_DIR)


def test_file_system_agent_create_directory_with_file_and_undo():
    """Test FileSystemAgent can create a directory and a file inside it and then undo both."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = FileSystemAgent(llm=llm)
    agent.start_conversation()
    
    os.makedirs(SPECIALIST_TEST_DIR, exist_ok=True)
    test_dir = os.path.join(SPECIALIST_TEST_DIR, "test_dir")
    test_file = os.path.join(test_dir, "file.txt")
    
    # Create directory and file
    os.makedirs(test_dir, exist_ok=True)
    with open(test_file, "w") as f:
        f.write("content")
    
    response = agent.run(
        f"Delete the directory at {test_dir} (which contains a file). "
        "Then undo that operation. "
        "Verify both the directory and the file inside it are restored."
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
    # Verify directory and file are restored
    assert path_exists(test_dir)
    assert path_exists(test_file)
    
    # Clean up
    empty_dir(path=SPECIALIST_TEST_DIR)


def test_file_system_agent_move_directory_with_files():
    """Test FileSystemAgent can move a directory with files inside it."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = FileSystemAgent(llm=llm)
    agent.start_conversation()
    
    os.makedirs(SPECIALIST_TEST_DIR, exist_ok=True)
    source_dir = os.path.join(SPECIALIST_TEST_DIR, "source_dir")
    dest_dir = os.path.join(SPECIALIST_TEST_DIR, "dest_dir")
    
    # Create source directory with files
    os.makedirs(source_dir, exist_ok=True)
    file1 = os.path.join(source_dir, "file1.txt")
    file2 = os.path.join(source_dir, "file2.txt")
    with open(file1, "w") as f:
        f.write("content1")
    with open(file2, "w") as f:
        f.write("content2")
    
    response = agent.run(
        f"Move the directory at {source_dir} to {dest_dir}. "
        "Verify the directory and all files inside it are moved."
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
    # Verify directory is moved
    assert not path_exists(source_dir)
    assert path_exists(dest_dir)
    # Verify files are moved
    moved_file1 = os.path.join(dest_dir, "file1.txt")
    moved_file2 = os.path.join(dest_dir, "file2.txt")
    assert path_exists(moved_file1)
    assert path_exists(moved_file2)
    
    # Clean up
    empty_dir(path=SPECIALIST_TEST_DIR)


def test_file_system_agent_move_directory_and_undo():
    """Test FileSystemAgent can move a directory and a file inside it and then undo it."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = FileSystemAgent(llm=llm)
    agent.start_conversation()
    
    os.makedirs(SPECIALIST_TEST_DIR, exist_ok=True)
    source_dir = os.path.join(SPECIALIST_TEST_DIR, "source_dir")
    dest_dir = os.path.join(SPECIALIST_TEST_DIR, "dest_dir")
    
    # Create source directory with file
    os.makedirs(source_dir, exist_ok=True)
    file1 = os.path.join(source_dir, "file1.txt")
    with open(file1, "w") as f:
        f.write("content1")
    
    response = agent.run(
        f"Move the directory at {source_dir} to {dest_dir}. "
        "Then undo that operation. "
        "Verify the directory and file are back at the original location."
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
    # Verify directory is back at original location
    assert path_exists(source_dir)
    assert path_exists(file1)
    # Verify it's not at destination
    assert not path_exists(dest_dir)
    
    # Clean up
    empty_dir(path=SPECIALIST_TEST_DIR)