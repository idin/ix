"""
Run loop utilities for BaseAgent.
"""

from typing import Dict, Any, List, Optional, Callable

from ...llm import LLM
from ..utils.return_modes import (
    CHAT_RESPONSE_MODES,
    TOOL_OUTPUT_VALUE_MODES,
    TOOL_FULL_OUTPUT_MODES,
)
from ..tool_management.tool_execution import extract_tool_output_value
from ..utils.verbose import (
    print_iteration,
    print_conversation_context,
    print_llm_response,
    print_tool_calls,
)


def handle_tool_calls(
    *,
    tool_calls: List[Dict[str, Any]],
    conversation_history: List[Dict[str, str]],
    process_tool_call: Callable[[Dict[str, Any]], Any],
    return_mode: str,
    accumulated_tool_results: List[Any],
    verbose: bool,
) -> None:
    """
    Handle tool calls from LLM response.
    
    Args:
        tool_calls: List of tool call dictionaries.
        conversation_history: Conversation history to update.
        process_tool_call: Function to process a single tool call.
        return_mode: Current return mode.
        accumulated_tool_results: List to accumulate tool results.
        verbose: Whether to print verbose output.
    """
    if verbose:
        print_tool_calls(tool_calls=tool_calls)
    
    # Add assistant message with tool_calls to conversation
    conversation_history.append({
        "role": "assistant",
        "content": None,
        "tool_calls": tool_calls,
    })
    
    # Execute each tool call and add results
    tool_results = []
    for tool_call in tool_calls:
        raw_result = process_tool_call(tool_call=tool_call)
        tool_results.append(raw_result)
    
    # If return_mode is a tool mode, accumulate results
    if return_mode in TOOL_OUTPUT_VALUE_MODES:
        # Extract output value from tool results (remove success/error metadata)
        extracted_results = [extract_tool_output_value(r) for r in tool_results]
        accumulated_tool_results.extend(extracted_results)
    elif return_mode in TOOL_FULL_OUTPUT_MODES:
        # Keep full output with metadata
        accumulated_tool_results.extend(tool_results)


def handle_text_response(
    *,
    response: str,
    conversation_history: List[Dict[str, str]],
    return_mode: str,
    accumulated_tool_results: List[Any],
    verbose: bool,
) -> Optional[Any]:
    """
    Handle text response from LLM.
    
    Args:
        response: The text response from LLM.
        conversation_history: Conversation history to update.
        return_mode: Current return mode.
        accumulated_tool_results: List of accumulated tool results.
        verbose: Whether to print verbose output.
    
    Returns:
        Response value if should return, None if should continue loop.
    """
    if len(response) > 0:
        conversation_history.append({"role": "assistant", "content": response})
    else:
        # Empty string response - still add it
        conversation_history.append({"role": "assistant", "content": response})
    
    # If return_mode is a tool mode and we have accumulated results, return them
    if return_mode not in CHAT_RESPONSE_MODES and accumulated_tool_results:
        if verbose:
            print(f"[Agent] Returning {len(accumulated_tool_results)} accumulated tool result(s)")
        if len(accumulated_tool_results) == 1:
            return accumulated_tool_results[0]
        else:
            return accumulated_tool_results
    
    return response


def handle_unexpected_response(
    *,
    response: Any,
    conversation_history: List[Dict[str, str]],
    return_mode: str,
    accumulated_tool_results: List[Any],
) -> Any:
    """
    Handle unexpected response type from LLM.
    
    Args:
        response: The unexpected response.
        conversation_history: Conversation history to update.
        return_mode: Current return mode.
        accumulated_tool_results: List of accumulated tool results.
    
    Returns:
        Response value.
    """
    response_str = str(response) if response else "Error: Empty response"
    conversation_history.append({"role": "assistant", "content": response_str})
    
    # If return_mode is a tool mode and we have accumulated results, return them
    if return_mode not in CHAT_RESPONSE_MODES and accumulated_tool_results:
        if len(accumulated_tool_results) == 1:
            return accumulated_tool_results[0]
        else:
            return accumulated_tool_results
    
    return response_str


def get_final_result(
    *,
    return_mode: str,
    accumulated_tool_results: List[Any],
) -> str:
    """
    Get final result when max iterations exceeded.
    
    Args:
        return_mode: Current return mode.
        accumulated_tool_results: List of accumulated tool results.
    
    Returns:
        Final result string or accumulated results.
    """
    if return_mode not in CHAT_RESPONSE_MODES and accumulated_tool_results:
        if len(accumulated_tool_results) == 1:
            return accumulated_tool_results[0]
        else:
            return accumulated_tool_results
    return "Error: Maximum iterations exceeded"


def execute_iteration(
    *,
    iteration: int,
    max_iterations: int,
    run_llm: LLM,
    conversation_history: List[Dict[str, str]],
    tools: Optional[List[Dict[str, Any]]],
    usage_tracker: Any,
    llm_key: str,
    return_mode: str,
    process_tool_call: Callable[[Dict[str, Any]], Any],
    accumulated_tool_results: List[Any],
    verbose: bool,
) -> tuple[bool, Any]:
    """
    Execute a single iteration of the run loop.
    
    Args:
        iteration: Current iteration number.
        max_iterations: Maximum number of iterations.
        run_llm: LLM instance to use.
        conversation_history: Conversation history.
        tools: Available tools (can be None).
        usage_tracker: Usage tracker instance.
        llm_key: Key for the LLM being used.
        return_mode: Current return mode.
        process_tool_call: Function to process a single tool call.
        accumulated_tool_results: List to accumulate tool results.
        verbose: Whether to print verbose output.
    
    Returns:
        Tuple of (should_continue, result). If should_continue is False, result contains the return value.
    """
    if verbose:
        print_iteration(iteration=iteration, max_iterations=max_iterations)
        print_conversation_context(conversation_history=conversation_history)
    
    # Query LLM - use cached tools if available
    if tools is not None:
        response = run_llm.query(
            messages=conversation_history,
            tools=tools,
        )
    else:
        response = run_llm.query(messages=conversation_history)
    
    if verbose:
        print_llm_response(response=response)
    
    # Track usage
    if run_llm.last_usage:
        usage_tracker.add_record(
            usage=run_llm.last_usage,
            cost=run_llm.last_cost,
            llm=llm_key,
        )
    
    # Check if response contains tool calls
    if isinstance(response, dict) and "tool_calls" in response:
        handle_tool_calls(
            tool_calls=response["tool_calls"],
            conversation_history=conversation_history,
            process_tool_call=process_tool_call,
            return_mode=return_mode,
            accumulated_tool_results=accumulated_tool_results,
            verbose=verbose,
        )
        return True, None  # Continue loop
    
    # Regular text response
    if isinstance(response, str):
        result = handle_text_response(
            response=response,
            conversation_history=conversation_history,
            return_mode=return_mode,
            accumulated_tool_results=accumulated_tool_results,
            verbose=verbose,
        )
        if result is not None:
            return False, result  # Return result
        return True, None  # Continue loop (shouldn't happen, but be safe)
    
    # Unexpected response type
    result = handle_unexpected_response(
        response=response,
        conversation_history=conversation_history,
        return_mode=return_mode,
        accumulated_tool_results=accumulated_tool_results,
    )
    return False, result

