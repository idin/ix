"""
Core registry operations for NameRegistry.

This module contains helper functions for the core operations of NameRegistry
to help keep the class size manageable.
"""

from typing import Optional
from collections import defaultdict

from .normalize import normalize_for_matching, normalize_strict, get_first_letter, extract_tokens
from .first_letter_dict import FirstLetterDict


def add_name_to_registry(
    registry,
    name: str,
) -> str:
    """
    Add a name to the registry (helper function).
    
    This is the core implementation of add_name, extracted to reduce class size.
    """
    # Canonical form is exactly as provided
    canonical = name
    
    # Get normalized forms for matching
    normalized = normalize_for_matching(name)
    strict = normalize_strict(name)
    
    # Get first letter
    first_letter = get_first_letter(name)
    if first_letter is None:
        raise ValueError(f"Name '{name}' has no alphabetic characters")
    
    # Check if we already have this name (by normalized form)
    if normalized in registry._normalized_to_canonical:
        # Already exists - increment count and return existing canonical
        existing_canonical = registry._normalized_to_canonical[normalized]
        existing_first_letter = get_first_letter(existing_canonical)
        if existing_first_letter and existing_first_letter in registry._names_by_letter:
            if existing_canonical in registry._names_by_letter[existing_first_letter]:
                registry._names_by_letter[existing_first_letter][existing_canonical]['count'] += 1
        return existing_canonical
    
    # Extract tokens from the name (already normalized by extract_tokens)
    tokens = extract_tokens(name)
    
    # Store normalized tokens with their positions
    # Note: tokens are already normalized, no need to normalize again
    token_data = []
    for i, token in enumerate(tokens):
        token_data.append({
            'token': token,
            'position': i,
            'normalized': token,  # Already normalized by extract_tokens
            'strict': normalize_strict(token)
        })
    
    # Create concatenated form (all tokens together, no spaces)
    concatenated = ''.join([t['normalized'] for t in token_data])
    
    # New name - add it
    registry._names_by_letter[first_letter][canonical] = {
        'normalized': normalized,
        'strict': strict,
        'count': 1,
        'tokens': token_data,
        'num_tokens': len(tokens),
        'concatenated': concatenated  # "johnsmith" for "John Smith"
    }
    
    # Update reverse lookups (using FirstLetterDict)
    registry._normalized_to_canonical[normalized] = canonical
    registry._strict_to_canonical[strict] = canonical
    registry._concatenated_to_canonical[concatenated] = canonical
    
    # Index tokens
    for token_info in token_data:
        token = token_info['token']
        token_normalized = token_info['normalized']
        token_first_letter = get_first_letter(token)
        
        if token_first_letter is None:
            continue
        
        # Add to token index
        if token_normalized not in registry._tokens_by_letter[token_first_letter]:
            registry._tokens_by_letter[token_first_letter][token_normalized] = {
                'names': [],
                'normalized': token_normalized,
                'strict': token_info['strict']
            }
        
        # Add this name to the token's list (if not already there)
        if canonical not in registry._tokens_by_letter[token_first_letter][token_normalized]['names']:
            registry._tokens_by_letter[token_first_letter][token_normalized]['names'].append(canonical)
    
    return canonical


def get_canonical_from_registry(
    registry,
    name: str,
) -> Optional[str]:
    """
    Get canonical name from registry (helper function).
    
    This is the core implementation of get_canonical, extracted to reduce class size.
    """
    normalized = normalize_for_matching(name)
    strict = normalize_strict(name)
    
    # Try normalized lookup first (most common)
    canonical = registry._normalized_to_canonical.get(normalized)
    if canonical:
        return canonical
    
    # Try strict lookup
    canonical = registry._strict_to_canonical.get(strict)
    if canonical:
        return canonical
    
    # Try concatenated lookup (for "johnsmith" -> "John Smith")
    canonical = registry._concatenated_to_canonical.get(strict)
    if canonical:
        return canonical
    
    # Try alias lookup
    canonical = registry._alias_to_canonical.get(normalized)
    if canonical:
        return canonical
    
    return None


