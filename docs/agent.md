# Agent

The Agent class provides a chatbot-style interface for interacting with LLMs, with support for tools, multiple conversations, object storage, and special object references.

## Overview

The `Agent` class extends `BaseAgent` with advanced features:
- **Multiple conversation management**: Handle multiple independent conversations
- **Special object system**: Reference system objects, saved objects, and tool call results in tool arguments
- **Built-in save/load tools**: Save and retrieve objects within conversations or globally
- **Advanced type conversion**: Automatic JSON/Python literal parsing for tool arguments
- **Object reference resolution**: Use `[sys:self]`, `[obj:name]`, etc. in tool arguments

## Basic Usage

```python
from ixmachina import Agent, LLM

# Create an LLM
llm = LLM(api_key="your-key", model_name="gpt-4")

# Create an agent
agent = Agent(llm=llm, system_prompt="You are a helpful assistant.")

# Run a conversation
response = agent.run("What is the capital of France?")
print(response)  # "The capital of France is Paris."

# Continue the conversation
response = agent.run("What about Germany?")
print(response)  # "The capital of Germany is Berlin."
```

## Multiple Conversations

The Agent can manage multiple independent conversations:

```python
# Start a new conversation
agent.start_conversation(conversation_id="user1")

# Run in that conversation
agent.run("Hello", conversation_id="user1")

# Switch to another conversation
agent.start_conversation(conversation_id="user2")
agent.run("Hi there", conversation_id="user2")

# Each conversation maintains its own history
```

**Key points**:
- Each conversation has its own history
- Conversation-scoped objects are isolated per conversation
- Global objects are shared across all conversations
- Use `conversation_id` parameter in `run()` to specify which conversation

## Special Objects

Special objects allow tools to access the agent itself, LLMs, and other system-level objects without them appearing in tool signatures.

### System Objects

System objects are predefined and always available:
- `[sys:self]` - The agent instance itself
- `[sys:llm]` - The default LLM instance
- `[sys:llm:name]` - A specific LLM instance (if multiple LLMs are provided)

You can add custom system objects:

```python
# Add a custom system object
agent['my_database'] = database_connection

# Now tools can reference it: [sys:my_database]
```

### Global Saved Objects

Global objects persist across all conversations:

```python
# Save a global object
agent.run("save(name='config', value={'api_key': '123'}, global_memory=True)")

# Reference it in any conversation
agent.run("load(name='config', global_memory=True)")
```

Reference in tool arguments: `[obj:object_name]`

### Conversation-Scoped Objects

Conversation-scoped objects are isolated to a specific conversation:

```python
# Save to current conversation
agent.run("save(name='user_preferences', value={'theme': 'dark'})")

# Load from current conversation
agent.run("load(name='user_preferences')")
```

Reference in tool arguments: `[conv_obj:conversation_id:object_name]`

### Tool Call Results

Reference results from previous tool calls in the same conversation:

```python
# First tool call returns a result
agent.run("search_web(query='python tutorial')")
# Tool call ID: "call_abc123"

# Reference that result in a later tool call
# Use: [tool_obj:conversation_id:call_abc123]
```

Reference in tool arguments: `[tool_obj:conversation_id:tool_call_id]`

## Built-in Tools

The Agent automatically provides these tools:

### `save` / `memorize`

Save an object to memory:

```python
# Save to conversation-scoped memory (default)
agent.run("save(name='favorite_color', value='blue')")

# Save to global memory
agent.run("save(name='app_config', value={'version': '1.0'}, global_memory=True)")

# memorize is an alias for save
agent.run("memorize(name='user_name', value='Alice')")
```

### `load` / `remember`

Load an object from memory:

```python
# Load from conversation-scoped memory (default)
agent.run("load(name='favorite_color')")

# Load from global memory
agent.run("load(name='app_config', global_memory=True)")

# remember is an alias for load
agent.run("remember(name='user_name')")
```

### `list_objects`

List saved objects, optionally filtered by name:

