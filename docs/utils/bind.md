# Tool Binding: Design and Philosophy

## The Problem We're Solving

When building AI agents that use tools, you often need tools to access external objects like:
- The agent itself (to memorize things, reflect, etc.)
- API clients (Gmail, databases, web services)
- Shared resources (calculators, storage, loggers)

### Why Traditional Approaches Don't Work

**Option 1: Pass everything as parameters**

```python
def send_email(to: str, subject: str, body: str, agent, gmail_client, logger, db):
    gmail_client.send(to=to, subject=subject, body=body)
    agent.memorize(f"Sent email to {to}")
    logger.log(f"Sent to {to}")
```

**Critical problem:** AI agents can't call this function!

When an agent sees this signature, it tries to generate a tool call like:

```json
{
  "name": "send_email",
  "arguments": {
    "to": "user@example.com",
    "subject": "Hello",
    "body": "...",
    "agent": ???,           // Can't serialize the agent object!
    "gmail_client": ???,    // Can't serialize the Gmail client!
    "logger": ???,          // Can't serialize the logger!
    "db": ???               // Can't serialize the database!
  }
}
```

The agent only has access to:
- Primitive types (strings, numbers, booleans)
- Lists and dictionaries of primitives
- References to previous tool call results (if we implement that)

It **cannot** create or pass complex objects like API clients or the agent itself.

**Option 2: Use closures**

```python
def create_tools(agent, gmail, logger):
    def send_email(to: str, subject: str, body: str):
        # Access agent, gmail, logger from closure
        gmail.send(to=to, subject=subject, body=body)
        agent.memorize(f"Sent email to {to}")
    return send_email
```

This works! But it's painful when you have:
- Multiple tools that need different combinations of objects
- Tools defined in different modules or files
- Tools that need to be registered dynamically
- Dozens of tools (you need a factory function for each)

**Option 3: Global variables**

```python
# module level
_agent = None
_gmail = None

def send_email(to: str, subject: str, body: str):
    global _agent, _gmail
    _gmail.send(...)
    _agent.memorize(...)
```

This works but is fragile:
- Global state makes testing harder
- No clear connection between tools and their dependencies
- Name collisions across modules
- Hard to have multiple agents or contexts

## Our Solution: `@bind` Decorator

The `@bind` decorator lets you attach objects to functions **without** them appearing in the function signature:

```python
from ixmachina.utils import bind, ToolContext

# Define the tool - notice clean signature with only the actual inputs
@bind(agent=my_agent, gmail=gmail_client)
def send_email(to: str, subject: str, body: str):
    """Send an email and memorize the action."""
    gmail.send(to=to, subject=subject, body=body)
    agent.memorize(f"Sent email to {to}")
```

**From the agent's perspective**, it sees:

```python
def send_email(to: str, subject: str, body: str):
    """Send an email and memorize the action."""
```

The agent can call this! It only needs to provide strings:

```json
{
  "name": "send_email",
  "arguments": {
    "to": "user@example.com",
    "subject": "Hello",
    "body": "How are you?"
  }
}
```

**Inside the function**, `agent` and `gmail` are magically available - they were injected by the decorator.

This solves the serialization problem: the agent only sees parameters it can actually provide, while the function still has access to the objects it needs.

## How It Works: The Technical Challenge

### Python's Name Resolution Order

