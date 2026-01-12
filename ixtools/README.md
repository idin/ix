# ixtools

Tools package providing reusable functions that can be used with agents for various tasks.

## Overview

`ixtools` provides a comprehensive collection of tools organized by category:

- **File System**: File and directory operations (read, write, copy, move, delete, compare)
- **Database**: Database operations (query execution, schema management, table operations)
- **Web**: Web scraping, search, URL fetching, username discovery
- **Text**: Text processing, name standardization, token matching
- **Math**: Mathematical operations, statistics, unit conversion, trigonometry
- **Media**: Media file information (images, audio, video)
- **Music**: Music information from Genius, MusicBrainz, Spotify
- **Pricing**: LLM model pricing information
- **String**: String utilities (type inference, smart truncation)
- **Wikipedia**: Wikipedia article retrieval and parsing

## Role

`ixtools` is the **tool library** - it provides a collection of reusable tools that agents can use to perform various tasks. Tools are independent functions that follow a consistent interface.

## Dependencies

- **ixcore**: Uses `constants` for tool output structure and utilities like `persist` for caching
- **No other internal dependencies**: Tools are independent and can be used standalone

## What Depends on ixtools

- **ixagent**: Agents can use tools from `ixtools` to extend their capabilities
- **No other packages depend on ixtools**: It's a library of tools for agents to use

## Key Components

### Tool Structure

All tools follow a consistent structure:

```python
def tool_name(param1: type, param2: type) -> dict:
    """
    Tool description.
    
    Args:
        param1: Description
        param2: Description
    
    Returns:
        Dictionary with:
        - success: bool
        - result: Tool-specific data
        - error: Optional error message
    """
    return {
        "success": True,
        "result": {...},
        "error": None
    }
```

### Tool Categories

#### File System (`ixtools.tools.file_system`)

- **Read**: Read text files, structured files (JSON, YAML, CSV), DataFrames, pickles
- **Write**: Write text files, structured files, DataFrames, pickles
- **Copy/Move**: Copy and move files/directories, change paths
- **Delete**: Delete files/directories (with recycle bin support)
- **List**: List directory contents
- **Compare**: Compare files and directories
- **Path Utils**: Path manipulation utilities

#### Database (`ixtools.tools.database`)

- **Connection**: Database connection management
- **Query Execution**: Execute SQL queries
- **Schema**: Get table schemas
- **Table Management**: Create tables, list tables

#### Web (`ixtools.tools.web`)

- **Fetch**: Fetch URLs, check URL status
- **Parse**: Parse HTML, extract content, summarize pages
- **Search**: Web search (Brave, DuckDuckGo)
- **Username Search**: Discover username patterns and availability

#### Text (`ixtools.tools.text`)

- **Name Registry**: Name standardization and matching
- **Utilities**: Token matching, name finding, text standardization

#### Math (`ixtools.tools.math`)

- **Calculate**: Basic calculations
- **Operate**: Mathematical operations
- **Statistics**: Statistical functions
- **Trigonometry**: Trigonometric functions
- **Unit Conversion**: Convert between units

#### Media (`ixtools.tools.media`)

- **Info**: Get metadata for images, audio, video
- **Media Info**: Unified media information retrieval

#### Music (`ixtools.tools.music`)

- **Genius**: Search songs, get lyrics
- **MusicBrainz**: Search and retrieve music information
- **Spotify**: Search Spotify catalog

#### Other Categories

- **Pricing**: Get LLM model pricing information
- **String**: String type inference, smart truncation
- **Wikipedia**: Wikipedia article retrieval and parsing

## Usage Example

### Standalone Tool Usage

```python
from ixtools.file_system.read import read_text_file
from ixtools.web.fetch import fetch_url

# Use tools directly
result = read_text_file(path="file.txt")
if result["success"]:
    print(result["result"]["data"])

# Fetch a URL
result = fetch_url(url="https://example.com")
```

### Using Tools with Agent

```python
from ixcore.llm import LLM
from ixagent import Agent
from ixtools.file_system.read import read_text_file
from ixtools.web.fetch import fetch_url

# Create agent with tools
agent = Agent(
    llm=LLM(provider="openai", model="gpt-4"),
    tools=[read_text_file, fetch_url]
)

# Agent can now use these tools
response = agent.run("Read the file at /path/to/file.txt and summarize it")
```

## Tool Output Structure

All tools return dictionaries with this structure:

```python
{
    "success": bool,      # Whether operation succeeded
    "result": {...},      # Tool-specific data (nested dict)
    "error": str | None   # Error message if failed
}
```

Tool-specific keys (like `data`, `path`, `content`) are nested inside `result`, not at the top level.

## Design Principles

- **Consistent Interface**: All tools follow the same output structure
- **Error Handling**: Tools return error dictionaries instead of raising exceptions (for agent compatibility)
- **Independence**: Tools can be used standalone or with agents
- **Caching**: Tools use `persist` decorator for result caching where appropriate
- **Type Safety**: Tools use type hints for better integration

## Installation

This package is part of the ix ecosystem. Requires `ixcore` as a dependency.

