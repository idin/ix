"""
Number range extraction.

Extracts numeric ranges, bounds, and constraints from text.
"""

from typing import Any, Dict, List, Optional

from ixcore import LLM
from ixutils import parse_json_robust


# Spec that can be used alone or combined with other specs
NUMBER_RANGES_SPEC = {
    "key": "number_ranges",
    "description": "numeric ranges, bounds, and constraints (between X and Y, at least X, at most Y, greater than, less than, minimum, maximum)",
    "fields": [
        "min: Lower bound value (or null if no lower bound)",
        "max: Upper bound value (or null if no upper bound)",
        "record_type: What it represents (age, price, count, weight, height, distance, duration, quantity, percentage, score, etc.)",
        "belongs_to: Entity name this belongs to (or null)",
        "unit: Unit of measurement (kg, cm, $, %, years, etc.) or null",
    ],
    "examples": [
        {"min": 20, "max": 30, "record_type": "age", "belongs_to": "candidates", "unit": "years"},
        {"min": 100, "max": None, "record_type": "price", "belongs_to": "product", "unit": "$"},
        {"min": None, "max": 50, "record_type": "weight", "belongs_to": "package", "unit": "kg"},
    ],
}


def _build_prompt(text: str) -> str:
    """Build the extraction prompt."""
    fields_str = "\n".join(f"- {f}" for f in NUMBER_RANGES_SPEC["fields"])
    examples_str = ",\n    ".join(str(e).replace("'", '"').replace("None", "null") for e in NUMBER_RANGES_SPEC["examples"])
    
    return f'''Extract {NUMBER_RANGES_SPEC["description"]} from this text.

Text: {text}

For each item provide:
{fields_str}

Use null for min if it's "less than", "at most", "maximum", "up to".
Use null for max if it's "greater than", "at least", "minimum", "more than".
Provide both min and max for ranges like "between X and Y" or "from X to Y".

Respond as a JSON list:
[
    {examples_str}
]

Only include ranges/bounds explicitly mentioned. Do not include single values (those go in numbers).
'''


def extract_number_ranges(
    llm: LLM,
    text: str,
    *,
    context: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Extract numeric ranges and bounds from text.
    
    Uses LLM to identify ranges (20-30), lower bounds (at least 20),
    and upper bounds (at most 30).
    
    Args:
        llm: LLM instance from ixcore.
        text: Text to extract from.
        context: Optional context to help LLM understand the text.
    
    Returns:
        List of range dictionaries with keys:
        - min: Lower bound (or null)
        - max: Upper bound (or null)
        - record_type: What the range represents
        - belongs_to: Entity name (optional)
        - unit: Unit of measurement (optional)
    
    Example:
        >>> ranges = extract_number_ranges(llm, "Candidates must be between 20 and 30 years old")
        >>> ranges
        [{"min": 20, "max": 30, "record_type": "age", "belongs_to": "candidates", "unit": "years"}]
        
        >>> ranges = extract_number_ranges(llm, "Price is at least $100")
        >>> ranges
        [{"min": 100, "max": null, "record_type": "price", "belongs_to": null, "unit": "$"}]
    """
    prompt = _build_prompt(text=text)
    if context:
        prompt = f"Context: {context}\n\n{prompt}"
    
    response = llm.query(user_prompt=prompt)
    parsed = parse_json_robust(response)
    
    if isinstance(parsed, list):
        return parsed
    return []
