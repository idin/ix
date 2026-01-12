"""
Object saving utilities for Agent.
"""

from typing import Optional, Any, Union
from ..memory.save_objects import ObjectToSave, MultipleObjectsToSave
from ..memory.memory import Memory


def save_objects_to_agent(
    *,
    result: Union[ObjectToSave, MultipleObjectsToSave],
    memory: Memory,
    conversation_id: Optional[str],
) -> None:
    """
    Save object(s) to agent's memory storage.
    
    Args:
        result: ObjectToSave or MultipleObjectsToSave wrapper.
        memory: Memory component instance.
        conversation_id: Optional conversation ID for conversation-scoped objects.
    """
    if isinstance(result, ObjectToSave):
        _save_single_object_to_memory(
            name=result.name,
            obj=result.object,
            conversation_scoped=result.conversation_scoped,
            memory=memory,
            conversation_id=conversation_id,
        )
    elif isinstance(result, MultipleObjectsToSave):
        for object_to_save in result:
            _save_single_object_to_memory(
                name=object_to_save.name,
                obj=object_to_save.object,
                conversation_scoped=object_to_save.conversation_scoped,
                memory=memory,
                conversation_id=conversation_id,
            )


def _save_single_object_to_memory(
    *,
    name: str,
    obj: Any,
    conversation_scoped: bool,
    memory: Memory,
    conversation_id: Optional[str],
) -> None:
    """
    Save a single object to memory.
    
    Args:
        name: Name to save the object under.
        obj: The object to save.
        conversation_scoped: If True, save as conversation-scoped object.
        memory: Memory component instance.
        conversation_id: Optional conversation ID for conversation-scoped objects.
    """
    if conversation_scoped:
        if conversation_id is None:
            # This shouldn't happen in practice, but handle gracefully
            raise ValueError("conversation_id required for conversation-scoped objects")
        memory.save_conversation_object(conversation_id, name, obj)
    else:
        memory.save_global_object(name, obj)

