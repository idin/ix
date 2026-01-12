# ixcore

Core foundation package providing LLM connections, utilities, and output formatting.

## Overview

`ixcore` is the foundational package that provides the core building blocks for the ix ecosystem. It contains:

- **LLM connections**: Unified interface for connecting to multiple LLM providers (OpenAI, Anthropic, etc.)
- **LLM-specific utilities**: Utilities for working with LLM responses and data
- **Output formatting**: Utilities for formatting LLM string outputs into structured data

## Role

`ixcore` is the **foundation layer** - it has minimal dependencies and provides essential LLM functionality that other packages depend on.

## Dependencies

- **External dependencies**: LLM provider SDKs (OpenAI, Anthropic)
- **Internal dependencies**: `ixutils` (for shared utilities like `persist`, `time`, `UsageTracker`, `EnvVar`)

**Note**: `ixcore` does not depend on `ixagent`, `ixmemory`, or `ixtools`. It uses `ixutils` for shared utilities but does not expose them in its public API.

## What Depends on ixcore

- **ixagent**: Uses `LLM` for LLM connections
- **ixmemory**: May use LLM connections for semantic operations
- **ixtools**: May use LLM connections for tool execution

## Quick Reference

**Main Exports:**
```python
from ixcore import LLM, format_output
from ixcore.utils import add_dictionaries, AddableDictionary, normalize_keys
```

**LLM Class:**
- `LLM(api_key, model_name, provider=None, pricing=None, fetch_pricing=False, use_cache=False, **kwargs)`
- `llm.query(user_prompt=None, system_prompt=None, messages=None, max_tokens=None, temperature=None, tools=None, **kwargs)` → str or dict
- `llm.get_total_usage()` → dict
- `llm.get_total_cost()` → dict
- `llm.calculate_cost_from_usage(input_tokens, output_tokens)` → dict or None
- Attributes: `last_usage`, `total_usage`, `last_cost`, `total_cost`, `usage_tracker`

**Format Output:**
- `format_output(llm, output_string, output_format=None, infer_format=False)` → Any

**Utils:**
- `add_dictionaries(dict1, dict2)` → dict
- `AddableDictionary` (supports `+` and `+=`)
- `normalize_key(key)` → str
- `normalize_keys(data)` → dict

## Key Components

### LLM (`ixcore.llm`)

The main LLM connection and querying interface.

**Main Class:**
- `LLM`: Unified interface for connecting to and querying LLM providers

**Features:**
- **Multi-provider support**: Works with OpenAI, Anthropic, and other providers
- **Auto-detection**: Automatically detects provider from model name (e.g., "gpt-4" → OpenAI, "claude-3" → Anthropic)
- **Environment variables**: Accepts `EnvVar` instances from `ixutils` for secure credential handling
- **Caching**: Optional response caching to avoid duplicate API calls
- **Usage tracking**: Built-in token usage and cost tracking
- **Pricing**: Automatic or manual pricing configuration for cost calculation
- **Tool support**: Convert Python functions to provider-specific tool formats (function calling)

**Usage:**
```python
from ixcore.llm import LLM
from ixutils import EnvVar

# Create LLM instance with API key
llm = LLM(
    api_key=EnvVar("OPENAI_API_KEY"),  # or pass string directly
    model_name="gpt-4o-mini",
    use_cache=True,  # Enable caching
    fetch_pricing=True,  # Auto-fetch pricing
)

# Query with user prompt
response = llm.query(user_prompt="What is the capital of France?")

# Query with system and user prompts
response = llm.query(
    system_prompt="You are a helpful assistant",
    user_prompt="Explain quantum computing",
    max_tokens=500,
    temperature=0.7,
)

# Query with messages
messages = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"},
    {"role": "user", "content": "What's 2+2?"},
]
response = llm.query(messages=messages)

# Query with tools (function calling)
def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"Weather in {location}: Sunny, 72°F"

response = llm.query(
    user_prompt="What's the weather in Paris?",
    tools=[get_weather],  # Pass functions as tools
)
# Response may be a dict with "tool_calls" if LLM decides to use tools

# Access usage information (attributes)
print(llm.last_usage)  # Last query usage: {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15}
print(llm.total_usage)  # Cumulative usage (AddableDictionary)
print(llm.last_cost)  # Last query cost: {"input_cost": 0.0001, "output_cost": 0.0002, "total_cost": 0.0003}
print(llm.total_cost)  # Cumulative cost (AddableDictionary)
print(llm.usage_tracker.records)  # Detailed usage records

# Access usage information (methods)
total_usage = llm.get_total_usage()  # Get total usage dict
total_cost = llm.get_total_cost()  # Get total cost dict

# Calculate cost manually
cost = llm.calculate_cost_from_usage(input_tokens=100, output_tokens=50)
# Returns: {"input_cost": 0.001, "output_cost": 0.002, "total_cost": 0.003} or None if no pricing
```

