"""
Agent initialization utilities.

This module manages system prompt instruction modules. All instructions are registered
here to ensure they are systematically included and not lost.
"""

from typing import List, Dict, Optional, Callable, Any, Union
from ...llm import LLM
from ...llm.tools import prepare_tools_for_provider
from ...utils.usage_tracker import UsageTracker
from ..memory.memory import Memory
from ..memory.references import ObjectReferenceResolver
from ..tool_management.built_in_tools import create_built_in_tools

# Instruction module registry - maps name to instruction generator function
_INSTRUCTION_MODULES: Dict[str, Callable[[], str]] = {}


def _create_memory_management_instruction() -> str:
    """
    Create memory management instruction text for system prompt.
    
    Returns:
        Memory management instruction string.
    """
    return (
        "Memory Management:\n"
        "When a user asks a question that seems to require information from previous conversations "
        "or saved data, you should retrieve saved objects using the 'remember' or 'load' function. "
        "IMPORTANT: If you don't know the exact name of the saved object, use 'list_objects' first "
        "to search for relevant saved objects. Use 'list_objects' with a name parameter for fuzzy matching "
        "when searching by partial name (e.g., if user asks about 'favorite color', search with 'color' or 'favorite'). "
        "After finding the object name with 'list_objects', use 'remember' or 'load' with that exact name. "
        "Remember that objects can be saved to conversation-scoped memory (default) or global memory. "
        "Use 'list_objects' with global_memory=True to search global memory, or False (default) for conversation-scoped memory."
    )


def _create_object_references_instruction() -> str:
    """
    Create special object references instruction text for system prompt.
    
    Returns:
        Object references instruction string.
    """
    return (
        "Special Object References in Tool Arguments:\n"
        "When calling tools, you can reference previously saved objects or tool results using special syntax with angle brackets:\n"
        "- <obj:object_name> - Reference a globally saved object\n"
        "- <conv_obj:conversation_id:object_name> - Reference a conversation-scoped saved object\n"
        "- <tool_obj:conversation_id:tool_call_id> - Reference the result from a previous tool call\n"
        "- <sys:key> - Reference system objects (like 'self' or 'llm')\n"
        "IMPORTANT: These references MUST be wrapped in angle brackets <> and passed as strings to tool arguments. "
        "The system will automatically resolve them to the actual objects. For example, if a tool needs a 'data' parameter "
        "and you want to use a previous tool call result, pass it as: data='<tool_obj:default:call_abc123>' where 'call_abc123' "
        "is the tool_call_id from the previous tool call. Always use the exact format shown in tool responses when referencing tool results. "
        "We use angle brackets instead of square brackets to avoid ambiguity with JSON arrays."
    )


def _create_tool_result_selection_instruction() -> str:
    """
    Create tool result selection instruction text for system prompt.
    
    Returns:
        Tool result selection instruction string.
    """
    return (
        "Tool Result Selection:\n"
        "When the user asks for specific tool results (e.g., 'give me the first one', 'give me the circle result'), "
        "you MUST use select_tool_result() to return previous results - DO NOT recalculate by calling the tools again.\n"
        "\n"
        "CRITICAL WORKFLOW:\n"
        "1. User asks for a previous result (e.g., 'first one', 'circle result', 'result from radius 5')\n"
        "2. Call list_recent_tool_calls() to see recent tool calls with their IDs, names, arguments, and results\n"
        "3. Match the user's description to the appropriate tool call in the list\n"
        "4. Extract the tool_call_id from the matching entry\n"
        "5. Call select_tool_result(tool_call_id='<actual_id>') with the REAL ID from list_recent_tool_calls()\n"
        "\n"
        "DO NOT:\n"
        "- Use placeholder IDs like 'call_abc123' or 'call_6' - always use list_recent_tool_calls() to find actual IDs\n"
        "- Recalculate by calling the tools again - use select_tool_result() to get previous results\n"
        "- Guess tool_call_ids - always query list_recent_tool_calls() first\n"
        "\n"
        "Examples:\n"
        "1. User asks for 'the first result' after calculating circle and square:\n"
        "   - Call list_recent_tool_calls(max_results=5) to see recent calls\n"
        "   - The list is in reverse chronological order (most recent last), so the FIRST call is at index 0\n"
        "   - Extract tool_call_id from that first entry\n"
        "   - Call select_tool_result(tool_call_id='<actual_id_from_list>') with that ID\n"
        "   - DO NOT call calculate_circle_area() again - use select_tool_result()\n"
        "\n"
        "2. User asks for 'the circle result' after calculating circle and square:\n"
        "   - Call list_recent_tool_calls() to see recent calls\n"
        "   - Find the entry where tool_name='calculate_circle_area' or arguments show radius=5\n"
        "   - Extract tool_call_id from that entry\n"
        "   - Call select_tool_result(tool_call_id='<actual_id_from_list>') with that ID\n"
        "   - DO NOT call calculate_circle_area() again - use select_tool_result()\n"
        "\n"
        "3. User asks for 'result from radius 5' after calculating with radius 5 and radius 10:\n"
        "   - Call list_recent_tool_calls() to see recent calls\n"
        "   - Find the entry where arguments show radius=5 (not radius=10)\n"
        "   - Extract tool_call_id from that entry\n"
        "   - Call select_tool_result(tool_call_id='<actual_id_from_list>') with that ID\n"
        "   - DO NOT call calculate_circle_area(radius=5) again - use select_tool_result()\n"
        "\n"
        "If you don't call select_tool_result(), all tool call results will be accumulated and returned."
    )


