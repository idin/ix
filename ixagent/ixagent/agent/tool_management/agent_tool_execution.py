"""
Agent-specific tool execution methods.
"""

from typing import Dict, Any, Optional, Callable
import inspect
from functools import partial
import json

from ...utils.json_parser import parse_json_or_python_literal
from .tool_management import convert_arguments_to_types as base_convert_arguments_to_types
from ..memory.save_objects import save_objects_if_they_need_to_be_saved
from ..memory.references import ObjectReferenceResolver
from ..core.exceptions import SpecialObjectKeyError
from ..utils.verbose import print_tool_result


def execute_tool(
    *,
    tool_name: str,
    arguments: Dict[str, Any],
    tool_functions: Dict[str, Callable],
    reference_resolver: ObjectReferenceResolver,
    memory,
    current_conversation_id: str,
    file_system_memory: Optional[Any] = None,
    return_raw: bool = False,
    conversation_id: Optional[str] = None,
) -> Any:
    """
    Execute a tool function with given arguments.
    
    Args:
        tool_name: Name of the tool to execute.
        arguments: Arguments to pass to the tool.
        tool_functions: Dictionary of tool functions.
        reference_resolver: ObjectReferenceResolver instance.
        memory: Memory component instance.
        current_conversation_id: Current conversation ID.
        file_system_memory: Optional file system memory to inject.
        return_raw: If True, return raw result; if False, return as string.
        conversation_id: ID of the conversation (for conversation-scoped saved objects).
    
    Returns:
        Tool execution result as a string (default) or raw result.
    """
    if tool_name not in tool_functions:
        error_msg = f"Error: Tool '{tool_name}' not found"
        return error_msg
    
    try:
        func = tool_functions[tool_name]
        # Resolve special object references
        arguments = reference_resolver.resolve_references_in_arguments(
            arguments, current_conversation_id
        )
        # Automatically inject file_system_memory if the tool accepts it and it's not provided
        arguments = inject_file_system_memory(
            func=func,
            arguments=arguments,
            file_system_memory=file_system_memory,
        )
        result = func(**arguments)
        # Save objects if they need to be saved
        result = save_objects_if_they_need_to_be_saved_wrapper(
            result_of_function_call=result,
            memory=memory,
            conversation_id=conversation_id,
        )
        return result if return_raw else str(result)
    except SpecialObjectKeyError as e:
        # Convert SpecialObjectKeyError to error message string so LLM can see it and retry
        # This allows the LLM to see the error with available IDs and retry with correct ID
        error_msg = f"Error: {str(e)}"
        return error_msg  # Always return as string so LLM can see the error message
    except Exception as e:
        return f"Error executing tool: {str(e)}"