**Return Value:**
- Normally returns a string with the LLM's text response
- If tools are used and LLM decides to call them, returns a dict with `"tool_calls"` key
- The dict contains tool call information including function name and arguments

**Provider Auto-Detection:**
- Models starting with "gpt" or "o1" → OpenAI
- Models starting with "claude" → Anthropic
- Can also explicitly specify `provider` parameter

**Caching:**
- Enable with `use_cache=True` in constructor
- Caches responses based on model, messages, and parameters
- Uses `ixutils.persist` for disk-based caching

**Usage Tracking:**
- Automatically tracks tokens and costs for each query
- **Attributes**: `last_usage`, `total_usage`, `last_cost`, `total_cost` (AddableDictionary instances)
- **Methods**: `get_total_usage()`, `get_total_cost()`, `calculate_cost_from_usage()`
- Includes `usage_tracker` (from `ixutils`) for detailed record-keeping

**Pricing:**
- Can provide pricing manually: `pricing={"input": 2.5, "output": 10.0}` or `pricing=2.5` (same for both)
- Can enable automatic pricing fetch: `fetch_pricing=True`
- Pricing is used to calculate costs automatically
- Use `calculate_cost_from_usage()` to calculate cost without making a query

**Tool/Function Calling:**
- Pass Python functions via `tools` parameter in `query()`
- Functions are automatically converted to provider-specific format
- If LLM decides to use tools, response is a dict with `"tool_calls"` key
- Otherwise, response is a string as usual

**Provider-Specific Parameters:**
- Pass additional parameters via `**kwargs` in `__init__()` or `query()`
- Parameters are merged (query kwargs override init kwargs)
- Example: `llm.query(..., top_p=0.9, frequency_penalty=0.5)` for OpenAI
- Example: `llm = LLM(..., top_p=0.9)` to set default for all queries

### Utils (`ixcore.utils`)

LLM-specific utility functions for working with LLM data and responses.

**Exports:**
- `add_dictionaries`: Add two dictionaries by summing numeric values for common keys
- `AddableDictionary`: Dictionary subclass that supports addition operations (`+` and `+=`)
- `normalize_key`: Normalize a single dictionary key (lowercase, hyphens to underscores)
- `normalize_keys`: Normalize all keys in a dictionary

**Usage:**
```python
from ixcore.utils import add_dictionaries, AddableDictionary, normalize_keys

# Add dictionaries (sums numeric values)
dict1 = {"tokens": 100, "cost": 0.01}
dict2 = {"tokens": 50, "cost": 0.005}
result = add_dictionaries(dict1, dict2)
# {"tokens": 150, "cost": 0.015}

# AddableDictionary with + operator
usage1 = AddableDictionary({"input_tokens": 100, "output_tokens": 50})
usage2 = AddableDictionary({"input_tokens": 200, "output_tokens": 75})
total = usage1 + usage2  # {"input_tokens": 300, "output_tokens": 125}

# Normalize keys (useful for model name normalization)
prices = {"GPT-4.1": 3.0, "gpt-4o": 2.5}
normalized = normalize_keys(prices)
# {"gpt_4.1": 3.0, "gpt_4o": 2.5}
```

**Note**: Shared utilities (like `persist`, `time`, `UsageTracker`, `EnvVar`) are in `ixutils`, not `ixcore.utils`. Import them directly from `ixutils`.

### Format Output (`ixcore.format_output`)

Convert LLM string outputs to desired structured formats.

