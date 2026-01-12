"""
Conversation memory for managing conversations, objects, and tool calls.
"""

from typing import Dict, List, Optional, Any


class ConversationMemory:
    """
    Memory component for managing conversations, objects, and tool calls.
    
    Handles:
    - Conversation history (messages)
    - Global objects (shared across all conversations)
    - Conversation-scoped objects (isolated per conversation)
    - Tool call results (referenced by tool call ID)
    - Tool call records (tracking tool calls per conversation)
    
    Args:
        system_object_prefix: Prefix for system object references.
        global_object_prefix: Prefix for global saved object references.
        conversation_object_prefix: Prefix for conversation-scoped object references.
        tool_call_object_prefix: Prefix for tool call result references.
    """
    
    def __init__(
        self,
        system_object_prefix: str = "sys:",
        global_object_prefix: str = "obj:",
        conversation_object_prefix: str = "conv_obj:",
        tool_call_object_prefix: str = "tool_obj:",
    ):
        # Store prefixes
        self.system_object_prefix = system_object_prefix.lower()
        self.global_object_prefix = global_object_prefix.lower()
        self.conversation_object_prefix = conversation_object_prefix.lower()
        self.tool_call_object_prefix = tool_call_object_prefix.lower()
        
        # Conversation history: {conversation_id: [messages]}
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
        
        # Global objects: {name: obj}
        self._global_objects: Dict[str, Any] = {}
        
        # Conversation-scoped objects: {conversation_id: {name: obj}}
        self._conversation_objects: Dict[str, Dict[str, Any]] = {}
        
        # Tool call result objects: {conversation_id: {tool_call_id: obj}}
        self._tool_call_objects: Dict[str, Dict[str, Any]] = {}
        
        # Tool call records: {conversation_id: [tool_calls]}
        self.conversation_tool_calls: Dict[str, List[Dict[str, Any]]] = {}
    
    def start_conversation(self, conversation_id: Optional[str] = None) -> str:
        """
        Start a new conversation or return existing one.
        
        Args:
            conversation_id: Optional conversation ID. If None, uses "default".
        
        Returns:
            The conversation ID.
        """
        if conversation_id is None:
            conversation_id = "default"
        
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
            self._conversation_objects[conversation_id] = {}
            self._tool_call_objects[conversation_id] = {}
            self.conversation_tool_calls[conversation_id] = []
        
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation history.
        
        Args:
            conversation_id: Conversation ID.
        
        Returns:
            List of conversation messages.
        
        Raises:
            KeyError: If conversation doesn't exist.
        """
        if conversation_id not in self.conversations:
            raise KeyError(f"Conversation '{conversation_id}' does not exist")
        return self.conversations[conversation_id]
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: Optional[str] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        tool_call_id: Optional[str] = None,
    ) -> None:
        """
        Add a message to conversation history.
        
        Args:
            conversation_id: Conversation ID.
            role: Message role (system, user, assistant, tool).
            content: Message content.
            tool_calls: Optional tool calls (for assistant messages).
            tool_call_id: Optional tool call ID (for tool messages).
        """
        if conversation_id not in self.conversations:
            self.start_conversation(conversation_id)
        
        message: Dict[str, Any] = {"role": role}
        if content is not None:
            message["content"] = content
        if tool_calls is not None:
            message["tool_calls"] = tool_calls
        if tool_call_id is not None:
            message["tool_call_id"] = tool_call_id
        
        self.conversations[conversation_id].append(message)
    
    def reset_conversation(self, conversation_id: str) -> None:
        """
        Reset a conversation, clearing all messages.
        
        Args:
            conversation_id: Conversation ID.
        """
        if conversation_id in self.conversations:
            self.conversations[conversation_id] = []
    
    def forget_conversation(self, conversation_id: str) -> None:
        """
        Forget a conversation completely.
        
        Args:
            conversation_id: Conversation ID.
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
        if conversation_id in self._conversation_objects:
            del self._conversation_objects[conversation_id]
        if conversation_id in self._tool_call_objects:
            del self._tool_call_objects[conversation_id]
        if conversation_id in self.conversation_tool_calls:
            del self.conversation_tool_calls[conversation_id]
    
    def list_conversations(self) -> List[str]:
        """
        List all conversation IDs.
        
        Returns:
            List of conversation IDs.
        """
        return list(self.conversations.keys())
    
    # Global objects
    def save_global_object(self, name: str, obj: Any) -> None:
        """
        Save an object to global storage.
        
        Args:
            name: Object name.
            obj: Object to save.
        """
        self._global_objects[name] = obj
    
    def load_global_object(self, name: str) -> Any:
        """
        Load an object from global storage.
        
        Args:
            name: Object name.
        
        Returns:
            The saved object.
        
        Raises:
            KeyError: If object doesn't exist.
        """
        if name not in self._global_objects:
            raise KeyError(f"Global object '{name}' does not exist")
        return self._global_objects[name]
    
    def list_global_objects(self, name_filter: Optional[str] = None) -> List[str]:
        """
        List global objects.
        
        Args:
            name_filter: Optional filter to match object names (fuzzy matching).
        
        Returns:
            List of object names.
        """
        if name_filter is None:
            return list(self._global_objects.keys())
        
        # Simple fuzzy matching - contains check
        name_filter_lower = name_filter.lower()
        return [
            name for name in self._global_objects.keys()
            if name_filter_lower in name.lower()
        ]
    
    # Conversation-scoped objects
    def save_conversation_object(
        self,
        conversation_id: str,
        name: str,
        obj: Any,
    ) -> None:
        """
        Save an object to conversation-scoped storage.
        
        Args:
            conversation_id: Conversation ID.
            name: Object name.
            obj: Object to save.
        """
        if conversation_id not in self._conversation_objects:
            self._conversation_objects[conversation_id] = {}
        self._conversation_objects[conversation_id][name] = obj
    
    def load_conversation_object(self, conversation_id: str, name: str) -> Any:
        """
        Load an object from conversation-scoped storage.
        
        Args:
            conversation_id: Conversation ID.
            name: Object name.
        
        Returns:
            The saved object.
        
        Raises:
            KeyError: If object doesn't exist.
        """
        if (
            conversation_id not in self._conversation_objects
            or name not in self._conversation_objects[conversation_id]
        ):
            raise KeyError(
                f"Conversation object '{name}' does not exist in conversation '{conversation_id}'"
            )
        return self._conversation_objects[conversation_id][name]
    
    def list_conversation_objects(
        self,
        conversation_id: str,
        name_filter: Optional[str] = None,
    ) -> List[str]:
        """
        List conversation-scoped objects.
        
        Args:
            conversation_id: Conversation ID.
            name_filter: Optional filter to match object names (fuzzy matching).
        
        Returns:
            List of object names.
        """
        if conversation_id not in self._conversation_objects:
            return []
        
        objects = list(self._conversation_objects[conversation_id].keys())
        
        if name_filter is None:
            return objects
        
        # Simple fuzzy matching - contains check
        name_filter_lower = name_filter.lower()
        return [
            name for name in objects
            if name_filter_lower in name.lower()
        ]
    
    # Tool call objects
    def save_tool_call_object(
        self,
        conversation_id: str,
        tool_call_id: str,
        obj: Any,
    ) -> None:
        """
        Save a tool call result object.
        
        Args:
            conversation_id: Conversation ID.
            tool_call_id: Tool call ID.
            obj: Object to save.
        """
        if conversation_id not in self._tool_call_objects:
            self._tool_call_objects[conversation_id] = {}
        self._tool_call_objects[conversation_id][tool_call_id] = obj
    
    def load_tool_call_object(self, conversation_id: str, tool_call_id: str) -> Any:
        """
        Load a tool call result object.
        
        Args:
            conversation_id: Conversation ID.
            tool_call_id: Tool call ID.
        
        Returns:
            The saved object.
        
        Raises:
            KeyError: If object doesn't exist.
        """
        if (
            conversation_id not in self._tool_call_objects
            or tool_call_id not in self._tool_call_objects[conversation_id]
        ):
            raise KeyError(
                f"Tool call object '{tool_call_id}' does not exist in conversation '{conversation_id}'"
            )
        return self._tool_call_objects[conversation_id][tool_call_id]
    
    # Tool call records
    def save_tool_call_record(
        self,
        conversation_id: str,
        tool_call: Dict[str, Any],
    ) -> None:
        """
        Save a tool call record.
        
        Args:
            conversation_id: Conversation ID.
            tool_call: Tool call dictionary.
        """
        if conversation_id not in self.conversation_tool_calls:
            self.conversation_tool_calls[conversation_id] = []
        self.conversation_tool_calls[conversation_id].append(tool_call)
    
    def get_tool_call_records(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get tool call records for a conversation.
        
        Args:
            conversation_id: Conversation ID.
        
        Returns:
            List of tool call records.
        """
        if conversation_id not in self.conversation_tool_calls:
            return []
        return self.conversation_tool_calls[conversation_id]

