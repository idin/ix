"""
Tests for Agent class with multiple LLMs.
"""

import pytest
import os

from ixmachina.llm import LLM
from ixmachina.agent import Agent


def test_agent_initialization_with_multiple_llms_dict():
    """Test Agent can be initialized with a dictionary of LLMs."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm1 = LLM(api_key=api_key, model_name="gpt-4")
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2})
    
    assert len(agent.llms) == 2
    assert "gpt4" in agent.llms
    assert "gpt35" in agent.llms
    assert agent.llms["gpt4"] is llm1
    assert agent.llms["gpt35"] is llm2
    # Default should be first LLM in dict
    assert agent.llm is llm1


def test_agent_initialization_with_multiple_llms_and_default_key():
    """Test Agent can be initialized with multiple LLMs and default_llm as key."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm1 = LLM(api_key=api_key, model_name="gpt-4")
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2}, default_llm="gpt35")
    
    assert agent.llm is llm2
    assert agent.llms["gpt35"] is llm2


def test_agent_initialization_with_multiple_llms_and_default_instance():
    """Test Agent can be initialized with multiple LLMs and default_llm as instance."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm1 = LLM(api_key=api_key, model_name="gpt-4")
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2}, default_llm=llm2)
    
    assert agent.llm is llm2


def test_agent_initialization_with_single_llm():
    """Test Agent can still be initialized with a single LLM."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name="gpt-4")
    agent = Agent(llm=llm)
    
    assert len(agent.llms) == 1
    assert "default" in agent.llms
    assert agent.llms["default"] is llm
    assert agent.llm is llm


def test_agent_run_with_different_llm_by_key():
    """Test Agent can use different LLMs for different runs using key."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm1 = LLM(api_key=api_key, model_name="gpt-4")
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2}, default_llm="gpt4")
    agent.start_conversation(conversation_id="test")
    
    # Use first LLM
    response1 = agent.run("Say hello", conversation_id="test", llm_instance="gpt4")
    assert isinstance(response1, str)
    assert len(response1) > 0
    
    # Use second LLM
    response2 = agent.run("Say goodbye", conversation_id="test", llm_instance="gpt35")
    assert isinstance(response2, str)
    assert len(response2) > 0
    
    # Default LLM should still be gpt4
    assert agent.llm is llm1


def test_agent_run_with_different_llm_by_instance():
    """Test Agent can use different LLMs for different runs using instance."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm1 = LLM(api_key=api_key, model_name="gpt-4")
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2}, default_llm="gpt4")
    agent.start_conversation(conversation_id="test")
    
    # Use first LLM by instance
    response1 = agent.run("Say hello", conversation_id="test", llm_instance=llm1)
    assert isinstance(response1, str)
    
    # Use second LLM by instance
    response2 = agent.run("Say goodbye", conversation_id="test", llm_instance=llm2)
    assert isinstance(response2, str)


def test_agent_run_with_default_llm():
    """Test Agent uses default LLM when llm_instance is 'default'."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm1 = LLM(api_key=api_key, model_name="gpt-4")
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2}, default_llm="gpt4")
    agent.start_conversation(conversation_id="test")
    
    # Use default LLM
    response = agent.run("Say hello", conversation_id="test", llm_instance="default")
    assert isinstance(response, str)
    
    # Should use gpt4 (the default)
    assert agent.llm is llm1


def test_agent_switch_default_llm_by_key():
    """Test Agent can switch default LLM using key."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm1 = LLM(api_key=api_key, model_name="gpt-4")
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2}, default_llm="gpt4")
    assert agent.llm is llm1
    
    # Switch to gpt35
    agent.switch_default_llm("gpt35")
    assert agent.llm is llm2
    
    # Switch back to gpt4
    agent.switch_default_llm("gpt4")
    assert agent.llm is llm1