**Main Function:**
- `format_output`: Convert LLM string outputs to int, float, dict, list, etc.

**Features:**
- **Direct parsing**: Attempts JSON parsing and type casting first
- **LLM-assisted conversion**: Uses the LLM to help convert if direct parsing fails
- **Format inference**: Can automatically infer the output format
- **Flexible JSON**: Handles JSON in markdown code blocks

**Usage:**
```python
from ixcore.format_output import format_output
from ixcore.llm import LLM
from ixutils import EnvVar

llm = LLM(api_key=EnvVar("OPENAI_API_KEY"), model_name="gpt-4o-mini")

# Get string response
response = llm.query(user_prompt="What is 2 + 2? Return only the number.")

# Convert to integer
number = format_output(llm=llm, output_string=response, output_format=int)
# or
number = format_output(llm=llm, output_string=response, output_format="int")

# Convert to dictionary
response = llm.query(user_prompt="Return a JSON object with name and age")
data = format_output(llm=llm, output_string=response, output_format=dict)

# Convert to list
response = llm.query(user_prompt="Return a JSON array of numbers 1-5")
numbers = format_output(llm=llm, output_string=response, output_format=list)

# Infer format automatically
response = llm.query(user_prompt="Return some data")
data = format_output(llm=llm, output_string=response, infer_format=True)

# Flexible JSON (can be dict or list)
response = llm.query(user_prompt="Return JSON data")
data = format_output(llm=llm, output_string=response, output_format="json")
```

**Supported Formats:**
- `int` or `"int"`: Integer numbers
- `float` or `"float"`: Floating point numbers
- `str` or `"str"`: Strings (returns as-is)
- `dict` or `"dict"`: Dictionaries/objects
- `list` or `"list"`: Lists/arrays
- `"json"`: JSON (can be dict or list, automatically determined)

## Complete Usage Example

```python
from ixcore.llm import LLM
from ixcore.format_output import format_output
from ixutils import EnvVar, set_cache_path

# Set cache path for LLM responses
set_cache_path(".cache/ixcore")

# Create LLM instance
llm = LLM(
    api_key=EnvVar("OPENAI_API_KEY"),
    model_name="gpt-4o-mini",
    use_cache=True,  # Enable caching
    fetch_pricing=True,  # Auto-fetch pricing
)

# Query the LLM
response = llm.query(
    user_prompt="What is the capital of France? Return only the city name.",
    max_tokens=50,
)

# Format output to string (already a string, but demonstrates usage)
capital = format_output(llm=llm, output_string=response, output_format=str)

# Query for structured data
response = llm.query(
    user_prompt="Return a JSON object with the name and population of Paris"
)
paris_data = format_output(llm=llm, output_string=response, output_format=dict)

# Check usage and costs
print(f"Total tokens: {llm.total_usage['total_tokens']}")
print(f"Total cost: ${llm.total_cost['total_cost']:.4f}")
print(f"Last query cost: ${llm.last_cost['total_cost']:.4f}")

# Access detailed usage records
for record in llm.usage_tracker.records:
    print(f"Model: {record.get('model')}, Tokens: {record.get('usage', {}).get('total_tokens')}")
```

## Design Philosophy

- **Focused on LLM operations**: Only contains LLM-specific functionality
- **Uses shared utilities**: Depends on `ixutils` for common utilities but doesn't expose them
- **Provider-agnostic**: Unified interface works with multiple LLM providers
- **Feature-rich**: Includes caching, usage tracking, pricing, and output formatting
- **Clean API**: Only exposes its own functionality, not dependencies

## Installation

### From Local Development

```bash
# Install in editable mode
cd /path/to/ixcore
pip install -e .
```

### As a Dependency

Add to your `pyproject.toml`:
```toml
[project]
dependencies = [
    "ixcore>=0.1.0",
    "ixutils>=0.1.0",  # Required dependency
]
```

### From PyPI (when published)

```bash
pip install ixcore
```

## Related Packages

- **ixutils**: Shared utilities (persist, time, UsageTracker, EnvVar, etc.)
- **ixagent**: Agent framework that uses `ixcore.LLM`
- **ixmemory**: Memory systems that may use LLM connections
- **ixtools**: Tool framework that may use LLM connections
