# Pricing Tools

Tools for fetching and extracting model pricing information from company websites. These tools help you understand the costs of using different AI models.

## Core Design Principles

### Web-Based Extraction

Pricing information is extracted from company websites using web search and LLM-based extraction. This approach is flexible and adapts to different website structures.

**Why implemented this way**: 
- Company websites have different structures and formats
- Pricing pages change over time
- LLM extraction can handle variations in presentation
- No need to maintain hardcoded parsers for each company

### Domain Filtering

Searches are filtered to company domains to ensure information comes from official sources.

**Why this matters**: Official pricing pages are authoritative and up-to-date. Filtering prevents getting pricing from third-party sources that may be outdated or incorrect.

## Understanding the Tools

### `get_model_prices` - Get Model Pricing

**What it does**: Searches the web for a company's pricing page, extracts pricing information using an LLM, and returns a dictionary of model names to prices.

**Why we use it**: Quickly get up-to-date pricing information for AI models without manually visiting each company's website.

**Why implemented this way**:
- Uses web search to find official pricing pages
- Filters results to company domains (ensures official sources)
- Uses LLM to extract structured pricing data (handles different page formats)
- Returns prices per million tokens (standardized unit)
- Handles different pricing types (input, output, cached_input, training, etc.)

**How to use**:
```python
from ixmachina.tools.pricing import get_model_prices
from ixmachina.llm import LLM

llm = LLM(api_key=openai_key, model_name="gpt-4")

# Get pricing for a company
result = get_model_prices(
    company="openai",
    llm=llm,
    max_search_results=5
)

if result["success"]:
    prices = result["prices"]
    for model_name, price_info in prices.items():
        if isinstance(price_info, dict):
            # Different prices for input/output
            print(f"{model_name}:")
            print(f"  Input: ${price_info.get('input', 0):.2f} per million tokens")
            print(f"  Output: ${price_info.get('output', 0):.2f} per million tokens")
        else:
            # Single price
            print(f"{model_name}: ${price_info:.2f} per million tokens")
    
    print(f"Source: {result['url']}")
```

**When to use**: 
- Comparing costs across different AI providers
- Calculating costs for a project
- Building pricing comparison tools
- Researching model pricing

**Note**: Requires an LLM instance for extraction. Can be passed directly or via special objects as `"use:llm"` in agent contexts.

---

## Common Patterns

### Comparing Companies

Get pricing from multiple companies for comparison:

```python
companies = ["openai", "anthropic", "google"]
all_prices = {}

for company in companies:
    result = get_model_prices(company=company, llm=llm)
    if result["success"]:
        all_prices[company] = result["prices"]

# Compare prices
for company, prices in all_prices.items():
    print(f"\n{company.upper()}:")
    for model, price in prices.items():
        print(f"  {model}: {price}")
```

### Error Handling

Always check for success and handle errors:

```python
result = get_model_prices(company="openai", llm=llm)
if not result["success"]:
    print(f"Error: {result['error']}")
    return
# Use result["prices"] here
```

### Understanding Price Structure

Prices can be structured in two ways:
- **Single price**: Model maps directly to a float (same price for input/output)
- **Different prices**: Model maps to a dict with "input" and "output" keys

```python
prices = result["prices"]

for model, price_info in prices.items():
    if isinstance(price_info, dict):
        # Different prices for input/output
        input_price = price_info.get("input", 0)
        output_price = price_info.get("output", 0)
    else:
        # Same price for both
        input_price = price_info
        output_price = price_info
```

---

## Design Decisions

### Why Web Search + LLM Extraction?

Instead of hardcoding parsers or maintaining API integrations:
- **Flexible**: Works with any company website structure
- **Adaptive**: LLM can handle format changes
- **Comprehensive**: Can extract all pricing information, not just what's in an API
- **No maintenance**: No need to update parsers when websites change

### Why Domain Filtering?

Ensures information comes from official sources:
- Official pages are authoritative
- Third-party sources may be outdated
- Reduces risk of incorrect information

### Why Per Million Tokens?

Standardized unit makes comparison easy:
- All models priced per token
- Million tokens is a common unit
- Easy to calculate costs for specific use cases

### Why Support Different Price Types?

Some models have different prices for:
- **Input**: Tokens sent to the model
- **Output**: Tokens generated by the model
- **Cached input**: Previously processed tokens (cheaper)
- **Training**: Fine-tuning costs

The tool extracts all pricing types when available, giving you complete cost information.

### Error Handling

The tool handles various error cases:
- No pricing page found: Searches but finds no official page
- Extraction failure: LLM can't extract pricing from page
- Network errors: Can't fetch web pages
- Invalid company: Company name doesn't match any domains

All errors are returned with clear messages to help diagnose issues.

