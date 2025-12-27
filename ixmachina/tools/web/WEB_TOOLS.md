# Web Tools

Tools for fetching content from URLs and making HTTP requests.

## When to Use What

- **`fetch_url`**: Use when you need the raw response content (HTML, text, binary data, etc.). Returns the content as a string and all response metadata.

- **`fetch_json`**: Use when you know the response will be JSON. Automatically parses the JSON and handles parsing errors. If parsing fails, the operation fails—you don't get raw content as a fallback.

- **`post_request`**: Use when you need to send data to a server (form submissions, API calls that require POST, etc.). Automatically JSON-encodes dictionary data.

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
