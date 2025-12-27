"""
Tests for get_model_prices function with OpenAI.
"""

import os

from ixmachina.tools.pricing import get_model_prices
from ixmachina.llm import LLM, EnvVar


# Reference pricing ranges (per million tokens) based on OpenAI's official pricing
# These are approximate ranges to validate results are reasonable
OPENAI_PRICE_RANGES = {
    "gpt-4o": {
        "input": (2.0, 3.0),  # $2.50 per 1M tokens
        "output": (8.0, 12.0),  # $10.00 per 1M tokens
    },
    "gpt-4o-mini": {
        "input": (0.1, 0.2),  # $0.15 per 1M tokens
        "output": (0.4, 0.8),  # $0.60 per 1M tokens
    },
    "gpt-4-turbo": {
        "input": (8.0, 12.0),  # $10.00 per 1M tokens
        "output": (28.0, 32.0),  # $30.00 per 1M tokens
    },
    "gpt-4": {
        "input": (28.0, 32.0),  # $30.00 per 1M tokens
        "output": (58.0, 62.0),  # $60.00 per 1M tokens
    },
    "gpt-3.5-turbo": {
        "input": (0.4, 0.6),  # $0.50 per 1M tokens
        "output": (1.4, 1.6),  # $1.50 per 1M tokens
    },
}


def test_get_openai_model_prices():
    """Test get_model_prices successfully retrieves OpenAI model pricing."""
    api_key = os.getenv("OPENAI_API_KEY")
    assert api_key is not None, "OPENAI_API_KEY environment variable not set"
    
    llm = LLM(api_key=EnvVar("OPENAI_API_KEY"), model_name="gpt-4o-mini")
    
    result = get_model_prices(company="openai", llm=llm, max_search_results=10)
    
    assert isinstance(result, dict)
    
    # If search fails, provide detailed error information
    if not result["success"]:
        error_msg = result.get("error", "Unknown error")
        # Check if it's a search issue or extraction issue
        if "Failed to find pricing pages" in error_msg:
            # Search failed - this is likely due to search engine HTML parsing issues
            # The search engines (DuckDuckGo/Startpage) may have changed their HTML structure
            # or are blocking automated requests. This is a known issue that needs to be fixed
            # in the search_web function's HTML parsing logic.
            print(f"\nWARNING: Search engine returned 0 results.")
            print(f"This indicates the HTML parsing in search_web needs to be updated.")
            print(f"Error: {error_msg}")
            print(f"\nTo fix this:")
            print(f"1. Check if DuckDuckGo/Startpage HTML structure has changed")
            print(f"2. Update the CSS selectors in _search_duckduckgo and _search_startpage")
            print(f"3. Consider using a different search method or API")
            # For now, we'll mark this as a known issue rather than failing
            # The test structure is correct, but the search functionality needs fixing
            assert False, (
                f"Search engine parsing issue: {error_msg}\n"
                f"The search_web function is not finding results from DuckDuckGo/Startpage.\n"
                f"This needs to be fixed in the HTML parsing logic."
            )
        else:
            # Other errors (extraction, parsing, etc.)
            assert False, f"Failed to get prices: {error_msg}"
    
    assert result["success"] is True
    assert "prices" in result
    assert isinstance(result["prices"], dict)
    assert len(result["prices"]) > 0, "No prices returned"
    assert result["company"] == "openai"
    assert result["url"] is not None
    assert "openai.com" in result["url"].lower()
    assert result["error"] is None


def test_get_openai_model_prices_has_expected_models():
    """Test that OpenAI pricing includes expected model names."""
    api_key = os.getenv("OPENAI_API_KEY")
    assert api_key is not None, "OPENAI_API_KEY environment variable not set"
    
    llm = LLM(api_key=EnvVar("OPENAI_API_KEY"), model_name="gpt-4o-mini")
    
    result = get_model_prices(company="openai", llm=llm, max_search_results=10)
    
    assert result["success"] is True
    
    prices = result["prices"]
    
    # Check that we have at least some model names (they might have underscores)
    model_names = list(prices.keys())
    assert len(model_names) > 0
    
    # Check that model names are strings
    for model_name in model_names:
        assert isinstance(model_name, str)
        # Model names should not have spaces (should be replaced with underscores)
        assert " " not in model_name, f"Model name '{model_name}' should not contain spaces"


def test_get_openai_model_prices_price_ranges():
    """Test that OpenAI pricing values are within reasonable ranges."""
    api_key = os.getenv("OPENAI_API_KEY")
    assert api_key is not None, "OPENAI_API_KEY environment variable not set"
    
    llm = LLM(api_key=EnvVar("OPENAI_API_KEY"), model_name="gpt-4o-mini")
    
    result = get_model_prices(company="openai", llm=llm, max_search_results=10)
    
    assert result["success"] is True
    
    prices = result["prices"]
    
    # Check that prices are reasonable (positive floats)
    for model_name, price_value in prices.items():
        if isinstance(price_value, dict):
            # Input/output pricing
            assert "input" in price_value or "output" in price_value
            if "input" in price_value:
                assert isinstance(price_value["input"], (int, float))
                assert price_value["input"] > 0
                assert price_value["input"] < 1000  # Sanity check: should be less than $1000 per 1M tokens
            if "output" in price_value:
                assert isinstance(price_value["output"], (int, float))
                assert price_value["output"] > 0
                assert price_value["output"] < 1000  # Sanity check
        else:
            # Single price value
            assert isinstance(price_value, (int, float))
            assert price_value > 0
            assert price_value < 1000  # Sanity check


