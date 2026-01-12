"""
Token matching utilities for NameRegistry.

Handles fuzzy matching of tokens against the registry's token index.
"""

from typing import Optional
from rapidfuzz import fuzz, process

from .normalize import normalize_for_matching, get_first_letter


def fuzzy_match_token(
    token: str,
    tokens_by_letter: dict,
    threshold: int = 80
) -> list[tuple[str, int]]:
    """
    Find fuzzy matches for a single token in the registry.
    
    Uses a two-stage approach for efficiency:
    1. Try exact match first (O(1) hash lookup)
    2. Fall back to batch fuzzy matching if no exact match
    
    Args:
        token: Token to match.
        tokens_by_letter: Token registry organized by first letter.
        threshold: Minimum similarity score.
        
    Returns:
        List of (registered_token, score) tuples for matches above threshold.
    """
    token_normalized = normalize_for_matching(token)
    token_first_letter = get_first_letter(token)
    
    if token_first_letter is None:
        return []
    
    # Get all tokens starting with same letter
    if token_first_letter not in tokens_by_letter:
        return []
    
    tokens_dict = tokens_by_letter[token_first_letter]
    
    # Stage 1: Try exact match first (O(1) hash lookup)
    if token_normalized in tokens_dict:
        return [(token_normalized, 100)]
    
    # Stage 2: No exact match, use batch fuzzy matching (much faster)
    # RapidFuzz can match one query against many candidates efficiently
    registered_tokens = list(tokens_dict.keys())
    # extractOne returns (match, score, index) or None
    results = process.extract(
        query=token_normalized,
        choices=registered_tokens,
        scorer=fuzz.ratio,
        score_cutoff=threshold,
        limit=None  # Get all matches above threshold
    )
    
    # Convert to our format: [(token, score)]
    matches = [(match, score) for match, score, _ in results]
    
    # Already sorted by score descending by RapidFuzz
    return matches


def score_name_match(
    name_canonical: str,
    name_tokens: list[dict],
    text_tokens: list[str],
    token_matches: dict[str, list[tuple[str, int]]]
) -> Optional[tuple[int, dict]]:
    """
    Score how well a name matches the text based on its tokens.
    
    Args:
        name_canonical: Canonical name to score.
        name_tokens: Token data for the name.
        text_tokens: Tokens extracted from text.
        token_matches: Dict of text_token -> [(registry_token, score)]
        
    Returns:
        Tuple of (total_score, details) or None if no match.
        Details include: matched_tokens, coverage, average_score, positions
    """
    if not name_tokens:
        return None
    
    # Try to match each name token to text tokens
    matched_name_tokens = {}  # name_token -> (text_position, score)
    
    for token_info in name_tokens:
        name_token = token_info['normalized']
        best_score = 0
        best_position = -1
        
        # Check each text token
        for text_pos, text_token in enumerate(text_tokens):
            if text_token not in token_matches:
                continue
            
            # Check if this text token matched our name token
            for matched_token, score in token_matches[text_token]:
                if matched_token == name_token:
                    if score > best_score:
                        best_score = score
                        best_position = text_pos
        
        if best_score > 0:
            matched_name_tokens[name_token] = (best_position, best_score)
    
    if not matched_name_tokens:
        return None
    
    # Calculate coverage (what fraction of name tokens matched)
    coverage = len(matched_name_tokens) / len(name_tokens)
    
    # Calculate average similarity score
    total_score = sum(score for _, score in matched_name_tokens.values())
    average_similarity = total_score / len(matched_name_tokens)
    
    # Combine coverage and average similarity
    # Coverage is more important than individual token scores
    final_score = int(coverage * 70 + average_similarity * 0.3)
    
    # Bonus for adjacent tokens
    positions = sorted([pos for pos, _ in matched_name_tokens.values()])
    if len(positions) > 1:
        # Check if positions are consecutive
        is_adjacent = all(positions[i+1] == positions[i] + 1 for i in range(len(positions) - 1))
        if is_adjacent:
            final_score = min(100, int(final_score * 1.1))  # 10% bonus
    
    # Calculate adjacency bonus
    adjacency_bonus = 0
    if len(positions) > 1:
        is_adjacent = all(positions[i+1] == positions[i] + 1 for i in range(len(positions) - 1))
        if is_adjacent:
            adjacency_bonus = 20  # Boost score for adjacent matches
    
    return (
        final_score,
        {
            'matched_tokens': matched_name_tokens,
            'coverage': coverage,
            'average_score': average_similarity,
            'adjacency_bonus': adjacency_bonus,
            'positions': positions
        }
    )