def inject_file_system_memory(
    func: Callable,
    arguments: Dict[str, Any],
    file_system_memory: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Automatically inject file_system_memory into tool arguments if the tool accepts it.
    
    Args:
        func: The tool function (can be a functools.partial object).
        arguments: Dictionary of tool arguments.
        file_system_memory: Optional file system memory to inject.
    
    Returns:
        Dictionary with file_system_memory injected if needed.
    """
    if file_system_memory is None:
        return arguments
    
    # Handle functools.partial objects - get signature from underlying function
    if isinstance(func, partial):
        underlying_func = func.func
        sig = inspect.signature(underlying_func)
        # Check if file_system_memory is already bound in the partial
        if func.keywords and 'file_system_memory' in func.keywords:
            # Already bound, don't inject and remove from arguments if present
            arguments.pop('file_system_memory', None)
            return arguments
    else:
        sig = inspect.signature(func)
    
    # Check if function has file_system_memory parameter
    if 'file_system_memory' in sig.parameters:
        # Only inject if not already provided or is None
        if 'file_system_memory' not in arguments or arguments.get('file_system_memory') is None:
            arguments['file_system_memory'] = file_system_memory
    
    return arguments


def save_objects_if_they_need_to_be_saved_wrapper(
    result_of_function_call: Any,
    memory,
    conversation_id: Optional[str] = None,
) -> Any:
    """
    Save objects if they need to be saved (wrapper for save_objects_if_they_need_to_be_saved).
    
    Args:
        result_of_function_call: The result of the function call.
        memory: Memory component instance.
        conversation_id: ID of the conversation (for conversation-scoped saved objects).
    
    Returns:
        The processed result of the function call (with ObjectToSave instances replaced).
    """
    conversation_saved_objects = None
    if conversation_id is not None:
        # Get conversation objects dict (create if needed)
        if conversation_id not in memory._conversation_objects:
            memory._conversation_objects[conversation_id] = {}
        conversation_saved_objects = memory._conversation_objects[conversation_id]
    
    return save_objects_if_they_need_to_be_saved(
        result_of_function_call=result_of_function_call,
        saved_objects=memory._global_objects,
        conversation_saved_objects=conversation_saved_objects,
        conversation_id=conversation_id,
    )


def convert_arguments_to_types(
    arguments: Dict[str, Any],
    tool_schema: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Convert function arguments to appropriate Python types based on schema.
    
    Extends BaseAgent's implementation with JSON/Python literal parsing.

    Args:
        arguments: Parsed JSON arguments dictionary.
        tool_schema: Tool schema in provider-specific format.

    Returns:
        Arguments dictionary with properly typed values.
    """
    # Start with base conversion
    converted = base_convert_arguments_to_types(
        arguments=arguments,
        tool_schema=tool_schema,
    )
    
    properties = tool_schema.get("function", {}).get("parameters", {}).get("properties", {})
    
    for param_name, param_schema in properties.items():
        if param_name in converted:
            param_type = param_schema.get("type", "string")
            value = converted[param_name]
            
            # Advanced: If schema says "string" but value looks like JSON or Python literal, try to parse it
            # This handles cases where the type annotation is unknown (like "any")
            # and the LLM passes complex objects as JSON strings or Python literals
            if param_type == "string" and isinstance(value, str):
                parsed = parse_json_or_python_literal(value)
                if parsed != value:  # Only replace if parsing succeeded
                    converted[param_name] = parsed
    
    return converted


def process_tool_call(
    *,
    tool_call: Dict[str, Any],
    tool_schemas: Dict[str, Dict[str, Any]],
    tool_functions: Dict[str, Callable],
    reference_resolver: ObjectReferenceResolver,
    memory,
    current_conversation_id: str,
    file_system_memory: Optional[Any] = None,
    verbose: bool = False,
    convert_arguments_to_types_func: Callable,
) -> Any:
    """
    Process a single tool call: extract, parse, convert types, execute, and track.
    
    Args:
        tool_call: The tool call dictionary from the LLM response.
        tool_schemas: Dictionary of tool schemas for type conversion.
        tool_functions: Dictionary of tool functions.
        reference_resolver: ObjectReferenceResolver instance.
        memory: Memory component instance.
        current_conversation_id: Current conversation ID.
        file_system_memory: Optional file system memory to inject.
        verbose: Whether to print verbose output.
        convert_arguments_to_types_func: Function to convert arguments to types.
    
    Returns:
        Raw result from the tool execution.
    """
    conversation_id = current_conversation_id
    
    function_name = tool_call["function"]["name"]
    arguments_json = tool_call["function"]["arguments"]
    
    # Parse JSON string to get arguments using robust parser
    # The parser handles malformed JSON including unquoted special object references
    function_args = parse_json_or_python_literal(arguments_json)
    if isinstance(function_args, str):
        # If it's still a string, try json.loads as fallback (for proper JSON)
        try:
            function_args = json.loads(function_args)
        except (json.JSONDecodeError, ValueError):
            # If that also fails, it's not valid JSON or Python literal
            raise ValueError(f"Invalid JSON in tool arguments: {arguments_json}")
    
    # Convert types based on schema if available
    if function_name in tool_schemas:
        function_args = convert_arguments_to_types_func(
            arguments=function_args,
            tool_schema=tool_schemas[function_name],
        )
    
    # Execute the function - get raw result for tracking, string for conversation
    raw_result = execute_tool(
        tool_name=function_name,
        arguments=function_args,
        tool_functions=tool_functions,
        reference_resolver=reference_resolver,
        memory=memory,
        current_conversation_id=current_conversation_id,
        file_system_memory=file_system_memory,
        return_raw=True,
        conversation_id=conversation_id,
    )
    string_result = str(raw_result)
    
    if verbose:
        print_tool_result(tool_name=function_name, result=raw_result)
    
    # Store tool result in conversation objects for later reference
    memory.save_tool_call_object(conversation_id, tool_call["id"], raw_result)
    
    # Track tool call with raw result
    memory.save_tool_call_record(conversation_id, {
        "tool_name": function_name,
        "arguments": function_args,
        "result": raw_result,
        "tool_call_id": tool_call["id"],
    })
    
    # Add tool response with matching tool_call_id (as string for LLM)
    memory.add_message(
        conversation_id,
        "tool",
        string_result,
        tool_call_id=tool_call["id"],
    )
    
    return raw_result

