"""
Tests for Agent using file system delete operations.
"""

import pytest
from tests.conftest import DEFAULT_TEST_MODEL
import os

from ixmachina.llm import LLM
from ixmachina.agent import Agent
from ixmachina.tools.file_system import (
    delete_file,
    delete_dir,
    path_exists,
    list_dir,
)
from ixmachina.tools.file_system import empty_dir
from ..agent_tools_file_system_constants import AGENT_FILE_SYSTEM_TEST_DIR


def test_agent_delete_file():
    """Test agent can delete a file."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    # Create test file
    os.makedirs(AGENT_FILE_SYSTEM_TEST_DIR, exist_ok=True)
    test_file = os.path.join(AGENT_FILE_SYSTEM_TEST_DIR, "file_to_delete.txt")
    
    with open(test_file, "w") as f:
        f.write("content")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[delete_file, path_exists])
    agent.start_conversation()

    response = agent.run(
        f"Delete the file at {test_file}. "
        "Then verify the file no longer exists."
    )

    assert isinstance(response, str)
    assert len(response) > 0
    # Verify file is gone
    assert not path_exists(test_file)

    # Clean up
    empty_dir(path=AGENT_FILE_SYSTEM_TEST_DIR)


def test_agent_delete_directory():
    """Test agent can delete a directory."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    # Create test directory structure
    os.makedirs(AGENT_FILE_SYSTEM_TEST_DIR, exist_ok=True)
    test_dir = os.path.join(AGENT_FILE_SYSTEM_TEST_DIR, "dir_to_delete")
    os.makedirs(test_dir)
    
    file1 = os.path.join(test_dir, "file1.txt")
    with open(file1, "w") as f:
        f.write("content1")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[delete_dir, path_exists])
    agent.start_conversation()

    response = agent.run(
        f"Delete the directory at {test_dir}. "
        "Then verify the directory no longer exists."
    )

    assert isinstance(response, str)
    assert len(response) > 0
    # Verify directory is gone
    assert not path_exists(test_dir)

    # Clean up
    empty_dir(path=AGENT_FILE_SYSTEM_TEST_DIR)

