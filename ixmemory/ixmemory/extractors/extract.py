"""
Combined extraction.

Uses specs from individual extractors to extract multiple types at once.
"""

from typing import Any, Dict, List, Optional, Union

from ixcore import LLM
from ixutils import parse_json_robust

from .entities import ENTITIES_SPEC
from .numbers import NUMBERS_SPEC
from .moments import MOMENTS_SPEC
from .attributes import ATTRIBUTES_SPEC
from .relationships import RELATIONSHIPS_SPEC
from .number_ranges import NUMBER_RANGES_SPEC
from .moment_ranges import MOMENT_RANGES_SPEC


# All available specs
SPECS = {
    "entities": ENTITIES_SPEC,
    "numbers": NUMBERS_SPEC,
    "moments": MOMENTS_SPEC,
    "attributes": ATTRIBUTES_SPEC,
    "relationships": RELATIONSHIPS_SPEC,
    "number_ranges": NUMBER_RANGES_SPEC,
    "moment_ranges": MOMENT_RANGES_SPEC,
}


def _format_example(example: Dict[str, Any]) -> str:
    """Format a single example as JSON string."""
    return str(example).replace("'", '"').replace("None", "null").replace("True", "true").replace("False", "false")


def _build_combined_prompt(text: str, specs: List[Dict[str, Any]]) -> str:
    """Build prompt for extracting multiple types."""
    sections = []
    example_parts = []
    
    for spec in specs:
        fields_str = "\n".join(f"    - {f}" for f in spec["fields"])
        sections.append(f"**{spec['key']}**: {spec['description']}\n{fields_str}")
        
        examples = ", ".join(_format_example(e) for e in spec["examples"])
        example_parts.append(f'    "{spec["key"]}": [{examples}]')
    
    sections_str = "\n\n".join(sections)
    examples_str = ",\n".join(example_parts)
    
    return f'''Extract the following from this text.

Text: {text}

{sections_str}

Respond as a JSON object:
{{
{examples_str}
}}

Only include items explicitly mentioned. Use empty lists for types with no matches.
'''


def extract(
    llm: LLM,
    text: str,
    types: List[str],
    *,
    context: Optional[str] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extract multiple types of information from text in one call.
    
    Args:
        llm: LLM instance from ixcore.
        text: Text to extract from.
        types: List of types to extract.
            Valid: "entities", "numbers", "moments", "attributes", "relationships",
                   "number_ranges", "moment_ranges"
        context: Optional context to help LLM understand the text.
    
    Returns:
        Dict with type names as keys, lists of extracted items as values.
    
    Example:
        >>> result = extract(llm, "Alice is 32 and works at Acme", types=["entities", "numbers"])
        >>> result
        {
            "entities": [{"name": "Alice", "type": "person"}, {"name": "Acme", "type": "organization"}],
            "numbers": [{"value": 32, "record_type": "age", "belongs_to": "Alice"}]
        }
    """
    # Validate types
    if not types:
        raise ValueError("types cannot be empty")
    
    for t in types:
        if t not in SPECS:
            raise ValueError(f"Unknown type: {t}. Valid: {', '.join(SPECS.keys())}")
    
    # Get specs for requested types
    specs = [SPECS[t] for t in types]
    
    # Build and send prompt
    prompt = _build_combined_prompt(text=text, specs=specs)
    if context:
        prompt = f"Context: {context}\n\n{prompt}"
    
    response = llm.query(user_prompt=prompt)
    parsed = parse_json_robust(response)
    
    # Ensure result has all requested types
    if isinstance(parsed, dict):
        result = {}
        for t in types:
            result[t] = parsed.get(t, [])
            if not isinstance(result[t], list):
                result[t] = []
        return result
    
    return {t: [] for t in types}
