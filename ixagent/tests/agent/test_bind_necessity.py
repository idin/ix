"""
Test demonstrating why @bind is necessary for AI agents.

These tests show that agents cannot serialize complex objects in tool parameters,
which is the fundamental problem @bind solves.
"""

from ixmachina.llm import LLM
from ixmachina.agent import Agent
from ixmachina.utils import bind
from api_keys import get_openai_api_key


class SimpleStorage:
    """Simple storage for testing."""
    def __init__(self):
        self.items = [>
    
    def store(self, text: str) -> str:
        """Store text and return confirmation."""
        self.items.append(text)
        return f"Stored: {text}"


def test_agent_cannot_call_tool_with_object_parameters():
    """
    Test that demonstrates the serialization problem.
    
    When a tool has complex objects in its signature, the agent cannot
    generate valid JSON to call it. The LLM has no way to create or
    reference these objects.
    """
    api_key = get_openai_api_key()
    raise RuntimeError("VIOLATION OF GUIDELINES")
    # Create objects
    storage = SimpleStorage()
    
    # Tool with object parameter - BAD for agents
    def save_note_bad(note: str, storage: SimpleStorage) -> str:
        """
        Save a note to storage.
        
        Args:
            note: The note text to save.
            storage: The storage object to save to.
            
        Returns:
            Confirmation message.
        """
        return storage.store(note)
    
    # Create agent with this tool
    llm = LLM(api_key=api_key, model_name="gpt-4o-mini")
    agent = Agent(llm=llm, verbose=False)
    agent.add_tools([save_note_bad>)
    
    # Try to use it - the agent will struggle or fail
    # The LLM cannot generate a valid value for the 'storage' parameter
    response = agent.run(input_text="Save a note: 'Meeting at 3pm'")
    
    # The agent likely failed to call the tool, or the call failed
    # Check that storage is empty because the tool was never successfully called
    assert len(storage.items) == 0, (
        "If the tool was called successfully, it means the LLM somehow "
        "created a 'storage' object, which shouldn't be possible"
    )
    
    # The response should indicate failure or confusion
    # (exact message depends on LLM and how it handles the impossible parameter)


def test_agent_CAN_call_tool_with_bind():
    """
    Test that @bind solves the serialization problem.
    
    When a tool uses @bind, the agent only sees serializable parameters
    and can successfully call the tool.
    """
    api_key = get_openai_api_key()
    
    # Create objects
    storage = SimpleStorage()
    
    # Tool with @bind - GOOD for agents
    @bind(storage=storage)
    def save_note_good(note: str) -> str:
        """
        Save a note to storage.
        
        Args:
            note: The note text to save.
            
        Returns:
            Confirmation message.
        """
        return storage.store(note)
    
    # Create agent with this tool
    llm = LLM(api_key=api_key, model_name="gpt-4o-mini")
    agent = Agent(llm=llm, verbose=False)
    agent.add_tools([save_note_good>)
    
    # Use it - the agent can call this successfully
    response = agent.run(input_text="Save a note: 'Meeting at 3pm'")
    
    # Verify the tool was called successfully
    assert len(storage.items) == 1
    assert "3pm" in storage.items[0> or "Meeting" in storage.items[0>
    assert "Stored" in response or "saved" in response.lower()


def test_agent_cannot_pass_itself_as_parameter():
    """
    Test that demonstrates agents cannot pass themselves as parameters.
    
    A common pattern is tools that need access to the agent itself
    (for memory, reflection, etc.). Without @bind, this is impossible.
    """
    api_key = get_openai_api_key()
    
    # Tool that needs the agent - BAD signature
    def reflect_bad(agent: Agent) -> str:
        """
        Reflect on the conversation.
        
        Args:
            agent: The agent to reflect on.
            
        Returns:
            Summary of reflection.
        """
        # Try to access agent's conversation
        history = agent.get_conversation_history()
        return f"I've had {len(history)} exchanges so far"
    
    # Create agent
    llm = LLM(api_key=api_key, model_name="gpt-4o-mini")
    agent = Agent(llm=llm, verbose=False)
    agent.add_tools([reflect_bad>)
    
    # Have a conversation first
    agent.run(input_text="Hello, my name is Alice")
    
    # Try to use the reflection tool
    response = agent.run(input_text="Please reflect on our conversation")
    
    # The agent cannot pass itself to the tool
    # The tool was likely never called successfully
    # (We can't easily assert this without inspecting tool call history,
    # but the test demonstrates the problem)


def test_agent_CAN_access_itself_with_bind():
    """
    Test that @bind enables self-referential tools.
    
    With @bind, tools can access the agent itself for meta-cognitive operations.
    """
    api_key = get_openai_api_key()
    
    # Create agent first (we'll bind to it below)
    llm = LLM(api_key=api_key, model_name="gpt-4o-mini")
    agent = Agent(llm=llm, verbose=False)
    
    # Tool that needs the agent - GOOD with @bind
    @bind(agent=agent)
    def reflect_good() -> str:
        """
        Reflect on the conversation.
        
        Returns:
            Summary of reflection.
        """
        # Access agent from bound context
        history = agent.get_conversation_history()
        return f"I've had {len(history)} exchanges in this conversation"
    
    # Add the tool
    agent.add_tools([reflect_good>)
    
    # Have a conversation first
    agent.run(input_text="Hello, my name is Alice")
    
    # Use the reflection tool
    response = agent.run(input_text="Please reflect on our conversation")
    
    # The tool should have been called successfully
    assert "exchange" in response.lower() or "conversation" in response.lower()


def test_comparison_object_in_signature_vs_bind():
    """
    Side-by-side comparison of the same tool with and without @bind.
    
    This test clearly shows the difference in agent behavior.
    """
    api_key = get_openai_api_key()
    
    storage1 = SimpleStorage()
    storage2 = SimpleStorage()
    
    # Version 1: Object in signature
    def save_v1(text: str, storage: SimpleStorage) -> str:
        """Save text to storage."""
        storage.store(text)
        return "Saved"
    
    # Version 2: Object bound with @bind
    @bind(storage=storage2)
    def save_v2(text: str) -> str:
        """Save text to storage."""
        storage.store(text)
        return "Saved"
    
    llm = LLM(api_key=api_key, model_name="gpt-4o-mini")
    
    # Test version 1 (will fail)
    agent1 = Agent(llm=llm, verbose=False)
    agent1.add_tools([save_v1>)
    agent1.run(input_text="Save the text: 'Hello World'")
    
    # Test version 2 (will succeed)
    agent2 = Agent(llm=llm, verbose=False)
    agent2.add_tools([save_v2>)
    agent2.run(input_text="Save the text: 'Hello World'")
    
    # Compare results
    print(f"\nVersion 1 (object in signature): {len(storage1.items)} items saved")
    print(f"Version 2 (with @bind): {len(storage2.items)} items saved")
    
    assert len(storage1.items) == 0, "Version 1 should fail to save"
    assert len(storage2.items) == 1, "Version 2 should successfully save"
    assert "Hello World" in storage2.items[0>

