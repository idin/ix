"""
Moment extraction.

Extracts dates, times, and partial temporal references from text.
"""

from typing import Any, Dict, List, Optional

from ixcore import LLM
from ixutils import parse_json_robust


# Spec that can be used alone or combined with other specs
MOMENTS_SPEC = {
    "key": "moments",
    "description": "dates, times, partial dates (not ranges)",
    "fields": [
        "year: Year if mentioned (or null)",
        "month: Month 1-12 if mentioned (or null)",
        "day: Day 1-31 if mentioned (or null)",
        "hour: Hour 0-23 if mentioned (or null)",
        "minute: Minute 0-59 if mentioned (or null)",
        "second: Second 0-59 if mentioned (or null)",
        "record_type: What it represents (birthdate, death_date, event_date, deadline, appointment, created_at, etc.)",
        "belongs_to: Entity name this belongs to (or null)",
    ],
    "examples": [
        {"year": 1992, "month": 3, "day": 15, "hour": None, "minute": None, "second": None, "record_type": "birthdate", "belongs_to": "Alice"},
        {"year": 2025, "month": 11, "day": None, "hour": None, "minute": None, "second": None, "record_type": "deadline", "belongs_to": "Project X"},
    ],
}


def _build_prompt(text: str) -> str:
    """Build the extraction prompt."""
    fields_str = "\n".join(f"- {f}" for f in MOMENTS_SPEC["fields"])
    examples_str = ",\n    ".join(str(e).replace("'", '"').replace("None", "null") for e in MOMENTS_SPEC["examples"])
    
    return f'''Extract {MOMENTS_SPEC["description"]} from this text.

Text: {text}

For each item provide:
{fields_str}

Respond as a JSON list:
[
    {examples_str}
]

Partial dates are fine. Only include items explicitly mentioned. Do not extract ranges.
'''


def extract_moments(
    llm: LLM,
    text: str,
    *,
    context: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Extract temporal values from text.
    
    Uses LLM to identify dates, times, and partial temporal references.
    Does not extract date ranges.
    
    Args:
        llm: LLM instance from ixcore.
        text: Text to extract from.
        context: Optional context to help LLM understand the text.
    
    Returns:
        List of moment dictionaries with keys:
        - year, month, day, hour, minute, second: Temporal components (nullable)
        - record_type: What the moment represents
        - belongs_to: Entity name (optional)
    
    Example:
        >>> moments = extract_moments(llm, "Alice was born on March 15, 1992")
        >>> moments
        [
            {"year": 1992, "month": 3, "day": 15, "hour": null, "minute": null,
             "second": null, "record_type": "birthdate", "belongs_to": "Alice"}
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
