# Web Tools

A collection of tools for interacting with the web: fetching content, searching, parsing HTML, and checking username availability.

## Core HTTP Tools

### `fetch_url` - Get Web Page Content

**What it does**: Downloads the full content of a web page and returns it as text.

**Why we use it**: When you need the actual HTML or text content from a page. This is the foundation for most web scraping tasks.

**Why implemented this way**: 
- Uses GET requests (standard for retrieving content)
- Automatically follows redirects
- Cached for 30 minutes to avoid redundant requests and improve performance
- Returns structured data with status codes, headers, and content
- Uses browser User-Agent by default to avoid blocking

**How to use**:
```python
result = fetch_url("https://example.com/page")
if result["success"]:
    html_content = result["content"]
    print(f"Status: {result['status_code']}")
else:
    print(f"Error: {result['error']}")
```

**When to use**: When you need the raw HTML/text content of a page. Use this for scraping, content extraction, or when you need to parse the page yourself.

---

### `fetch_json` - Get JSON Data

**What it does**: Fetches a URL and automatically parses the response as JSON.

**Why we use it**: Many APIs return JSON. This function handles both the HTTP request and JSON parsing in one step, with proper error handling if the response isn't valid JSON.

**Why implemented this way**:
- Built on top of `fetch_url` to reuse HTTP logic
- Fails explicitly if JSON parsing fails (doesn't return raw content)
- Cached for 15 minutes (shorter than `fetch_url` since JSON APIs may update more frequently) to reduce redundant API calls
- Returns parsed JSON data directly, not a string

**How to use**:
```python
result = fetch_json("https://api.example.com/data")
if result["success"]:
    data = result["data"]  # Already parsed JSON (dict or list)
    print(data["key"])
```

**When to use**: When calling JSON APIs. Don't use this for HTML pages or non-JSON content.

---

### `post_request` - Send Data to a Server

**What it does**: Sends an HTTP POST request with data (typically JSON).

**Why we use it**: For submitting forms, calling APIs that require POST, or sending data to web services.

**Why implemented this way**:
- Automatically JSON-encodes dictionary data
- Sets appropriate Content-Type header
- Uses same error handling pattern as other fetch functions
- Not cached (POST requests are typically state-changing)

**How to use**:
```python
result = post_request(
    "https://api.example.com/submit",
    data={"name": "John", "email": "john@example.com"}
)
if result["success"]:
    print(result["content"])
```

**When to use**: When you need to send data to a server (form submissions, API calls that modify state).

---

### `check_url_status` - Check if a URL Exists

**What it does**: Checks if a website is accessible without downloading the full content. Uses HEAD requests by default for efficiency.

**Why we use it**: Much faster than `fetch_url` when you only need to know if a URL exists, what status code it returns, or what kind of error occurred. Perfect for validation, health checks, or checking many URLs quickly.

**Why implemented this way**:
- Uses HEAD requests by default (doesn't download body, just headers)
- Falls back to GET if HEAD isn't supported
- Provides detailed error information (DNS errors, connection errors, timeouts, HTTP status codes)
- Cached for 1 hour (status codes don't change frequently) to avoid redundant checks
- Returns structured error information instead of just raising exceptions

**How to use**:
```python
result = check_url_status("https://example.com/page")
if result["exists"]:
    print(f"URL exists with status {result['status_code']}")
else:
    print(f"Error: {result['error_type']} - {result['error_message']}")
```

**When to use**: 
- Validating URLs before processing
- Health checks
- Checking if resources are accessible
- When you need error details but not content
- **Don't use this** when you need the actual page content (use `fetch_url` instead)

---

## Domain and URL Utilities

### `extract_domain` - Get Clean Domain Name

**What it does**: Extracts a normalized domain name from any URL format. Always returns lowercase, removes `www.` and other common subdomains, handles multi-level TLDs correctly.

**Why we use it**: URLs come in many formats. This function ensures you always get a consistent, clean domain name for comparison or storage.

**Why implemented this way**:
- Handles full URLs, partial URLs, domains with/without www, and even URL patterns with placeholders
- Removes common subdomain prefixes (www, ww2, www2, etc.)
- Correctly handles multi-level TLDs like `bbc.co.uk` (returns `bbc.co.uk`, not `co.uk`)
- Always returns lowercase for consistency
- Returns `None` if extraction fails (doesn't raise exceptions)

**How to use**:
```python
domain = extract_domain("https://www.github.com/user/octocat")
# Returns: "github.com"

domain = extract_domain("https://www.bbc.co.uk/news")
# Returns: "bbc.co.uk"

domain = extract_domain("https://github.com/{username}")
# Returns: "github.com"
```

**When to use**: Whenever you need to extract or normalize a domain name from a URL. Use this before comparing domains or storing them.

---

### `filter_by_domain` - Filter URLs by Domain

**What it does**: Filters a list of URLs to keep only those matching (or not matching) specified domains.

**Why we use it**: When you have a list of URLs and want to filter them by domain. Used internally by `search_web` for whitelist/blacklist filtering.

**Why implemented this way**:
- Supports both positive (include) and negative (exclude) filtering
- Handles subdomains correctly (e.g., `api.github.com` matches filter `github.com`)
- Works with single domain or list of domains
- Uses `filter_type` parameter for clarity ("include" or "exclude")

**How to use**:
```python
urls = [
    "https://github.com/user",
    "https://stackoverflow.com/question",
    "https://example.com/page"
]

# Keep only GitHub URLs
github_urls = filter_by_domain(urls, "github.com", filter_type="include")

# Exclude GitHub URLs
non_github_urls = filter_by_domain(urls, "github.com", filter_type="exclude")

# Multiple domains
tech_urls = filter_by_domain(
    urls,
    ["github.com", "stackoverflow.com"],
    filter_type="include"
)
```

**When to use**: When you need to filter URLs by domain. Typically used internally, but available if you need to filter your own URL lists.

---

## HTML Parsing Tools

### `parse_html` - Parse and Extract from HTML

**What it does**: Parses HTML content and optionally extracts specific elements using CSS selectors.

**Why we use it**: HTML is messy. This function uses BeautifulSoup to parse it properly and extract what you need.

**Why implemented this way**:
- Uses BeautifulSoup's robust HTML parser (handles malformed HTML)
- Supports CSS selectors for flexible element selection
- Returns structured data (text, HTML, attributes) for each element
- Extracts page title automatically
- Returns full text if no selector provided

**How to use**:
```python
# Parse and get full text
result = parse_html(html_content)
if result["success"]:
    print(result["text"])  # All text from page
    print(result["title"])  # Page title

# Extract specific elements
result = parse_html(html_content, selector=".article-title")
if result["success"]:
    for element in result["elements"]:
        print(element["text"])
        print(element["html"])
```

**When to use**: When you need to extract specific content from HTML. Use CSS selectors to target the elements you want.

---

### `extract_text` - Get Plain Text from HTML

**What it does**: Removes all HTML tags and returns just the text content.

**Why we use it**: Quick way to get readable text from HTML without dealing with tags or structure.

**Why implemented this way**: Simple wrapper around BeautifulSoup's text extraction. No selectors, no structure—just text.

**How to use**:
```python
text = extract_text(html_content)
# Returns: "This is the text content without any HTML tags"
```

**When to use**: When you just need the text content and don't care about structure or specific elements.

---

### `find_elements` - Find Elements by CSS Selector

**What it does**: Finds HTML elements matching a CSS selector and returns their details.

**Why we use it**: When you need to find specific elements (links, headings, divs, etc.) by their CSS selector.

**Why implemented this way**: Direct CSS selector matching. Returns structured data for each match.

**How to use**:
```python
elements = find_elements(html_content, "a.link")
for elem in elements:
    print(elem["text"])  # Link text
    print(elem["attributes"]["href"])  # Link URL
```

**When to use**: When you need to find specific HTML elements by CSS selector.

---

### `extract_from_page` - Extract Information Using LLM

**What it does**: Fetches a web page and uses an LLM to extract specific information from it.

**Why we use it**: Sometimes you need to extract information that's not easily parseable with CSS selectors. The LLM can understand context and find information even if the HTML structure varies.

**Why implemented this way**:
- Combines `fetch_url` and LLM extraction
- Uses browser User-Agent to avoid blocking
- Truncates content if too long (LLMs have token limits)
- Returns extracted information as text

**How to use**:
```python
result = extract_from_page(
    url="https://example.com/product",
    query="What is the price?",
    llm=my_llm
)
if result["success"]:
    print(result["extracted"])  # The extracted information
```

**When to use**: When you need to extract information that requires understanding context or when HTML structure is inconsistent. More expensive than CSS selectors but more flexible.

---

## Web Search

### `search_web` - Search the Internet

**What it does**: Searches the web using Brave Search API and returns results. Supports domain whitelisting and blacklisting.

**Why we use it**: When you need to find information on the internet programmatically. Brave Search provides high-quality results without the limitations of scraping search engines.

**Why implemented this way**:
- Uses Brave Search API (requires API key)
- Domain filtering happens after search (more flexible than search engine filters)
- Blacklist applied first, then whitelist (allows excluding spam, then narrowing to trusted domains)
- Results are cached for 1 day (search results don't change that frequently) to reduce API costs and improve performance
- Returns structured results with title, URL, and snippet

**How to use**:
```python
# Basic search
result = search_web("python programming", max_results=10)

# Search with domain whitelist (only results from these domains)
result = search_web(
    "python tutorial",
    domain_whitelist=["python.org", "realpython.com"],
    max_results=10
)

# Search with domain blacklist (exclude these domains)
result = search_web(
    "python tutorial",
    domain_blacklist=["spam.com", "ads.com"],
    max_results=10
)

# Both whitelist and blacklist
result = search_web(
    "python tutorial",
    domain_whitelist=["python.org"],
    domain_blacklist=["ads.python.org"],  # Exclude ads subdomain
    max_results=10
)

if result["success"]:
    for item in result["results"]:
        print(f"{item['title']}: {item['url']}")
```

**When to use**: 
- Finding information on the internet
- Discovering URLs related to a topic
- Research tasks
- **Note**: Requires Brave API key (set `BRAVE_API_KEY` environment variable)

---

### `search_web_simple` - Simple Search Results

**What it does**: Same as `search_web` but returns just the results list (no metadata).

**Why we use it**: Convenience function when you only need the results, not the full response structure.

**How to use**:
```python
results = search_web_simple("python programming")
# Returns: [{"title": "...", "url": "...", "snippet": "..."}, ...]
```

**When to use**: When you just need the results list and don't care about success status or metadata.

---

## Username Availability Checking

The username checking system works in three stages:

1. **Discover URL pattern** - Find how usernames appear in URLs (e.g., `github.com/{username}`)
2. **Discover signature** - Learn what distinguishes existing vs non-existing usernames
3. **Check availability** - Use the signature to check if a username exists

### `discover_username_url_pattern` - Find Username URL Format

**What it does**: Automatically discovers how usernames appear in URLs on a domain by searching the web.

**Why we use it**: Different sites use different URL patterns. GitHub uses `/user`, PyPI uses `/user/{username}/`, Reddit uses `/user/{username}`. This function finds the pattern automatically.

**Why implemented this way**:
- Uses web search to find profile URLs (no hardcoded patterns)
- Validates that found URLs actually contain the domain and username
- Works generically for any domain (no site-specific logic)
- Cached for 30 days (URL patterns don't change often) to avoid redundant web searches
- Requires Brave API key (uses web search)

**How to use**:
```python
result = discover_username_url_pattern(
    domain="github.com",
    existing_username="octocat",
    brave_api_key=api_key
)
if result["success"]:
    print(result["url_pattern"])  # "https://github.com/{username}"
```

**When to use**: When you need to find the URL pattern for a domain. Usually called automatically by higher-level functions.

---

### `discover_username_signature` - Learn What Distinguishes Existing vs Non-Existing Usernames

**What it does**: Tests known existing and non-existing usernames to discover what makes them different (status codes, error types, content keywords).

**Why we use it**: Different sites respond differently. Some return 404 for non-existing users, others return 200 with "user not found" text. This function learns the pattern automatically.

**Why implemented this way**:
- Tests real usernames to discover patterns (no assumptions)
- Identifies distinguishing factors (status_code, error_type, content_keywords)
- Validates that the signature can actually distinguish between existing and non-existing
- Works generically for any domain
- Cached for 14 days (signatures are relatively stable) to avoid redundant discovery requests
- Can work with just a domain (discovers URL pattern first) or with a URL pattern

**How to use**:
```python
# With domain (discovers URL pattern first)
result = discover_username_signature(
    domain="github.com",
    brave_api_key=api_key
)

# With URL pattern (if you already know it)
result = discover_username_signature(
    url_pattern="https://github.com/{username}",
    existing_username="octocat"
)

if result["success"]:
    signature = result["existing_signature"]
    print(f"Existing users have status {signature['status_code']}")
    print(f"Distinguishing factors: {result['distinguishing_factors']}")
```

**When to use**: When you need to learn how a domain distinguishes existing from non-existing usernames. Usually called automatically, but useful if you want to discover signatures for new domains.

---

### `check_username_availability` - Check Multiple Usernames

**What it does**: Checks which usernames are available (don't exist) and which are unavailable (exist) on a domain.

**Why we use it**: The main function for checking username availability. Handles the full workflow: discovering URL pattern, discovering signature, then checking each username.

**Why implemented this way**:
- Can work with just a domain (discovers everything automatically)
- Can work with a URL pattern (if you already know it)
- Checks multiple usernames efficiently
- Uses cached single-username checks for performance
- Returns organized results (available, unavailable, undetermined)

**How to use**:
```python
# Check multiple usernames on a domain
result = check_username_availability(
    usernames=["alice", "bob", "charlie"],
    domain="github.com",
    brave_api_key=api_key
)

if result["success"]:
    print(f"Available: {result['available_usernames']}")
    print(f"Unavailable: {result['unavailable_usernames']}")
    print(f"Undetermined: {result['undetermined_usernames']}")
    
    # Check individual results
    for username, status in result["results"].items():
        print(f"{username}: exists={status['exists']}")
```

**When to use**: When you need to check username availability on a domain. This is the main function you'll use.

---

### `check_single_username_exists` - Check One Username

**What it does**: Checks if a single username exists using a known signature.

**Why we use it**: Lower-level function used by `check_username_availability`. Cached individually for performance when checking many usernames.

**Why implemented this way**:
- Requires pre-discovered signature (faster than discovering each time)
- Cached for 7 days (username existence doesn't change frequently) to avoid redundant checks when checking multiple usernames
- Used internally by `check_username_availability` for efficiency

**How to use**: Usually called automatically by `check_username_availability`. Use directly only if you have a signature and want to check one username efficiently.

---

## Cache Control

All cached functions support cache control:

You can disable caching for a specific call using `use_cache=False`:
```python
result = fetch_url("https://example.com", use_cache=False)
```

You can delete cached values:
```python
fetch_url.delete("https://example.com")
```

You can check if a value is cached:
```python
if fetch_url.exists("https://example.com"):
    print("This URL is cached")
```

---

## Common Patterns

### Error Handling

Always check `success` before using results:
```python
result = fetch_url("https://example.com")
if not result["success"]:
    print(f"Error: {result['error']}")
    return
# Use result["content"] here
```

### Using Custom Headers

```python
headers = {"Authorization": f"Bearer {token}"}
result = fetch_url("https://api.example.com/data", headers=headers)
```

### Domain Filtering in Search

```python
# Only get results from trusted domains
result = search_web(
    "python tutorial",
    domain_whitelist=["python.org", "realpython.com"],
    max_results=10
)

# Exclude spam domains
result = search_web(
    "python tutorial",
    domain_blacklist=["spam.com", "ads.com"],
    max_results=10
)
```

### Checking Username Availability

```python
# Simple check
result = check_username_availability(
    usernames=["alice", "bob"],
    domain="github.com",
    brave_api_key=api_key
)

# With known URL pattern (faster)
result = check_username_availability(
    usernames=["alice", "bob"],
    url_pattern="https://github.com/{username}",
    brave_api_key=api_key
)
```

---

## Design Decisions

### Why Brave Search Only?

We removed DuckDuckGo support because:
- Brave Search provides more reliable, consistent results
- Domain filtering works better when applied after search
- Reduces maintenance burden (one search engine to maintain)
- Brave API provides structured results without HTML parsing

### Why Domain Filtering After Search?

Domain filtering happens in `search_web`, not in `search_brave`, because:
- More flexible (can combine whitelist and blacklist)
- Works consistently regardless of search engine
- Allows excluding subdomains (e.g., whitelist `github.com` but blacklist `ads.github.com`)

### Why Signature-Based Username Checking?

Instead of hardcoding rules for each site, we use signature discovery because:
- Works for any domain automatically
- Adapts if sites change their behavior
- No maintenance needed for new sites
- More reliable than assuming status codes

### Why Caching?

Web requests are slow and expensive. Caching:
- Reduces redundant requests
- Improves performance
- Saves API costs (Brave charges per request)
- Makes development faster (don't wait for network)

Cache expiration times are set based on how frequently data changes:
- Search results: 1 day (results are relatively stable)
- URL status: 1 hour (status codes don't change often)
- Username signatures: 14 days (site behavior is stable)
- Page content: 30 minutes (content may update)

