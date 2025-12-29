"""
Tests for Agent using file system move operations (change_path, move_into).
"""

import pytest
from tests.conftest import DEFAULT_TEST_MODEL
import os

from ixmachina.llm import LLM
from ixmachina.agent import Agent
from ixmachina.tools.file_system import (
    change_path,
    move_into,
    path_exists,
    list_dir,
)
from ixmachina.tools.file_system import empty_dir
from ..agent_tools_file_system_constants import AGENT_FILE_SYSTEM_TEST_DIR


def test_agent_move_file_to_new_path():
    """Test agent can move a file to a new path."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    # Create test file
    os.makedirs(AGENT_FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(AGENT_FILE_SYSTEM_TEST_DIR, "old.txt")
    dest_file = os.path.join(AGENT_FILE_SYSTEM_TEST_DIR, "new.txt")
    
    with open(source_file, "w") as f:
        f.write("file content")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[change_path, path_exists])
    agent.start_conversation()

    response = agent.run(
        f"Move the file at {source_file} to {dest_file}. "
        "Then verify the source file is gone and the destination file exists."
    )

    assert isinstance(response, str)
    assert len(response) > 0
    # Verify source is gone
    assert not path_exists(source_file)
    # Verify destination exists
    assert path_exists(dest_file)
    
    # Verify content
    with open(dest_file, "r") as f:
        assert f.read() == "file content"

    # Clean up
    empty_dir(path=AGENT_FILE_SYSTEM_TEST_DIR)


def test_agent_move_directory_to_new_path():
    """Test agent can move a directory to a new path."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    # Create test directory structure
    os.makedirs(AGENT_FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_dir = os.path.join(AGENT_FILE_SYSTEM_TEST_DIR, "old_dir")
    dest_dir = os.path.join(AGENT_FILE_SYSTEM_TEST_DIR, "new_dir")
    os.makedirs(source_dir)
    
    file1 = os.path.join(source_dir, "file1.txt")
    with open(file1, "w") as f:
        f.write("content1")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[change_path, path_exists])
    agent.start_conversation()

    response = agent.run(
        f"Move the directory at {source_dir} to {dest_dir}. "
        "Then verify the source directory is gone and the destination directory exists."
    )

    assert isinstance(response, str)
    assert len(response) > 0
    # Verify source is gone
    assert not path_exists(source_dir)
    # Verify destination exists
    assert path_exists(dest_dir)
    # Verify file moved with directory
    moved_file = os.path.join(dest_dir, "file1.txt")
    assert path_exists(moved_file)

    # Clean up
    empty_dir(path=AGENT_FILE_SYSTEM_TEST_DIR)


def test_agent_move_file_into_directory():
    """Test agent can move a file into a directory."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    # Create test file and directory
    os.makedirs(AGENT_FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(AGENT_FILE_SYSTEM_TEST_DIR, "file.txt")
    dest_dir = os.path.join(AGENT_FILE_SYSTEM_TEST_DIR, "dest_dir")
    os.makedirs(dest_dir)
    
    with open(source_file, "w") as f:
        f.write("file content")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[move_into, list_dir, path_exists])
    agent.start_conversation()

    response = agent.run(
        f"Move the file at {source_file} into the directory {dest_dir}. "
        "Then list the contents of the destination directory to verify the file is there."
    )

    assert isinstance(response, str)
    assert len(response) > 0
    # Verify source is gone
    assert not path_exists(source_file)
    # Verify file exists in destination
    moved_file = os.path.join(dest_dir, "file.txt")
    assert path_exists(moved_file)

    # Clean up
    empty_dir(path=AGENT_FILE_SYSTEM_TEST_DIR)

