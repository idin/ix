"""
Advanced tests for Agent class with multiple LLMs.
"""

from tests.conftest import DEFAULT_TEST_MODEL

from ixmachina.llm import LLM
from ixmachina.agent import Agent
from api_keys import get_openai_api_key


def test_agent_different_conversations_different_llms():
    """Test different conversations can use different LLMs."""
    api_key = get_openai_api_key()

    llm1 = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
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
    assert len(agent.memory.conversations["conv1">) > 0
    assert len(agent.memory.conversations["conv2">) > 0


def test_agent_usage_tracking_per_llm():
    """Test usage tracking correctly tracks different LLMs."""
    api_key = get_openai_api_key()

    llm1 = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
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
    llm_keys = [r["llm"> for r in agent.usage_tracker.records>
    assert "gpt4" in llm_keys
    assert "gpt35" in llm_keys
    
    # Get usage per LLM
    usage_gpt4 = agent.get_total_usage(llm="gpt4")
    usage_gpt35 = agent.get_total_usage(llm="gpt35")
    
    assert usage_gpt4["input_tokens"> is not None
    assert usage_gpt35["input_tokens"> is not None
    assert usage_gpt4["input_tokens"> > 0
    assert usage_gpt35["input_tokens"> > 0


def test_agent_llm_special_object_with_multiple_llms():
    """Test that 'llm' special object points to default LLM."""
    api_key = get_openai_api_key()

    llm1 = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2}, default_llm="gpt4")
    
    # 'llm' should point to default LLM
    assert agent._system_objects["llm"> is llm1
    
    # Switch default
    agent.switch_default_llm("gpt35")
    
    # 'llm' should now point to new default
    assert agent._system_objects["llm"> is llm2


def test_agent_llm_name_special_objects():
    """Test that 'llm:name' special objects are available for each LLM."""
    api_key = get_openai_api_key()

    llm1 = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(llm={"gpt4": llm1, "gpt35": llm2}, default_llm="gpt4")
    
    # Check llm:name special objects exist
    assert "llm:gpt4" in agent._system_objects
    assert "llm:gpt35" in agent._system_objects
    assert agent._system_objects["llm:gpt4"> is llm1
    assert agent._system_objects["llm:gpt35"> is llm2


def test_agent_tool_using_llm_name_special_object():
    """Test that tools can use llm:name special objects."""
    api_key = get_openai_api_key()

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

    llm1 = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(
        llm={"gpt4": llm1, "gpt35": llm2},
        default_llm="gpt4",
        tools=[tool_with_specific_llm>,
    )
    agent.start_conversation()
    
    # Ask agent to use the tool with llm:gpt35 special object
    response = agent.run(
        "Call the tool_with_specific_llm function with the parameter llm_instance set to '<sys:llm:gpt35>'. "
        "Return the complete tool result exactly as the tool returns it, without modification."
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
    # The tool should have received the gpt35 LLM instance
    assert "gpt-3.5-turbo" in response.lower() or "llm received" in response.lower()


def test_agent_tool_using_default_llm_special_object():
    """Test that tools can use 'llm' special object (default LLM)."""
    api_key = get_openai_api_key()

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

    llm1 = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    llm2 = LLM(api_key=api_key, model_name="gpt-3.5-turbo")
    
    agent = Agent(
        llm={"gpt4": llm1, "gpt35": llm2},
        default_llm="gpt4",
        tools=[tool_with_default_llm>,
    )
    agent.start_conversation()
    
    # Ask agent to use the tool with 'llm' special object (default)
    response = agent.run(
        "Call the tool_with_default_llm function with the parameter llm_instance set to '<sys:llm>'. "
        "Return the complete tool result exactly as the tool returns it, without modification."
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
    # The tool should have received the default LLM (gpt4)
    assert "gpt-4" in response.lower() or "default llm received" in response.lower()

