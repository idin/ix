# ixmachina

A Python package to simplify and wrap connections to LLMs with RAG, memory, and MCP support.

## Installation

```bash
pip install ixmachina
```

## Environment Variables

The following environment variables are required or recommended:

### Required

- **`OPENAI_API_KEY`**: Your OpenAI API key. Get it from https://platform.openai.com/api-keys
- **`BRAVE_API_KEY`**: Your Brave Search API key. Get it from https://api-dashboard.search.brave.com/

### Optional

- **`ANTHROPIC_API_KEY`**: Your Anthropic API key (if using Claude models). Get it from https://console.anthropic.com/

Set these in your shell configuration file (e.g., `~/.zshrc` for zsh):

```bash
export OPENAI_API_KEY="your-openai-api-key"
export BRAVE_API_KEY="your-brave-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"  # Optional
```