def test_get_openai_model_prices_specific_models():
    """Test that specific OpenAI models have pricing within expected ranges."""
    api_key = os.getenv("OPENAI_API_KEY")
    assert api_key is not None, "OPENAI_API_KEY environment variable not set"
    
    llm = LLM(api_key=EnvVar("OPENAI_API_KEY"), model_name="gpt-4o-mini")
    
    result = get_model_prices(company="openai", llm=llm, max_search_results=10)
    
    assert result["success"] is True
    
    prices = result["prices"]
    
    # Check for common model names (case-insensitive, with variations)
    found_models = []
    for model_name in prices.keys():
        model_lower = model_name.lower()
        # Check if any expected model name appears in the returned model name
        for expected_model in OPENAI_PRICE_RANGES.keys():
            if expected_model.replace("-", "_") in model_lower or expected_model in model_lower:
                found_models.append((model_name, expected_model))
                break
    
    # We should find at least one common model
    assert len(found_models) > 0, f"No expected models found. Got: {list(prices.keys())}"
    
    # Validate prices for found models
    for returned_name, expected_model in found_models:
        price_value = prices[returned_name]
        expected_ranges = OPENAI_PRICE_RANGES[expected_model]
        
        if isinstance(price_value, dict):
            # Check input price if available
            if "input" in price_value and "input" in expected_ranges:
                input_price = price_value["input"]
                min_price, max_price = expected_ranges["input"]
                assert min_price <= input_price <= max_price, (
                    f"{returned_name} input price {input_price} is outside expected range "
                    f"[{min_price}, {max_price}]"
                )
            
            # Check output price if available
            if "output" in price_value and "output" in expected_ranges:
                output_price = price_value["output"]
                min_price, max_price = expected_ranges["output"]
                assert min_price <= output_price <= max_price, (
                    f"{returned_name} output price {output_price} is outside expected range "
                    f"[{min_price}, {max_price}]"
                )
        else:
            # Single price - check if it's within input range (most common)
            if "input" in expected_ranges:
                min_price, max_price = expected_ranges["input"]
                # Allow some flexibility for single price values
                assert min_price * 0.5 <= price_value <= max_price * 2, (
                    f"{returned_name} price {price_value} is outside reasonable range "
                    f"based on expected input range [{min_price}, {max_price}]"
                )


def _get_price_value(price_data):
    """Helper to get a single price value from dict or float."""
    if isinstance(price_data, dict):
        # Use input price if available, otherwise output, otherwise average
        if "input" in price_data:
            return price_data["input"]
        elif "output" in price_data:
            return price_data["output"]
        elif len(price_data) > 0:
            # Average of all values
            return sum(price_data.values()) / len(price_data)
        else:
            return None
    elif isinstance(price_data, (int, float)):
        return price_data
    else:
        return None


def test_get_openai_model_prices_relative_pricing():
    """Test that model pricing follows expected relative relationships."""
    api_key = os.getenv("OPENAI_API_KEY")
    assert api_key is not None, "OPENAI_API_KEY environment variable not set"
    
    llm = LLM(api_key=EnvVar("OPENAI_API_KEY"), model_name="gpt-4o-mini")
    
    result = get_model_prices(company="openai", llm=llm, max_search_results=10)
    
    assert result["success"] is True
    
    prices = result["prices"]
    
    # Helper function to find model by name (case-insensitive, with variations)
    def find_model_price(model_search_terms):
        """Find model price by searching for terms in model names."""
        for model_name, price_value in prices.items():
            model_lower = model_name.lower()
            for term in model_search_terms:
                if term.lower() in model_lower:
                    return model_name, price_value
        return None, None
    
    # Test: GPT-4.1 > GPT-4.1_mini > GPT-4.1_nano
    gpt41_name, gpt41_price = find_model_price(["gpt-4.1", "gpt_4.1"])
    gpt41_mini_name, gpt41_mini_price = find_model_price(["gpt-4.1-mini", "gpt_4.1_mini", "gpt-4.1_mini"])
    gpt41_nano_name, gpt41_nano_price = find_model_price(["gpt-4.1-nano", "gpt_4.1_nano", "gpt-4.1_nano"])
    
    if gpt41_name and gpt41_mini_name:
        gpt41_val = _get_price_value(gpt41_price)
        gpt41_mini_val = _get_price_value(gpt41_mini_price)
        if gpt41_val is not None and gpt41_mini_val is not None:
            assert gpt41_val > gpt41_mini_val, (
                f"GPT-4.1 ({gpt41_name}: {gpt41_val}) should be more expensive than "
                f"GPT-4.1_mini ({gpt41_mini_name}: {gpt41_mini_val})"
            )
    
    if gpt41_mini_name and gpt41_nano_name:
        gpt41_mini_val = _get_price_value(gpt41_mini_price)
        gpt41_nano_val = _get_price_value(gpt41_nano_price)
        if gpt41_mini_val is not None and gpt41_nano_val is not None:
            assert gpt41_mini_val > gpt41_nano_val, (
                f"GPT-4.1_mini ({gpt41_mini_name}: {gpt41_mini_val}) should be more expensive than "
                f"GPT-4.1_nano ({gpt41_nano_name}: {gpt41_nano_val})"
            )
    
    # Test: o4-mini > GPT-4.1
    o4_mini_name, o4_mini_price = find_model_price(["o4-mini", "o4_mini"])
    
    if o4_mini_name and gpt41_name:
        o4_mini_val = _get_price_value(o4_mini_price)
        gpt41_val = _get_price_value(gpt41_price)
        if o4_mini_val is not None and gpt41_val is not None:
            assert o4_mini_val > gpt41_val, (
                f"o4-mini ({o4_mini_name}: {o4_mini_val}) should be more expensive than "
                f"GPT-4.1 ({gpt41_name}: {gpt41_val})"
            )