```python
# List all objects in current conversation
agent.run("list_objects()")

# Fuzzy search for objects
agent.run("list_objects(name='color')")  # Finds 'favorite_color', 'background_color', etc.

# List global objects
agent.run("list_objects(global_memory=True)")
```

## Object References in Tool Arguments

Tools can reference special objects using bracket notation in their arguments:

```python
@bind(agent=my_agent)
def analyze_with_agent(data: str, agent_ref: str = "[sys:self]"):
    """
    Analyze data using the agent.
    
    Args:
        data: Data to analyze
        agent_ref: Reference to agent (default: [sys:self])
    """
    # agent_ref will be automatically resolved to the agent instance
    agent = agent_ref  # This is the actual agent object
    return agent.run(f"Analyze this: {data}")
```

**Reference formats**:
- `[sys:key]` - System objects
- `[obj:object_name]` - Global saved objects
- `[conv_obj:conversation_id:object_name]` - Conversation-scoped objects
- `[tool_obj:conversation_id:tool_call_id]` - Tool call results

**Important**: References must be wrapped in square brackets and passed as strings. The agent automatically resolves them when calling tools.

## Multiple LLMs

You can provide multiple LLMs and switch between them:

```python
# Create multiple LLMs
gpt4 = LLM(api_key=key1, model_name="gpt-4")
claude = LLM(api_key=key2, model_name="claude-3-opus")

# Create agent with multiple LLMs
agent = Agent(
    llm={"gpt4": gpt4, "claude": claude},
    default_llm="gpt4"
)

# Use default LLM
agent.run("Hello")

# Use specific LLM for a run
agent.run("Complex analysis", llm_instance="claude")

# Switch default LLM
agent.switch_default_llm("claude")
```

## Saving Objects from Tools

Tools can return objects to be saved:

```python
from ixmachina.agent import save_as

def fetch_user_data(user_id: str):
    """Fetch user data and save it."""
    data = {"id": user_id, "name": "Alice"}
    
    # Return object to save
    return save_as(name=f"user_{user_id}", value=data)
```

The agent automatically saves objects returned from tools. Use `conversation_scoped=True` (default) for conversation-scoped storage, or `conversation_scoped=False` for global storage.

## Type Conversion

The agent automatically converts tool arguments to the correct types:

```python
def process_data(count: int, enabled: bool, items: list):
    """Process data with typed parameters."""
    # Agent automatically converts:
    # - "10" → 10 (int)
    # - "true" → True (bool)
    # - "[1, 2, 3]" → [1, 2, 3] (list)
    pass
```

The agent uses JSON/Python literal parsing to convert string arguments to their expected types.

## Conversation Management

```python
# Start a new conversation
agent.start_conversation(conversation_id="chat1")

# Get conversation history
history = agent.get_conversation_history(conversation_id="chat1")

# Delete a conversation (removes history and conversation-scoped objects)
agent.forget_conversation(conversation_id="chat1")

# List all conversation IDs
conversation_ids = agent.list_conversations()
```

## Usage Tracking

The agent tracks token usage and costs:

```python
# Get usage for a specific conversation
usage = agent.get_usage(conversation_id="chat1")

# Get total usage across all conversations
total_usage = agent.get_total_usage()

# Get cost information (if pricing is configured)
cost = agent.get_total_cost()
```

## Design Decisions

### Why Special Objects?

Special objects solve the serialization problem: AI agents can only pass primitive types (strings, numbers, etc.) in tool arguments. Special objects allow tools to access complex objects (like the agent itself) without requiring them in the function signature.

### Why Multiple Conversations?

Multiple conversations enable:
- Handling multiple users simultaneously
- Isolating conversation context
- Managing conversation-scoped data separately
- Building multi-user applications

### Why Built-in Save/Load Tools?

Save/load tools enable agents to:
- Remember information across turns
- Build up knowledge over time
- Access previously computed results
- Maintain state between conversations (with global memory)

### Why Object References in Arguments?

Object references allow:
- Tools to access the agent for recursive calls
- Passing tool results to subsequent tools
- Sharing objects between tools without explicit parameters
- Building complex tool chains

