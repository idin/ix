# Name Matching and Standardization Tool

## What is NameRegistry?

`NameRegistry` is a tool for tracking, matching, and standardizing names in text. It's designed to handle real-world messiness: typos, variations, different casing, and different separators (spaces, underscores, hyphens).

**Example use case**: You have files named "john_smith_report.pdf", "John-Smith-data.xlsx", "johnsmith_notes.txt". The registry recognizes all three refer to "John Smith" and can standardize them.

## Why This Tool Exists

### The Problem
- File names, database entries, and user inputs rarely match exactly
- "john smith", "John_Smith", "johnsmith", and "John-Smith" are all the same person
- Simple string matching fails; fuzzy matching alone is too slow
- Names have structure (first + last) that should be exploited

### Our Solution
Token-based matching with first-letter indexing:
1. **Break names into tokens** ("John Smith" → ["john", "smith"])
2. **Index by first letter** (only compare "john" against names starting with "j")
3. **Fuzzy match intelligently** (match tokens, not full strings)
4. **Handle concatenation** ("johnsmith" automatically matches "John Smith")

This makes matching **10-100x faster** than naive fuzzy matching while being more accurate.

## When to Use NameRegistry

### Good Use Cases
- **File organization**: Standardize file names with person names, band names, artist names
- **Data cleaning**: Match database entries with slight variations
- **Text extraction**: Find known names in documents or file paths
- **Alias handling**: Map nicknames to canonical names ("Johnny" → "John Smith")

### Not Designed For
- **Entity extraction from scratch** (doesn't discover new names, only matches known ones)
- **Full-text search** (designed for short strings like file names, not documents)
- **Real-time autocomplete** (optimized for batch processing)

## Key Design Decisions

### Case Preservation vs. Matching
- **When adding**: Exact case is preserved ("Chris de Burgh" stays as-is)
- **When matching**: Case-insensitive ("chris de burgh" finds "Chris de Burgh")
- **Why**: Canonical names should look correct, but matching should be flexible

### Token-Based, Not Character-Based
- Fuzzy matches happen at token level, not character level
- "John Smith" won't match "Joan Smith" even though they're similar strings
- But "john_smiths" will match "John Smith" because tokens match
- **Why**: Names have structure. We want "John Smith" and "Jane Smith" to be clearly different, but "john-smith" and "john_smith" to be the same.

### First-Letter Indexing
- Names are organized by their first letter before any matching
- "John" only compared against names starting with "j"
- **Why**: With 10,000 names, this reduces search space from 10,000 to ~400

### Concatenated Form Recognition
- "johnsmith" automatically registered as a lookup form for "John Smith"
- No need to explicitly add it
- **Why**: Common pattern in file names and URLs

### Aliases for Nicknames
- Must be explicitly added: `registry.add_alias("John Smith", "Johnny")`
- Not automatic (unlike concatenation)
- **Why**: Nickname relationships are domain-specific and ambiguous

## Quick Start

```python
from ixmachina.tools.text import NameRegistry

# Create and populate registry
registry = NameRegistry()
registry.add_name("John Smith")
registry.add_name("Jane Doe")
registry.add_alias("John Smith", "Johnny")

# Find names in text
result = registry.find_name_in_text("johnny_report.pdf")
# Returns: ("John Smith", 100, {...details...})

# Standardize file names
result = registry.standardize_names_in_text("john_smith_and_jane_doe_report.pdf")
# Returns: {
#   'standardized_text': 'John Smith and Jane Doe report.pdf',
#   'names_found': ['John Smith', 'Jane Doe'],
#   ...
# }

# Save and load
registry.save_to_json("names.json")  # Human-readable
registry.save_to_pickle("names.pkl")  # Faster
loaded = NameRegistry.load_from_json("names.json")
```

## Important Behaviors

### Overlap Prevention
When multiple names match overlapping positions, only the best match is used:
- Text: "john_smith_report.pdf"
- If registry has both "John" and "John Smith"
- Only "John Smith" is returned (longer/better match wins)

### Threshold Tuning
- `threshold`: Minimum score for overall name match (default: 70)
- `token_threshold`: Minimum score for individual tokens (default: 80)
- Lower = more permissive, higher = more strict
- **When to adjust**: If getting too many false positives, increase thresholds

### Token Position Matters
- Tokens must appear in order (can have gaps)
- "smith john" won't match "John Smith"
- **Why**: Prevents nonsensical matches

## Choosing Between Methods

| Method | Use When |
|--------|----------|
| `add_name()` | Adding canonical names to track |
| `add_alias()` | Mapping nicknames/variations to canonical names |
| `get_canonical()` | Quick O(1) lookup for exact/concatenated forms |
| `find_name_in_text()` | Finding the best matching name in short text |
| `find_all_names_in_text()` | Finding all matching names (e.g., multiple people in filename) |
| `standardize_names_in_text()` | Replacing all found names with canonical forms |
| `save_to_json()` | Saving for humans to inspect or version control |
| `save_to_pickle()` | Saving for production (faster, not human-readable) |

## Performance Notes

- Adding 1,000 names: ~100ms
- Finding name in text: ~1-5ms
- Standardizing text: ~5-10ms
- Scales well to 10,000+ names (first-letter indexing keeps it fast)

## Agent Integration

For AI agents, `NameRegistry` should be instantiated once and passed to tools using the `@bind` decorator (see `bind.md` in utils documentation). The registry is not serializable as a tool parameter.