def register_instruction(name: str, generate_func: Callable[[], str]) -> None:
    """
    Register an instruction module.
    
    Args:
        name: Unique name for the instruction module (e.g., "memory_management").
        generate_func: Function that generates the instruction text (takes no args, returns str).
    
    Raises:
        ValueError: If a module with the same name is already registered.
    """
    if name in _INSTRUCTION_MODULES:
        raise ValueError(
            f"Instruction module '{name}' is already registered. "
            f"Use unregister_instruction() first or use a different name."
        )
    _INSTRUCTION_MODULES[name] = generate_func


def unregister_instruction(name: str) -> None:
    """
    Unregister an instruction module.
    
    Args:
        name: Name of the module to unregister.
    
    Raises:
        KeyError: If the module is not registered.
    """
    if name not in _INSTRUCTION_MODULES:
        raise KeyError(f"Instruction module '{name}' is not registered.")
    del _INSTRUCTION_MODULES[name]


def list_instruction_modules() -> List[str]:
    """
    List all registered instruction module names.
    
    Returns:
        List of module names in registration order.
    """
    return list(_INSTRUCTION_MODULES.keys())


# Register default instructions when module is imported
register_instruction("memory_management", _create_memory_management_instruction)
register_instruction("object_references", _create_object_references_instruction)
register_instruction("tool_result_selection", _create_tool_result_selection_instruction)


def create_memory_guidance() -> str:
    """
    Create memory guidance text for system prompt (legacy function for backward compatibility).
    
    Returns:
        Combined memory management and object references instruction string.
    """
    return generate_instructions(["memory_management", "object_references"])


def generate_instructions(module_names: Optional[List[str]] = None) -> str:
    """
    Generate instruction text from registered modules.
    
    Args:
        module_names: Optional list of module names to include. If None, includes all.
    
    Returns:
        Combined instruction text from all specified modules, separated by double newlines.
    """
    if module_names is None:
        module_names = list(_INSTRUCTION_MODULES.keys())
    
    instructions = []
    for name in module_names:
        if name not in _INSTRUCTION_MODULES:
            raise KeyError(f"Instruction module '{name}' is not registered.")
        instruction_text = _INSTRUCTION_MODULES[name]()
        if instruction_text.strip():
            instructions.append(instruction_text)
    
    return "\n\n".join(instructions)


def enhance_system_prompt(
    system_prompt: Optional[str],
    instruction_modules: Optional[List[str]] = None,
) -> str:
    """
    Enhance system prompt with registered instruction modules.
    
    Args:
        system_prompt: Original system prompt (can be None).
        instruction_modules: Optional list of instruction module names to include.
                           If None, includes all registered modules.
    
    Returns:
        Enhanced system prompt with all specified instruction modules.
    """
    instructions = generate_instructions(module_names=instruction_modules)
    
    if system_prompt:
        return system_prompt + "\n\n" + instructions
    else:
        return instructions


def initialize_agent_components(
    *,
    agent_instance: Any,
    system_object_prefix: str,
    global_object_prefix: str,
    conversation_object_prefix: str,
    tool_call_object_prefix: str,
    default_return_mode: Optional[str],
    tools: Optional[List[Callable]],
    memory: Memory,
    current_conversation_id_getter: Callable[[], str],
    llm_provider: str,
) -> None:
    """
    Initialize and apply agent components (tools, schemas, prefixes, etc.) to agent instance.
    
    Args:
        agent_instance: Agent instance to apply components to.
        system_object_prefix: Prefix for system objects.
        global_object_prefix: Prefix for global objects.
        conversation_object_prefix: Prefix for conversation-scoped objects.
        tool_call_object_prefix: Prefix for tool call objects.
        default_return_mode: Default return mode.
        tools: Optional list of user-provided tools.
        memory: Memory component instance.
        current_conversation_id_getter: Callable that returns current conversation ID.
        llm_provider: LLM provider name.
    """
    # Normalize prefixes and return mode
    agent_instance.system_object_prefix = system_object_prefix.lower()
    agent_instance.global_object_prefix = global_object_prefix.lower()
    agent_instance.conversation_object_prefix = conversation_object_prefix.lower()
    agent_instance.tool_call_object_prefix = tool_call_object_prefix.lower()
    agent_instance.default_return_mode = default_return_mode.lower() if default_return_mode else None
    
    # Add built-in save/load tools
    built_in_tools = create_built_in_tools(
        memory=memory,
        current_conversation_id_getter=current_conversation_id_getter,
    )
    all_tools = (built_in_tools + tools) if tools else built_in_tools
    
    # Initialize tool functions and schemas
    if all_tools:
        # Build tool function mapping
        for tool in all_tools:
            tool_name = tool.__name__
            agent_instance.tool_functions[tool_name] = tool
        
        # Prepare tools for current provider
        prepared = prepare_tools_for_provider(all_tools, llm_provider)
        agent_instance.tools = prepared["tools"]
        agent_instance.tool_schemas = prepared["schemas"]
    else:
        agent_instance.tools = None
        agent_instance.tool_schemas = {}

