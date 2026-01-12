"""
Conversation management utilities for Agent.

This module provides utility functions that work with Agent's Memory component.
The Memory type is not imported to avoid circular dependencies - functions accept
any object that implements the Memory interface (has methods like start_conversation,
add_message, etc.).
"""

from typing import List, Dict, Optional, Any


def start_conversation(
    *,
    conversation_id: Optional[str],
    current_conversation_id: str,
    memory: Any,  # Memory component (from ixagent) - not typed to avoid circular import
    system_prompt: Optional[str],
) -> str:
    """
    Start a new conversation or switch to an existing one.
    
    Args:
        conversation_id: Optional conversation ID. Uses current if not provided.
        current_conversation_id: Current conversation ID.
        memory: Memory component instance.
        system_prompt: Optional system prompt to add to conversation.
    
    Returns:
        The conversation ID that was started.
    """
    if conversation_id is None:
        conversation_id = current_conversation_id
    
    # Start conversation in memory
    memory.start_conversation(conversation_id)
    
    # Initialize conversation with system prompt if available
    if system_prompt:
        memory.add_message(conversation_id, "system", system_prompt)
    
    return conversation_id


def get_conversation(
    *,
    conversation_id: Optional[str],
    current_conversation_id: str,
    memory: Any,  # Memory component (from ixagent) - not typed to avoid circular import
) -> List[Dict[str, str]]:
    """
    Get conversation history for a given ID.
    
    Args:
        conversation_id: Optional conversation ID. Uses current if not provided.
        current_conversation_id: Current conversation ID.
        memory: Memory component instance.
    
    Returns:
        List of conversation messages.
    
    Raises:
        ValueError: If conversation doesn't exist.
    """
    if conversation_id is None:
        conversation_id = current_conversation_id
    
    try:
        return memory.get_conversation(conversation_id)
    except KeyError:
        raise ValueError(
            f"Conversation '{conversation_id}' does not exist. "
            f"Call start_conversation('{conversation_id}') first."
        )


def reset_conversation(
    *,
    conversation_id: Optional[str],
    current_conversation_id: str,
    memory: Any,  # Memory component (from ixagent) - not typed to avoid circular import
    system_prompt: Optional[str],
) -> None:
    """
    Reset a conversation, clearing all messages except system prompt.
    
    Args:
        conversation_id: Optional conversation ID. Uses current if not provided.
        current_conversation_id: Current conversation ID.
        memory: Memory component instance.
        system_prompt: Optional system prompt to re-add after reset.
    
    Raises:
        ValueError: If conversation doesn't exist.
    """
    if conversation_id is None:
        conversation_id = current_conversation_id
    
    if conversation_id not in memory.conversations:
        raise ValueError(
            f"Conversation '{conversation_id}' does not exist. "
            f"Call start_conversation('{conversation_id}') first."
        )
    
    # Reset conversation in memory
    memory.reset_conversation(conversation_id)
    
    # Re-add system prompt if available
    if system_prompt:
        memory.add_message(conversation_id, "system", system_prompt)


def forget_conversation(
    *,
    conversation_id: Optional[str],
    current_conversation_id: str,
    memory: Any,  # Memory component (from ixagent) - not typed to avoid circular import
) -> Optional[str]:
    """
    Forget a conversation completely, or all conversations if no ID provided.
    
    Note: Usage tracking and tool call tracking for deleted conversations are preserved.
    
    Args:
        conversation_id: Optional conversation ID. If None, forgets all conversations.
        current_conversation_id: Current conversation ID.
        memory: Memory component instance.
    
    Returns:
        New current conversation ID (if current was deleted, returns "default", otherwise None).
    """
    if conversation_id is None:
        # Forget all conversations
        for conv_id in list(memory.conversations.keys()):
            memory.forget_conversation(conv_id)
        return "default"  # Reset to default when all are deleted
    else:
        # Forget specific conversation
        if conversation_id in memory.conversations:
            memory.forget_conversation(conversation_id)
            # If we deleted the current conversation, reset to default
            if conversation_id == current_conversation_id:
                return "default"
        # Note: usage_records and conversation_tool_calls are NOT deleted - tracking is preserved
        return None

