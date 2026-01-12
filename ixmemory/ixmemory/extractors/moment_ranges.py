"""
Moment range extraction.

Extracts date/time ranges, bounds, and periods from text.
"""

from typing import Any, Dict, List, Optional

from ixcore import LLM
from ixutils import parse_json_robust


# Spec that can be used alone or combined with other specs
MOMENT_RANGES_SPEC = {
    "key": "moment_ranges",
    "description": "date/time ranges, bounds, and periods (from X to Y, since X, until Y, before, after)",
    "fields": [
        "start: Start moment object with year/month/day/hour/minute/second (or null if no start bound)",
        "end: End moment object with year/month/day/hour/minute/second (or null if no end bound)",
        "record_type: What it represents (employment_period, availability, deadline_range, operating_hours, etc.)",
        "belongs_to: Entity name this belongs to (or null)",
    ],
    "examples": [
        {"start": {"year": 2020, "month": 1, "day": None, "hour": None, "minute": None, "second": None}, "end": {"year": 2025, "month": 12, "day": None, "hour": None, "minute": None, "second": None}, "record_type": "employment_period", "belongs_to": "Alice"},
        {"start": {"year": None, "month": None, "day": None, "hour": 9, "minute": 0, "second": None}, "end": {"year": None, "month": None, "day": None, "hour": 17, "minute": 0, "second": None}, "record_type": "operating_hours", "belongs_to": "store"},
        {"start": {"year": 2020, "month": None, "day": None, "hour": None, "minute": None, "second": None}, "end": None, "record_type": "since", "belongs_to": "membership"},
    ],
}


def _build_prompt(text: str) -> str:
    """Build the extraction prompt."""
    fields_str = "\n".join(f"- {f}" for f in MOMENT_RANGES_SPEC["fields"])
    
    return f'''Extract {MOMENT_RANGES_SPEC["description"]} from this text.

Text: {text}

For each item provide:
{fields_str}

Each moment object has: year, month (1-12), day (1-31), hour (0-23), minute (0-59), second (0-59).
Use null for unknown components.
Use null for start if it's "until", "before", "by".
Use null for end if it's "since", "from", "after", "starting".
Provide both start and end for ranges like "from X to Y" or "between X and Y".

Respond as a JSON list:
[
    {{"start": {{"year": 2020, "month": 1, "day": null, "hour": null, "minute": null, "second": null}}, "end": {{"year": 2025, "month": 12, "day": null, "hour": null, "minute": null, "second": null}}, "record_type": "employment_period", "belongs_to": "Alice"}},
    {{"start": null, "end": {{"year": 2025, "month": 6, "day": 30, "hour": null, "minute": null, "second": null}}, "record_type": "deadline", "belongs_to": "project"}}
]

Only include ranges/bounds explicitly mentioned. Do not include single moments (those go in moments).
'''


def extract_moment_ranges(
    llm: LLM,
    text: str,
    *,
    context: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Extract date/time ranges and bounds from text.
    
    Uses LLM to identify ranges (Jan to March), lower bounds (since 2020),
    and upper bounds (until 2025).
    
    Args:
        llm: LLM instance from ixcore.
        text: Text to extract from.
        context: Optional context to help LLM understand the text.
    
    Returns:
        List of range dictionaries with keys:
        - start: Start moment object (or null)
        - end: End moment object (or null)
        - record_type: What the range represents
        - belongs_to: Entity name (optional)
    
    Example:
        >>> ranges = extract_moment_ranges(llm, "Alice worked there from 2020 to 2025")
        >>> ranges
        [{"start": {"year": 2020, ...}, "end": {"year": 2025, ...}, 
          "record_type": "employment_period", "belongs_to": "Alice"}]
        
        >>> ranges = extract_moment_ranges(llm, "Store is open 9am to 5pm")
        >>> ranges
        [{"start": {"hour": 9, ...}, "end": {"hour": 17, ...}, 
          "record_type": "operating_hours", "belongs_to": "Store"}]
    """
    prompt = _build_prompt(text=text)
    if context:
        prompt = f"Context: {context}\n\n{prompt}"
    
    response = llm.query(user_prompt=prompt)
    parsed = parse_json_robust(response)
    
    if isinstance(parsed, list):
        return parsed
    return []