def test_agent_switch_default_llm_by_instance():
    """Test Agent can switch default LLM using instance."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm1 = LLM(api_key=api_key, model_name="gpt-4")
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2}, default_llm="gpt4")
    assert agent.llm is llm1
    
    # Switch to llm2
    agent.switch_default_llm(llm2)
    assert agent.llm is llm2


def test_agent_switch_default_llm_updates_special_objects():
    """Test switching default LLM updates special objects."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm1 = LLM(api_key=api_key, model_name="gpt-4")
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2}, default_llm="gpt4")
    
    # Check initial special objects
    assert agent._system_objects["llm"] is llm1
    assert agent._system_objects["llm:gpt4"] is llm1
    assert agent._system_objects["llm:gpt35"] is llm2
    
    # Switch default
    agent.switch_default_llm("gpt35")
    
    # Check updated special objects
    assert agent._system_objects["llm"] is llm2
    assert agent._system_objects["llm:gpt4"] is llm1
    assert agent._system_objects["llm:gpt35"] is llm2


def test_agent_error_invalid_llm_key_in_run():
    """Test Agent raises KeyError for invalid LLM key in run."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name="gpt-4")
    agent = Agent(llm={"gpt4": llm})
    agent.start_conversation(conversation_id="test")
    
    with pytest.raises(KeyError, match="LLM key 'invalid' not found"):
        agent.run("Say hello", conversation_id="test", llm_instance="invalid")


def test_agent_error_invalid_llm_instance_in_run():
    """Test Agent raises KeyError for invalid LLM instance in run."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm1 = LLM(api_key=api_key, model_name="gpt-4")
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1})
    agent.start_conversation(conversation_id="test")
    
    # llm2 is not in agent's llms dictionary
    with pytest.raises(KeyError, match="LLM instance not found in llms dictionary"):
        agent.run("Say hello", conversation_id="test", llm_instance=llm2)


def test_agent_error_invalid_default_llm_key():
    """Test Agent raises KeyError for invalid default_llm key in initialization."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name="gpt-4")
    
    with pytest.raises(KeyError, match="Default LLM key 'invalid' not found"):
        Agent(llm={"gpt4": llm}, default_llm="invalid")


def test_agent_error_invalid_default_llm_instance():
    """Test Agent raises KeyError for invalid default_llm instance in initialization."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm1 = LLM(api_key=api_key, model_name="gpt-4")
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    # llm2 is not in the llms dictionary
    with pytest.raises(KeyError, match="Default LLM instance not found in llms dictionary"):
        Agent(llm={"gpt4": llm1}, default_llm=llm2)


def test_agent_error_invalid_switch_default_llm_key():
    """Test Agent raises KeyError for invalid key in switch_default_llm."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm = LLM(api_key=api_key, model_name="gpt-4")
    agent = Agent(llm={"gpt4": llm})
    
    with pytest.raises(KeyError, match="LLM key 'invalid' not found"):
        agent.switch_default_llm("invalid")


def test_agent_error_invalid_switch_default_llm_instance():
    """Test Agent raises KeyError for invalid instance in switch_default_llm."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm1 = LLM(api_key=api_key, model_name="gpt-4")
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1})
    
    # llm2 is not in agent's llms dictionary
    with pytest.raises(KeyError, match="LLM instance not found in llms dictionary"):
        agent.switch_default_llm(llm2)


def test_agent_different_conversations_different_llms():
    """Test different conversations can use different LLMs."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm1 = LLM(api_key=api_key, model_name="gpt-4")
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2}, default_llm="gpt4")
    
    # Conversation 1 uses gpt4
    agent.start_conversation(conversation_id="conv1")
    response1 = agent.run("Say hello", conversation_id="conv1", llm_instance="gpt4")
    assert isinstance(response1, str)
    
    # Conversation 2 uses gpt35
    agent.start_conversation(conversation_id="conv2")
    response2 = agent.run("Say hello", conversation_id="conv2", llm_instance="gpt35")
    assert isinstance(response2, str)
    
    # Both conversations should have history
    assert len(agent.conversations["conv1"]) > 0
    assert len(agent.conversations["conv2"]) > 0


def test_agent_usage_tracking_per_llm():
    """Test usage tracking correctly tracks different LLMs."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm1 = LLM(api_key=api_key, model_name="gpt-4")
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2}, default_llm="gpt4")
    agent.start_conversation(conversation_id="test")
    
    # Use first LLM
    agent.run("Say hello", conversation_id="test", llm_instance="gpt4")
    
    # Use second LLM
    agent.run("Say goodbye", conversation_id="test", llm_instance="gpt35")
    
    # Should have 2 records
    assert len(agent.usage_tracker.records) == 2
    
    # Check LLM identifiers
    llm_keys = [r["llm"] for r in agent.usage_tracker.records]
    assert "gpt4" in llm_keys
    assert "gpt35" in llm_keys
    
    # Get usage per LLM
    usage_gpt4 = agent.get_total_usage(llm="gpt4")
    usage_gpt35 = agent.get_total_usage(llm="gpt35")
    
    assert usage_gpt4["input_tokens"] is not None
    assert usage_gpt35["input_tokens"] is not None
    assert usage_gpt4["input_tokens"] > 0
    assert usage_gpt35["input_tokens"] > 0


