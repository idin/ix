"""
Tool processing utilities for BaseAgent.
"""

import json
from typing import Dict, Any, Callable

from .tool_management import convert_arguments_to_types


def process_tool_call(
    *,
    tool_call: Dict[str, Any],
    tool_schemas: Dict[str, Dict[str, Any]],
    execute_tool_func: Callable[[str, Dict[str, Any], bool], Any],
    conversation_history: list,
    verbose: bool,
) -> Any:
    """
    Process a single tool call: extract, parse, convert types, execute.
    
    Args:
        tool_call: The tool call dictionary from the LLM response.
        tool_schemas: Dictionary of tool schemas for type conversion.
        execute_tool_func: Function to execute the tool.
        conversation_history: Conversation history to update.
        verbose: Whether to print verbose output.
    
    Returns:
        Raw result from the tool execution.
    """
    # Lazy import to avoid circular dependencies
    from ..utils.verbose import print_tool_result
    
    function_name = tool_call["function"]["name"]
    arguments_json = tool_call["function"]["arguments"]
    
    # Parse JSON string to get arguments
    try:
        function_args = json.loads(arguments_json)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in tool arguments: {arguments_json}")
    
    # Convert types based on schema if available
    if function_name in tool_schemas:
        function_args = convert_arguments_to_types(
            arguments=function_args,
            tool_schema=tool_schemas[function_name]
        )
    
    # Execute the function - get raw result for tracking, string for conversation
    raw_result = execute_tool_func(
        tool_name=function_name,
        arguments=function_args,
        return_raw=True,
    )
    string_result = str(raw_result)
    
    if verbose:
        print_tool_result(tool_name=function_name, result=raw_result)
    
    # Add tool response with matching tool_call_id (as string for LLM)
    conversation_history.append({
        "role": "tool",
        "tool_call_id": tool_call["id"],
        "content": string_result,
    })
    
    return raw_result

