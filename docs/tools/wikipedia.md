# Wikipedia Tools

Tools for searching and retrieving Wikipedia articles. These tools provide structured access to Wikipedia's vast knowledge base.

## Core Design Principles

### Title Normalization

Wikipedia article titles can be written in many ways (with/without spaces, different capitalization, redirects). The tools automatically normalize titles to their canonical form.

**Why this matters**: Users shouldn't need to know the exact Wikipedia title format. The tools handle variations automatically.

### Structured Access

Wikipedia articles have structure: sections, infoboxes, links. These tools provide access to specific parts, not just raw text.

**Why implemented this way**: Different use cases need different information. Sometimes you want the full article, sometimes just a section or the infobox.

## Understanding the Tools

### `search_wikipedia` - Search for Articles

**What it does**: Searches Wikipedia for articles matching a query and returns results with titles, snippets, and page IDs.

**Why we use it**: Find articles when you don't know the exact title, or discover related articles.

**Why implemented this way**:
- Uses Wikipedia's search API (no authentication required)
- Returns structured results with relevance information
- Supports multiple languages
- Provides snippets to help identify relevant articles

**How to use**:
```python
from ixmachina.tools.wikipedia import search_wikipedia

result = search_wikipedia("Python programming language", limit=5)
if result["success"]:
    for article in result["results"]:
        print(f"{article['title']}: {article['snippet']}")
        print(f"Page ID: {article['page_id']}")
```

**When to use**: When you need to find articles by topic, or when you're not sure of the exact article title.

---

### `normalize_article_title` - Normalize Title

**What it does**: Converts an article title to its canonical form, handling redirects and title variations.

**Why we use it**: Wikipedia titles have specific formatting rules. This function ensures you get the correct canonical title.

**Why implemented this way**:
- Handles redirects automatically
- Normalizes capitalization and spacing
- Resolves title variations
- Returns the canonical title used by Wikipedia

**How to use**:
```python
from ixmachina.tools.wikipedia import normalize_article_title

result = normalize_article_title("python (programming language)")
if result["success"]:
    print(result["canonical_title"])  # "Python (programming language)"
```

**When to use**: Before retrieving articles, to ensure you're using the correct title format. Usually called automatically by other functions.

---

### `get_wikipedia_article` - Get Article Content

**What it does**: Retrieves the full content or summary of a Wikipedia article.

**Why we use it**: Get article text for reading, analysis, or processing.

**Why implemented this way**:
- Automatically normalizes title first
- Supports full content or summary-only mode
- Handles multiple languages
- Returns structured data with metadata (page ID, URL, etc.)

**How to use**:
```python
from ixmachina.tools.wikipedia import get_wikipedia_article

# Get full article
result = get_wikipedia_article("Python (programming language)")
if result["success"]:
    print(f"Title: {result['title']}")
    print(f"Content length: {len(result['content'])} characters")
    print(f"Summary: {result['extract']}")

# Get summary only (faster, shorter)
result = get_wikipedia_article(
    "Python (programming language)",
    summary_only=True
)
if result["success"]:
    print(result["content"])  # Just the summary
```

**When to use**: When you need the full article text or a summary. Use `summary_only=True` for quick overviews.

---

### `get_article_section` - Get Specific Section

**What it does**: Retrieves a specific section from a Wikipedia article.

**Why we use it**: Articles can be long. Sometimes you only need one section.

**Why implemented this way**:
- Finds sections by name or index
- Returns section content with heading
- Handles nested sections
- More efficient than retrieving the full article

**How to use**:
```python
from ixmachina.tools.wikipedia import get_article_section

# Get section by name
result = get_article_section(
    title="Python (programming language)",
    section="History"
)
if result["success"]:
    print(result["section_content"])

# Get section by index (0-based)
result = get_article_section(
    title="Python (programming language)",
    section_index=2
)
```

**When to use**: When you need information from a specific part of an article, not the whole thing.

---

### `get_article_infobox` - Get Infobox Data

