"""
Integration tests for @bind decorator with Agent.

Tests that tools decorated with @bind work correctly when added to an Agent
and invoked through natural language prompts.

IMPORTANT RULES FOR @bind DECORATOR TESTS:
1. Bound objects are AUTOMATICALLY INJECTED by the decorator into the function's global scope
2. Bound objects should NOT appear in function signatures
3. Local variables must have DIFFERENT names than bound object keys
   Example: storage_obj = SimpleStorage(), then @bind(storage=storage_obj)
4. Inside decorated functions, use the bound object names directly (storage, email, etc.)
   These are injected by the decorator into globals, NOT passed as parameters

CORRECT:
    storage_obj = SimpleStorage()
    @bind(storage=storage_obj)
    def my_func(x: int):
        storage.store(x)  # 'storage' is found in globals

WRONG:
    storage = SimpleStorage()
    @bind(storage=storage)
    def my_func(x: int, storage):  # ❌ Don't put storage in signature!
        storage.store(x)
"""

import os
import pytest
from ixmachina.llm import LLM
from ixmachina.agent import Agent
from ixmachina.utils import ToolContext, bind


class SimpleStorage:
    """Simple storage for testing."""
    def __init__(self):
        self.items = []
    
    def store(self, text: str) -> str:
        """Store text and return confirmation."""
        self.items.append(text)
        return f"Stored: {text}"


class Calculator:
    """Simple calculator for testing."""
    def __init__(self):
        self.history = []
    
    def calculate(self, expression: str) -> float:
        """Evaluate a mathematical expression."""
        result = eval(expression)
        self.history.append(f"{expression} = {result}")
        return result


def test_bind_with_agent_using_context():
    """Test that @bind with ToolContext works when tool is added to agent."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")
    
    # Create objects
    storage_obj = SimpleStorage()
    calc_obj = Calculator()
    ctx = ToolContext(storage=storage_obj, calc=calc_obj)
    
    
    # Create tool with bound objects
    @bind(context=ctx)
    def calculate_and_store(expression: str) -> str:
        """
        Calculate a mathematical expression and store the result.
        
        Args:
            expression: Mathematical expression to evaluate (e.g., "2 + 2", "10 * 5").
            
        Returns:
            String describing the calculation and storage.
        """
        result = calc.calculate(expression)
        storage.store(f"Calculated: {expression} = {result}")
        return f"Result: {result}, stored successfully"
    
    # Create agent and add tool
    llm = LLM(api_key=api_key, model_name="gpt-4o-mini")
    agent = Agent(llm=llm, verbose=False)
    agent.add_tools([calculate_and_store])
    
    # Agent should use the tool
    response = agent.run(input_text="Calculate 15 + 27 and store the result")
    
    # Verify the tool was called and objects were used
    assert len(calc_obj.history) == 1
    assert "15+27" in calc_obj.history[0] or "15 + 27" in calc_obj.history[0]
    assert len(storage_obj.items) == 1
    assert "42" in storage_obj.items[0]
    assert "42" in response


def test_bind_with_agent_using_direct_kwargs():
    """Test that @bind with direct kwargs works when tool is added to agent."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")
    
    # Create objects
    storage_obj = SimpleStorage()
    
    # Create tool with bound object
    @bind(storage=storage_obj)
    def save_note(note: str) -> str:
        """
        Save a note to storage.
        
        Args:
            note: The note text to save.
            
        Returns:
            Confirmation message.
        """
        result = storage.store(note)
        return result
    
    # Create agent and add tool
    llm = LLM(api_key=api_key, model_name="gpt-4o-mini")
    agent = Agent(llm=llm, verbose=False)
    agent.add_tools([save_note])
    
    # Agent should use the tool
    response = agent.run(input_text="Save a note: 'Meeting at 3pm tomorrow'")
    
    # Verify the tool was called
    assert len(storage_obj.items) == 1
    assert "3pm" in storage_obj.items[0] or "Meeting" in storage_obj.items[0]


