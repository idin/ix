"""
Object reference resolution for agent.
"""

from typing import Dict, Any, Optional
from ..core.exceptions import SpecialObjectKeyError


class ObjectReferenceResolver:
    """
    Resolves object references in tool arguments.
    
    Handles references like:
    - <sys:key> - System objects
    - <obj:name> - Global saved objects
    - <conv_obj:conversation_id:name> - Conversation-scoped objects
    - <tool_obj:conversation_id:tool_call_id> - Tool call results
    
    Note: We use angle brackets <prefix:content> instead of square brackets [prefix:content]
    to avoid ambiguity with JSON arrays. Angle brackets are never valid JSON syntax,
    making them unambiguous and easy to detect.
    """
    
    def __init__(
        self,
        memory,  # Memory component
        system_objects: Dict[str, Any],  # System objects dict
        system_object_prefix: str = "sys:",
        global_object_prefix: str = "obj:",
        conversation_object_prefix: str = "conv_obj:",
        tool_call_object_prefix: str = "tool_obj:",
    ):
        """
        Initialize resolver.
        
        Args:
            memory: Memory component instance.
            system_objects: Dictionary of system objects.
            system_object_prefix: Prefix for system objects.
            global_object_prefix: Prefix for global objects.
            conversation_object_prefix: Prefix for conversation-scoped objects.
            tool_call_object_prefix: Prefix for tool call objects.
        """
        self.memory = memory
        self.system_objects = system_objects
        self.system_object_prefix = system_object_prefix.lower()
        self.global_object_prefix = global_object_prefix.lower()
        self.conversation_object_prefix = conversation_object_prefix.lower()
        self.tool_call_object_prefix = tool_call_object_prefix.lower()
    
    def extract_content_after_prefix(self, value: str, prefix: str) -> Optional[str]:
        """
        Extract content after a prefix in a reference string.
        
        Args:
            value: The reference string (e.g., "<sys:self>").
            prefix: The prefix to look for (e.g., "sys:").
        
        Returns:
            The content after the prefix, or None if not found.
            Note: Returns the original case of the content (not lowercased) to preserve
            case-sensitive identifiers like tool_call_ids.
        """
        if not isinstance(value, str):
            return None
        
        value_stripped = value.strip()
        prefix_lower = prefix.lower()
        
        # Check if value matches pattern <prefix...> (angle brackets for unambiguous signature)
        if value_stripped.lower().startswith("<") and value_stripped.lower().endswith(">"):
            # Extract content with original case preserved
            content = value_stripped[1:-1].strip()
            # Check prefix case-insensitively
            if content.lower().startswith(prefix_lower):
                # Return content after prefix with original case preserved
                return content[len(prefix_lower):].strip()
        
        return None
    
    def resolve_system_object_reference(self, content: str, original_value: str) -> Any:
        """Resolve <sys:key> reference."""
        # System object keys are case-insensitive
        content_lower = content.lower()
        for key, value in self.system_objects.items():
            if key.lower() == content_lower:
                return value
        
        available = ", ".join(self.system_objects.keys())
        raise SpecialObjectKeyError(
            f"System object '{content}' not found. Available system objects: {available}"
        )
    
    def resolve_tool_call_result_reference(
        self,
        content: str,
        original_value: str,
        conversation_id: str,
    ) -> Any:
        """Resolve <tool_obj:conversation_id:tool_call_id> reference."""
        parts = content.split(":", 1)
        if len(parts) != 2:
            raise SpecialObjectKeyError(
                f"Invalid tool call object reference format: {original_value}. "
                f"Expected format: <tool_obj:conversation_id:tool_call_id>"
            )
        
        ref_conversation_id, tool_call_id = parts
        
        # Use conversation_id from reference if provided, otherwise use current
        if ref_conversation_id:
            conversation_id = ref_conversation_id
        
        try:
            return self.memory.load_tool_call_object(conversation_id, tool_call_id)
        except KeyError as e:
            available = list(self.memory._tool_call_objects.get(conversation_id, {}).keys())
            available_str = ", ".join(available[:10])  # Show first 10
            if len(available) > 10:
                available_str += f", ... ({len(available)} total)"
            raise SpecialObjectKeyError(
                f"Tool call object '{tool_call_id}' not found in conversation '{conversation_id}'. "
                f"Available tool call IDs: {available_str}"
            ) from e
    
    def resolve_conversation_scoped_saved_object_reference(
        self,
        content: str,
        original_value: str,
        conversation_id: str,
    ) -> Any:
        """Resolve <conv_obj:conversation_id:object_name> reference."""
        parts = content.split(":", 1)
        if len(parts) != 2:
            raise SpecialObjectKeyError(
                f"Invalid conversation-scoped object reference format: {original_value}. "
                f"Expected format: <conv_obj:conversation_id:object_name>"
            )
        
        ref_conversation_id, object_name = parts
        
        # Use conversation_id from reference if provided, otherwise use current
        if ref_conversation_id:
            conversation_id = ref_conversation_id
        
        try:
            return self.memory.load_conversation_object(conversation_id, object_name)
        except KeyError as e:
            available = self.memory.list_conversation_objects(conversation_id)
            available_str = ", ".join(available[:10])  # Show first 10
            if len(available) > 10:
                available_str += f", ... ({len(available)} total)"
            raise SpecialObjectKeyError(
                f"Conversation-scoped object '{object_name}' not found in conversation '{conversation_id}'. "
                f"Available objects: {available_str}"
            ) from e
    
    def resolve_global_saved_object_reference(self, content: str, original_value: str) -> Any:
        """Resolve <obj:object_name> reference."""
        try:
            return self.memory.load_global_object(content)
        except KeyError as e:
            available = self.memory.list_global_objects()
            available_str = ", ".join(available[:10])  # Show first 10
            if len(available) > 10:
                available_str += f", ... ({len(available)} total)"
            raise SpecialObjectKeyError(
                f"Global object '{content}' not found. Available objects: {available_str}"
            ) from e
    
    def resolve_references_in_arguments(
        self,
        arguments: Dict[str, Any],
        conversation_id: str,
    ) -> Dict[str, Any]:
        """
        Resolve all object references in tool arguments.
        
        Args:
            arguments: Dictionary of tool arguments (may contain reference strings).
            conversation_id: Current conversation ID.
        
        Returns:
            Dictionary with references resolved to actual objects.
        """
        resolved = {}
        
        for key, value in arguments.items():
            if isinstance(value, str):
                # Check for system object reference
                content = self.extract_content_after_prefix(value, self.system_object_prefix)
                if content is not None:
                    resolved[key] = self.resolve_system_object_reference(content, value)
                    continue
                
                # Check for tool call result reference
                content = self.extract_content_after_prefix(value, self.tool_call_object_prefix)
                if content is not None:
                    resolved[key] = self.resolve_tool_call_result_reference(
                        content, value, conversation_id
                    )
                    continue
                
                # Check for conversation-scoped saved object reference
                content = self.extract_content_after_prefix(value, self.conversation_object_prefix)
                if content is not None:
                    resolved[key] = self.resolve_conversation_scoped_saved_object_reference(
                        content, value, conversation_id
                    )
                    continue
                
                # Check for global saved object reference
                content = self.extract_content_after_prefix(value, self.global_object_prefix)
                if content is not None:
                    resolved[key] = self.resolve_global_saved_object_reference(content, value)
                    continue
            
            # Recursively process nested dictionaries and lists
            elif isinstance(value, dict):
                resolved[key] = self.resolve_references_in_arguments(value, conversation_id)
            elif isinstance(value, list):
                resolved[key] = [
                    self.resolve_references_in_arguments({"item": item}, conversation_id)["item"]
                    if isinstance(item, (dict, str))
                    else item
                    for item in value
                ]
            
            # No reference found, keep original value
            if key not in resolved:
                resolved[key] = value
        
        return resolved

