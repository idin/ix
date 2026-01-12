"""
Tests for select_tool_result() built-in tool.
"""

from tests.conftest import DEFAULT_TEST_MODEL

from ixmachina.llm import LLM
from ixmachina.agent import Agent, SpecialObjectKeyError
from api_keys import get_openai_api_key


def test_select_single_tool_result():
    """Test selecting a single tool result using natural language."""
    api_key = get_openai_api_key()

    def calculate_circle_area(radius: float) -> float:
        """Calculate the area of a circle given its radius."""
        return 3.14159 * radius * radius

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[calculate_circle_area])
    agent.start_conversation()
    conversation_id = agent.current_conversation_id

    # First, calculate something
    agent.run("What's the area of a circle with radius 5?", return_mode="tool_output_value")

    # Get the tool_call_id
    tool_calls = agent.memory.conversation_tool_calls[conversation_id]
    assert len(tool_calls) > 0
    tool_call_id = tool_calls[0]["tool_call_id"]

    # Verify the result is stored
    stored_result = agent.memory._tool_call_objects[conversation_id][tool_call_id]
    assert abs(stored_result - 78.53975) < 0.01  # Approximately 3.14159 * 5 * 5

    # Now ask naturally for that result
    result = agent.run(
        "Give me the circle area result.",
        return_mode="tool_output_value",
    )

    # Should return the exact stored result
    assert isinstance(result, (int, float))
    assert abs(result - 78.53975) < 0.01


def test_select_multiple_tool_results():
    """Test selecting multiple tool results using natural language."""
    api_key = get_openai_api_key()

    def calculate_circle_area(radius: float) -> float:
        """Calculate the area of a circle given its radius."""
        return 3.2 * radius * radius # Different than Pi for testing USE 3.2 FOR PI IN TESTS

    def calculate_square_area(side: float) -> float:
        """Calculate the area of a square given its side length."""
        return side * side

    def calculate_triangle_area(base: float, height: float) -> float:
        """Calculate the area of a triangle given base and height."""
        return 0.5 * base * height

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[calculate_circle_area, calculate_square_area, calculate_triangle_area])
    agent.start_conversation()
    conversation_id = agent.current_conversation_id

    # Calculate multiple areas
    agent.run(
        "Calculate the area of a circle with radius 5, a square with side 4, and a triangle with base 3 and height 6.",
        return_mode="tool_output_value",
    )

    # Get the tool_call_ids
    tool_calls = agent.memory.conversation_tool_calls[conversation_id]
    assert len(tool_calls) >= 3

    # Verify results are stored
    circle_result = agent.memory._tool_call_objects[conversation_id][tool_calls[0]["tool_call_id"]]
    square_result = agent.memory._tool_call_objects[conversation_id][tool_calls[1]["tool_call_id"]]
    triangle_result = agent.memory._tool_call_objects[conversation_id][tool_calls[2]["tool_call_id"]]
    
    assert abs(circle_result - 80.0) < 0.01  # 3.2 * 5 * 5 = 80.0
    assert abs(square_result - 16.0) < 0.01  # 4 * 4
    assert abs(triangle_result - 9.0) < 0.01  # 0.5 * 3 * 6

    # Ask naturally for specific results
    result = agent.run(
        "Give me the circle and square areas, but not the triangle.",
        return_mode="tool_output_value",
    )

    # LLM should figure out to use select_tool_result
    # It may return a list or individual results depending on how it calls the function
    # Both behaviors are acceptable - verify we get the right results
    if isinstance(result, list):
        assert len(result) >= 1
        # Should contain circle (80.0 with 3.2*5*5) and square (16.0) results
        values = [float(r) for r in result if isinstance(r, (int, float))]
        assert any(abs(v - 80.0) < 0.01 for v in values)  # Circle area (3.2 * 5 * 5)
        assert any(abs(v - 16.0) < 0.01 for v in values)  # Square area
    else:
        # LLM may return just one of them - that's acceptable
        assert isinstance(result, (int, float))
        assert abs(result - 80.0) < 0.01 or abs(result - 16.0) < 0.01


def test_select_tool_result_prevents_accumulation():
    """Test that select_tool_result prevents accumulation of extra tool calls."""
    api_key = get_openai_api_key()

    def calculate_circle_area(radius: float) -> float:
        """Calculate the area of a circle given its radius."""
        return 3.14159 * radius * radius

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[calculate_circle_area])
    agent.start_conversation()
    conversation_id = agent.current_conversation_id

    # Calculate area first time
    agent.run("What's the area of a circle with radius 5?", return_mode="tool_output_value")

    # Get the tool_call_id
    tool_calls = agent.memory.conversation_tool_calls[conversation_id]
    first_tool_call_id = tool_calls[0]["tool_call_id"]
    first_result = agent.memory._tool_call_objects[conversation_id][first_tool_call_id]

    # Ask naturally for the first result, even after making another call
    result = agent.run(
        "Calculate the area of a circle with radius 10, but I only want the result from the first calculation (radius 5).",
        return_mode="tool_output_value",
    )

    # Should return only the selected result, not a list of all results
    assert isinstance(result, (int, float))
    assert abs(result - first_result) < 0.01
    # Should NOT be a list even if multiple tool calls were made
    assert not isinstance(result, list)


