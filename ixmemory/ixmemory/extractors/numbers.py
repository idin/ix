"""
Number extraction.

Extracts numeric values with their meaning from text.
"""

from typing import Any, Dict, List, Optional

from ixcore import LLM
from ixutils import parse_json_robust


# Spec that can be used alone or combined with other specs
NUMBERS_SPEC = {
    "key": "numbers",
    "description": "numeric values with meaning (not ranges)",
    "fields": [
        "value: The numeric value",
        "record_type: What it represents (age, price, count, weight, height, distance, duration, quantity, percentage, score, etc.)",
        "belongs_to: Entity name this belongs to (or null)",
        "unit: Unit of measurement (kg, cm, $, %, years, etc.) or null",
    ],
    "examples": [
        {"value": 32, "record_type": "age", "belongs_to": "Alice", "unit": "years"},
        {"value": 65, "record_type": "weight", "belongs_to": "Alice", "unit": "kg"},
    ],
}


def _build_prompt(text: str) -> str:
    """Build the extraction prompt."""
    fields_str = "\n".join(f"- {f}" for f in NUMBERS_SPEC["fields"])
    examples_str = ",\n    ".join(str(e).replace("'", '"').replace("None", "null") for e in NUMBERS_SPEC["examples"])
    
    return f'''Extract {NUMBERS_SPEC["description"]} from this text.

Text: {text}

For each item provide:
{fields_str}

Respond as a JSON list:
[
    {examples_str}
]

Only include items explicitly mentioned. Do not extract ranges.
'''


def extract_numbers(
    llm: LLM,
    text: str,
    *,
    context: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Extract numeric values from text.
    
    Uses LLM to identify numbers and their semantic meaning.
    Does not extract ranges.
    
    Args:
        llm: LLM instance from ixcore.
        text: Text to extract from.
        context: Optional context to help LLM understand the text.
    
    Returns:
        List of number dictionaries with keys:
        - value: Numeric value
        - record_type: What the number represents
        - belongs_to: Entity name (optional)
        - unit: Unit of measurement (optional)
    
    Example:
        >>> numbers = extract_numbers(llm, "Alice is 32 years old and weighs 65kg")
        >>> numbers
        [
            {"value": 32, "record_type": "age", "belongs_to": "Alice", "unit": "years"},
            {"value": 65, "record_type": "weight", "belongs_to": "Alice", "unit": "kg"}
        ]
    """
    prompt = _build_prompt(text=text)
    if context:
        prompt = f"Context: {context}\n\n{prompt}"
    
    response = llm.query(user_prompt=prompt)
    parsed = parse_json_robust(response)
    
    if isinstance(parsed, list):
        return parsed
    return []
