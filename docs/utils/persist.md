# Persist Decorator

A flexible caching/persistence decorator for function results. Caches function outputs based on argument hashing, supporting both in-memory and disk-based storage with optional expiration.

## What It Does

The `@persist` decorator automatically caches the results of function calls. When you call a decorated function with the same arguments, it returns the cached result instead of re-executing the function.

**Why we use it**: 
- Avoid redundant expensive operations (API calls, web requests, computations)
- Improve performance by reusing results
- Reduce costs (fewer API calls)
- Speed up development (don't wait for network requests during testing)

## Basic Usage

```python
from ixmachina.utils.persist import persist

@persist()
def expensive_function(x, y):
    # This will only execute once per unique (x, y) combination
    result = do_expensive_computation(x, y)
    return result

# First call: executes function
result1 = expensive_function(1, 2)

# Second call with same args: returns cached result
result2 = expensive_function(1, 2)  # Fast! No computation

# Different args: executes function again
result3 = expensive_function(3, 4)  # Executes, then caches
```

## Storage Options

### Disk Caching (Default)

By default, results are cached to disk in `.cache/ix/<function_name>/` directory.

```python
@persist()
def fetch_data(url):
    # Results cached to disk
    return requests.get(url).json()
```

**Why disk caching**:
- Persists across program restarts
- Can handle large amounts of data
- Survives crashes
- Good for expensive operations you don't want to repeat

### Memory Caching

For faster access, cache in memory only (lost when program exits):

```python
@persist(memory=True)
def quick_computation(x):
    # Results cached in memory only
    return x * 2
```

**Why memory caching**:
- Much faster than disk (no I/O)
- Good for frequently-called functions
- Use when you don't need persistence across restarts

## Expiration Mechanism

### How Expiration Works

When `expire_seconds` is set, cached results are considered expired after that many seconds. The expiration mechanism uses **timestamps** to track when results were cached.

#### For Memory Cache

1. **When caching**: Stores `time.time()` timestamp with the result
2. **When checking**: Compares current time with stored timestamp
3. **Expiration check**: `(current_time - cache_timestamp) < expire_seconds`

```python
@persist(memory=True, expire_seconds=3600)  # 1 hour
def get_data():
    return fetch_from_api()

# First call: executes and stores with timestamp
result1 = get_data()  # Timestamp: 1000.0

# 30 minutes later (timestamp: 1180.0)
result2 = get_data()  # Returns cached (1800 < 3600)

# 2 hours later (timestamp: 8200.0)
result3 = get_data()  # Expired! Executes again (7200 >= 3600)
```

#### For Disk Cache

Disk caching uses **two timestamp mechanisms** for reliability:

1. **File modification time** (`os.path.getmtime`): The filesystem's record of when the file was last modified
2. **Stored timestamp**: A `time.time()` timestamp stored inside the pickle file

**Why two mechanisms?**
- File mtime is fast to check (no file read needed)
- Stored timestamp is more accurate (survives file copies, preserves exact cache time)
- Both are checked for safety

**Expiration check process**:
1. Check file mtime: `(current_time - file_mtime) >= expire_seconds` → expired
2. If file mtime check passes, read file and check stored timestamp: `(current_time - stored_timestamp) >= expire_seconds` → expired
3. If both checks pass, use cached result

```python
@persist(expire_seconds=86400)  # 1 day
def fetch_url(url):
    return requests.get(url).text

# First call: creates cache file with timestamp
result1 = fetch_url("https://example.com")
# File created at: 1000.0 (Unix timestamp)
# Stored timestamp: 1000.0

# 12 hours later: 53200.0
result2 = fetch_url("https://example.com")
# File mtime check: (53200 - 1000) = 52200 < 86400 ✓
# Stored timestamp check: (53200 - 1000) = 52200 < 86400 ✓
# Returns cached result

# 2 days later: 173800.0
result3 = fetch_url("https://example.com")
# File mtime check: (173800 - 1000) = 172800 >= 86400 ✗
# Expired! Executes function and updates cache
```

**Important notes**:
- Timestamps are stored as Unix timestamps (seconds since epoch) using `time.time()`
- Expiration is checked **every time** the function is called (not periodically)
- Expired cache entries are **not automatically deleted** - they're just ignored
- If a cache file is corrupted or missing timestamp, it's treated as expired

### No Expiration

If `expire_seconds` is `None` (default), cached results never expire:

```python
@persist()  # No expiration
def stable_data():
    return {"version": "1.0"}  # This will be cached forever
```

**When to use no expiration**:
- Data that never changes
- Expensive operations you want to cache permanently
- Development/testing scenarios

## Cache Path Management

### Global Cache Path

You can set a global cache path that all cached functions use:

```python
from ixmachina.utils.persist import set_cache_path, persist

# Set global cache path (e.g., in tests)
set_cache_path(".cache/test")

@persist()
def my_function(x):
    return x * 2

# Cache files will be in .cache/test/my_function/
```

**Why global cache path**:
- Useful for tests (isolate test cache from production)
- Can change cache location for entire application
- Individual functions can still override with `cache_path` parameter

### Per-Call Cache Path

You can override the cache path for a specific call:

```python
@persist()
def my_function(x, cache_path=None):
    return x * 2

# Use default cache path
result1 = my_function(1)

# Use custom cache path for this call
result2 = my_function(1, cache_path=".cache/custom")
```

**Note**: The `cache_path` parameter is automatically added to decorated functions. You don't need to include it in your function signature.

## Cache Control

### Disable Caching for a Call

You can skip the cache for a specific call:

```python
@persist()
def fetch_data(url, use_cache=True):
    return requests.get(url).json()

# Use cache (default)
result1 = fetch_data("https://api.example.com/data")

# Skip cache, always execute
result2 = fetch_data("https://api.example.com/data", use_cache=False)
```

**When to disable caching**:
- Testing with fresh data
- Debugging (want to see actual function execution)
- When you know data has changed

### Delete Cached Value

Remove a specific cached entry:

```python
@persist()
def fetch_data(url):
    return requests.get(url).json()

# Cache a result
result = fetch_data("https://api.example.com/data")

# Delete the cached value
fetch_data.delete("https://api.example.com/data")

# Next call will execute function again
result = fetch_data("https://api.example.com/data")  # Executes
```

**Use cases**:
- Invalidate specific cache entries
- Clear cache for changed data
- Testing (reset cache state)

### Check if Cached

Check if a value is cached (and not expired):

```python
@persist(expire_seconds=3600)
def fetch_data(url):
    return requests.get(url).json()

# Check if cached
if fetch_data.exists("https://api.example.com/data"):
    print("This URL is cached and not expired")
else:
    print("Not cached or expired")
```

**Use cases**:
- Conditional logic based on cache state
- Debugging cache behavior
- Pre-checking before expensive operations

## How Argument Hashing Works

The cache key is generated by hashing function arguments. This ensures:
- Same arguments → same cache key → same cached result
- Different arguments → different cache key → different cached result

**Hashing process**:
1. Arguments are serialized (JSON for simple types, pickle for complex types)
2. SHA-256 hash is computed
3. First 16 characters of hash used as filename (sufficient uniqueness)

**Important**:
- `cache_path` and `use_cache` parameters are **excluded** from the hash
- This means `func(x, cache_path="A")` and `func(x, cache_path="B")` use the same cache entry
- Only actual function arguments affect the cache key

## Cache File Structure

### Disk Cache Organization

```
.cache/ix/
  ├── function_name_1/
  │   ├── abc123def456.cache
  │   ├── def456ghi789.cache
  │   └── ...
  ├── function_name_2/
  │   ├── xyz789abc123.cache
  │   └── ...
  └── ...
```

**Structure**:
- Base directory: `.cache/ix` (or global cache path)
- Subdirectory: Function name (one per decorated function)
- Files: `{hash[:16]}.cache` (pickle files containing cached data)

### Cache File Format

Each cache file is a pickle file containing:
```python
{
    "result": <function_return_value>,  # The actual cached result
    "timestamp": 1234567890.123,        # Unix timestamp when cached (if expiration set)
}
```

**Why pickle**:
- Handles any Python object (not just JSON-serializable)
- Preserves object types and structure
- Standard Python serialization format

## Common Patterns

### Caching API Calls

```python
@persist(expire_seconds=3600)  # Cache for 1 hour
def fetch_user_data(user_id):
    return requests.get(f"https://api.example.com/users/{user_id}").json()

# First call: API request
user = fetch_user_data(123)

# Within 1 hour: Returns cached result
user = fetch_user_data(123)  # No API call

# After 1 hour: API request again
user = fetch_user_data(123)  # Fresh data
```

### Caching Expensive Computations

```python
@persist()  # Cache forever (computation is deterministic)
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# First call: Computes
result = fibonacci(30)

# Subsequent calls: Instant (cached)
result = fibonacci(30)  # Fast!
```

### Testing with Cache Control

```python
# In test setup
from ixmachina.utils.persist import set_cache_path

def test_my_function():
    # Use test-specific cache
    set_cache_path(".cache/test")
    
    # Test with fresh data
    result = my_function("test", use_cache=False)
    
    # Test with cached data
    result = my_function("test", use_cache=True)
```

### Conditional Caching

```python
@persist(expire_seconds=3600)
def fetch_data(url, force_refresh=False):
    if force_refresh:
        # Delete cache and fetch fresh
        fetch_data.delete(url)
    return requests.get(url).json()

# Normal usage (uses cache)
data = fetch_data("https://api.example.com/data")

# Force refresh
data = fetch_data("https://api.example.com/data", force_refresh=True)
```

## Design Decisions

### Why Two Timestamp Checks for Disk Cache?

1. **File mtime check**: Fast, no file read needed. Good for quick expiration checks.
2. **Stored timestamp check**: More accurate, survives file operations (copy, move). Ensures correctness.

Both are checked because:
- File mtime can be unreliable (system clock changes, file copies)
- Stored timestamp is authoritative but requires file read
- Checking both provides redundancy and performance

### Why SHA-256 Hashing?

- Cryptographic hash ensures uniqueness
- Deterministic (same input → same hash)
- Collision-resistant (practically unique)
- Fast computation

### Why Exclude `cache_path` and `use_cache` from Hash?

These are cache control parameters, not function arguments. Including them would create separate cache entries for the same logical function call, which defeats the purpose of caching.

### Why Pickle for Cache Files?

- Handles any Python object (not limited to JSON types)
- Preserves object types and structure
- Standard Python serialization
- Works with complex nested structures

### Why 16 Characters of Hash for Filename?

- SHA-256 produces 64-character hex strings
- First 16 characters provide sufficient uniqueness for practical purposes
- Shorter filenames are easier to work with
- Collision probability is negligible for typical use cases

## Performance Considerations

### Memory vs Disk

- **Memory cache**: ~1000x faster access, but limited by RAM
- **Disk cache**: Slower access (~1ms vs ~1μs), but unlimited size

**Choose based on**:
- Access frequency: Frequent → memory, occasional → disk
- Data size: Small → memory, large → disk
- Persistence needs: Temporary → memory, permanent → disk

### Expiration Check Overhead

- **Memory**: Negligible (just timestamp comparison)
- **Disk**: Small overhead (file mtime check + optional file read)

For high-frequency calls, consider:
- Longer expiration times (fewer checks)
- Memory caching (faster checks)
- No expiration (no checks)

## Troubleshooting

### Cache Not Working

1. Check if `use_cache=False` was passed
2. Verify cache path is writable
3. Check expiration (may have expired)
4. Ensure arguments are hashable

### Stale Cache

1. Use `function.delete()` to clear specific entries
2. Set `use_cache=False` for fresh data
3. Reduce `expire_seconds` if data changes frequently
4. Manually delete cache files if needed

### Cache Files Growing Large

1. Set expiration to limit cache lifetime
2. Periodically clean old cache files
3. Use memory cache for temporary data
4. Consider cache size limits (not built-in)

