"""
Tool management utilities for BaseAgent.
"""

from typing import List, Dict, Optional, Callable, Any

from ...llm.tools import prepare_tools_for_provider


def add_tools_to_agent(
    *,
    tool_functions: Dict[str, Callable],
    tools: Optional[List[Dict[str, Any]]],
    tool_schemas: Dict[str, Dict[str, Any]],
    new_tools: List[Callable],
    provider: str,
) -> tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """
    Add tools to the agent and prepare them for the provider.
    
    Args:
        tool_functions: Dictionary mapping tool names to functions.
        tools: Current tools list (can be None).
        tool_schemas: Current tool schemas dictionary.
        new_tools: List of new callable functions to add.
        provider: LLM provider name.
    
    Returns:
        Tuple of (updated_tools, updated_tool_schemas).
    """
    if not new_tools:
        return tools, tool_schemas
    
    # Add tool functions to mapping
    for tool in new_tools:
        tool_name = tool.__name__
        tool_functions[tool_name] = tool
    
    # Re-prepare all tools for current provider
    all_tools = list(tool_functions.values())
    prepared = prepare_tools_for_provider(all_tools, provider)
    
    return prepared["tools"], prepared["schemas"]


def convert_arguments_to_types(
    *,
    arguments: Dict[str, Any],
    tool_schema: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Convert function arguments to appropriate Python types based on schema.
    
    Args:
        arguments: Parsed JSON arguments dictionary.
        tool_schema: Tool schema in provider-specific format.
    
    Returns:
        Arguments dictionary with properly typed values.
    """
    properties = tool_schema.get("function", {}).get("parameters", {}).get("properties", {})
    converted = arguments.copy()
    
    for param_name, param_schema in properties.items():
        if param_name in converted:
            param_type = param_schema.get("type", "string")
            value = converted[param_name]
            
            # Coerce types if needed (JSON parsing usually handles this, but be safe)
            if param_type == "integer" and not isinstance(value, int):
                try:
                    converted[param_name] = int(value)
                except (ValueError, TypeError):
                    pass  # Keep original if conversion fails
            elif param_type == "number" and not isinstance(value, (int, float)):
                try:
                    converted[param_name] = float(value)
                except (ValueError, TypeError):
                    pass
            elif param_type == "boolean" and not isinstance(value, bool):
                if isinstance(value, str):
                    converted[param_name] = value.lower() in ("true", "1", "yes")
                else:
                    converted[param_name] = bool(value)
    
    return converted

