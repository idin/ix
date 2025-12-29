"""
Tests for Agent using file system copy operations (clone, copy_into).
"""

import pytest
from tests.conftest import DEFAULT_TEST_MODEL
import os

from ixmachina.llm import LLM
from ixmachina.agent import Agent
from ixmachina.tools.file_system import (
    clone_to_path,
    copy_into,
    list_dir,
    path_exists,
    compare_files,
    compare_dirs,
)
from ixmachina.tools.file_system import empty_dir
from ..agent_tools_file_system_constants import AGENT_FILE_SYSTEM_TEST_DIR


def test_agent_clone_file():
    """Test agent can clone a file to a new path."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    # Create test file
    os.makedirs(AGENT_FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_file = os.path.join(AGENT_FILE_SYSTEM_TEST_DIR, "source.txt")
    dest_file = os.path.join(AGENT_FILE_SYSTEM_TEST_DIR, "cloned.txt")
    
    with open(source_file, "w") as f:
        f.write("original content")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[clone_to_path, path_exists, compare_files])
    agent.start_conversation()

    response = agent.run(
        f"Clone the file at {source_file} to {dest_file}. "
        "Then verify both files exist and have the same content."
    )

    assert isinstance(response, str)
    assert len(response) > 0
    # Verify both files exist
    assert path_exists(source_file)
    assert path_exists(dest_file)
    
    # Verify files are identical
    compare_result = compare_files(file_path_1=source_file, file_path_2=dest_file)
    assert compare_result["success"] is True
    assert compare_result["are_equal"] is True

    # Clean up
    empty_dir(path=AGENT_FILE_SYSTEM_TEST_DIR)


def test_agent_clone_directory():
    """Test agent can clone a directory to a new path."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")

    # Create test directory structure
    os.makedirs(AGENT_FILE_SYSTEM_TEST_DIR, exist_ok=True)
    source_dir = os.path.join(AGENT_FILE_SYSTEM_TEST_DIR, "source_dir")
    dest_dir = os.path.join(AGENT_FILE_SYSTEM_TEST_DIR, "cloned_dir")
    os.makedirs(source_dir)
    
    file1 = os.path.join(source_dir, "file1.txt")
    file2 = os.path.join(source_dir, "file2.txt")
    with open(file1, "w") as f:
        f.write("content1")
    with open(file2, "w") as f:
        f.write("content2")

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[clone_to_path, path_exists, compare_dirs])
    agent.start_conversation()

    response = agent.run(
        f"Clone the directory at {source_dir} to {dest_dir}. "
        "Then verify both directories exist and have the same content."
    )

    assert isinstance(response, str)
    assert len(response) > 0
    # Verify both directories exist
    assert path_exists(source_dir)
    assert path_exists(dest_dir)
    
    # Verify directories are identical
    compare_result = compare_dirs(dir_path_1=source_dir, dir_path_2=dest_dir)
    assert compare_result["success"] is True
    assert compare_result["are_equal"] is True

    # Clean up
    empty_dir(path=AGENT_FILE_SYSTEM_TEST_DIR)


def test_agent_copy_file_into_directory():
    """Test agent can copy a file into a directory."""
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
    agent = Agent(llm=llm, tools=[copy_into, list_dir, path_exists])
    agent.start_conversation()

    response = agent.run(
        f"Copy the file at {source_file} into the directory {dest_dir}. "
        "Then list the contents of the destination directory to verify the file is there."
    )

    assert isinstance(response, str)
    assert len(response) > 0
    # Verify source still exists
    assert path_exists(source_file)
    # Verify copy exists in destination
    copied_file = os.path.join(dest_dir, "file.txt")
    assert path_exists(copied_file)

    # Clean up
    empty_dir(path=AGENT_FILE_SYSTEM_TEST_DIR)

