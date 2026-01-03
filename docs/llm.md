# LLM

The LLM class provides a unified interface for connecting to and querying various LLM providers (OpenAI, Anthropic, etc.) without requiring separate classes for each provider.

## Overview

The `LLM` class:
- **Unified interface**: Same API for all providers
- **Auto-detection**: Automatically detects provider from model name
- **Usage tracking**: Tracks tokens and costs
- **Pricing support**: Automatic or manual pricing configuration
- **Environment variables**: Support for `EnvVar` for secure credential management

## Basic Usage

```python
from ixmachina import LLM

# Create an LLM (provider auto-detected from model name)
llm = LLM(api_key="your-key", model_name="gpt-4")

# Query the LLM
response = llm.query("What is the capital of France?")
print(response)  # "The capital of France is Paris."
```

## Provider Auto-Detection

The provider is automatically detected from the model name:

```python
# OpenAI models
llm = LLM(api_key=key, model_name="gpt-4")  # Provider: "openai"
llm = LLM(api_key=key, model_name="gpt-3.5-turbo")  # Provider: "openai"
llm = LLM(api_key=key, model_name="o1-preview")  # Provider: "openai"

# Anthropic models
llm = LLM(api_key=key, model_name="claude-3-opus")  # Provider: "anthropic"
llm = LLM(api_key=key, model_name="claude-3-sonnet")  # Provider: "anthropic"
```

You can also explicitly specify the provider:

```python
llm = LLM(api_key=key, model_name="custom-model", provider="openai")
```

## Environment Variables

Use `EnvVar` for secure credential management:

```python
from ixmachina.llm import LLM, EnvVar

# Read API key from environment variable
llm = LLM(api_key=EnvVar("OPENAI_API_KEY"), model_name="gpt-4")

# EnvVar automatically reads from environment
# Equivalent to: os.getenv("OPENAI_API_KEY")
```

## Usage Tracking

The LLM automatically tracks token usage:

```python
# Query the LLM
response = llm.query("Hello")

# Get last usage
last_usage = llm.last_usage
# Returns: {"input_tokens": 5, "output_tokens": 10, "total_tokens": 15}

# Get total usage
total_usage = llm.total_usage
# Returns: {"input_tokens": 100, "output_tokens": 200, "total_tokens": 300}
```

## Cost Tracking

Configure pricing to track costs:

```python
# Single price (same for input and output)
llm = LLM(
    api_key=key,
    model_name="gpt-4",
    pricing=2.5  # $2.50 per million tokens
)

# Different prices for input and output
llm = LLM(
    api_key=key,
    model_name="gpt-4",
    pricing={"input": 2.5, "output": 10.0}  # $2.50 input, $10.00 output per million tokens
)

# Query and check costs
response = llm.query("Hello")
last_cost = llm.last_cost
# Returns: {"input_cost": 0.0000125, "output_cost": 0.0001, "total_cost": 0.0001125}

total_cost = llm.total_cost
# Returns: {"input_cost": 0.001, "output_cost": 0.01, "total_cost": 0.011}
```

## Automatic Pricing Fetching

Enable automatic pricing fetching:

```python
llm = LLM(
    api_key=key,
    model_name="gpt-4",
    fetch_pricing=True  # Automatically fetch pricing from web
)

# Pricing is fetched lazily on first query if not already set
response = llm.query("Hello")  # Pricing fetched here if needed
```

## Conversation History

The LLM maintains conversation history:

```python
# Start a conversation
llm.query("My name is Alice")

# Continue the conversation
llm.query("What's my name?")  # "Your name is Alice."

# Get conversation history
history = llm.conversation_history
# Returns: [
#     {"role": "user", "content": "My name is Alice"},
#     {"role": "assistant", "content": "Nice to meet you, Alice!"},
#     {"role": "user", "content": "What's my name?"},
#     {"role": "assistant", "content": "Your name is Alice."}
# ]
```

## Function Calling / Tools

The LLM supports function calling:

```python
def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"Weather in {location}: Sunny, 72°F"

# Define tools
tools = [get_weather]

# Query with tools
response = llm.query(
    "What's the weather in Paris?",
    tools=tools
)

# LLM can call tools and get results
```

## Provider-Specific Parameters

Pass provider-specific parameters via `**kwargs`:

```python
# OpenAI-specific parameters
llm = LLM(
    api_key=key,
    model_name="gpt-4",
    temperature=0.7,
    max_tokens=1000
)

# Anthropic-specific parameters
llm = LLM(
    api_key=key,
    model_name="claude-3-opus",
    max_tokens=4096
)
```

## Design Decisions

### Why Unified Interface?

A unified interface means:
- Same code works with any provider
- Easy to switch providers
- Consistent API across providers
- Less code to maintain

### Why Auto-Detection?

Auto-detection:
- Reduces boilerplate (don't need to specify provider)
- Prevents errors (can't mismatch provider and model)
- Makes code cleaner

### Why Usage Tracking?

Usage tracking enables:
- Monitoring token consumption
- Cost analysis
- Budget management
- Performance optimization

### Why Automatic Pricing?

Automatic pricing:
- Always up-to-date pricing
- No manual configuration needed
- Accurate cost tracking
- Works for all supported models

