"""
OpenAI tool conversion utilities.
"""

import inspect
from functools import partial
from typing import Callable, Dict, Any, List


def function_to_openai_tool(func: Callable) -> Dict[str, Any]:
    """
    Convert a Python function to OpenAI tool format.

    Args:
        func: The function to convert (can be a functools.partial object).

    Returns:
        OpenAI tool format dictionary.
    """
    # Handle functools.partial objects - get signature from underlying function
    if isinstance(func, partial):
        # Get the underlying function
        underlying_func = func.func
        # Get signature from underlying function
        sig = inspect.signature(underlying_func)
        # Remove parameters that are already bound in the partial
        bound_args = set(func.keywords.keys()) if func.keywords else set()
        bound_args.update(func.args if func.args else [])
    else:
        sig = inspect.signature(func)
        bound_args = set()
    doc = inspect.getdoc(func) or ""
    
    properties = {}
    required = []
    
    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue
        # Skip parameters that are already bound in partial
        if isinstance(func, partial):
            # Check if this parameter is bound by position
            param_index = list(sig.parameters.keys()).index(param_name)
            if param_index < len(func.args):
                continue
            # Check if this parameter is bound by keyword
            if param_name in bound_args:
                continue
        
        param_type = "string"
        if param.annotation != inspect.Parameter.empty:
            if param.annotation == int:
                param_type = "integer"
            elif param.annotation == float:
                param_type = "number"
            elif param.annotation == bool:
                param_type = "boolean"
            elif param.annotation == dict:
                param_type = "object"
            elif param.annotation == list:
                param_type = "array"
        
        properties[param_name] = {
            "type": param_type,
            "description": "",
        }
        if param.default == inspect.Parameter.empty:
            required.append(param_name)
    
    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": doc.split("\n\n")[0] if doc else "",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


def convert_tools_to_openai(tools: List[Callable]) -> List[Dict[str, Any]]:
    """
    Convert a list of Python functions to OpenAI tool format.

    Args:
        tools: List of callable functions.

    Returns:
        List of OpenAI tool format dictionaries.
    """
    return [function_to_openai_tool(tool) for tool in tools]


def get_tool_schemas_for_openai(tools: List[Callable]) -> Dict[str, Dict[str, Any]]:
    """
    Get tool schemas for type conversion in OpenAI format.

    Args:
        tools: List of callable functions.

    Returns:
        Dictionary mapping tool names to their schemas.
    """
    schemas = {}
    for tool in tools:
        schemas[tool.__name__] = function_to_openai_tool(tool)
    return schemas

