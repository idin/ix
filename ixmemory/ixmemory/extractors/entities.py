"""
Entity extraction.

Extracts people, places, organizations, and concepts from text.
"""

from typing import Any, Dict, List, Optional

from ixcore import LLM
from ixutils import parse_json_robust


# Spec that can be used alone or combined with other specs
ENTITIES_SPEC = {
    "key": "entities",
    "description": "people, places, organizations, concepts, brands, products, projects",
    "fields": [
        "name: The name as mentioned in text",
        "type: One of person, place, organization, concept, brand, product, project",
        "description: Brief description (optional)",
    ],
    "examples": [
        {"name": "John Smith", "type": "person", "description": "A software engineer"},
        {"name": "Acme Corp", "type": "organization", "description": "A technology company"},
    ],
}


def _build_prompt(text: str) -> str:
    """Build the extraction prompt."""
    fields_str = "\n".join(f"- {f}" for f in ENTITIES_SPEC["fields"])
    examples_str = ",\n    ".join(str(e).replace("'", '"') for e in ENTITIES_SPEC["examples"])
    
    return f'''Extract {ENTITIES_SPEC["description"]} from this text.

Text: {text}

For each item provide:
{fields_str}

Respond as a JSON list:
[
    {examples_str}
]

Only include items explicitly mentioned. Do not infer or assume.
'''


def extract_entities(
    llm: LLM,
    text: str,
    *,
    context: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Extract entities from text.
    
    Uses LLM to identify people, places, organizations, and concepts.
    
    Args:
        llm: LLM instance from ixcore.
        text: Text to extract from.
        context: Optional context to help LLM understand the text.
    
    Returns:
        List of entity dictionaries with keys:
        - name: Display name
        - type: Entity type (person, place, organization, concept)
        - description: Optional description
    
    Example:
        >>> entities = extract_entities(llm, "Alice works at Acme Corp in London")
        >>> entities
        [
            {"name": "Alice", "type": "person"},
            {"name": "Acme Corp", "type": "organization"},
            {"name": "London", "type": "place"}
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
