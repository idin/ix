# Tools Overview

This directory contains documentation for all tool categories in `ixmachina`. Each category provides specialized functionality for different domains. Use this overview to find the right tools for your task, then refer to the detailed documentation for specific usage.

## Tool Categories

### Database Tools
**Purpose**: SQLite database operations with safe connection management

**What you can do**:
- Create and manage database connections (file-based or in-memory)
- Execute SQL queries with parameterization (prevents SQL injection)
- Create tables, list tables, and inspect schemas
- Automatic connection lifecycle management

**Best for**: Building databases, data storage, structured data management

**See**: [database.md](database.md) for detailed documentation

---

### File System Tools
**Purpose**: Safe file and directory operations with undo capabilities

**What you can do**:
- Read and write files (text, structured data, dataframes)
- Copy, move, and clone files/directories
- Delete with recycle bin (recoverable deletions)
- Compare files and directories
- List directory contents
- Track actions for undo/redo functionality

**Key features**:
- No overwriting allowed (prevents accidental data loss)
- Recycle bin system (deletions are recoverable)
- Explicit naming (clear distinction between move, copy, clone operations)

**Best for**: File management, data organization, safe file operations

**See**: [file_system.md](file_system.md) for detailed documentation

---

### Media Tools
**Purpose**: Extract metadata from audio, video, and image files

**What you can do**:
- Get comprehensive metadata for any media file
- Audio: sample rate, bitrate, duration, format
- Video: resolution, frame rate, codec, duration
- Image: dimensions, format, colour depth, EXIF data
- Automatic type detection

**Best for**: Media analysis, file organization, content management

**See**: [media.md](media.md) for detailed documentation

---

### Music Tools
**Purpose**: Access music information from multiple APIs

**What you can do**:
- **MusicBrainz**: Comprehensive metadata, releases, recordings (free, no auth)
- **Spotify**: Popularity, audio features, recommendations (requires OAuth)
- **Genius**: Lyrics and annotations (requires API key)

**Best for**: Music discovery, metadata collection, lyrics analysis

**See**: [music.md](music.md) for detailed documentation

---

### Pricing Tools
**Purpose**: Extract AI model pricing from company websites

**What you can do**:
- Search for official pricing pages
- Extract pricing using LLM (handles different website formats)
- Get prices per million tokens (standardized unit)
- Handle different pricing types (input, output, cached, training)

**Best for**: Cost comparison, budget planning, pricing research

**See**: [pricing.md](pricing.md) for detailed documentation

---

### String Tools
**Purpose**: Intelligent string manipulation and type inference

**What you can do**:
- Infer data types from strings (dict, list, int, float, bool, str)
- Smart text truncation (preserves relevant sections based on search terms)
- JSON parsing with LLM fallback

**Best for**: Data processing, text preparation for LLMs, type conversion

**See**: [string.md](string.md) for detailed documentation

---

### Text Tools
**Purpose**: Name matching and standardization

**What you can do**:
- Track and match names with variations (typos, casing, separators)
- Standardize names in text (file names, database entries)
- Handle aliases and nicknames
- Token-based matching (fast and accurate)

**Best for**: File organization, data cleaning, name standardization

**See**: [text.md](text.md) for detailed documentation

---

### Web Tools
**Purpose**: Web fetching, parsing, searching, and username checking

**What you can do**:
- **Fetching**: Get web pages, JSON APIs, check URL status
- **Parsing**: Extract text, parse HTML, find elements with CSS selectors
- **Search**: Search the web using Brave Search API
- **Username checking**: Check username availability across domains
- Domain filtering, HTML extraction, LLM-based content extraction

**Best for**: Web scraping, content extraction, research, username validation

**See**: [web.md](web.md) for detailed documentation

---

### Wikipedia Tools
**Purpose**: Search and retrieve Wikipedia articles

**What you can do**:
- Search for articles by topic
- Get full articles or summaries
- Extract specific sections
- Get structured data from infoboxes
- Find related articles through links
- Automatic title normalization

**Best for**: Research, knowledge extraction, fact-finding

**See**: [wikipedia.md](wikipedia.md) for detailed documentation

---

## Common Patterns

### Tool Output Structure

All tools return a standardized dictionary structure:
```python
{
    "success": bool,      # Whether operation succeeded
    "result": {...},      # Primary output data
    "error": str | None   # Error message if failed
}
```

Always check `success` before using results.

### Caching

Many tools use caching to improve performance:
- Web requests: 15-60 minutes (depending on data stability)
- Music searches: 15-30 minutes
- Wikipedia: No caching (always fresh)

You can disable caching with `use_cache=False` or delete cached values.

### Error Handling

All tools return structured errors. Always check the `success` key:
```python
result = some_tool(...)
if not result["success"]:
    print(f"Error: {result['error']}")
    return
# Use result["result"] here
```

### Agent Integration

Tools are designed to work with the `Agent` class. The agent automatically:
- Passes required parameters (like database connections, LLM instances)
- Handles tool execution
- Manages tool output extraction

See the [Agent documentation](../agent.md) for details on using tools with agents.

---

## Choosing the Right Tool

**File operations?** → [file_system.md](file_system.md)

**Web content?** → [web.md](web.md)

**Database work?** → [database.md](database.md)

**Media files?** → [media.md](media.md)

**Music information?** → [music.md](music.md)

**Text processing?** → [string.md](string.md) or [text.md](text.md)

**Wikipedia?** → [wikipedia.md](wikipedia.md)

**Pricing research?** → [pricing.md](pricing.md)

---

## Design Philosophy

All tools follow these principles:

1. **Safety first**: Operations that could cause data loss require explicit confirmation or use safety mechanisms (like recycle bins)

2. **Explicit over implicit**: Function names clearly indicate what they do (e.g., `move_dir_into` vs `change_dir_path`)

3. **Structured output**: Consistent return format makes tools predictable and easy to use

4. **Error handling**: All tools return structured errors, never raise exceptions

5. **Caching**: Tools that make external requests are cached appropriately to reduce costs and improve performance

For detailed information about any tool category, see the individual documentation files.