When Python looks up a variable name, it searches in this order:
1. **Local** scope (variables defined inside the function)
2. **Enclosing** scope (closures from outer functions)
3. **Global** scope (module-level variables)
4. **Built-in** scope (Python's built-in names)

This is called the LEGB rule: Local → Enclosing → Global → Built-in.

### Why We Can't Use Closures

Initially, we tried using closures (enclosing scope):

```python
def bind(**objects):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Try to inject objects somehow?
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

**Problem:** There's no way to inject variables into the function's local scope after it's defined! Python's bytecode is compiled, and the function's local variables are fixed.

### Why We Can't Use Parameters

We could inject objects as keyword arguments:

```python
def wrapper(*args, **kwargs):
    kwargs.update(bound_objects)  # Add agent, gmail, etc.
    return func(*args, **kwargs)
```

**Problem:** Now the function signature must accept these parameters:

```python
def send_email(to: str, subject: str, body: str, agent, gmail):
    #                                              ^^^^^^^^^^^^^^
    #                                         Defeats the purpose!
```

This defeats our goal of keeping signatures clean.

### Our Solution: Global Scope Injection

Since we can't modify Local or Enclosing scopes, we inject into the Global scope:

```python
import types

# Copy the function's globals
new_globals = func.__globals__.copy()

# Add our bound objects
new_globals.update(bound_objects)

# Create a new function with the updated globals
new_func = types.FunctionType(
    func.__code__,      # Same bytecode
    new_globals,        # Globals now include our objects
    func.__name__,
    func.__defaults__,
    func.__closure__     # Preserve closure if any
)
```

When the function executes, it looks up `agent` and `gmail` as global variables and finds our injected objects.

## Design Trade-offs

### ✅ Advantages

1. **Clean function signatures**: Only actual parameters appear
2. **No closure overhead**: Doesn't create nested functions
3. **Works with agents**: Functions can be inspected, their docstrings work properly
4. **Flexible**: Can use `ToolContext` for shared objects or bind individually
5. **Introspectable**: Bound objects are stored in `func._bound_objects`

### ⚠️ Risks and Limitations

**Risk: Global namespace pollution**

Bound objects override global variables with the same name. If your module has:

```python
agent = None  # Some global variable

@bind(agent=my_agent)
def tool():
    print(agent)  # Will see my_agent, not the global None
```

**Mitigation:** Use distinctive names for bound objects. We document this prominently with a WARNING in the docstring.

**Limitation: Can't override at runtime**

Once bound, the objects are "baked in":

```python
@bind(storage=storage1)
def save(text):
    storage.store(text)

# This won't work - storage is already bound to storage1
save("hello", storage=storage2)  # TypeError: unexpected keyword argument
```

This is intentional - bound objects are meant to be stable context, not dynamic parameters.

## The `dir()` Bug We Fixed

Initial implementation used `dir(context)` to extract object names from `ToolContext`:

```python
objects_to_bind = {
    key: getattr(context, key)
    for key in dir(context)
    if not key.startswith('_')
}
```

**Problem:** `dir()` returns ALL attributes, including methods and properties! If someone subclassed `ToolContext`, those methods would get injected into function globals.

**Fix:** Store object names explicitly:

```python
class ToolContext:
    def __init__(self, **objects):
        self._object_names = set(objects.keys())  # Store what was passed
        for name, obj in objects.items():
            setattr(self, name, obj)

# Later, only bind what was explicitly stored
objects_to_bind = {
    key: getattr(context, key)
    for key in context._object_names  # Only user-provided objects
}
```

## Usage Patterns

### Pattern 1: Direct Binding

Best for one-off tools:

```python
@bind(storage=my_storage, logger=my_logger)
def log_and_store(message: str):
    logger.log(message)
    storage.store(message)
```

### Pattern 2: ToolContext for Shared Objects

Best when multiple tools share the same objects:

```python
ctx = ToolContext(agent=my_agent, gmail=gmail_client, db=database)

@bind(context=ctx)
def send_email(to: str):
    gmail.send(to=to)
    agent.memorize(f"Sent to {to}")

@bind(context=ctx)
def save_contact(name: str, email: str):
    db.save(name, email)
    agent.memorize(f"Saved {name}")
```

### Pattern 3: Context + Additional Objects

Mix shared context with tool-specific objects:

```python
ctx = ToolContext(agent=my_agent, gmail=gmail_client)

# This tool also needs a special formatter
@bind(context=ctx, formatter=email_formatter)
def send_formatted_email(to: str, template: str):
    body = formatter.format(template)
    gmail.send(to=to, body=body)
    agent.memorize(f"Sent {template} to {to}")
```

## Why This Matters for AI Agents

This isn't just about clean code - it's about making tools **callable by AI agents at all**.

### The Fundamental Constraint

AI agents communicate through JSON (or similar structured formats). When an LLM decides to use a tool, it generates:

```json
{
  "tool_name": "send_email",
  "arguments": {
    "to": "user@example.com",
    "subject": "Hello"
  }
}
```

The agent can only provide:
- ✅ Primitives: strings, numbers, booleans, null
- ✅ Collections: lists and dictionaries of primitives
- ✅ References: `<sys:self]`, `<obj:saved_object]` (our special syntax)
- ❌ Complex objects: API clients, database connections, file handles, etc.

### Why `@bind` is Essential

Without `@bind`, you must choose:

1. **Include objects in signature** → Agent can't serialize them → Tool is unusable
2. **Use closures** → Works, but creates massive boilerplate for tool registration
3. **Use global variables** → Works, but fragile and hard to test

With `@bind`:
- Agent sees only serializable parameters
- Function has access to complex objects
- Tool registration is straightforward
- Testing is still possible (you can test the unbound function)

### Agent Workflow

Here's what happens when an agent uses a bound tool:

1. **Agent sees clean signature:**
   ```python
   def send_email(to: str, subject: str, body: str):
       """Send an email and memorize the action."""
   ```

2. **Agent generates tool call:**
   ```json
   {"tool": "send_email", "args": {"to": "...", "subject": "...", "body": "..."}}
   ```

3. **Framework executes:**
   ```python
   # The bound function is called
   send_email(to="...", subject="...", body="...")
   
   # Inside, 'agent' and 'gmail' are available via globals
   # The function executes successfully
   ```

4. **Agent sees result:**
   ```json
   {"status": "success", "message": "Email sent"}
   ```

The agent never needs to know about `agent` or `gmail` - they're hidden in the implementation.

### Dynamic Tool Registration

Agents often need to add tools mid-conversation:

```python
# Start with basic tools
agent = Agent(llm=llm, tools=[list_files, read_file])

