"""
Agent-specific run loop with multi-conversation support.
"""

from typing import Dict, Any, List, Optional, Callable, Union
from ...llm import LLM
from ..utils.return_modes import (
    CHAT_RESPONSE_MODES,
    TOOL_OUTPUT_VALUE_MODES,
    TOOL_FULL_OUTPUT_MODES,
    ALL_VALID_MODES,
)
from ..utils.verbose import (
    print_iteration,
    print_conversation_context,
    print_llm_response,
    print_tool_calls,
)


def run_agent(
    *,
    input_text: str,
    memory,
    current_conversation_id: str,
    conversation_id: Optional[str],
    return_mode: str,
    run_llm: LLM,
    llm_key: str,
    tools: Optional[List[Dict[str, Any]]],
    usage_tracker: Any,
    process_tool_call_func: Callable[[Dict[str, Any], Optional[str]], Any],
    extract_tool_output_value_func: Callable[[Any], Any],
    verbose: bool,
    max_iterations: int = 10,
) -> Any:
    """
    Execute agent run loop with multi-conversation support.
    
    Args:
        input_text: The user's input message.
        memory: Memory component instance.
        current_conversation_id: Current conversation ID (will be updated).
        conversation_id: Optional conversation ID. Uses current if not provided.
        return_mode: Return mode (validated).
        run_llm: LLM instance to use.
        llm_key: Key for the LLM being used.
        tools: Available tools (can be None).
        usage_tracker: Usage tracker instance.
        process_tool_call_func: Function to process a single tool call.
        extract_tool_output_value_func: Function to extract tool output value.
        verbose: Whether to print verbose output.
        max_iterations: Maximum number of iterations.
    
    Returns:
        The agent's response based on return_mode.
    """
    # Resolve conversation_id if not provided
    if conversation_id is None:
        conversation_id = current_conversation_id
    
    # Add user message to conversation history
    memory.add_message(conversation_id, "user", input_text)
    
    # Get conversation history for this ID (refresh after adding message)
    conversation_history = memory.get_conversation(conversation_id)
    
    # Accumulate results across iterations for tool return modes
    accumulated_tool_results: List[Any] = []
    
    iteration = 0
    while iteration < max_iterations:
        iteration += 1
        
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
        
        # Track usage for this conversation
        if run_llm.last_usage:
            usage_tracker.add_record(
                usage=run_llm.last_usage,
                cost=run_llm.last_cost,
                llm=llm_key,
                conversation_id=conversation_id,
            )
        
        # Check if response contains tool calls
        if isinstance(response, dict) and "tool_calls" in response:
            # Handle tool calling - can be multiple tool calls
            tool_calls = response["tool_calls"]
            
            if verbose:
                print_tool_calls(tool_calls=tool_calls)
            
            # Add assistant message with tool_calls to conversation
            memory.add_message(conversation_id, "assistant", None, tool_calls=tool_calls)
            conversation_history = memory.get_conversation(conversation_id)
            
            # Execute each tool call and add results
            tool_results = []
            selected_result = None  # Track if select_tool_result was called
            for tool_call in tool_calls:
                # Check if this is select_tool_result call
                tool_name = tool_call.get("function", {}).get("name", "")
                if tool_name == "select_tool_result" and return_mode in TOOL_OUTPUT_VALUE_MODES:
                    # This is a selection call - execute it and store the result
                    raw_result = process_tool_call_func(
                        tool_call=tool_call,
                        conversation_id=conversation_id,
                    )
                    selected_result = extract_tool_output_value_func(raw_result)
                    # Don't accumulate this - we'll return it directly
                else:
                    # Regular tool call - execute and accumulate
                    raw_result = process_tool_call_func(
                        tool_call=tool_call,
                        conversation_id=conversation_id,
                    )
                    tool_results.append(raw_result)
                # Refresh conversation history after each tool call
                conversation_history = memory.get_conversation(conversation_id)
            
            # If select_tool_result was called, return that result immediately
            if selected_result is not None:
                if verbose:
                    print(f"[Agent] Returning selected tool result via select_tool_result()")
                return selected_result
            
            # If return_mode is a tool mode, accumulate results and continue
            if return_mode in TOOL_OUTPUT_VALUE_MODES:
                # Extract output value from tool results (remove success/error metadata)
                extracted_results = [extract_tool_output_value_func(r) for r in tool_results]
                accumulated_tool_results.extend(extracted_results)
            elif return_mode in TOOL_FULL_OUTPUT_MODES:
                # Keep full output with metadata
                accumulated_tool_results.extend(tool_results)
            elif return_mode not in CHAT_RESPONSE_MODES:
                raise ValueError(
                    f"Invalid return_mode: {return_mode}. "
                    "Must be one of: 'chat_response' (or 'response', 'chat'), "
                    "'tool_output_value' (or 'tool_value', 'output_value', 'value'), "
                    "'tool_full_output' (or 'tool_full', 'full_output', 'full')"
                )
            
            # Continue the loop to get final response
            continue
        
        # Regular text response - ensure it's a string
        if isinstance(response, str) and len(response) > 0:
            memory.add_message(conversation_id, "assistant", response)
            conversation_history = memory.get_conversation(conversation_id)
            # If return_mode is a tool mode and we have accumulated results, return them
            if return_mode not in CHAT_RESPONSE_MODES and accumulated_tool_results:
                if verbose:
                    print(f"[Agent] Returning {len(accumulated_tool_results)} accumulated tool result(s)")
                if len(accumulated_tool_results) == 1:
                    return accumulated_tool_results[0]
                else:
                    return accumulated_tool_results
            return response
        elif isinstance(response, str):
            # Empty string response - still add it and return
            memory.add_message(conversation_id, "assistant", response)
            conversation_history = memory.get_conversation(conversation_id)
            # If return_mode is a tool mode and we have accumulated results, return them
            if return_mode not in CHAT_RESPONSE_MODES and accumulated_tool_results:
                if len(accumulated_tool_results) == 1:
                    return accumulated_tool_results[0]
                else:
                    return accumulated_tool_results
            return response
        else:
            # Unexpected response type
            response_str = str(response) if response else "Error: Empty response"
            memory.add_message(conversation_id, "assistant", response_str)
            conversation_history = memory.get_conversation(conversation_id)
            # If return_mode is a tool mode and we have accumulated results, return them
            if return_mode not in CHAT_RESPONSE_MODES and accumulated_tool_results:
                if len(accumulated_tool_results) == 1:
                    return accumulated_tool_results[0]
                else:
                    return accumulated_tool_results
            return response_str
    
    # If we've exceeded max iterations, return accumulated tool results or error
    if return_mode not in CHAT_RESPONSE_MODES and accumulated_tool_results:
        if len(accumulated_tool_results) == 1:
            return accumulated_tool_results[0]
        else:
            return accumulated_tool_results
    return "Error: Maximum iterations exceeded"

