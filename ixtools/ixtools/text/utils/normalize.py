"""
Text normalization utilities.

Provides functions for normalizing text for comparison, matching, and standardization.
"""

import re
from typing import Optional


def normalize_for_matching(text: str) -> str:
    """
    Normalize text for fuzzy matching.
    
    Converts text to a standardized form suitable for comparison:
    - Lowercase
    - Remove extra whitespace
    - Remove special characters except spaces
    - Collapse multiple spaces to single space
    
    This is used for fuzzy matching where we want to be lenient about
    formatting differences but strict about content.
    
    Args:
        text: Text to normalize.
        
    Returns:
        Normalized text.
        
    Example:
        >>> normalize_for_matching("John_Smith")
        'john smith'
        >>> normalize_for_matching("ANNE-MARIE  Wilson")
        'anne marie wilson'
        >>> normalize_for_matching("john.smith")
        'john smith'
    """
    # Lowercase
    text = text.lower()
    
    # Replace underscores, hyphens, dots, and other separators with spaces
    text = re.sub(r'[_\-\.]', ' ', text)
    
    # Remove special characters except spaces
    text = re.sub(r'[^a-z0-9\s]', '', text)
    
    # Collapse multiple spaces to single space
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    return text.strip()


def normalize_strict(text: str) -> str:
    """
    Strict normalization - remove ALL whitespace and special characters.
    
    This creates a completely stripped-down version for very aggressive matching:
    - Lowercase
    - Remove ALL whitespace
    - Remove ALL special characters
    - Only keep letters and numbers
    
    Use this when you want to match "JohnSmith" with "john_smith" or "John Smith".
    
    Args:
        text: Text to normalize.
        
    Returns:
        Strictly normalized text (no spaces, no special chars).
        
    Example:
        >>> normalize_strict("John Smith")
        'johnsmith'
        >>> normalize_strict("Anne-Marie_Wilson")
        'anniemariewilson'
    """
    # Lowercase
    text = text.lower()
    
    # Remove ALL non-alphanumeric characters
    text = re.sub(r'[^a-z0-9]', '', text)
    
    return text


def get_first_letter(text: str) -> Optional[str]:
    """
    Get the first alphabetic letter from text.
    
    Skips over numbers and special characters to find the first letter.
    Returns lowercase letter or None if no letters found.
    
    Args:
        text: Text to extract first letter from.
        
    Returns:
        First alphabetic letter (lowercase) or None if no letters.
        
    Example:
        >>> get_first_letter("John Smith")
        'j'
        >>> get_first_letter("123 Main St")
        'm'
        >>> get_first_letter("  Anne")
        'a'
        >>> get_first_letter("456")
        None
    """
    # Find first alphabetic character
    match = re.search(r'[a-zA-Z]', text)
    if match:
        return match.group(0).lower()
    return None


def extract_tokens(text: str) -> list[str]:
    """
    Extract word tokens from text.
    
    Splits text on whitespace and special characters, returning
    only tokens with alphabetic content.
    
    Args:
        text: Text to tokenize.
        
    Returns:
        List of tokens (words).
        
    Example:
        >>> extract_tokens("John_Smith-Wilson")
        ['john', 'smith', 'wilson']
        >>> extract_tokens("2024_Anne_Marie.txt")
        ['anne', 'marie', 'txt']
    """
    # Normalize first
    normalized = normalize_for_matching(text)
    
    # Split on whitespace
    tokens = normalized.split()
    
    # Filter out tokens that are only numbers
    return [t for t in tokens if re.search(r'[a-z]', t)]

