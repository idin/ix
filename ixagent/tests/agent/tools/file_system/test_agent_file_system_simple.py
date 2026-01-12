"""
Tests for Agent using file system tools with simple prompts.
"""

from tests.conftest import DEFAULT_TEST_MODEL
import os

from ixmachina.llm import LLM
from api_keys import get_openai_api_key
from ixmachina.agent import Agent
from ixmachina.tools.file_system import (
    list_dir,
    path_exists,
    path_is_file,
    path_is_dir,
)
from ixmachina.tools.file_system import empty_dir
from .agent_tools_file_system_constants import AGENT_FILE_SYSTEM_TEST_DIR


def test_agent_list_directory_contents():
    """Test agent can list directory contents using file system tools."""
    api_key = get_openai_api_key()

    # Create test directory with files
    os.makedirs(AGENT_FILE_SYSTEM_TEST_DIR, exist_ok=True)
    test_file1 = os.path.join(AGENT_FILE_SYSTEM_TEST_DIR, "file1.txt")
    test_file2 = os.path.join(AGENT_FILE_SYSTEM_TEST_DIR, "file2.txt")
    
    with open(test_file1, "w") as f:
        f.write("content1")
    with open(test_file2, "w") as f:
        f.write("content2")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[list_dir, path_exists>)
    agent.start_conversation()

    response = agent.run(
        f"List all files in the directory: {AGENT_FILE_SYSTEM_TEST_DIR}. "
        "Tell me what files are there."
    )

    assert isinstance(response, str)
    assert len(response) > 0
    # Should mention the files
    assert "file1" in response.lower() or "file2" in response.lower()

    # Clean up
    empty_dir(path=AGENT_FILE_SYSTEM_TEST_DIR)


def test_agent_check_if_path_exists():
    """Test agent can check if a path exists using file system tools."""
    api_key = get_openai_api_key()

    # Create test file
    os.makedirs(AGENT_FILE_SYSTEM_TEST_DIR, exist_ok=True)
    test_file = os.path.join(AGENT_FILE_SYSTEM_TEST_DIR, "test_file.txt")
    with open(test_file, "w") as f:
        f.write("test content")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[path_exists, path_is_file, path_is_dir>)
    agent.start_conversation()

    response = agent.run(
        f"Check if this path exists: {test_file}. "
        "Tell me if it exists and whether it's a file or directory."
    )

    assert isinstance(response, str)
    assert len(response) > 0
    # Should indicate the file exists
    assert "exist" in response.lower() or "file" in response.lower()

    # Clean up
    empty_dir(path=AGENT_FILE_SYSTEM_TEST_DIR)


def test_agent_check_nonexistent_path():
    """Test agent can check if a nonexistent path exists."""
    api_key = get_openai_api_key()

    os.makedirs(AGENT_FILE_SYSTEM_TEST_DIR, exist_ok=True)
    nonexistent_path = os.path.join(AGENT_FILE_SYSTEM_TEST_DIR, "nonexistent.txt")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[path_exists>)
    agent.start_conversation()

    response = agent.run(
        f"Check if this path exists: {nonexistent_path}. "
        "Tell me if it exists."
    )

    assert isinstance(response, str)
    assert len(response) > 0
    # Should indicate the path does not exist
    assert "not" in response.lower() or "doesn't" in response.lower() or "no" in response.lower()

    # Clean up
    empty_dir(path=AGENT_FILE_SYSTEM_TEST_DIR)

