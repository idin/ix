"""
Text standardization operations for NameRegistry.

Handles standardizing names in text by replacing them with canonical forms.
"""

from .normalize import extract_tokens
from .name_finding import find_all_names_in_text


def standardize_names_in_text(
    registry,
    text: str,
    threshold: int = 70,
    token_threshold: int = 80
) -> dict:
    """
    Standardize ALL names in text by replacing them with their canonical forms.
    
    Finds all matching names and replaces them in the original text,
    preserving formatting and non-name portions.
    
    Args:
        registry: NameRegistry instance.
        text: Text to standardize (often a file name).
        threshold: Minimum score for name match.
        token_threshold: Minimum score for token matches.
        
    Returns:
        Dictionary with keys:
        - standardized_text: Text with names replaced by canonical forms
        - original_text: Original input text
        - names_found: List of canonical names that were found and replaced
        - num_replacements: Number of names replaced
    """
    # Find all names in the text
    matches = find_all_names_in_text(registry, text, threshold, token_threshold)
    
    if not matches:
        return {
            'standardized_text': text,
            'original_text': text,
            'names_found': [],
            'num_replacements': 0
        }
    
    # Extract tokens to find their positions in the original text
    text_tokens = extract_tokens(text)
    if not text_tokens:
        return {
            'standardized_text': text,
            'original_text': text,
            'names_found': [],
            'num_replacements': 0
        }
    
    # Build a map of which text token positions are "claimed" by which name
    # This prevents overlapping replacements
    token_to_name = {}  # position -> (canonical_name, sorted_positions)
    
    for canonical_name, score, details in matches:
        # Get positions this name matched
        positions = details['positions']
        
        # Check if any of these positions are already claimed
        conflict = any(pos in token_to_name for pos in positions)
        
        if not conflict:
            # Claim all these positions for this name
            # We only store at the first position
            first_pos = min(positions)
            token_to_name[first_pos] = (canonical_name, sorted(positions))
    
    # Sort by position to process in order
    sorted_matches = sorted(token_to_name.items(), key=lambda x: x[0])
    
    # Build list of replacements: (start_char, end_char, replacement)
    replacements = []
    found_names = []
    text_lower = text.lower()
    
    for first_token_pos, (canonical_name, positions) in sorted_matches:
        # Get the tokens for this name
        tokens_to_find = [text_tokens[pos] for pos in positions]
        
        # Find the character span in the original text
        # Start with the first token
        first_token = tokens_to_find[0]
        last_token = tokens_to_find[-1]
        
        # Start searching after previous replacement (if any)
        search_start = 0
        if replacements:
            search_start = replacements[-1][1]
        
        # Find first token
        first_char_idx = text_lower.find(first_token, search_start)
        if first_char_idx == -1:
            continue
        
        # Find last token (must be after first token)
        last_char_idx = text_lower.find(last_token, first_char_idx + len(first_token))
        if last_char_idx == -1:
            # Single token case
            if len(tokens_to_find) == 1:
                last_char_idx = first_char_idx
            else:
                continue
        
        # The span is from first_char_idx to end of last token
        span_start = first_char_idx
        span_end = last_char_idx + len(last_token)
        
        replacements.append((span_start, span_end, canonical_name))
        found_names.append(canonical_name)
    
    # Apply replacements from end to start to preserve indices
    standardized = text
    for start, end, replacement in reversed(replacements):
        standardized = standardized[:start] + replacement + standardized[end:]
    
    return {
        'standardized_text': standardized,
        'original_text': text,
        'names_found': list(set(found_names)),  # Unique names
        'num_replacements': len(found_names)
    }

