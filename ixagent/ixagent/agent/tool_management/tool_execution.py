"""
Tool execution utilities for BaseAgent.
"""

from typing import Dict, Any, Callable

from ...tools.constants import RESULT_KEY, SUCCESS_KEY, ERROR_KEY


def execute_tool(
    *,
    tool_functions: Dict[str, Callable],
    tool_name: str,
    arguments: Dict[str, Any],
    return_raw: bool = False,
) -> Any:
    """
    Execute a tool function with given arguments.
    
    Args:
        tool_functions: Dictionary mapping tool names to functions.
        tool_name: Name of the tool to execute.
        arguments: Arguments to pass to the tool.
        return_raw: If True, return raw result; if False, return as string.
    
    Returns:
        Tool execution result as a string (default) or raw result.
    """
    if tool_name not in tool_functions:
        error_msg = f"Error: Tool '{tool_name}' not found"
        return error_msg
    
    try:
        func = tool_functions[tool_name]
        result = func(**arguments)
        return result if return_raw else str(result)
    except Exception as e:
        return f"Error executing tool: {str(e)}"


def extract_tool_output_value(tool_result: Any) -> Any:
    """
    Extract the output value from a tool result, removing metadata.
    
    Uses the standard RESULT_KEY from tool constants to extract the primary output.
    If RESULT_KEY is present, returns it directly (standardized output).
    Otherwise falls back to removing success/error metadata and returning the remaining fields.
    
    Args:
        tool_result: The raw tool result with metadata.
    
    Returns:
        The extracted output value without metadata.
    """
    if isinstance(tool_result, dict) and SUCCESS_KEY in tool_result:
        # If RESULT_KEY is present, return it directly (standardized output)
        if RESULT_KEY in tool_result:
            return tool_result[RESULT_KEY]
        # Fallback: Extract all fields except success and error
        output = {k: v for k, v in tool_result.items() if k not in (SUCCESS_KEY, ERROR_KEY)}
        # If only one field remains, return that value directly
        if len(output) == 1:
            return next(iter(output.values()))
        # Otherwise return the dict without success/error
        return output
    return tool_result

