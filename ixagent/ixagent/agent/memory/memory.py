"""
Memory component for agent - composed of conversation, graph, and semantic memory.
"""

from typing import Optional

from .conversation_memory import ConversationMemory
from ...graph_memory import GraphMemory
from ...semantic_memory import SemanticMemory
from ..core.component import AgentComponent


class Memory(AgentComponent):
    """
    Memory component for agent - composed of three parts:
    
    - ConversationMemory: Conversations, objects, tool call results
    - GraphMemory: Graph-based storage for nodes and edges
    - SemanticMemory: Semantic storage for objects and facts with relationships
    """
    
    def __init__(
        self,
        system_object_prefix: str = "sys:",
        global_object_prefix: str = "obj:",
        conversation_object_prefix: str = "conv_obj:",
        tool_call_object_prefix: str = "tool_obj:",
        graph_memory_database_path: Optional[str] = None,
        semantic_memory_database_path: Optional[str] = None,
        semantic_memory_auto_embed: bool = True,
        semantic_memory_embedding_generator=None,
    ):
        """
        Initialize Memory component with all three parts.
        
        Args:
            system_object_prefix: Prefix for system object references.
            global_object_prefix: Prefix for global saved object references.
            conversation_object_prefix: Prefix for conversation-scoped object references.
            tool_call_object_prefix: Prefix for tool call result references.
            graph_memory_database_path: Optional database path for GraphMemory.
            semantic_memory_database_path: Optional database path for SemanticMemory.
            semantic_memory_auto_embed: Whether to auto-generate embeddings for SemanticMemory.
            semantic_memory_embedding_generator: Optional embedding generator for SemanticMemory.
        """
        super().__init__()
        
        # Conversation memory (conversations, objects, tool calls)
        self.conversation = ConversationMemory(
            system_object_prefix=system_object_prefix,
            global_object_prefix=global_object_prefix,
            conversation_object_prefix=conversation_object_prefix,
            tool_call_object_prefix=tool_call_object_prefix,
        )
        
        # Graph memory (nodes and edges)
        self.graph = GraphMemory(
            database_path=graph_memory_database_path,
        )
        
        # Semantic memory (objects and facts with relationships)
        self.semantic = SemanticMemory(
            database_path=semantic_memory_database_path,
            auto_embed=semantic_memory_auto_embed,
            embedding_generator=semantic_memory_embedding_generator,
        )
        
        # Store prefixes for backward compatibility
        self.system_object_prefix = system_object_prefix.lower()
        self.global_object_prefix = global_object_prefix.lower()
        self.conversation_object_prefix = conversation_object_prefix.lower()
        self.tool_call_object_prefix = tool_call_object_prefix.lower()
    
    # Delegate conversation memory methods for backward compatibility
    @property
    def conversations(self):
        """Get conversations dictionary."""
        return self.conversation.conversations
    
    @property
    def conversation_tool_calls(self):
        """Get conversation tool calls dictionary."""
        return self.conversation.conversation_tool_calls
    
    def start_conversation(self, conversation_id=None):
        """Start a new conversation."""
        return self.conversation.start_conversation(conversation_id)
    
    def get_conversation(self, conversation_id):
        """Get conversation history."""
        return self.conversation.get_conversation(conversation_id)
    
    def add_message(self, conversation_id, role, content=None, tool_calls=None, tool_call_id=None):
        """Add a message to conversation history."""
        return self.conversation.add_message(conversation_id, role, content, tool_calls, tool_call_id)
    
    def reset_conversation(self, conversation_id):
        """Reset a conversation."""
        return self.conversation.reset_conversation(conversation_id)
    
    def forget_conversation(self, conversation_id):
        """Forget a conversation."""
        return self.conversation.forget_conversation(conversation_id)
    
    def list_conversations(self):
        """List all conversation IDs."""
        return self.conversation.list_conversations()
    
    def save_global_object(self, name, obj):
        """Save an object to global storage."""
        return self.conversation.save_global_object(name, obj)
    
    def load_global_object(self, name):
        """Load an object from global storage."""
        return self.conversation.load_global_object(name)
    
    def list_global_objects(self, name_filter=None):
        """List global objects."""
        return self.conversation.list_global_objects(name_filter)
    
    def save_conversation_object(self, conversation_id, name, obj):
        """Save an object to conversation-scoped storage."""
        return self.conversation.save_conversation_object(conversation_id, name, obj)
    
    def load_conversation_object(self, conversation_id, name):
        """Load an object from conversation-scoped storage."""
        return self.conversation.load_conversation_object(conversation_id, name)
    
    def list_conversation_objects(self, conversation_id, name_filter=None):
        """List conversation-scoped objects."""
        return self.conversation.list_conversation_objects(conversation_id, name_filter)
    
    def save_tool_call_object(self, conversation_id, tool_call_id, obj):
        """Save a tool call result object."""
        return self.conversation.save_tool_call_object(conversation_id, tool_call_id, obj)
    
    def load_tool_call_object(self, conversation_id, tool_call_id):
        """Load a tool call result object."""
        return self.conversation.load_tool_call_object(conversation_id, tool_call_id)
    
    def save_tool_call_record(self, conversation_id, tool_call):
        """Save a tool call record."""
        return self.conversation.save_tool_call_record(conversation_id, tool_call)
    
    def get_tool_call_records(self, conversation_id):
        """Get tool call records for a conversation."""
        return self.conversation.get_tool_call_records(conversation_id)
    
    # Expose private attributes for backward compatibility
    @property
    def _global_objects(self):
        """Get global objects dictionary."""
        return self.conversation._global_objects
    
    @property
    def _conversation_objects(self):
        """Get conversation objects dictionary."""
        return self.conversation._conversation_objects
    
    @property
    def _tool_call_objects(self):
        """Get tool call objects dictionary."""
        return self.conversation._tool_call_objects
