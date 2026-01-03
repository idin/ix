"""
Constants for tool return dictionaries.

All tools should use these constants for consistent return structure.
The primary output/result should always be in RESULT_KEY.

## Tool Output Dictionary Structure

All tools must return a dictionary with the following structure:

```python
{
    SUCCESS_KEY: bool,      # True if operation succeeded, False otherwise
    RESULT_KEY: Any,        # Primary output/result of the tool (see below)
    ERROR_KEY: Optional[str] # Error message if operation failed, None if successful
}
```

### RESULT_KEY Structure

The RESULT_KEY contains the primary output of the tool. Tool-specific keys (like file paths,
data objects, etc.) must be nested INSIDE RESULT_KEY, not at the top level.

**Correct structure:**
```python
{
    SUCCESS_KEY: True,
    RESULT_KEY: {
        "data": "file content",  # Primary output (the actual file data)
        "metadata": { WRONG. I TOLD YOU THIS IS NOT WHAT I WANT. METADATA SHOULD BE OUTSIDE OF RESULT, 
            "path": "/path/to/file"  # Tool-specific metadata (nested under metadata)
        }
    },
    ERROR_KEY: None
}
```

**Incorrect structure (tool-specific keys at top level):**
```python
{
    SUCCESS_KEY: True,
    RESULT_KEY: "file content",
    "path": "/path/to/file",  # WRONG: tool-specific key at top level
    ERROR_KEY: None
}
```

### Why This Structure?

1. **Consistency**: The agent's `_extract_tool_output_value()` method expects RESULT_KEY
   to contain the primary output, making it easy to extract just the result.

2. **Separation of Concerns**: Top-level keys (SUCCESS_KEY, ERROR_KEY, RESULT_KEY) are
   metadata about the operation. Tool-specific data belongs in RESULT_KEY.

3. **Type Safety**: The agent can reliably extract `result[RESULT_KEY]` knowing it contains
   all the tool's output data.

### Examples

**Read operation:**
```python
{
    SUCCESS_KEY: True,
    RESULT_KEY: {
        "data": "Hello, world!",  # The actual file data
        "metadata": {
            "path": "/tmp/file.txt"  # Metadata nested separately
        }
    },
    ERROR_KEY: None
}
```

**Write operation:**
```python
{
    SUCCESS_KEY: True,
    RESULT_KEY: {
        "data": "Hello, world!",  # Written content (primary output)
        "metadata": {
            "path": "/tmp/file.txt"  # Metadata nested separately
        }
    },
    ERROR_KEY: None
}
```

**Error case:**
```python
{
    SUCCESS_KEY: False,
    RESULT_KEY: None,
    ERROR_KEY: "File does not exist: /tmp/missing.txt"
}
```
"""

# Standard return keys - ALL tools must use these
SUCCESS_KEY = "success"
ERROR_KEY = "error"
RESULT_KEY = "result"  # Primary output/result of the tool - ALWAYS use this for the main return value (just the data, not metadata)
METADATA_KEY = "metadata"  # Tool-specific metadata (like file paths) - separate from result

