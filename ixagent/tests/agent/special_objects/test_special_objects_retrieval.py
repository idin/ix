"""
Tests for Agent special object retrieval functionality.
"""

from tests.conftest import DEFAULT_TEST_MODEL

from ixmachina.llm import LLM
from ixmachina.agent import Agent, SpecialObjectKeyError
from api_keys import get_openai_api_key


def test_agent_special_object_retrieval_direct():
    """Test that special objects are correctly retrieved from argument values."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)
    
    # Test retrieving 'self' special object
    result = agent._add_system_objects_to_tool_arguments({"agent": "<sys:self>"})
    assert "agent" in result
    assert result["agent"] == agent
    
    # Test retrieving 'llm' special object
    result = agent._add_system_objects_to_tool_arguments({"llm": "<sys:llm>"})
    assert "llm" in result
    assert result["llm"] == llm


def test_agent_special_object_retrieval_with_regular_args():
    """Test that special objects work alongside regular arguments."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)
    
    # Test mix of special objects and regular arguments
    result = agent._add_system_objects_to_tool_arguments({
        "regular_arg": "normal_value",
        "agent": "<sys:self>",
        "another_regular": 42
    })
    
    assert result["regular_arg"] == "normal_value"
    assert result["agent"] == agent
    assert result["another_regular"] == 42


def test_agent_special_object_case_insensitive():
    """Test that special object matching is case insensitive."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)
    
    # Test with uppercase prefix
    result = agent._add_system_objects_to_tool_arguments({"agent": "<SYS:SELF>"})
    assert result["agent"] == agent
    
    # Test with mixed case
    result = agent._add_system_objects_to_tool_arguments({"agent": "<Sys:Self>"})
    assert result["agent"] == agent
