"""
Detection of extractable content types.

Checks which types of information exist in text before extraction.
Uses grouped detection to avoid overwhelming the LLM with too many types.
"""

from typing import Any, Dict, List, Optional

from ixcore import LLM
from ixutils import parse_json_robust

from .extract import extract


# Group A: Structure (entities and their connections)
DETECT_STRUCTURE_PROMPT = '''Analyze this text and determine which types of information are present.

Text: {text}

Check for:
- entities: people, places, organizations, concepts, brands, products, projects
- relationships: connections between entities (works_at, lives_in, knows, owns, etc.)

Respond as a JSON object with true/false for each type:
{{
    "entities": true,
    "relationships": false
}}

Only mark true if that type of information is explicitly present in the text.
'''

# Group B: Data (values and properties)
DETECT_DATA_PROMPT = '''Analyze this text and determine which types of information are present.

Text: {text}

Check for:
- numbers: single numeric values with meaning (ages, prices, counts, measurements)
- moments: single dates, times, partial dates
- attributes: text-based properties (occupations, colours, nationalities, descriptions)
- number_ranges: numeric ranges or bounds (between X and Y, at least X, at most Y, greater than, less than)
- moment_ranges: date/time ranges or bounds (from X to Y, since X, until Y, before, after)

Respond as a JSON object with true/false for each type:
{{
    "numbers": true,
    "moments": false,
    "attributes": true,
    "number_ranges": false,
    "moment_ranges": false
}}

Only mark true if that type of information is explicitly present in the text.
'''

# Type groupings
STRUCTURE_TYPES = ["entities", "relationships"]
DATA_TYPES = ["numbers", "moments", "attributes", "number_ranges", "moment_ranges"]
ALL_TYPES = STRUCTURE_TYPES + DATA_TYPES


def _detect_group(
    llm: LLM,
    text: str,
    prompt_template: str,
    types: List[str],
    context: Optional[str] = None,
) -> Dict[str, bool]:
    """Detect types for a single group."""
    prompt = prompt_template.format(text=text)
    if context:
        prompt = f"Context: {context}\n\n{prompt}"
    
    response = llm.query(user_prompt=prompt)
    parsed = parse_json_robust(response)
    
    if isinstance(parsed, dict):
        return {t: bool(parsed.get(t, False)) for t in types}
    
    return {t: False for t in types}


def detect(
    llm: LLM,
    text: str,
    *,
    context: Optional[str] = None,
) -> Dict[str, bool]:
    """
    Detect which types of extractable information exist in text.
    
    Uses grouped detection (2 LLM calls) to avoid overwhelming with too many types:
    - Group A (Structure): entities, relationships
    - Group B (Data): numbers, moments, attributes, number_ranges, moment_ranges
    
    Args:
        llm: LLM instance from ixcore.
        text: Text to analyze.
        context: Optional context to help LLM understand the text.
    
    Returns:
        Dict with type names as keys, booleans as values.
        True means that type of information is present.
    
    Example:
        >>> present = detect(llm, "Alice is 32 years old and works at Acme Corp")
        >>> present
        {
            "entities": True, "relationships": True,
            "numbers": True, "moments": False, "attributes": False,
            "number_ranges": False, "moment_ranges": False
        }
    """
    # Detect structure types (entities, relationships)
    structure_result = _detect_group(
        llm=llm,
        text=text,
        prompt_template=DETECT_STRUCTURE_PROMPT,
        types=STRUCTURE_TYPES,
        context=context,
    )
    
    # Detect data types (numbers, moments, attributes, ranges)
    data_result = _detect_group(
        llm=llm,
        text=text,
        prompt_template=DETECT_DATA_PROMPT,
        types=DATA_TYPES,
        context=context,
    )
    
    # Merge results
    return {**structure_result, **data_result}


def detect_and_extract(
    llm: LLM,
    text: str,
    *,
    context: Optional[str] = None,
) -> Dict[str, List[Dict]]:
    """
    Detect what's present, then extract only those types.
    
    Convenience function that combines detect() and extract().
    
    Args:
        llm: LLM instance from ixcore.
        text: Text to analyze and extract from.
        context: Optional context to help LLM understand the text.
    
    Returns:
        Dict with type names as keys, lists of extracted items as values.
        Only includes types that were detected as present.
    
    Example:
        >>> result = detect_and_extract(llm, "Alice is 32 and works at Acme")
        >>> result
        {
            "entities": [{"name": "Alice", ...}, {"name": "Acme", ...}],
            "numbers": [{"value": 32, ...}],
            "relationships": [{"source": "Alice", "relationship": "works_at", ...}]
        }
    """
    # First detect what's present (2 calls: structure + data)
    present = detect(llm=llm, text=text, context=context)
    
    # Get types that are present
    types_to_extract = [t for t, is_present in present.items() if is_present]
    
    if not types_to_extract:
        return {}
    
    # Extract only what's present
    return extract(llm=llm, text=text, types=types_to_extract, context=context)