def test_bind_with_agent_combining_context_and_kwargs():
    """Test that @bind with ToolContext + additional kwargs works with agent."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")
    
    # Create objects
    storage_obj = SimpleStorage()
    calc_obj = Calculator()
    ctx = ToolContext(storage=storage_obj, calc=calc_obj)
    
    # Additional object not in context
    log_dict = {"entries": []}
    
    # Create tool with context + additional object
    @bind(context=ctx, log=log_dict)
    def calculate_store_and_log(expression: str) -> str:
        """
        Calculate an expression, store it, and log the operation.
        
        Args:
            expression: Mathematical expression to evaluate.
            
        Returns:
            Confirmation message.
        """
        result = calc.calculate(expression)
        storage.store(f"{expression} = {result}")
        log["entries"].append(f"Operation: {expression}")
        return f"Calculated {expression} = {result}, stored and logged"
    
    # Create agent and add tool
    llm = LLM(api_key=api_key, model_name="gpt-4o-mini")
    agent = Agent(llm=llm, verbose=False)
    agent.add_tools([calculate_store_and_log])
    
    # Agent should use the tool
    response = agent.run(input_text="Calculate 7 * 8")
    
    # Verify all three objects were used
    assert len(calc_obj.history) == 1
    assert len(storage_obj.items) == 1
    assert len(log_dict["entries"]) == 1
    assert "56" in response or "7" in calc_obj.history[0]


def test_bind_preserves_docstring_for_agent():
    """Test that agent can see the original docstring of decorated tools."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")
    
    storage_obj = SimpleStorage()
    
    @bind(storage=storage_obj)
    def special_tool(data: str) -> str:
        """
        This is a special tool with a unique docstring.
        It does something very specific with the data.
        
        Args:
            data: Some important data to process.
            
        Returns:
            Processed result.
        """
        storage.store(data)
        return f"Processed: {data}"
    
    # Verify docstring is preserved
    assert "special tool" in special_tool.__doc__
    assert "very specific" in special_tool.__doc__
    
    # Create agent and add tool
    llm = LLM(api_key=api_key, model_name="gpt-4o-mini")
    agent = Agent(llm=llm, verbose=False)
    agent.add_tools([special_tool])
    
    # Agent should be able to use the tool based on its docstring
    response = agent.run(input_text="Use the special tool to process 'test data'")
    
    # Verify the tool was called
    assert len(storage_obj.items) >= 1
    assert any("test" in item.lower() for item in storage_obj.items)


def test_bind_multiple_tools_with_shared_context():
    """Test multiple tools sharing the same ToolContext with an agent."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")
    
    # Create shared context
    storage_obj = SimpleStorage()
    calc_obj = Calculator()
    ctx = ToolContext(storage=storage_obj, calc=calc_obj)
    
    # Create multiple tools sharing the context
    @bind(context=ctx)
    def add_numbers(a: int, b: int) -> str:
        """
        Add two numbers and store the result.
        
        Args:
            a: First number.
            b: Second number.
            
        Returns:
            The sum.
        """
        result = calc.calculate(f"{a}+{b}")
        storage.store(f"Addition: {a} + {b} = {result}")
        return str(result)
    
    @bind(context=ctx)
    def multiply_numbers(a: int, b: int) -> str:
        """
        Multiply two numbers and store the result.
        
        Args:
            a: First number.
            b: Second number.
            
        Returns:
            The product.
        """
        result = calc.calculate(f"{a}*{b}")
        storage.store(f"Multiplication: {a} * {b} = {result}")
        return str(result)
    
    # Create agent and add both tools
    llm = LLM(api_key=api_key, model_name="gpt-4o-mini")
    agent = Agent(llm=llm, verbose=False)
    agent.add_tools([add_numbers, multiply_numbers])
    
    # Agent should use both tools
    response1 = agent.run(input_text="Add 10 and 20")
    response2 = agent.run(input_text="Multiply 7 and 6")
    
    # Verify both tools were called and shared the same storage/calc
    assert len(calc_obj.history) == 2
    assert len(storage_obj.items) == 2
    assert any("30" in item for item in storage_obj.items)
    assert any("42" in item for item in storage_obj.items)

