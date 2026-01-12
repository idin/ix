"""
Utility functions for text tools.

This package contains internal helper functions and classes used by the
text tools, but are not meant to be used directly by users.
"""

from .normalize import normalize_for_matching, normalize_strict, get_first_letter, extract_tokens
from .first_letter_dict import FirstLetterDict
from .token_matching import fuzzy_match_token, score_name_match
from .name_finding import find_name_in_text, find_all_names_in_text
from .standardize_names_in_text import standardize_names_in_text
from .save_load import save_to_json, load_from_json, save_to_pickle, load_from_pickle

__all__ = [
    'normalize_for_matching',
    'normalize_strict',
    'get_first_letter',
    'extract_tokens',
    'FirstLetterDict',
    'fuzzy_match_token',
    'score_name_match',
    'find_name_in_text',
    'find_all_names_in_text',
    'standardize_names_in_text',
    'save_to_json',
    'load_from_json',
    'save_to_pickle',
    'load_from_pickle',
]

