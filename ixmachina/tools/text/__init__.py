"""
Text processing and entity recognition tools.

This package provides tools for:
- Name tracking and matching (fuzzy matching with standardization)
- Text normalization (for comparison and matching)
- Entity extraction from text
- First-letter-indexed dictionaries for efficient lookups

Main class: NameRegistry - handles all name registration and matching operations.
"""

"""
Text processing and entity recognition tools.

This package provides tools for:
- Name tracking and matching (fuzzy matching with standardization)
- Text normalization (for comparison and matching)
- Entity extraction from text
- First-letter-indexed dictionaries for efficient lookups

Main class: NameRegistry - handles all name registration and matching operations.
"""

from .name_registry import NameRegistry
from .utils.normalize import (
    normalize_for_matching,
    normalize_strict,
    get_first_letter,
    extract_tokens
)
from .utils.first_letter_dict import FirstLetterDict

__all__ = [
    'NameRegistry',
    'normalize_for_matching',
    'normalize_strict',
    'get_first_letter',
    'extract_tokens',
    'FirstLetterDict',
]