def add_alias_to_registry(
    registry,
    canonical_name: str,
    alias: str,
) -> dict:
    """
    Add an alias for a canonical name (helper function).
    
    This is the core implementation of add_alias, extracted to reduce class size.
    """
    # Check if canonical name exists
    first_letter = get_first_letter(canonical_name)
    if first_letter is None or first_letter not in registry._names_by_letter:
        return {
            'success': False,
            'error': f"Canonical name '{canonical_name}' not found in registry",
            'canonical_name': canonical_name,
            'alias': alias
        }
    
    if canonical_name not in registry._names_by_letter[first_letter]:
        return {
            'success': False,
            'error': f"Canonical name '{canonical_name}' not found in registry",
            'canonical_name': canonical_name,
            'alias': alias
        }
    
    # Normalize the alias
    alias_normalized = normalize_for_matching(alias)
    
    # Check if alias already points to a different canonical name
    existing_canonical = registry._alias_to_canonical.get(alias_normalized)
    if existing_canonical and existing_canonical != canonical_name:
        return {
            'success': False,
            'error': f"Alias '{alias}' already points to '{existing_canonical}'",
            'canonical_name': canonical_name,
            'alias': alias,
            'existing_canonical': existing_canonical
        }
    
    # Add the alias
    registry._alias_to_canonical[alias_normalized] = canonical_name
    
    # Track aliases in the name's data
    name_data = registry._names_by_letter[first_letter][canonical_name]
    if 'aliases' not in name_data:
        name_data['aliases'] = []
    
    if alias not in name_data['aliases']:
        name_data['aliases'].append(alias)
    
    return {
        'success': True,
        'canonical_name': canonical_name,
        'alias': alias,
        'aliases': name_data['aliases']
    }


def get_all_tokens_from_registry(
    registry,
    sort_by_frequency: bool = False,
) -> list[tuple[str, int]]:
    """
    Get all tokens from registry (helper function).
    
    This is the core implementation of get_all_tokens, extracted to reduce class size.
    """
    tokens = []
    
    for letter_dict in registry._tokens_by_letter.values():
        for token, data in letter_dict.items():
            frequency = len(data['names'])
            tokens.append((token, frequency))
    
    if sort_by_frequency:
        tokens.sort(key=lambda x: x[1], reverse=True)
    else:
        tokens.sort(key=lambda x: x[0])
    
    return tokens


def get_name_tokens_from_registry(
    registry,
    canonical_name: str,
) -> Optional[list[str]]:
    """
    Get tokens for a canonical name (helper function).
    
    This is the core implementation of get_name_tokens, extracted to reduce class size.
    """
    first_letter = get_first_letter(canonical_name)
    if first_letter is None:
        return None
    
    if first_letter not in registry._names_by_letter:
        return None
    
    if canonical_name not in registry._names_by_letter[first_letter]:
        return None
    
    token_data = registry._names_by_letter[first_letter][canonical_name]['tokens']
    return [t['token'] for t in token_data]


def get_usage_count_from_registry(
    registry,
    canonical_name: str,
) -> int:
    """
    Get usage count for a canonical name (helper function).
    
    This is the core implementation of get_usage_count, extracted to reduce class size.
    """
    first_letter = get_first_letter(canonical_name)
    if first_letter is None:
        return 0
    
    if first_letter not in registry._names_by_letter:
        return 0
    
    if canonical_name not in registry._names_by_letter[first_letter]:
        return 0
    
    return registry._names_by_letter[first_letter][canonical_name]['count']


def get_all_names_from_registry(
    registry,
    sort_by_usage: bool = False,
) -> list[tuple[str, int]]:
    """
    Get all names from registry (helper function).
    
    This is the core implementation of get_all_names, extracted to reduce class size.
    """
    names = []
    
    for letter_dict in registry._names_by_letter.values():
        for canonical, data in letter_dict.items():
            names.append((canonical, data['count']))
    
    if sort_by_usage:
        names.sort(key=lambda x: x[1], reverse=True)
    else:
        names.sort(key=lambda x: x[0])
    
    return names