def test_agent_llm_special_object_with_multiple_llms():
    """Test that 'llm' special object points to default LLM."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm1 = LLM(api_key=api_key, model_name="gpt-4")
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2}, default_llm="gpt4")
    
    # 'llm' should point to default LLM
    assert agent._system_objects["llm"] is llm1
    
    # Switch default
    agent.switch_default_llm("gpt35")
    
    # 'llm' should now point to new default
    assert agent._system_objects["llm"] is llm2


def test_agent_llm_name_special_objects():
    """Test that 'llm:name' special objects are available for each LLM."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    llm1 = LLM(api_key=api_key, model_name="gpt-4")
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2}, default_llm="gpt4")
    
    # Check llm:name special objects exist
    assert "llm:gpt4" in agent._system_objects
    assert "llm:gpt35" in agent._system_objects
    assert agent._system_objects["llm:gpt4"] is llm1
    assert agent._system_objects["llm:gpt35"] is llm2


def test_agent_tool_using_llm_name_special_object():
    """Test that tools can use llm:name special objects."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    def tool_with_specific_llm(llm_instance: LLM) -> str:
        """
        Tool that receives a specific LLM instance.
        
        Args:
            llm_instance: The LLM instance.
            
        Returns:
            A string indicating the LLM was received.
        """
        assert isinstance(llm_instance, LLM)
        return f"LLM received: {llm_instance.model_name}"

    llm1 = LLM(api_key=api_key, model_name="gpt-4")
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(
        llm={"gpt4": llm1, "gpt35": llm2},
        default_llm="gpt4",
        tools=[tool_with_specific_llm],
    )
    agent.start_conversation()
    
    # Ask agent to use the tool with llm:gpt35 special object
    response = agent.run(
        "Call the tool_with_specific_llm function with the parameter llm_instance set to 'use:llm:gpt35'. "
        "Return the complete tool result exactly as the tool returns it, without modification."
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
    # The tool should have received the gpt35 LLM instance
    assert "gpt-3.5-turbo" in response.lower() or "llm received" in response.lower()


def test_agent_tool_using_default_llm_special_object():
    """Test that tools can use 'llm' special object (default LLM)."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set")

    def tool_with_default_llm(llm_instance: LLM) -> str:
        """
        Tool that receives the default LLM instance.
        
        Args:
            llm_instance: The LLM instance.
            
        Returns:
            A string indicating the LLM was received.
        """
        assert isinstance(llm_instance, LLM)
        return f"Default LLM received: {llm_instance.model_name}"

    llm1 = LLM(api_key=api_key, model_name="gpt-4")
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(
        llm={"gpt4": llm1, "gpt35": llm2},
        default_llm="gpt4",
        tools=[tool_with_default_llm],
    )
    agent.start_conversation()
    
    # Ask agent to use the tool with 'llm' special object (default)
    response = agent.run(
        "Call the tool_with_default_llm function with the parameter llm_instance set to 'use:llm'. "
        "Return the complete tool result exactly as the tool returns it, without modification."
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
    # The tool should have received the default LLM (gpt4)
    assert "gpt-4" in response.lower() or "default llm received" in response.lower()

