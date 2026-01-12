# ixutils

Shared utilities package providing common utilities used across the ix ecosystem.

## Overview

`ixutils` provides shared utilities that are used by multiple packages in the ix ecosystem:

- **persist**: Caching decorator for function results
- **time**: Time utilities (UTC timestamps, ISO parsing, etc.)
- **database**: SQLite database connection helpers
- **env_var**: Environment variable handling for credentials
- **usage_tracker**: Usage and cost tracking for LLMs and agents
- **json_parser**: JSON and Python literal parsing utilities
- **fuzzy_match**: String fuzzy matching utilities
- **file_system**: File system utilities (path checking, reading, writing, listing, trash)

## Role

`ixutils` is the **utilities foundation** - it has no dependencies and provides common functionality that other packages need.

## Dependencies

- **No dependencies**: `ixutils` is a pure utilities package with no external dependencies

## Using ixutils in Your Package

### Adding as a Dependency

1. Add to your `pyproject.toml`:
```toml
[project]
dependencies = [
    "ixutils>=0.1.0",
]
```

2. Import and use in your code:
```python
from ixutils import persist, set_cache_path, utc_now_iso

# Your code here
```

### Example: Using in Another Package

```python
# In your package's __init__.py or module
from ixutils import persist, set_cache_path
from ixutils import utc_now_iso, current_timestamp

# Set cache path for your package
set_cache_path(".cache/your_package_name")

@persist(expire_seconds=3600)
def your_cached_function(arg1, arg2):
    # Your implementation
    return result
```

## What Depends on ixutils

- **ixcore**: Uses `persist` for LLM caching and `time` utilities
- **ixagent**: Uses `persist` for cache path management
- **ixmemory**: Uses `time` utilities and `database` helpers
- **ixtools**: Uses `persist` for caching and `time` utilities

## Key Components

### Persist (`ixutils.persist`)

Caching decorator for function results with memory and disk caching support.

**Top-level exports (from `ixutils`):**
- `persist`: Decorator for caching function results
- `set_cache_path`: Set the global cache directory
- `get_cache_path`: Get the current cache directory

**Lower-level exports (from `ixutils.persist`):**
- `hash_data`: Hash arbitrary data structures
- `hash_arguments`: Hash function arguments for cache keys
- `resolve_cache_file_path`: Resolve cache file path from parameters
- `get_from_disk_cache`: Read from disk cache
- `set_to_disk_cache`: Write to disk cache
- `get_from_memory_cache`: Read from memory cache
- `set_to_memory_cache`: Write to memory cache
- `DEFAULT_CACHE_PATH`: Default cache path constant
- `_CACHE_MISS`: Sentinel object for cache misses

**Features:**
- Memory and disk caching
- Expiration support
- Automatic cache invalidation
- Configurable cache paths
- Cache management methods: `.delete()`, `.exists()`, and `.clear_all()`

**Basic Usage:**
```python
from ixutils import persist, set_cache_path, get_cache_path

# Set global cache path
set_cache_path(".cache/my_app")

# Basic disk caching
@persist()
def expensive_function(x: int) -> int:
    # Expensive computation
    return x * 2

# Memory caching with expiration
@persist(memory=True, expire_seconds=3600, max_entries=100)
def fast_function(x: int) -> int:
    return x * 2

# Cache management
expensive_function.delete(5)  # Delete cached value for specific arguments
exists = expensive_function.exists(5)  # Check if value is cached
expensive_function.clear_all()  # Clear all cached entries for this function
```

**Advanced Usage (for packages that need lower-level access):**
```python
from ixutils import get_cache_path
from ixutils.persist import (
    hash_data,
    hash_arguments,
    resolve_cache_file_path,
    get_from_disk_cache,
    set_to_disk_cache,
    DEFAULT_CACHE_PATH,
    _CACHE_MISS,
)

# Use lower-level utilities for custom caching logic
cache_path = get_cache_path() or DEFAULT_CACHE_PATH
file_path = resolve_cache_file_path(
    cache_key="my_key",
    arg_hash=hash_data({"key": "value"}),
    cache_path_override=None,
    default_cache_path=cache_path,
    memory=False,
)

# Direct cache operations
cached_value = get_from_disk_cache(file_path, expire_seconds=3600)
if cached_value is not _CACHE_MISS:
    return cached_value

# Store in cache
set_to_disk_cache(file_path, value={"result": "data"})
```

