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

# Agent-facing tool functions (require @bind with NameRegistry instance)
# These are not yet implemented as separate files - they should be created when needed
# from .add_name_to_registry import add_name_to_registry
# from .find_name import find_name
# from .find_all_names import find_all_names
# from .standardize_text import standardize_text
# from .add_name_alias import add_name_alias
# from .get_all_names_in_registry import get_all_names_in_registry
# from .save_registry import save_registry

__all__ = [
    'NameRegistry',
    'normalize_for_matching',
    'normalize_strict',
    'get_first_letter',
    'extract_tokens',
    'FirstLetterDict',
    # Agent tools - commented out until files are created
    # 'add_name_to_registry',
    # 'find_name',
    # 'find_all_names',
    # 'standardize_text',
    # 'add_name_alias',
    # 'get_all_names_in_registry',
    # 'save_registry',
]

