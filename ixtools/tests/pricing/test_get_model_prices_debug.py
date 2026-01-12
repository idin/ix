"""
Debug tests for get_model_prices to understand extraction issues.
"""

from ixtools.pricing import get_model_prices
from ixtools.web import search_web, fetch_url, extract_from_page
from ixtools.web import extract_text
from ixtools.string import smart_truncate_text
from ixcore import LLM
from ixutils import EnvVar
from tests.api_keys import get_openai_api_key


def test_debug_extraction_process():
    """Debug what text is being sent to the LLM during extraction."""
    api_key = get_openai_api_key()
    
    llm = LLM(api_key=EnvVar("OPENAI_API_KEY"), model_name="gpt-4o-mini")
    
    # Step 1: Search for pricing pages
    search_result = search_web(
        query="openai model pricing per million tokens",
        max_results=5,
        search_engine="brave",
        domain_whitelist="openai.com",
    )
    
    assert search_result["success"] is True, f"Search failed: {search_result.get('error')}"
    assert search_result["count"] > 0, "No search results found"
    
    # Step 2: Fetch the first result
    url = search_result["results"][0]["url"]
    print(f"\n=== Testing URL: {url} ===")
    
    # Try multiple URLs if first one fails
    page_response = None
    for result in search_result["results"]:
        test_url = result["url"]
        page_response = fetch_url(url=test_url)
        if page_response["success"]:
            url = test_url
            break
    
    if not page_response or not page_response["success"]:
        # If all URLs fail, try the actual get_model_prices to see what URL it uses
        print(f"\nAll URLs failed. Trying get_model_prices to see what works...")
        result = get_model_prices(company="openai", llm=llm, max_search_results=10)
        if result["success"]:
            print(f"get_model_prices succeeded with URL: {result['url']}")
            url = result["url"]
            page_response = fetch_url(url=url)
    
    assert page_response and page_response["success"] is True, (
        f"Failed to fetch any URL. Last error: {page_response.get('error') if page_response else 'No response'}\n"
        f"Tried URLs: {[r['url'] for r in search_result['results']]}"
    )
    
    # Step 3: Extract text
    text = extract_text(page_response["content"])
    print(f"\nFull text length: {len(text)} characters")
    
    # Step 4: Test smart truncation
    search_terms = [
        "gpt-4", "gpt-4o", "gpt-4o-mini", "gpt-3.5", "gpt-4-turbo",
        "ada", "babbage", "curie", "davinci",
        "pricing", "price", "token", "per million",
    ]
    
    truncated = smart_truncate_text(
        text=text,
        search_terms=search_terms,
        max_length=8000,
    )
    
    print(f"Truncated text length: {len(truncated)} characters")
    print(f"Reduction: {len(text) - len(truncated)} characters removed")
    
    # Step 5: Check which models appear in truncated text
    models_to_check = ["gpt-4", "gpt-4o", "gpt-4o-mini", "gpt-3.5", "gpt-4-turbo", "ada", "babbage", "curie", "davinci"]
    models_found = []
    for model in models_to_check:
        if model.lower() in truncated.lower():
            models_found.append(model)
    
    print(f"\nModels found in truncated text: {models_found}")
    print(f"Models NOT found: {set(models_to_check) - set(models_found)}")
    
    # Step 6: Show a sample of the truncated text
    print(f"\n=== Sample of truncated text (first 500 chars) ===")
    print(truncated[:500])
    print(f"\n=== Sample of truncated text (last 500 chars) ===")
    print(truncated[-500:])
    
    # Step 7: Try extraction and see what LLM returns
    extraction_result = extract_from_page(
        url=url,
        query=(
            "Extract ALL model names and their pricing per million tokens in dollars. "
            "Include every model mentioned on the page (GPT-4, GPT-4o, GPT-4o-mini, GPT-3.5-turbo, GPT-4-turbo, Ada, Babbage, Curie, Davinci, etc.). "
            "Return as a JSON dictionary where keys are model names. "
            "If pricing differs by type (input, output, cached_input, training, etc.), each model should map to a dictionary with 'input' and 'output' keys (as floats). "
            "If pricing is the same for all types, map directly to a float. "
            "Always include both input and output prices if they are different. "
            "Extract ALL models, not just one."
        ),
        llm=llm,
        search_terms=search_terms,
    )
    
    print(f"\n=== LLM Extraction Result ===")
    print(f"Success: {extraction_result['success']}")
    if extraction_result["success"]:
        print(f"Extracted content (first 1000 chars):")
        print(extraction_result["extracted"][:1000])
        print(f"\nFull extracted content length: {len(extraction_result['extracted'])} characters")
    else:
        print(f"Error: {extraction_result.get('error')}")
    
    # Assertions for debugging
    assert len(models_found) > 0, f"No models found in truncated text. This indicates smart truncation may be focusing on wrong sections."
    assert extraction_result["success"] is True, f"Extraction failed: {extraction_result.get('error')}"

