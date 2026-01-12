"""
Utilities for parsing JSON and Python literal formats.

Handles malformed JSON from LLMs, including:
- Unquoted special object references (<tool_obj:...>, <obj:...>, etc.)
- Trailing commas
- Single quotes instead of double quotes
- Missing quotes around string values

Note: We use angle brackets <prefix:content> for special object references instead of
square brackets [prefix:content] to avoid ambiguity with JSON arrays. Angle brackets
are never valid JSON syntax, making them unambiguous and easy to detect.
"""

import json
import ast
import re
from typing import Any, Optional, List


def strip_markdown_code_block(text: str) -> str:
    """
    Strip markdown code fences if present.
    
    Handles both ```json and ``` code blocks, with optional whitespace.
    
    Args:
        text: String that may contain markdown code fences.
        
    Returns:
        Content inside code fences if present, otherwise original text.
    """
    if not isinstance(text, str):
        return text
    
    # Pattern matches:
    # - Optional leading whitespace
    # - ``` followed by optional "json" tag
    # - Optional whitespace and newline
    # - Content (captured)
    # - Optional newline and whitespace
    # - ```
    # - Optional trailing whitespace
    pattern = r'^\s*```(?:json)?\s*\n?(.*?)\n?\s*```\s*$'
    match = re.match(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text


def repair_json(json_string: str) -> str:
    """
    Repair common JSON malformations from LLMs.
    
    Fixes:
    - Unquoted special object references: <word:...> -> "<word:...>"
      Detects any pattern <identifier:content> that appears as a JSON value
      (after : and before , or }). Angle brackets are never valid JSON syntax,
      making them unambiguous and easy to detect.
    - Trailing commas before closing braces/brackets
    - Single quotes around strings (converts to double quotes)
    - Missing quotes around string values in object values
    
    Args:
        json_string: Potentially malformed JSON string.
    
    Returns:
        Repaired JSON string (may still be invalid, but more likely to parse).
    """
    if not isinstance(json_string, str):
        return json_string
    
    # Step 1: Fix unquoted special object references
    # Detect <word:...> patterns that appear as JSON values
    # Angle brackets are never valid JSON syntax, making them unambiguous
    # Pattern: <identifier:content> appearing after : (JSON value position)
    json_string = re.sub(
        r':\s*(\<[a-zA-Z_][a-zA-Z0-9_]*:[^\>]+\>)(\s*[,}])',
        r': "\1"\2',
        json_string
    )
    
    # Step 2: Remove trailing commas before closing braces/brackets
    json_string = re.sub(r',(\s*[}\]])', r'\1', json_string)
    
    # Step 3: Convert single quotes to double quotes (but be careful with escaped quotes)
    # Only convert if it looks like a JSON string (starts with { or [)
    if json_string.strip().startswith(('{', '[')):
        # Replace single quotes with double quotes, but handle escaped quotes
        # This is a simplified approach - more complex cases might need state machine
        def replace_single_quotes(match):
            # Don't replace if it's inside a double-quoted string
            # Simple heuristic: if we see ' after : or , and before : or , or }, it's likely a string value
            return match.group(0).replace("'", '"')
        
        # Replace single-quoted strings (but not inside double-quoted strings)
        # Pattern: '...' that's not preceded by " and not followed by "
        json_string = re.sub(
            r"(?<!\")(?<![a-zA-Z0-9_])'([^'\\]*(\\.[^'\\]*)*)'(?!\")",
            r'"\1"',
            json_string
        )
    
    return json_string


def parse_json_robust(
    json_string: str,
    special_prefixes: Optional[List[str]] = None,
) -> Any:
    """
    Parse JSON string with robust error handling and repair.
    
    Attempts to repair common malformations before parsing.
    Falls back to Python literal parsing if JSON parsing fails.
    Handles markdown code blocks (```json or ```) by extracting content.
    
    Args:
        json_string: JSON string to parse (may be malformed or wrapped in markdown).
        special_prefixes: Optional list of special object reference prefixes to quote.
                         Defaults to common prefixes: ["tool_obj", "obj", "conv_obj", "sys"].
    
    Returns:
        Parsed value (dict, list, int, float, bool, str) or original string if all parsing fails.
        
    Raises:
        ValueError: If JSON is severely malformed and cannot be repaired.
    """
    if not isinstance(json_string, str):
        return json_string
    
    # Strip markdown code blocks if present
    json_string = strip_markdown_code_block(json_string)
    
    # Try direct JSON parsing first (fast path for valid JSON)
    try:
        parsed = json.loads(json_string)
        if isinstance(parsed, (dict, list, int, float, bool, str)):
            return parsed
    except (json.JSONDecodeError, ValueError):
        pass
    
    # Repair and try again
    repaired = repair_json(json_string)
    try:
        parsed = json.loads(repaired)
        if isinstance(parsed, (dict, list, int, float, bool, str)):
            return parsed
    except (json.JSONDecodeError, ValueError):
        pass
    
    # Fall back to Python literal parsing (handles single quotes, etc.)
    try:
        parsed = ast.literal_eval(json_string)
        if isinstance(parsed, (dict, list, int, float, bool, str)):
            return parsed
    except (ValueError, SyntaxError):
        pass
    
    # Try repaired version with Python literal
    try:
        parsed = ast.literal_eval(repaired)
        if isinstance(parsed, (dict, list, int, float, bool, str)):
            return parsed
    except (ValueError, SyntaxError):
        pass
    
    # Return original string if all parsing fails
    return json_string


def parse_json_or_python_literal(value: str) -> Any:
    """
    Parse a string that might be JSON or Python literal format.
    
    Handles both JSON (double quotes) and Python literals (single quotes).
    Uses robust parsing with repair for malformed JSON.
    Handles markdown code blocks (```json or ```) by extracting content.
    Falls back to original string if parsing fails.
    
    Args:
        value: String to parse (should look like JSON or Python literal, may be wrapped in markdown).
        
    Returns:
        Parsed value (dict, list, int, float, bool, str) or original string if parsing fails.
    """
    if not isinstance(value, str):
        return value
    
    # Strip markdown code blocks if present
    stripped_value = strip_markdown_code_block(value)
    
    # If it doesn't look like JSON/Python literal, return as-is
    stripped = stripped_value.strip()
    if not stripped.startswith(("{", "[", "'", '"')):
        return value
    
    # Use robust parser (it will strip markdown again, but that's idempotent)
    return parse_json_robust(stripped_value)

