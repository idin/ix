"""
Tests for ConversationMemory operations.
"""

from ixmemory.conversation_memory.conversation_memory import ConversationMemory


def test_start_conversation():
    """Test starting a new conversation."""
    memory = ConversationMemory()
    
    conv_id = memory.start_conversation()
    assert conv_id == "default"
    
    conv_id = memory.start_conversation(conversation_id="custom_id")
    assert conv_id == "custom_id"
    
    conversations = memory.list_conversations()
    assert "default" in conversations
    assert "custom_id" in conversations


def test_add_message():
    """Test adding messages to a conversation."""
    memory = ConversationMemory()
    
    memory.add_message(
        conversation_id="test",
        role="user",
        content="Hello",
    )
    
    conversation = memory.get_conversation(conversation_id="test")
    assert len(conversation) == 1
    assert conversation[0]['role'] == "user"
    assert conversation[0]['content'] == "Hello"


def test_add_message_with_tool_calls():
    """Test adding a message with tool calls."""
    memory = ConversationMemory()
    
    tool_calls = [
        {"id": "call_1", "function": "search", "arguments": '{"query": "test"}'}
    ]
    
    memory.add_message(
        conversation_id="test",
        role="assistant",
        content=None,
        tool_calls=tool_calls,
    )
    
    conversation = memory.get_conversation(conversation_id="test")
    assert len(conversation) == 1
    assert conversation[0]['role'] == "assistant"
    assert conversation[0]['tool_calls'] == tool_calls


def test_reset_conversation():
    """Test resetting a conversation."""
    memory = ConversationMemory()
    
    memory.add_message(conversation_id="test", role="user", content="Hello")
    memory.add_message(conversation_id="test", role="assistant", content="Hi")
    
    conversation = memory.get_conversation(conversation_id="test")
    assert len(conversation) == 2
    
    memory.reset_conversation(conversation_id="test")
    
    conversation = memory.get_conversation(conversation_id="test")
    assert len(conversation) == 0


def test_forget_conversation():
    """Test forgetting a conversation completely."""
    memory = ConversationMemory()
    
    memory.add_message(conversation_id="test", role="user", content="Hello")
    
    conversations = memory.list_conversations()
    assert "test" in conversations
    
    memory.forget_conversation(conversation_id="test")
    
    conversations = memory.list_conversations()
    assert "test" not in conversations


def test_save_and_load_global_object():
    """Test saving and loading global objects."""
    memory = ConversationMemory()
    
    memory.save_global_object(name="test_obj", obj={"key": "value"})
    
    obj = memory.load_global_object(name="test_obj")
    assert obj == {"key": "value"}


def test_load_global_object_not_found():
    """Test loading a global object that doesn't exist."""
    memory = ConversationMemory()
    
    try:
        memory.load_global_object(name="nonexistent")
        assert False, "Should have raised KeyError"
    except KeyError as e:
        assert "nonexistent" in str(e)


def test_list_global_objects():
    """Test listing global objects."""
    memory = ConversationMemory()
    
    memory.save_global_object(name="obj1", obj={})
    memory.save_global_object(name="obj2", obj={})
    memory.save_global_object(name="other_obj", obj={})
    
    all_objects = memory.list_global_objects()
    assert len(all_objects) == 3
    
    filtered = memory.list_global_objects(name_filter="obj")
    assert len(filtered) == 3
    
    filtered = memory.list_global_objects(name_filter="other")
    assert len(filtered) == 1
    assert filtered[0] == "other_obj"


def test_save_and_load_conversation_object():
    """Test saving and loading conversation-scoped objects."""
    memory = ConversationMemory()
    
    memory.save_conversation_object(
        conversation_id="test",
        name="conv_obj",
        obj={"data": "value"},
    )
    
    obj = memory.load_conversation_object(conversation_id="test", name="conv_obj")
    assert obj == {"data": "value"}


def test_load_conversation_object_not_found():
    """Test loading a conversation object that doesn't exist."""
    memory = ConversationMemory()
    
    try:
        memory.load_conversation_object(conversation_id="test", name="nonexistent")
        assert False, "Should have raised KeyError"
    except KeyError as e:
        assert "nonexistent" in str(e)


def test_list_conversation_objects():
    """Test listing conversation-scoped objects."""
    memory = ConversationMemory()
    
    memory.save_conversation_object(conversation_id="test", name="obj1", obj={})
    memory.save_conversation_object(conversation_id="test", name="obj2", obj={})
    
    objects = memory.list_conversation_objects(conversation_id="test")
    assert len(objects) == 2
    assert "obj1" in objects
    assert "obj2" in objects


def test_save_and_load_tool_call_object():
    """Test saving and loading tool call objects."""
    memory = ConversationMemory()
    
    memory.save_tool_call_object(
        conversation_id="test",
        tool_call_id="call_1",
        obj={"result": "success"},
    )
    
    obj = memory.load_tool_call_object(conversation_id="test", tool_call_id="call_1")
    assert obj == {"result": "success"}


def test_save_tool_call_record():
    """Test saving tool call records."""
    memory = ConversationMemory()
    
    tool_call = {
        "id": "call_1",
        "function": "search",
        "arguments": '{"query": "test"}',
    }
    
    memory.save_tool_call_record(conversation_id="test", tool_call=tool_call)
    
    records = memory.get_tool_call_records(conversation_id="test")
    assert len(records) == 1
    assert records[0] == tool_call