# Later, add email capabilities
@bind(agent=agent, gmail=gmail_client)
def send_email(to: str, subject: str):
    gmail.send(to=to, subject=subject)
    agent.memorize(f"Sent to {to}")

agent.add_tools([send_email])
```

Without `@bind`, you'd need:
```python
# Ugly closure approach
def create_email_tool(agent, gmail):
    def send_email(to: str, subject: str):
        gmail.send(to=to, subject=subject)
        agent.memorize(f"Sent to {to}")
    return send_email

agent.add_tools([create_email_tool(agent, gmail)])
```

`@bind` makes this natural and readable.

### Self-Reference: Agent as a Tool Parameter

A common pattern is tools that need access to the agent itself:

```python
@bind(agent=my_agent)
def reflect_on_conversation():
    """Analyze the current conversation and summarize key points."""
    history = agent.get_conversation_history()
    summary = analyze(history)
    agent.memorize(f"Key points: {summary}")
    return summary
```

The agent can call this tool to introspect its own conversation! But it doesn't need to pass itself as a parameter (which would be impossible to serialize).

This enables powerful meta-cognitive patterns:
- Self-reflection tools
- Memory management tools
- Conversation analysis tools
- Planning and strategy tools

## When NOT to Use This

Don't use `@bind` if:
- Your function truly needs the object as a parameter (for testing, flexibility)
- The object changes frequently between calls
- You're building a simple script without tool registration

In those cases, regular function parameters are clearer.

## Implementation Details for Contributors

### Preserving Function Metadata

We copy all metadata to make the bound function behave like the original:

```python
new_func.__dict__.update(func.__dict__)      # Custom attributes
new_func.__doc__ = func.__doc__              # Docstring
new_func.__annotations__ = func.__annotations__  # Type hints
new_func.__module__ = func.__module__        # Module path
new_func.__qualname__ = func.__qualname__    # Qualified name
```

This ensures tools like agents, debuggers, and documentation generators see the bound function as identical to the original.

### Preserving Closures

We preserve the original closure with `func.__closure__`:

```python
new_func = types.FunctionType(
    func.__code__,
    new_globals,
    func.__name__,
    func.__defaults__,
    func.__closure__  # ← Important!
)
```

This matters for nested functions that capture variables from outer scopes.

### Keyword-Only Arguments

The `bind()` function uses `*,` to force keyword-only arguments:

```python
def bind(*, context=None, **bound_objects):
    #      ^
    #      Forces everything after to be keyword-only
```

This prevents confusion between `@bind(ctx)` (wrong) and `@bind(context=ctx)` (correct).

## Summary

The `@bind` decorator is a carefully crafted solution to a real problem in AI agent tool design. It balances:
- **Ergonomics**: Clean, readable function signatures
- **Functionality**: Objects are accessible where needed
- **Safety**: Documented risks with clear mitigation strategies
- **Flexibility**: Multiple usage patterns for different scenarios

The implementation leverages Python's `types.FunctionType` to inject objects at the only feasible level (globals) while preserving all function metadata and behaviour. It's not magic - it's understanding Python's scoping rules and working within their constraints.

