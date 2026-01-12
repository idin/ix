# ixmemory

Memory systems package providing persistent storage for objects, facts, relationships, and graph-based data.

## Overview

`ixmemory` provides a unified `Memory` class that gives access to three memory systems:

- **Semantic Memory**: Object storage with metadata, embeddings, and fact-based relationships
- **Graph Memory**: Graph-based storage with nodes, edges, and path finding
- **Conversation Memory**: Conversation history, objects, and tool call management

## Role

`ixmemory` is the **persistence layer** - it provides long-term memory storage that can be used by agents or independently. It's designed to work alongside the agent's working memory (in `ixagent`) for different use cases.

## Dependencies

- **ixcore**: Uses utilities like `time` functions and database helpers
- **ixagent** (minimal): Uses `AgentComponent` as a base class for consistency (memory can work independently)

## What Depends on ixmemory

- **ixagent**: Can optionally use `GraphMemory` and `SemanticMemory` for persistent memory storage
- **No other packages depend on ixmemory**: It's an optional enhancement for agents

## Key Components

The `Memory` class provides access to three memory systems:

### Semantic Memory (`memory.semantic`)

Object storage with metadata, embeddings, and fact-based relationships.

**Features:**
- Object storage with metadata (tags, timestamps, access tracking)
- Fact-based relationships (n-ary relationships with roles)
- Semantic search using embeddings
- SQLite backend for persistence
- Support for text, number, and date object types

### Graph Memory (`memory.graph`)

Graph-based storage system with nodes, edges, and path finding.

**Features:**
- Node and edge storage
- Path finding algorithms
- Graph queries and traversal
- SQLite backend for persistence
- Can share database with semantic memory

### Conversation Memory (`memory.conversation`)

Conversation history, objects, and tool call management.

**Features:**
- Conversation history (messages)
- Global objects (shared across all conversations)
- Conversation-scoped objects (isolated per conversation)
- Tool call results and records

## Usage Example

```python
from ixmemory import Memory

# Create unified memory system
memory = Memory(database_path="memory.db")

# Use semantic memory
memory.semantic.save_object(
    name="Alice",
    description="Software engineer",
    value={"age": 30, "city": "San Francisco"}
)

# Search for similar objects
results = memory.semantic.find_similar_objects("Python developer", limit=5)

# Save a fact (relationship)
memory.semantic.save_fact(
    text="Alice works at TechCorp",
    relationship_type="works_at",
    objects=[
        {"role": "person", "object_id": "person_1"},
        {"role": "company", "object_id": "company_1"}
    ]
)

# Use graph memory
memory.graph.add_node("person_1", label="Person", properties={"name": "Alice"})
memory.graph.add_node("company_1", label="Company", properties={"name": "TechCorp"})
memory.graph.add_edge("person_1", "company_1", relationship="works_at")
path = memory.graph.find_path("person_1", "company_1")

# Use conversation memory
conversation_id = memory.conversation.start_conversation()
memory.conversation.add_message(conversation_id, role="user", content="Hello")
```

## Design Philosophy

- **Separate from Agent Memory**: `ixmemory` provides long-term persistent storage, while the agent's `Memory` component (in `ixagent`) handles working/session storage (conversations, tool call results)
- **Independent Operation**: Memory systems can be used independently or integrated with agents
- **Flexible Storage**: Supports both in-memory and persistent SQLite storage
- **Cross-Referencing**: SemanticMemory and GraphMemory can reference each other for unified queries

## Installation

This package is part of the ix ecosystem. Requires `ixcore` as a dependency.

