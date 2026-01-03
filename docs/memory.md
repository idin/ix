# Memory

The Memory system provides persistent storage for objects and facts with relationships, semantic search, and graph traversal capabilities.

## Overview

The `MemoryStore` class provides:
- **Object storage**: Store objects with metadata, descriptions, and embeddings
- **Fact-based relationships**: Create n-ary relationships between objects
- **Graph traversal**: Find related objects through relationship chains
- **Semantic search**: Search objects and facts using embeddings
- **SQLite backend**: Persistent storage with optional in-memory mode

## Basic Usage

```python
from ixmachina.memory import MemoryStore

# Create a memory store
memory = MemoryStore(database_path="memory.db")

# Save an object
memory.save_object(
    object_id="person_1",
    name="Alice",
    description="Software engineer",
    value={"age": 30, "city": "San Francisco"}
)

# Retrieve an object
alice = memory.get_object("person_1")
print(alice.name)  # "Alice"
print(alice.value)  # {"age": 30, "city": "San Francisco"}
```

## Objects

Objects are the primary storage unit. They can store any Python object (pickled):

```python
# Save an object with metadata
memory.save_object(
    object_id="project_1",
    name="Web App",
    description="A web application for task management",
    value={"status": "active", "team_size": 5},
    object_type="project",
    tags=["web", "python", "django"],
    metadata={"start_date": "2024-01-01"}
)

# Get object
project = memory.get_object("project_1")

# Update object
memory.update_object(
    object_id="project_1",
    description="A web application for task management (updated)",
    value={"status": "completed", "team_size": 5}
)

# Delete object
memory.delete_object("project_1")
```

## Facts and Relationships

Facts create relationships between objects. Facts support n-ary relationships (more than two objects):

```python
# Create a fact linking multiple objects
memory.save_fact(
    fact_id="fact_1",
    text="Alice works on Web App project",
    relationship_type="works_on",
    object_ids=["person_1", "project_1"],  # Multiple objects
    roles=["employee", "project"]  # Roles for each object
)

# Get fact
fact = memory.get_fact("fact_1")

# Find objects related to an object
related = memory.get_related_objects("person_1")
# Returns objects related to person_1 through facts

# Find facts involving an object
facts = memory.get_facts_for_object("person_1")
# Returns all facts where person_1 is involved
```

## Graph Traversal

Find objects through relationship chains:

```python
# Find objects within N degrees of separation
neighbors = memory.get_neighbors("person_1", max_depth=2)

# Find path between two objects
path = memory.find_path("person_1", "project_1")
# Returns sequence of facts connecting the objects
```

## Semantic Search

Search objects and facts using embeddings:

```python
# Search objects by description (semantic)
results = memory.search_objects(
    query="software engineer in San Francisco",
    limit=10
)
# Returns objects with similar descriptions

# Search facts by text (semantic)
results = memory.search_facts(
    query="works on project",
    limit=10
)
# Returns facts with similar text
```

## Embeddings

Embeddings are automatically generated when `auto_embed=True` (default):

```python
# Auto-embedding enabled (default)
memory = MemoryStore(database_path="memory.db", auto_embed=True)

# Embeddings generated automatically when saving
memory.save_object(
    object_id="obj_1",
    name="Test",
    description="A test object"
)
# Embedding generated automatically

# Use custom embedding generator
from ixmachina.memory import EmbeddingGenerator

custom_generator = EmbeddingGenerator()
memory = MemoryStore(
    database_path="memory.db",
    embedding_generator=custom_generator
)
```

## In-Memory Mode

Use in-memory database for testing or temporary storage:

```python
# In-memory database (not persisted)
memory = MemoryStore(database_path=None)  # or ":memory:"

# Data is lost when memory object is deleted
```

## Search and Filtering

```python
# Search objects by name (exact match)
objects = memory.search_objects_by_name("Alice")

# Get objects by type
projects = memory.get_objects_by_type("project")

# Get objects by tags
web_projects = memory.get_objects_by_tags(["web", "python"])

# List all objects
all_objects = memory.list_objects()
```

## Design Decisions

### Why SQLite?

SQLite provides:
- Persistent storage without external dependencies
- ACID transactions
- Good performance for moderate data sizes
- Easy to backup and migrate
- Optional in-memory mode for testing

### Why Facts Instead of Simple Edges?

Facts support:
- N-ary relationships (more than two objects)
- Roles for objects in relationships
- Rich metadata on relationships
- Text descriptions of relationships
- Semantic search on relationships

### Why Automatic Embeddings?

Automatic embeddings:
- Enable semantic search out of the box
- No manual embedding generation needed
- Consistent embedding model across all objects
- Better search results than keyword matching

### Why Object Types and Tags?

Object types and tags enable:
- Filtering and categorization
- Type-specific queries
- Flexible metadata organization
- Easy discovery of related objects

