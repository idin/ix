# String Tools

Tools for string manipulation, type inference, and smart text processing. These tools help you work with text data more intelligently.

## Core Design Principles

### Smart Processing

These tools go beyond simple string operations. They understand context, infer types, and make intelligent decisions about how to process text.

**Why this matters**: Real-world text data is messy. These tools handle variations, edge cases, and common patterns automatically.

### Type Safety

Type inference helps you understand what data you're working with before processing it.

**Why implemented this way**: Knowing the type of data helps you choose the right processing approach and avoid errors.

## Understanding the Tools

### `infer_string_type` - Infer Data Type

**What it does**: Determines the best type a string can be converted to (dict, list, int, float, bool, or str).

**Why we use it**: When you receive string data (from APIs, files, user input) and need to know what it represents before processing it.

**Why implemented this way**:
- First tries JSON parsing (fastest, most reliable)
- Falls back to LLM if JSON parsing fails (handles non-JSON formats)
- Returns both the inferred type and converted value
- Handles edge cases (empty strings, whitespace, etc.)

**How to use**:
```python
from ixmachina.tools.string import infer_string_type

# JSON string (fast path)
result = infer_string_type('{"name": "John", "age": 30}')
if result["success"]:
    print(f"Type: {result['type']}")  # "dict"
    print(f"Value: {result['value']}")  # {"name": "John", "age": 30}
    print(f"Method: {result['method']}")  # "json"

# Non-JSON string (LLM path)
result = infer_string_type(
    "This is a list: apple, banana, cherry",
    llm=my_llm
)
if result["success"]:
    print(f"Type: {result['type']}")  # "list"
    print(f"Value: {result['value']}")  # ["apple", "banana", "cherry"]
    print(f"Method: {result['method']}")  # "llm"
```

**When to use**: 
- Processing data from unknown sources
- Validating user input
- Converting string data to appropriate types
- When you need to know the structure of data before processing

**Note**: LLM inference is optional. If no LLM is provided and JSON parsing fails, the function returns a fallback result indicating the string should remain as text.

---

### `smart_truncate_text` - Intelligent Text Truncation

**What it does**: Truncates text intelligently by finding relevant sections based on search terms, rather than just cutting at a character limit.

**Why we use it**: When you need to shorten text but want to preserve the most relevant parts, not just the beginning.

**Why implemented this way**:
- Finds all occurrences of search terms in the text
- Identifies the range (min to max position) where terms appear
- Truncates around that range with a 5% buffer on each side
- Preserves context around important content

**How to use**:
```python
from ixmachina.tools.string import smart_truncate_text

long_text = "..."  # Very long text

# Truncate around specific terms
truncated = smart_truncate_text(
    text=long_text,
    search_terms=["Python", "programming"],
    max_length=8000
)

# Multiple terms
truncated = smart_truncate_text(
    text=long_text,
    search_terms=["API", "authentication", "tokens"],
    max_length=5000
)

# No terms (falls back to simple truncation)
truncated = smart_truncate_text(
    text=long_text,
    max_length=3000
)
```

**When to use**: 
- Preparing text for LLM processing (staying within token limits)
- Extracting relevant sections from long documents
- Creating summaries that focus on specific topics
- When you need to preserve important content while reducing length

**Note**: If no search terms are provided, the function falls back to simple truncation (first N characters).

---

## Common Patterns

### Processing Unknown Data

Use type inference before processing:

```python
data_string = get_data_from_source()  # Unknown format

result = infer_string_type(data_string, llm=my_llm)
if result["success"]:
    data = result["value"]
    data_type = result["type"]
    
    if data_type == "dict":
        # Process as dictionary
        process_dict(data)
    elif data_type == "list":
        # Process as list
        process_list(data)
    else:
        # Process as other type
        process_other(data)
```

### Preparing Text for LLMs

Use smart truncation to focus on relevant content:

```python
# Long document
document = get_long_document()

# User's query
query = "authentication and security"

# Extract relevant section
relevant_section = smart_truncate_text(
    text=document,
    search_terms=query.split(),  # Split query into terms
    max_length=8000  # LLM token limit
)

# Send to LLM
llm_response = llm.query(relevant_section)
```

### Error Handling

Always check for success:

```python
result = infer_string_type(text, llm=my_llm)
if not result["success"]:
    print(f"Error: {result.get('error', 'Unknown error')}")
    # Handle error (maybe treat as plain text)
    return

# Use result["type"] and result["value"]
```

---

## Design Decisions

### Why JSON First, LLM Second?

JSON parsing is:
- **Fast**: No API calls needed
- **Reliable**: Exact parsing, no ambiguity
- **Free**: No LLM costs

LLM inference is:
- **Flexible**: Handles non-JSON formats
- **Expensive**: Requires API calls
- **Slower**: Network latency

The two-step approach gives you the best of both: fast JSON parsing when possible, flexible LLM inference when needed.

### Why Search Terms for Truncation?

Instead of just cutting at a character limit:
- **Preserves relevance**: Keeps important content
- **Context-aware**: Maintains context around search terms
- **User-focused**: Truncates based on what the user cares about

This is especially important for LLM processing, where you want to send the most relevant information.

### Why 5% Buffer?

When truncating around search terms, a 5% buffer on each side:
- Provides context around matches
- Prevents cutting mid-sentence
- Balances relevance with length

The buffer size is a balance between preserving context and staying within length limits.

### Why Fallback to Simple Truncation?

If no search terms are provided:
- Still useful: Sometimes you just need to shorten text
- Predictable: First N characters is a known behavior
- No overhead: No search needed

This makes the function useful even when you don't have specific terms to search for.