def get_statistics_from_registry(registry) -> dict:
    """
    Get statistics from registry (helper function).
    
    This is the core implementation of get_statistics, extracted to reduce class size.
    """
    total_names = sum(
        len(letter_dict)
        for letter_dict in registry._names_by_letter.values()
    )
    
    total_tokens = sum(
        len(letter_dict)
        for letter_dict in registry._tokens_by_letter.values()
    )
    
    names_by_letter = {
        letter: len(letter_dict)
        for letter, letter_dict in registry._names_by_letter.items()
    }
    
    tokens_by_letter = {
        letter: len(letter_dict)
        for letter, letter_dict in registry._tokens_by_letter.items()
    }
    
    # Get most used names
    all_names = get_all_names_from_registry(registry, sort_by_usage=True)
    most_used = all_names[:10]
    
    # Get most common tokens
    all_tokens = get_all_tokens_from_registry(registry, sort_by_frequency=True)
    most_common_tokens = all_tokens[:10]
    
    return {
        'total_names': total_names,
        'total_tokens': total_tokens,
        'total_lookups': registry._total_lookups,
        'names_by_letter': dict(sorted(names_by_letter.items())),
        'tokens_by_letter': dict(sorted(tokens_by_letter.items())),
        'most_used': most_used,
        'most_common_tokens': most_common_tokens
    }


def get_names_containing_token_from_registry(
    registry,
    token: str,
) -> list[str]:
    """
    Get names containing a token (helper function).
    
    This is the core implementation of get_names_containing_token, extracted to reduce class size.
    """
    token_normalized = normalize_for_matching(token)
    token_first_letter = get_first_letter(token)
    
    if token_first_letter is None:
        return []
    
    if token_first_letter not in registry._tokens_by_letter:
        return []
    
    if token_normalized not in registry._tokens_by_letter[token_first_letter]:
        return []
    
    return registry._tokens_by_letter[token_first_letter][token_normalized]['names'].copy()


def get_aliases_from_registry(
    registry,
    canonical_name: str,
) -> Optional[list[str]]:
    """
    Get aliases for a canonical name (helper function).
    
    This is the core implementation of get_aliases, extracted to reduce class size.
    """
    first_letter = get_first_letter(canonical_name)
    if first_letter is None:
        return None
    
    if first_letter not in registry._names_by_letter:
        return None
    
    if canonical_name not in registry._names_by_letter[first_letter]:
        return None
    
    name_data = registry._names_by_letter[first_letter][canonical_name]
    return name_data.get('aliases', []).copy() if 'aliases' in name_data else []


def get_names_by_letter_from_registry(
    registry,
    letter: str,
) -> list[str]:
    """
    Get names by letter (helper function).
    
    This is the core implementation of get_names_by_letter, extracted to reduce class size.
    """
    letter = letter.lower()
    if letter not in registry._names_by_letter:
        return []
    
    return sorted(registry._names_by_letter[letter].keys())


def get_registry_length(registry) -> int:
    """
    Get total number of unique names in registry (helper function).
    
    This is the core implementation of __len__, extracted to reduce class size.
    """
    return sum(
        len(letter_dict)
        for letter_dict in registry._names_by_letter.values()
    )


def registry_contains_name(registry, name: str) -> bool:
    """
    Check if a name exists in the registry (helper function).
    
    This is the core implementation of __contains__, extracted to reduce class size.
    """
    return get_canonical_from_registry(registry, name) is not None


def get_registry_repr(registry) -> str:
    """
    Get string representation of registry (helper function).
    
    This is the core implementation of __repr__, extracted to reduce class size.
    """
    total_tokens = sum(
        len(letter_dict)
        for letter_dict in registry._tokens_by_letter.values()
    )
    return f"NameRegistry(names={get_registry_length(registry)}, tokens={total_tokens}, lookups={registry._total_lookups})"
