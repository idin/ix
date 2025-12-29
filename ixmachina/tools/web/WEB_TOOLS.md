# Web Tools

Tools for fetching content from URLs and making HTTP requests.

## When to Use What

### Basic HTTP Requests

- **`fetch_url`**: Use when you need the raw response content (HTML, text, binary data, etc.). Returns the content as a string and all response metadata.

- **`fetch_json`**: Use when you know the response will be JSON. Automatically parses the JSON and handles parsing errors. If parsing fails, the operation fails—you don't get raw content as a fallback.

- **`post_request`**: Use when you need to send data to a server (form submissions, API calls that require POST, etc.). Automatically JSON-encodes dictionary data.

- **`check_url_status`**: Use when you need to check if a website exists and what kind of error it returns. This is more efficient than `fetch_url` because it uses HEAD requests by default and provides detailed error information (DNS errors, connection errors, timeouts, HTTP status codes). Use this for URL validation, health checks, or when you only need to know if a resource is accessible, not its content.

### Username Existence Checking

There are three approaches to checking if a username exists on a platform:

#### 1. `check_username_exists` - Hardcoded Rules (Recommended for Supported Platforms)

**When to use**: When checking usernames on platforms that are already supported (GitHub, PyPI, Instagram, Twitter, LinkedIn, Reddit, Stack Overflow, Medium, YouTube, GitLab, Bitbucket, npm, Docker Hub).

**Why**: This is the fastest and most reliable method. It uses pre-configured rules for each platform that combine HTTP status codes and content keyword detection. The rules are maintained in the codebase and tested.

**Example**:
```python
result = check_username_exists(username="octocat", platform="github")
if result["exists"]:
    print(f"Username exists!")
elif result["exists"] is False:
    print(f"Username does not exist.")
else:
    print(f"Could not determine: {result['error']}")
```

#### 2. `check_username_adaptive` - Adaptive Discovery (For New Platforms)

**When to use**: When checking usernames on platforms that are NOT in the supported list, or when you want to ensure the detection logic is up-to-date for a platform that may have changed.

**Why**: This function automatically discovers the platform's signature by testing known existing and non-existing usernames. It then uses that signature to check your target username. This is useful for:
- New platforms not yet in the hardcoded list
- Platforms that may have changed their response patterns
- One-off checks where you don't want to maintain hardcoded rules

**How it works**: 
1. Tests a known existing username (uses defaults from `KNOWN_EXISTING_USERNAMES` if not provided)
2. Tests a known non-existing username (generates one if not provided)
3. Compares responses to discover distinguishing patterns (status codes, content keywords)
4. Validates that the patterns can actually distinguish between existing and non-existing
5. Uses the discovered signature to check your target username

**Example**:
```python
result = check_username_adaptive(
    username="myusername",
    platform="newplatform",
    url_template="https://newplatform.com/users/{username}",
    known_existing_username="verified_user",  # Optional - uses default if available
)
```

**Important**: The function validates that the existing username actually works (returns 200 or accessible status). If it doesn't, the function fails with an error—existing usernames must always work.

#### 3. `discover_username_signature` + `check_username_with_signature` - Manual Control

**When to use**: When you want to discover a signature once and reuse it for multiple username checks, or when you need fine-grained control over the discovery process.

**Why**: If you're checking many usernames on the same platform, discovering the signature once and reusing it is more efficient than calling `check_username_adaptive` for each username.

**Example**:
```python
# Discover signature once
signature_result = discover_username_signature(
    platform="newplatform",
    url_template="https://newplatform.com/users/{username}",
    known_existing_username="verified_user",
)
signature = signature_result["signature"]

# Check multiple usernames using the same signature
for username in ["user1", "user2", "user3"]:
    result = check_username_with_signature(
        username=username,
        signature=signature,
    )
    print(f"{username}: exists={result['exists']}")
```

### Choosing the Right Approach

- **Use `check_username_exists`** if the platform is in the supported list (GitHub, PyPI, etc.)
- **Use `check_username_adaptive`** if the platform is new or you want automatic discovery
- **Use `discover_username_signature` + `check_username_with_signature`** if you need to check many usernames on the same platform and want to optimize by discovering the signature once

## Important Behaviors

### Error Handling

All functions return a dictionary with a `success` boolean. Always check `success` before using the response data. If `success` is `False`, check the `error` field for details.

### Timeouts

All functions have a default timeout of 30 seconds. If a request takes longer, it will fail. You can override this with the `timeout` parameter.

### Headers

You can pass custom headers to any function. Common use cases:
- Authentication tokens: `headers={"Authorization": "Bearer token"}`
- Custom user agents: `headers={"User-Agent": "MyApp/1.0"}`
- Content type for POST: `headers={"Content-Type": "application/json"}`

Note: `post_request` automatically sets `Content-Type: application/json` when you pass `data`, but you can override it with custom headers.

### Redirects

All functions follow redirects automatically. The `url` field in the response shows the final URL after all redirects.

## Return Value Structure

All functions return a dictionary with:
- `success`: Boolean indicating if the operation succeeded
- `error`: Error message if failed (None if successful)
- `status_code`: HTTP status code (even on failure, if a response was received)
- `url`: Final URL after redirects
- `headers`: Response headers as a dictionary

Additionally:
- `fetch_url` and `post_request` return `content` (string) and `content_type`
- `fetch_json` returns `data` (parsed JSON object/list) instead of `content`

## Common Patterns

### Checking for Success

```python
result = fetch_url("https://example.com")
if not result["success"]:
    print(f"Failed: {result['error']}")
    return
# Use result["content"] here
```

### Handling Different Status Codes

```python
result = fetch_url("https://api.example.com/data")
if result["success"]:
    if result["status_code"] == 200:
        # Process content
    elif result["status_code"] == 404:
        # Handle not found
    else:
        # Handle other status codes
```

### Making Authenticated Requests

```python
headers = {"Authorization": f"Bearer {token}"}
result = fetch_json("https://api.example.com/data", headers=headers)
```
