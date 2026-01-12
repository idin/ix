"""
Relationship extraction.

Extracts connections between entities.
"""

from typing import Any, Dict, List, Optional

from ixcore import LLM
from ixutils import parse_json_robust


# Spec that can be used alone or combined with other specs
RELATIONSHIPS_SPEC = {
    "key": "relationships",
    "description": "connections between entities",
    "fields": [
        "source: Name of the source entity",
        "relationship: Type (works_at, lives_in, knows, owns, created, married_to, parent_of, member_of, located_in, part_of, etc.)",
        "target: Name of the target entity",
        "bidirectional: true if goes both ways (married_to, friends_with), false otherwise",
    ],
    "examples": [
        {"source": "Alice", "relationship": "works_at", "target": "Acme Corp", "bidirectional": False},
        {"source": "Alice", "relationship": "married_to", "target": "Bob", "bidirectional": True},
    ],
}


def _build_prompt(text: str) -> str:
    """Build the extraction prompt."""
    fields_str = "\n".join(f"- {f}" for f in RELATIONSHIPS_SPEC["fields"])
    examples_str = ",\n    ".join(
        str(e).replace("'", '"').replace("True", "true").replace("False", "false")
        for e in RELATIONSHIPS_SPEC["examples"]
    )
    
    return f'''Extract {RELATIONSHIPS_SPEC["description"]} from this text.

Text: {text}

For each item provide:
{fields_str}

Respond as a JSON list:
[
    {examples_str}
]

Only include relationships explicitly stated or strongly implied.
'''


def extract_relationships(
    llm: LLM,
    text: str,
    *,
    context: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Extract relationships between entities from text.
    
    Uses LLM to identify how entities are connected.
    
    Args:
        llm: LLM instance from ixcore.
        text: Text to extract from.
        context: Optional context to help LLM understand the text.
    
    Returns:
        List of relationship dictionaries with keys:
        - source: Source entity name
        - relationship: Type of relationship
        - target: Target entity name
        - bidirectional: Whether relationship goes both ways
    
    Example:
        >>> relationships = extract_relationships(llm, "Alice works at Acme Corp and is married to Bob")
        >>> relationships
        [
            {"source": "Alice", "relationship": "works_at", "target": "Acme Corp", "bidirectional": false},
            {"source": "Alice", "relationship": "married_to", "target": "Bob", "bidirectional": true}
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