### Time (`ixutils.time`)

Unified time utilities for consistent timestamp handling.

**Exports:**
- `utc_now_iso`: Get current UTC time as ISO format string
- `utc_now`: Get current UTC datetime object
- `parse_iso`: Parse ISO format strings to datetime
- `from_timestamp`: Convert Unix timestamp to ISO string
- `from_timestamp_datetime`: Convert Unix timestamp to datetime
- `current_timestamp`: Get current Unix timestamp
- `delay`: Sleep for specified seconds
- `strptime`: Parse datetime strings with format

**Usage:**
```python
from ixutils import utc_now_iso, utc_now, parse_iso, current_timestamp, delay

# Get current time
now_iso = utc_now_iso()  # "2024-01-15T10:30:45.123456+00:00"
now_dt = utc_now()  # datetime object

# Parse ISO strings
dt = parse_iso("2024-01-15T10:30:45+00:00")

# Timestamps
ts = current_timestamp()  # 1705315845.123456
dt = from_timestamp_datetime(ts)

# Sleep
delay(1.5)  # Sleep for 1.5 seconds
```

### Database (`ixutils.database`)

SQLite database connection helpers with automatic configuration.

**Exports:**
- `create_database_connection`: Create and configure SQLite connections

**Features:**
- In-memory or file-based databases
- Row factory configuration (returns dict-like Row objects)
- Optional table initialization callback

**Usage:**
```python
from ixutils import create_database_connection

# In-memory database
conn = create_database_connection()

# File-based database
conn = create_database_connection(database_path="data.db")

# With table initialization
def init_tables(conn):
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")

conn = create_database_connection(
    database_path="data.db",
    initialize_tables=init_tables
)
```

### Usage Tracker (`ixutils.usage_tracker`)

Track usage and costs for LLMs and agents.

**Exports:**
- `UsageTracker`: Class for tracking usage and costs

**Usage:**
```python
from ixutils import UsageTracker

tracker = UsageTracker()

# Track usage
tracker.add_record(
    usage={"tokens": 100, "requests": 1},
    cost=0.002,
    llm="gpt-4"
)

# Get totals
total_cost = tracker.get_total_cost()
total_usage = tracker.get_total_usage()
```

### JSON Parser (`ixutils.json_parser`)

Robust JSON parsing with repair capabilities for malformed JSON and LLM responses.

**Exports:**
- `repair_json`: Repair common JSON issues (unquoted keys, trailing commas)
- `parse_json_robust`: Parse JSON with automatic repair
- `parse_json_or_python_literal`: Parse JSON or Python literal format

**Features:**
- Handles markdown code blocks (```json or ```) from LLM responses
- Repairs unquoted special object references (`<tool_obj:...>`, `<obj:...>`, etc.)
- Removes trailing commas
- Converts single quotes to double quotes
- Falls back to Python literal parsing if JSON parsing fails

**Usage:**
```python
from ixutils import parse_json_robust, parse_json_or_python_literal

# Parse with automatic repair
data = parse_json_robust('{key: "value",}')  # Handles unquoted keys and trailing commas

# Handle markdown code blocks from LLMs
data = parse_json_robust('```json\n{"entities": true}\n```')  # Extracts and parses JSON
data = parse_json_robust('```\n{"entities": true}\n```')  # Works without json tag too

# Parse JSON or Python literal
data = parse_json_or_python_literal('{"key": "value"}')  # JSON
data = parse_json_or_python_literal("{'key': 'value'}")  # Python dict
data = parse_json_or_python_literal('```json\n{"key": "value"}\n```')  # Markdown code block
```

### Fuzzy Match (`ixutils.fuzzy_match`)

String fuzzy matching utilities.

**Exports:**
- `fuzzy_match`: Find best matching string from a list