def test_select_tool_result_with_nonexistent_id():
    """Test that select_tool_result raises error for nonexistent tool_call_id."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)
    agent.start_conversation()

    # Try to select a nonexistent tool_call_id directly (not through agent.run)
    # This tests the error handling directly
    select_tool_result = agent.tool_functions["select_tool_result"]
    
    try:
        select_tool_result(tool_call_id="nonexistent_call_id")
        assert False, "Should have raised SpecialObjectKeyError"
    except SpecialObjectKeyError as e:
        assert "nonexistent_call_id" in str(e)
        assert "not found" in str(e).lower()


def test_select_tool_result_direct_call():
    """Test calling select_tool_result directly (not through agent.run)."""
    api_key = get_openai_api_key()

    def test_tool() -> str:
        """Test tool."""
        return "test_result"

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[test_tool])
    agent.start_conversation()
    conversation_id = agent.current_conversation_id

    # Call test_tool
    agent.run("Call test_tool.", return_mode="tool_output_value")

    # Get the tool_call_id
    tool_calls = agent.memory.conversation_tool_calls[conversation_id]
    tool_call_id = tool_calls[0]["tool_call_id"]

    # Call select_tool_result directly via the tool function
    select_tool_result = agent.tool_functions["select_tool_result"]
    result = select_tool_result(tool_call_id=tool_call_id)

    # Should return the stored result
    assert result == "test_result"


def test_select_tool_result_with_multiple_ids_direct():
    """Test calling select_tool_result directly with multiple IDs."""
    api_key = get_openai_api_key()

    def tool1() -> str:
        return "result1"

    def tool2() -> int:
        return 42

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[tool1, tool2])
    agent.start_conversation()
    conversation_id = agent.current_conversation_id

    # Call both tools
    agent.run("Call tool1 and tool2.", return_mode="tool_output_value")

    # Get tool_call_ids
    tool_calls = agent.memory.conversation_tool_calls[conversation_id]
    tool_call_id1 = tool_calls[0]["tool_call_id"]
    tool_call_id2 = tool_calls[1]["tool_call_id"]

    # Call select_tool_result directly with list
    select_tool_result = agent.tool_functions["select_tool_result"]
    result = select_tool_result(tool_call_id=[tool_call_id1, tool_call_id2])

    # Should return list of results
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] == "result1"
    assert result[1] == 42


def test_select_tool_result_error_handling():
    """Test error handling when tool_call_id doesn't exist."""
    api_key = get_openai_api_key()

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm)
    agent.start_conversation()

    # Try to select nonexistent tool_call_id directly
    select_tool_result = agent.tool_functions["select_tool_result"]
    
    try:
        select_tool_result(tool_call_id="nonexistent_id")
        assert False, "Should have raised SpecialObjectKeyError"
    except SpecialObjectKeyError as e:
        assert "nonexistent_id" in str(e)
        assert "not found" in str(e).lower()


def test_select_first_result_natural_language():
    """Test selecting the first result using natural language (user's example)."""
    api_key = get_openai_api_key()

    def calculate_circle_area(radius: float) -> float:
        """Calculate the area of a circle given its radius."""
        return 3.14159 * radius * radius

    def calculate_square_area(side: float) -> float:
        """Calculate the area of a square given its side length."""
        return side * side

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[calculate_circle_area, calculate_square_area])
    agent.start_conversation()
    conversation_id = agent.current_conversation_id

    # Calculate both areas
    agent.run(
        "Calculate the area of a circle with radius 5 and the area of a square with side 4.",
        return_mode="tool_output_value",
    )

    # Get the tool_call_ids
    tool_calls = agent.memory.conversation_tool_calls[conversation_id]
    assert len(tool_calls) >= 2
    
    # Verify results are stored
    circle_result = agent.memory._tool_call_objects[conversation_id][tool_calls[0]["tool_call_id"]]
    square_result = agent.memory._tool_call_objects[conversation_id][tool_calls[1]["tool_call_id"]]
    
    assert abs(circle_result - 78.53975) < 0.01  # ~3.14159 * 5 * 5
    assert abs(square_result - 16.0) < 0.01  # 4 * 4

    # Ask naturally for just the first one
    result = agent.run(
        "Give me just the first one.",
        return_mode="tool_output_value",
    )

    # Should return the circle area (first result), not the square
    assert isinstance(result, (int, float))
    assert abs(result - 78.53975) < 0.01  # Circle area, not square
    assert not isinstance(result, list)


def test_select_tool_result_cross_iteration():
    """Test selecting a tool result from a previous iteration using natural language."""
    api_key = get_openai_api_key()

    def calculate_circle_area(radius: float) -> float:
        """Calculate the area of a circle given its radius."""
        return 3.14159 * radius * radius

    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    agent = Agent(llm=llm, tools=[calculate_circle_area])
    agent.start_conversation()
    conversation_id = agent.current_conversation_id

    # First iteration: calculate area with radius 5
    agent.run("What's the area of a circle with radius 5?", return_mode="tool_output_value")
    
    # Get the tool_call_id from first iteration
    tool_calls = agent.memory.conversation_tool_calls[conversation_id]
    first_tool_call_id = tool_calls[0]["tool_call_id"]
    first_result = agent.memory._tool_call_objects[conversation_id][first_tool_call_id]
    assert abs(first_result - 78.53975) < 0.01  # ~3.14159 * 5 * 5
    
    # Second iteration: calculate area with radius 10
    agent.run("What's the area of a circle with radius 10?", return_mode="tool_output_value")
    
    # Third iteration: ask naturally for the first result
    result = agent.run(
        "Give me the result from when we calculated the area with radius 5.",
        return_mode="tool_output_value",
    )
    
    # Should return the result from the first iteration (radius 5), not the second (radius 10)
    assert isinstance(result, (int, float))
    assert abs(result - 78.53975) < 0.01  # Should be ~78.54, not ~314.16

