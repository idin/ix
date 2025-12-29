"""
Tests for Agent using file system undo operations.
"""

import pytest
from tests.conftest import DEFAULT_TEST_MODEL
import os

from ixmachina.llm import LLM
from ixmachina.agent import Agent
from ixmachina.tools.file_system import (
    clone_to_path,
    change_path,
    delete_file,
    delete_dir,
    path_exists,
    FileSystemMemory,
    undo,
)
from ixmachina.tools.file_system import empty_dir
from ..agent_tools_file_system_constants import AGENT_FILE_SYSTEM_TEST_DIR


def test_agent_undo_file_operation():
    """Test agent can undo a file operation using FileSystemMemory."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    # Create test file
    os.makedirs(AGENT_FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(AGENT_FILE_SYSTEM_TEST_DIR, "source.txt")
    dest_file = os.path.join(AGENT_FILE_SYSTEM_TEST_DIR, "moved.txt")
    
    with open(source_file, "w") as f:
        f.write("original content")

    file_system_memory = FileSystemMemory()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[change_path, undo])
    agent.start_conversation()
    
    # Store memory in agent's special objects so tool can access it
    agent.save_as(name="file_system_memory", obj=file_system_memory)

    response = agent.run(
        f"Move the file at {source_file} to {dest_file} using file_system_memory='[obj:file_system_memory]'. "
        "Then undo that operation using the undo function with file_system_memory='[obj:file_system_memory]'. "
        "Verify the file is back at the original location."
    )

    assert isinstance(response, str)
    assert len(response) > 0
    # Verify file is back at original location
    assert path_exists(source_file)
    assert not path_exists(dest_file)

    # Clean up
    empty_dir(path=AGENT_FILE_SYSTEM_TEST_DIR)


def test_agent_undo_delete_operation():
    """Test agent can undo a delete operation."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    # Create test file
    os.makedirs(AGENT_FILE_SYSTEM_TEST_DIR, exist_ok=True)
    test_file = os.path.join(AGENT_FILE_SYSTEM_TEST_DIR, "file_to_delete.txt")
    
    with open(test_file, "w") as f:
        f.write("content")

    file_system_memory = FileSystemMemory()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[delete_file, undo])
    agent.start_conversation()
    
    # Store memory in agent's special objects
    agent.save_as(name="file_system_memory", obj=file_system_memory)

    response = agent.run(
        f"Delete the file at {test_file} using file_system_memory='[obj:file_system_memory]'. "
        "Then undo that operation using the undo function with file_system_memory='[obj:file_system_memory]'. "
        "Verify the file is restored."
    )

    assert isinstance(response, str)
    assert len(response) > 0
    # Verify file is restored
    assert path_exists(test_file)

    # Clean up
    empty_dir(path=AGENT_FILE_SYSTEM_TEST_DIR)


def test_agent_undo_clone_operation():
    """Test agent can undo a clone operation."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    # Create test file
    os.makedirs(AGENT_FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(AGENT_FILE_SYSTEM_TEST_DIR, "source.txt")
    cloned_file = os.path.join(AGENT_FILE_SYSTEM_TEST_DIR, "cloned.txt")
    
    with open(source_file, "w") as f:
        f.write("original content")

    file_system_memory = FileSystemMemory()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[clone_to_path, undo])
    agent.start_conversation()
    
    # Store memory in agent's special objects
    agent.save_as(name="file_system_memory", obj=file_system_memory)

    response = agent.run(
        f"Clone the file at {source_file} to {cloned_file} using file_system_memory='[obj:file_system_memory]'. "
        "Then undo that operation using the undo function with file_system_memory='[obj:file_system_memory]'. "
        "Verify the cloned file is removed but the source file remains."
    )

    assert isinstance(response, str)
    assert len(response) > 0
    # Verify source still exists
    assert path_exists(source_file)
    # Verify cloned file is gone
    assert not path_exists(cloned_file)

    # Clean up
    empty_dir(path=AGENT_FILE_SYSTEM_TEST_DIR)


def test_agent_undo_delete_directory_operation():
    """Test agent can undo a directory delete operation."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    # Create test directory
    os.makedirs(AGENT_FILE_SYSTEM_TEST_DIR, exist_ok=True)
    test_dir = os.path.join(AGENT_FILE_SYSTEM_TEST_DIR, "dir_to_delete")
    os.makedirs(test_dir)
    
    file1 = os.path.join(test_dir, "file1.txt")
    with open(file1, "w") as f:
        f.write("content1")

    file_system_memory = FileSystemMemory()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[delete_dir, undo])
    agent.start_conversation()
    
    # Store memory in agent's special objects
    agent.save_as(name="file_system_memory", obj=file_system_memory)

    response = agent.run(
        f"Delete the directory at {test_dir} using file_system_memory='[obj:file_system_memory]'. "
        "Then undo that operation using the undo function with file_system_memory='[obj:file_system_memory]'. "
        "Verify the directory is restored."
    )

    assert isinstance(response, str)
    assert len(response) > 0
    # Verify directory is restored
    assert path_exists(test_dir)
    assert path_exists(file1)

    # Clean up
    empty_dir(path=AGENT_FILE_SYSTEM_TEST_DIR)

