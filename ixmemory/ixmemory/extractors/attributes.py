"""
Attribute extraction.

Extracts text-based properties/attributes of entities (not numbers or dates).
"""

from typing import Any, Dict, List, Optional

from ixcore import LLM
from ixutils import parse_json_robust


# Spec that can be used alone or combined with other specs
ATTRIBUTES_SPEC = {
    "key": "attributes",
    "description": "text-based properties (not numbers or dates)",
    "fields": [
        "entity: Name of the entity this attribute belongs to",
        "attribute: Type of attribute (occupation, colour, nationality, status, description, title, role, material, etc.)",
        "value: The text value",
    ],
    "examples": [
        {"entity": "Alice", "attribute": "occupation", "value": "software engineer"},
        {"entity": "The car", "attribute": "colour", "value": "red"},
    ],
}


def _build_prompt(text: str) -> str:
    """Build the extraction prompt."""
    fields_str = "\n".join(f"- {f}" for f in ATTRIBUTES_SPEC["fields"])
    examples_str = ",\n    ".join(str(e).replace("'", '"') for e in ATTRIBUTES_SPEC["examples"])
    
    return f'''Extract {ATTRIBUTES_SPEC["description"]} from this text.

Text: {text}

For each item provide:
{fields_str}

Respond as a JSON list:
[
    {examples_str}
]

Only include items explicitly mentioned. Do not include numbers or dates.
'''


def extract_attributes(
    llm: LLM,
    text: str,
    *,
    context: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Extract text-based attributes from text.
    
    Uses LLM to identify non-numeric, non-temporal properties of entities.
    
    Args:
        llm: LLM instance from ixcore.
        text: Text to extract from.
        context: Optional context to help LLM understand the text.
    
    Returns:
        List of attribute dictionaries with keys:
        - entity: Entity name the attribute belongs to
        - attribute: Type of attribute
        - value: Text value
    
    Example:
        >>> attributes = extract_attributes(llm, "Alice is a software engineer who drives a red car")
        >>> attributes
        [
            {"entity": "Alice", "attribute": "occupation", "value": "software engineer"},
            {"entity": "car", "attribute": "colour", "value": "red"}
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