**What it does**: Extracts structured data from a Wikipedia article's infobox (the sidebar with key facts).

**Why we use it**: Infoboxes contain structured data (dates, locations, measurements) that's easier to work with than free text.

**Why implemented this way**:
- Parses infobox HTML/JSON
- Returns structured key-value pairs
- Handles different infobox formats
- More reliable than extracting from article text

**How to use**:
```python
from ixmachina.tools.wikipedia import get_article_infobox

result = get_article_infobox("Python (programming language)")
if result["success"]:
    infobox = result["infobox"]
    for key, value in infobox.items():
        print(f"{key}: {value}")
```

**When to use**: When you need structured facts about a topic (birth dates, locations, measurements, etc.).

---

### `get_article_links` - Get Article Links

**What it does**: Retrieves all links from a Wikipedia article, optionally filtered by link text or target.

**Why we use it**: Discover related articles, build knowledge graphs, or analyze article connections.

**Why implemented this way**:
- Returns both link text and target titles
- Supports filtering by text or target
- Handles internal and external links
- Useful for exploring related topics

**How to use**:
```python
from ixmachina.tools.wikipedia import get_article_links

# Get all links
result = get_article_links("Python (programming language)")
if result["success"]:
    for link in result["links"]:
        print(f"{link['text']} -> {link['target']}")

# Filter by link text
result = get_article_links(
    "Python (programming language)",
    filter_text="programming"
)
```

**When to use**: When you need to discover related articles or analyze connections between topics.

---

## Common Patterns

### Finding and Reading Articles

Combine search and retrieval:

```python
# Search first
search_result = search_wikipedia("Python programming", limit=1)
if search_result["success"]:
    article_title = search_result["results"][0]["title"]
    
    # Get full article
    article_result = get_wikipedia_article(article_title)
    if article_result["success"]:
        print(article_result["content"])
```

### Getting Structured Data

Use infobox for facts:

```python
result = get_article_infobox("Albert Einstein")
if result["success"]:
    infobox = result["infobox"]
    birth_date = infobox.get("born", "Unknown")
    print(f"Born: {birth_date}")
```

### Exploring Related Topics

Use links to discover related articles:

```python
result = get_article_links("Python (programming language)")
if result["success"]:
    # Get links to related programming languages
    programming_languages = [
        link for link in result["links"]
        if "programming language" in link["target"].lower()
    ]
    for lang in programming_languages:
        print(lang["target"])
```

### Error Handling

Always check for success:

```python
result = get_wikipedia_article("NonExistentArticle")
if not result["success"]:
    print(f"Error: {result['error']}")
    return
# Use result["content"] here
```

---

## Design Decisions

### Why Title Normalization?

Wikipedia titles have specific rules:
- Spaces vs. underscores
- Capitalization rules
- Redirects (multiple titles point to same article)
- Special characters

Normalization ensures you always get the correct article, regardless of how the title is written.

### Why Multiple Access Methods?

Different use cases need different information:
- **Full article**: Complete information, analysis
- **Summary**: Quick overview, introductions
- **Section**: Specific information, focused reading
- **Infobox**: Structured facts, data extraction
- **Links**: Related topics, exploration

Providing multiple methods makes the tools useful for many scenarios.

### Why Support Multiple Languages?

Wikipedia exists in many languages:
- Same article may have different information in different languages
- Users may prefer their native language
- Some topics are better covered in specific languages

Language support makes the tools accessible to a global audience.

### Why Structured Output?

All functions return structured dictionaries:
- Consistent interface across all functions
- Easy to process programmatically
- Clear error handling
- Metadata included (page IDs, URLs, etc.)

This makes it easy to build applications on top of these tools.

### Error Handling

The tools handle various error cases:
- **Article not found**: Title doesn't exist
- **Section not found**: Section name doesn't exist
- **No infobox**: Article doesn't have an infobox
- **Network errors**: Can't reach Wikipedia API

All errors are returned with clear messages to help diagnose issues.

