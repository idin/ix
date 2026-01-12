"""
Counting operations for strings, words, items, and element occurrences.

Provides functions to count characters, words, items in iterables, and
occurrences of specific elements.
"""

from typing import Dict, Any, Union, List, Tuple, Set, Optional, Iterable
from collections import Counter

from ..constants import SUCCESS_KEY, RESULT_KEY, ERROR_KEY


def count_characters(
    text: str,
    case_sensitive: bool = False,
) -> Dict[str, Any]:
    """
    Count the number of characters in a string without exceptions (spaces are characters)
    as well as the length of the string and number of unique characters.
    
    Args:
        text: The string to count characters in.
        case_sensitive: If False, treat uppercase and lowercase characters as the same
            when counting unique characters (default: False).
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - result: Dictionary containing:
                - total: Total number of characters (including spaces).
                - unique_elements: Dictionary mapping each unique character to its count.
                - total_unique: Number of unique characters.
            - error: Error message if operation failed (None if successful).
    """
    try:
        if not isinstance(text, str):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Expected string, got {type(text).__name__}",
            }
        
        total = len(text)
        
        # Count characters (case-sensitive or not)
        if case_sensitive:
            char_counts = Counter(text)
        else:
            char_counts = Counter(text.lower())
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: {
                "total": total,
                "unique_elements": dict(char_counts),
                "total_unique": len(char_counts),
            },
            ERROR_KEY: None,
        }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error counting characters: {str(e)}",
        }


def count_words(
    text: str,
    case_sensitive: bool = False,
) -> Dict[str, Any]:
    """
    Count the number of each unique word, 
    as well as total number of unique words and total number of words.
    
    Words are separated by whitespace. Empty strings return 0 words.
    
    Args:
        text: The string to count words in.
        case_sensitive: If False, treat uppercase and lowercase words as the same
            when counting unique words (default: False).
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - result: Dictionary containing:
                - unique_elements: Dictionary mapping each unique word to its count.
                - total_unique: Number of unique words.
                - total: Total number of words.
            - error: Error message if operation failed (None if successful).
    """
    try:
        if not isinstance(text, str):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Expected string, got {type(text).__name__}",
            }
        
        words = text.split()
        total = len(words)
        
        # Count words (case-sensitive or not)
        if case_sensitive:
            word_counts = Counter(words)
        else:
            word_counts = Counter(word.lower() for word in words)
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: {
                "unique_elements": dict(word_counts),
                "total_unique": len(word_counts),
                "total": total,
            },
            ERROR_KEY: None,
        }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error counting words: {str(e)}",
        }


def count_items(
    iterable: Union[List[Any], Tuple[Any, ...], Set[Any], str],
) -> Dict[str, Any]:
    """
    Count the number of items in an iterable, 
    as well as the number of unique items and total number of items.
    
    Args:
        iterable: The iterable to count items in (list, tuple, set, or string).
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - result: Dictionary containing:
                - unique_elements: Dictionary mapping each unique item to its count.
                - total_unique: Number of unique items.
                - total: Total number of items.
            - error: Error message if operation failed (None if successful).
    """
    try:
        if not isinstance(iterable, (list, tuple, set, str)):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Expected list, tuple, set, or string, got {type(iterable).__name__}",
            }
        
        # Convert to list for counting (handles sets and tuples)
        iterable_list = list(iterable)
        total = len(iterable_list)
        
        # Count unique elements
        item_counts = Counter(iterable_list)
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: {
                "unique_elements": dict(item_counts),
                "total_unique": len(item_counts),
                "total": total,
            },
            ERROR_KEY: None,
        }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error counting items: {str(e)}",
        }


def count(
    iterable: Union[List[Any], Tuple[Any, ...], Set[Any], str],
) -> Dict[str, Any]:
    """
    Count the total number of elements in an iterable.
    
    This is a simple wrapper that returns the length of the iterable.
    
    Args:
        iterable: The iterable to count (list, tuple, set, or string).
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - result: Total number of elements.
            - error: Error message if operation failed (None if successful).
    """
    try:
        if not isinstance(iterable, (list, tuple, set, str)):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Expected list, tuple, set, or string, got {type(iterable).__name__}",
            }
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: len(iterable),
            ERROR_KEY: None,
        }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error counting: {str(e)}",
        }


def count_occurrences(
    iterable: Union[List[Any], Tuple[Any, ...], Set[Any], str],
    elements: Optional[Union[List[Any], Tuple[Any, ...], Set[Any], Any]] = None,
) -> Dict[str, Any]:
    """
    Count the occurrences of elements in an iterable.
    
    If no elements are provided, count each unique element and return statistics
    including total number of unique elements and total number of elements.
    If elements are provided, count only those elements and return a dictionary
    of the counts, including which elements existed and total occurrences.
    
    If iterable is a string:
        - If elements are provided, count occurrences of those characters/substrings.
        - If elements are not provided, count words and characters.
    
    Args:
        iterable: The iterable to count occurrences in (list, tuple, set, or string).
        elements: The elements to count occurrences of. If None, count all elements.
            Can be a single element, list, tuple, or set.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - result: Dictionary containing:
                - If elements provided: Dictionary mapping each element to its count,
                  plus "total_occurrences" (sum of all counts) and "elements_found"
                  (list of elements that were found in the iterable).
                - If elements not provided: Dictionary with "unique_elements" (count of
                  each unique element), "total_unique" (number of unique elements),
                  "total_elements" (total count), and for strings: "words" and "characters".
            - error: Error message if operation failed (None if successful).
    """
    try:
        if not isinstance(iterable, (list, tuple, set, str)):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Expected list, tuple, set, or string, got {type(iterable).__name__}",
            }
        
        # Handle string case when no elements provided
        if isinstance(iterable, str) and elements is None:
            words = iterable.split()
            word_counts = Counter(words)
            char_counts = Counter(iterable)
            
            return {
                SUCCESS_KEY: True,
                RESULT_KEY: {
                    "words": {
                        "unique_elements": dict(word_counts),
                        "total_unique": len(word_counts),
                        "total_elements": len(words),
                    },
                    "characters": {
                        "unique_elements": dict(char_counts),
                        "total_unique": len(char_counts),
                        "total_elements": len(iterable),
                    },
                },
                ERROR_KEY: None,
            }
        
        # Convert iterable to list for easier processing
        iterable_list = list(iterable)
        
        # If no elements provided, count all unique elements
        if elements is None:
            counter = Counter(iterable_list)
            return {
                SUCCESS_KEY: True,
                RESULT_KEY: {
                    "unique_elements": dict(counter),
                    "total_unique": len(counter),
                    "total_elements": len(iterable_list),
                },
                ERROR_KEY: None,
            }
        
        # Normalize elements to a list
        if isinstance(elements, (list, tuple, set)):
            elements_list = list(elements)
        else:
            elements_list = [elements]
        
        # Count occurrences of specified elements
        counter = Counter(iterable_list)
        element_counts = {}
        elements_found = []
        total_occurrences = 0
        
        for element in elements_list:
            count = counter.get(element, 0)
            element_counts[element] = count
            if count > 0:
                elements_found.append(element)
            total_occurrences += count
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: {
                "counts": element_counts,
                "total_occurrences": total_occurrences,
                "elements_found": elements_found,
            },
            ERROR_KEY: None,
        }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error counting occurrences: {str(e)}",
        }