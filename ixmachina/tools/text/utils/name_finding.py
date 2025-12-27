"""
Name finding and searching operations for NameRegistry.

Handles finding names in text using token-based and direct matching.
"""

from .normalize import extract_tokens, get_first_letter
from .token_matching import fuzzy_match_token, score_name_match


def find_name_in_text(
    registry,
    text: str,
    threshold: int = 70,
    token_threshold: int = 80
):
    """
    Find the best matching name from the registry in the given text.
    
    Uses a two-stage approach:
    1. Quick direct lookup (handles concatenated forms like "johnsmith")
    2. Token-based fuzzy matching if no direct match
    
    Args:
        registry: NameRegistry instance.
        text: Text to search in.
        threshold: Minimum score for name match.
        token_threshold: Minimum score for individual token matches.
        
    Returns:
        Tuple of (canonical_name, score, details) for best match, or None if no match.
    """
    # Extract tokens from text
    text_tokens = extract_tokens(text)
    if not text_tokens:
        return None
    
    # Quick check: Try direct name lookup first (handles concatenated forms like "johnsmith")
    # This is O(1) and much faster than token-based matching
    for text_token in text_tokens:
        canonical = registry.get_canonical(text_token)
        if canonical:
            # Found exact match! Get the name's token data for details
            first_letter = get_first_letter(canonical)
            if first_letter and first_letter in registry._names_by_letter:
                name_data = registry._names_by_letter[first_letter].get(canonical)
                if name_data:
                    # Return with perfect score
                    return (
                        canonical,
                        100,
                        {
                            'matched_tokens': name_data['tokens'],
                            'coverage': 1.0,
                            'positions': [text_tokens.index(text_token)],
                            'average_similarity': 100
                        }
                    )
    
    # Fuzzy match each text token against registry tokens
    token_matches = {}  # text_token -> [(registry_token, score)]
    
    for text_token in text_tokens:
        matches = fuzzy_match_token(text_token, registry._tokens_by_letter, token_threshold)
        if matches:
            token_matches[text_token] = matches
    
    if not token_matches:
        return None
    
    # Get candidate names from matched tokens
    candidate_names = set()
    for text_token, matches in token_matches.items():
        for registry_token, _ in matches:
            # Get all names containing this registry token
            names = registry.get_names_containing_token(registry_token)
            candidate_names.update(names)
    
    if not candidate_names:
        return None
    
    # Score each candidate name
    scored_candidates = []
    for candidate_name in candidate_names:
        name_tokens = registry.get_name_tokens(candidate_name)
        if not name_tokens:
            continue
        
        result = score_name_match(
            candidate_name,
            name_tokens,
            text_tokens,
            token_matches
        )
        if result:
            score, details = result
            if score >= threshold:
                scored_candidates.append((candidate_name, score, details))
    
    if not scored_candidates:
        return None
    
    # Return best match
    scored_candidates.sort(key=lambda x: (x[1], x[2]['coverage']), reverse=True)
    
    # Increment lookup counter
    registry._total_lookups += 1
    
    return scored_candidates[0]


def find_all_names_in_text(
    registry,
    text: str,
    threshold: int = 70,
    token_threshold: int = 80
) -> list[tuple[str, int, dict]]:
    """
    Find all names from the registry in the given text.
    
    Unlike find_name_in_text which returns the best match, this function
    returns ALL names that match above the threshold.
    
    Args:
        registry: NameRegistry instance.
        text: Text to search in.
        threshold: Minimum score for name match.
        token_threshold: Minimum score for individual token matches.
        
    Returns:
        List of (canonical_name, score, details) tuples, sorted by score descending.
    """
    # Extract tokens from text
    text_tokens = extract_tokens(text)
    if not text_tokens:
        return []
    
    # Fuzzy match each text token
    token_matches = {}
    for text_token in text_tokens:
        matches = fuzzy_match_token(text_token, registry._tokens_by_letter, token_threshold)
        if matches:
            token_matches[text_token] = matches
    
    if not token_matches:
        return []
    
    # Get candidate names
    candidate_names = set()
    for text_token, matches in token_matches.items():
        for registry_token, _ in matches:
            names = registry.get_names_containing_token(registry_token)
            candidate_names.update(names)
    
    if not candidate_names:
        return []
    
    # Score all candidates
    scored_candidates = []
    for candidate_name in candidate_names:
        name_tokens = registry.get_name_tokens(candidate_name)
        if not name_tokens:
            continue
        
        result = score_name_match(
            candidate_name,
            name_tokens,
            text_tokens,
            token_matches
        )
        if result:
            score, details = result
            if score >= threshold:
                scored_candidates.append((candidate_name, score, details))
    
    # Sort by score and coverage
    scored_candidates.sort(key=lambda x: (x[1], x[2]['coverage']), reverse=True)
    
    # Increment lookup counter
    registry._total_lookups += 1
    
    return scored_candidates

