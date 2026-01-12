# ixagent

Agent package for building chatbot-style interactions with LLMs, tool calling, and conversation management.

## Overview

`ixagent` provides the `Agent` class - a sophisticated chatbot-style interface that:

- Maintains conversation history across multiple interactions
- Supports function calling with tools
- Manages multiple LLM instances
- Handles object references and memory
- Executes tools and processes their results
- Tracks usage and costs

## Role

`ixagent` is the **orchestration layer** - it coordinates LLMs (from `ixcore`), tools (from `ixtools`), and optionally memory systems (from `ixmemory`) to create interactive AI agents.

## Dependencies

- **ixcore**: Uses `LLM` for LLM connections, `UsageTracker` for tracking, `persist` for caching, and various utilities
- **ixtools** (optional): Can use tools from `ixtools` for agent capabilities
- **ixmemory** (optional): Can use `GraphMemory` and `SemanticMemory` for persistent memory

## What Depends on ixagent

- **ixmemory**: Uses `AgentComponent` as a base class for memory components (for consistency, though memory can work independently)
- **No other packages depend on ixagent**: It's the top-level user-facing package

## Key Components

### Agent (`ixagent.agent.core.agent`)

- `Agent`: Main agent class for chatbot-style interactions
- `BaseAgent`: Simpler base agent implementation
- `SpecialObjectKeyError`: Exception for object reference errors

### Memory (`ixagent.agent.memory`)

- `Memory`: Agent's working memory component (conversations, objects, tool call results)
- `ConversationMemory`: Conversation history and object storage
- `ObjectReferenceResolver`: Resolves object references in tool arguments

### Cognition (`ixagent.agent.cognition`)

- `Cognition`: LLM management, usage tracking, system object references
- `LLMManagement`: Helper functions for managing multiple LLMs

### Tool Management (`ixagent.agent.tool_management`)

- Tool registration and activation
- Tool execution and result processing
- Argument type conversion
- Tool schema preparation

### Execution (`ixagent.agent.execution`)

- `run_agent`: Main agent execution loop
- Tool calling iteration logic
- Return mode handling

### Specialists (`ixagent.agent.specialists`)

- `FileSystemAgent`: Pre-configured agent with file system tools
- `WebAgent`: Pre-configured agent with web tools
- `DatabaseAgent`: Pre-configured agent with database tools
- `ToolkitAgent`: Agent with custom tool sets

## Usage Example

```python
from ixcore.llm import LLM
from ixagent import Agent

# Create LLM
llm = LLM(provider="openai", model="gpt-4")

# Create agent
agent = Agent(
    llm=llm,
    system_prompt="You are a helpful assistant.",
    verbose=True
)

# Run agent
response = agent.run("What is the weather today?")
print(response)
```

## Architecture

The Agent uses a modular architecture:

- **Memory**: Manages conversations, objects, and tool call results
- **Cognition**: Manages LLMs, usage tracking, and system objects
- **Tool Management**: Handles tool registration, execution, and processing
- **Execution**: Orchestrates the conversation loop

## Installation

This package is part of the ix ecosystem. Requires `ixcore` as a dependency.

