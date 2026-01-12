"""
Built-in tools for Agent (save, load, list_objects, memorize, remember, select_tool_result).
"""

from typing import List, Callable, Any, Optional, Union, Dict
from ...utils.fuzzy_match import fuzzy_match
from ..memory.save_objects import save_as
from ..core.exceptions import SpecialObjectKeyError


def create_built_in_tools(
    memory,
    current_conversation_id_getter: Callable[[], str],
) -> List[Callable]:
    """
    Create built-in save/load tools with aliases.
    
    Args:
        memory: Memory component instance.
        current_conversation_id_getter: Callable that returns the current conversation ID.
    
    Returns:
        List of tool functions (save, load, memorize, remember, list_objects).
    """
    def save(name: str, value: Any, global_memory: bool = False):
        """
        Save an object to conversation-scoped or global storage.
        
        Args:
            name: Name to save the object under.
            value: The object to save.
            global_memory: If True, save to global storage.
                         If False, save to conversation-scoped storage (default).
        
        Returns:
            ObjectToSave wrapper that will be processed by the agent.
        """
        return save_as(name=name, obj=value, conversation_scoped=not global_memory)
    
    def load(name: str, global_memory: bool = False) -> any:
        """
        Load an object from conversation-scoped or global storage.
        
        Use this function when the user asks a question that might require information from saved objects.
        If the user asks about something that was saved in a previous conversation, use global_memory=True.
        If you don't know the exact object name, try using a descriptive query - fuzzy matching will find similar names.
        
        Supports fuzzy matching: if exact name not found, searches for similar names.
        
        Args:
            name: Name of the object to load. Can be exact name or a descriptive query for fuzzy matching.
                 Examples: "company_name", "company name", "favorite color", "user_name"
            global_memory: If True, load from global storage (persists across all conversations).
                         If False, load from conversation-scoped storage (default, only in current conversation).
                         Use True when the user asks about something that might have been saved in a previous conversation.
        
        Returns:
            The loaded object.
        """
        if global_memory:
            # Try exact match first
            try:
                return memory.load_global_object(name)
            except KeyError:
                # Try fuzzy matching
                all_objects = memory.list_global_objects()
                matched_names = fuzzy_match(
                    query=name,
                    candidates=all_objects,
                    threshold=0.5,
                    max_results=1,
                )
                if matched_names:
                    return memory.load_global_object(matched_names[0])
                raise KeyError(f"Global object '{name}' not found")
        else:
            conversation_id = current_conversation_id_getter()
            try:
                return memory.load_conversation_object(conversation_id, name)
            except KeyError:
                # Try fuzzy matching
                all_objects = memory.list_conversation_objects(conversation_id)
                matched_names = fuzzy_match(
                    query=name,
                    candidates=all_objects,
                    threshold=0.5,
                    max_results=1,
                )
                if matched_names:
                    return memory.load_conversation_object(conversation_id, matched_names[0])
                raise KeyError(f"Conversation-scoped object '{name}' not found in conversation '{conversation_id}'")
    
    def list_objects(name: Optional[str] = None, global_memory: bool = False, max_results: Optional[int] = 20) -> List[str]:
        """
        List saved object names, optionally filtered by fuzzy name matching.
        
        Args:
            name: Optional name to fuzzy match against. If provided, returns only
                 objects whose names match the query. If None, returns all objects.
            global_memory: If True, list from global storage.
                         If False, list from conversation-scoped storage (default).
            max_results: Maximum number of results to return when name is provided.
                       Default: 20. Ignored if name is None.
        
        Returns:
            List of object names, sorted by relevance if name is provided.
        """
        if global_memory:
            all_names = memory.list_global_objects()
        else:
            conversation_id = current_conversation_id_getter()
            all_names = memory.list_conversation_objects(conversation_id)
        
        if not name:
            # Return all names, sorted alphabetically
            return sorted(all_names)
        
        # Use fuzzy matching to find relevant names
        matched_names = fuzzy_match(
            query=name,
            candidates=all_names,
            threshold=0.5,  # Lower threshold for more lenient matching
            max_results=max_results,
        )
        return matched_names
    
    def list_recent_tool_calls(max_results: Optional[int] = 10) -> List[Dict[str, Any]]:
        """
        List recent tool calls with their IDs, names, arguments, and results.
        
        Use this function to find tool_call_ids when the user asks for specific results
        (e.g., "give me the first one", "give me the circle result"). This helps you
        identify which tool_call_id corresponds to which tool call.
        
        Args:
            max_results: Maximum number of recent tool calls to return. Default: 10.
        
        Returns:
            List of dictionaries, each containing:
            - tool_call_id: The ID to use with select_tool_result()
            - tool_name: Name of the tool that was called
            - arguments: Arguments passed to the tool
            - result: The result returned by the tool
        
        Examples:
            # List recent tool calls to find IDs
            recent_calls = list_recent_tool_calls(max_results=5)
            # Returns: [
            #   {"tool_call_id": "call_xyz789", "tool_name": "calculate_circle_area", "arguments": {"radius": 5}, "result": 78.54},
            #   {"tool_call_id": "call_abc123", "tool_name": "calculate_square_area", "arguments": {"side": 4}, "result": 16}
            # ]
        """
        conversation_id = current_conversation_id_getter()
        records = memory.get_tool_call_records(conversation_id)
        
        # Return most recent first, limited by max_results
        if max_results is not None:
            # Ensure max_results is an int (handle string conversion from LLM)
            try:
                max_results_int = int(max_results)
            except (ValueError, TypeError):
                max_results_int = 10  # Default if conversion fails
            # Get last N records (most recent)
            records = records[-max_results_int:] if max_results_int > 0 else records
        else:
            records = records[:]
        
        # Return in reverse order (most recent first)
        return list(reversed(records))
    
    def select_tool_result(tool_call_id: Union[str, List[str]]) -> Union[Any, List[Any]]:
        """
        Select one or more tool call results to return.
        
        Use this function when you want to explicitly return specific tool call results
        instead of accumulating all results. This is especially useful when you've made
        multiple tool calls but only want to return specific results.
        
        Args:
            tool_call_id: Either:
                - A single tool_call_id string (e.g., "call_xyz789") to return one result
                - A list of tool_call_ids (e.g., ["call_xyz789", "call_abc123"]) to return multiple results
                IMPORTANT: You MUST use the actual tool_call_id from list_recent_tool_calls(). 
                Call list_recent_tool_calls() first to see available IDs.
        
        Returns:
            - If tool_call_id is a string: The result object from the specified tool call
            - If tool_call_id is a list: A list of result objects in the same order as the IDs
        
        Raises:
            SpecialObjectKeyError: If a tool_call_id is not found. The error will list available IDs.
        
        Examples:
            # Return single result
            select_tool_result(tool_call_id="call_xyz")
            
            # Return multiple results
            select_tool_result(tool_call_id=["call_abc123", "call_xyz789"])
        """
        conversation_id = current_conversation_id_getter()
        
        def load_with_helpful_error(tid: str) -> Any:
            """Load tool call object, raising helpful error with available IDs if not found."""
            try:
                return memory.load_tool_call_object(conversation_id, tid)
            except KeyError as e:
                available = list(memory._tool_call_objects.get(conversation_id, {}).keys())
                if not available:
                    raise SpecialObjectKeyError(
                        f"Tool call object '{tid}' not found. No tool calls have been made yet in this conversation. "
                        f"Make some tool calls first, then use list_recent_tool_calls() to see their IDs."
                    ) from e
                
                available_str = ", ".join(available[:10])
                if len(available) > 10:
                    available_str += f", ... ({len(available)} total)"
                
                raise SpecialObjectKeyError(
                    f"Tool call object '{tid}' not found in conversation '{conversation_id}'. "
                    f"Available tool call IDs: {available_str}. "
                    f"ERROR: You must call list_recent_tool_calls() first to get the actual tool_call_ids. "
                    f"Then use the real ID from that list. Do not guess or use placeholder IDs."
                ) from e
        
        if isinstance(tool_call_id, list):
            # Return list of results
            results = []
            for tid in tool_call_id:
                result = load_with_helpful_error(tid)
                results.append(result)
            return results
        else:
            # Return single result
            return load_with_helpful_error(tool_call_id)
    
    # Aliases
    memorize = save
    memorize.__name__ = 'memorize'
    remember = load
    remember.__name__ = 'remember'
    
    return [save, load, memorize, remember, list_objects, list_recent_tool_calls, select_tool_result]