**Usage:**
```python
from ixutils import fuzzy_match

options = ["apple", "banana", "cherry"]
best_match = fuzzy_match("appl", options)  # Returns "apple"
```

### Environment Variables (`ixutils.env_var`)

Environment variable handling for credentials and configuration.

**Exports:**
- `EnvVar`: Class for representing and reading environment variables

**Features:**
- Represents environment variable names without exposing values
- Optional default values
- Lazy evaluation - reads from environment when needed
- Useful for credential handling in APIs and services

**Usage:**
```python
from ixutils import EnvVar

# Create an environment variable reference
api_key = EnvVar("OPENAI_API_KEY")

# Use with optional default
api_key_with_default = EnvVar("OPENAI_API_KEY", default="sk-default")

# Get the actual value (reads from environment)
try:
    value = api_key.get_value()  # Reads from os.getenv("OPENAI_API_KEY")
except ValueError:
    # Environment variable not set and no default provided
    pass

# EnvVar objects can be passed to functions that accept credentials
# The actual value will be read when needed
```

**Common Use Case:**
```python
from ixutils import EnvVar

# In your code, accept EnvVar or string
def initialize_llm(api_key):
    if isinstance(api_key, EnvVar):
        api_key = api_key.get_value()
    # Use api_key...
    
# Users can pass either:
initialize_llm(EnvVar("OPENAI_API_KEY"))  # Reads from environment
initialize_llm("sk-...")  # Or pass directly
```

### File System (`ixutils.file_system`)

File system utilities for common file operations.

**Exports:**
- `path_exists`: Check if a path exists
- `path_is_dir`: Check if a path is a directory
- `path_is_file`: Check if a path is a file
- `read_text_file`: Read text content from a file
- `write_text_file`: Write text content to a file
- `list_dir`: List directory contents
- `move_to_trash`: Move files/directories to macOS Trash

**Features:**
- Simple utility functions that return values directly (not in tool format)
- Proper error handling with descriptive exceptions
- Cross-platform path handling
- macOS Trash support for safe file deletion

**Usage:**
```python
from ixutils.file_system import (
    path_exists,
    path_is_file,
    path_is_dir,
    read_text_file,
    write_text_file,
    list_dir,
    move_to_trash,
)

# Path checking
if path_exists("data.txt"):
    if path_is_file("data.txt"):
        content = read_text_file("data.txt")

# File operations
write_text_file("output.txt", "Hello, world!", mode="x")  # Exclusive create
write_text_file("output.txt", "Updated", mode="w")  # Overwrite
write_text_file("log.txt", "New entry\n", mode="a")  # Append

# Directory listing
items = list_dir(".", include_hidden=False)
for item in items:
    print(f"{item['name']} ({item['type']})")

# Safe deletion (moves to Trash)
move_to_trash("old_file.txt")  # Can be recovered from Trash
```

## Quick Start

```python
from ixutils import persist, set_cache_path, utc_now_iso, create_database_connection

# Set cache path for your application
set_cache_path(".cache/my_app")

# Use persist decorator for caching
@persist(memory=True, expire_seconds=3600)
def expensive_function(x: int) -> int:
    return x * 2

# Use time utilities
timestamp = utc_now_iso()

# Create database connection
conn = create_database_connection(database_path="data.db")
```

## Design Philosophy

- **No Dependencies**: Pure utilities with no external dependencies
- **Shared Functionality**: Only utilities used by multiple packages
- **Simple and Focused**: Each utility has a clear, single purpose
- **Independent**: Can be used standalone or as part of the ix ecosystem

## Installation

### From Local Development

If you're developing locally and want to use `ixutils` in other packages:

```bash
# Install in editable mode
pip install -e /path/to/ixutils

# Or from the ixutils directory
cd /path/to/ixutils
pip install -e .
```

### As a Dependency in Other Packages

Add `ixutils` to your package's `pyproject.toml`:

```toml
[project]
dependencies = [
    "ixutils>=0.1.0",
]
```

Or if installing from a local path during development:

```toml
[project]
dependencies = [
    "ixutils @ file:///path/to/ixutils",
]
```

### From PyPI (when published)

```bash
pip install ixutils
```

