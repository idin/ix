"""
Set operations for working with sets and dictionaries.

Supports standard set operations (intersection, union, difference, etc.)
on sets and dictionaries (using dictionary keys as the set elements).
"""

from typing import Dict, Any, Union, Set, List, Tuple

from ..constants import SUCCESS_KEY, RESULT_KEY, ERROR_KEY


def _create_set(elements: Union[Set[Any], Dict[Any, Any], List[Any], Tuple[Any, ...], Any]) -> Union[Set[Any], Dict[Any, Any]]:
    """
    Create a set from a list of elements or one element.
    
    Args:
        elements: Elements to convert to a set. Can be a set, dict, list, tuple, or single element.
    
    Returns:
        Set or dict (if input was a dict, returns as-is).
    """
    if isinstance(elements, (set, dict)):
        return elements
    elif isinstance(elements, (list, tuple)):
        return set(elements)
    else:
        return set([elements])


def intersection(
    set1: Union[Set[Any], Dict[Any, Any], List[Any], Tuple[Any, ...], Any],
    set2: Union[Set[Any], Dict[Any, Any], List[Any], Tuple[Any, ...], Any],
) -> Dict[str, Any]:
    """
    Calculate the intersection of two sets.
    
    For dictionaries, uses keys as the set elements. When one operand is a dict
    and the other is a set, returns a dictionary with only the common keys.
    
    Args:
        set1: First set (can be set, dict, list, tuple, or single element).
        set2: Second set (can be set, dict, list, tuple, or single element).
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - result: Intersection result (set or dict with common keys).
            - error: Error message if operation failed (None if successful).
    """
    try:
        set1 = _create_set(set1)
        set2 = _create_set(set2)

        if isinstance(set1, set) and isinstance(set2, set):
            return {
                SUCCESS_KEY: True,
                RESULT_KEY: set1 & set2,
                ERROR_KEY: None,
            }
        elif isinstance(set1, dict) and isinstance(set2, set):
            common = set1.keys() & set2
            return {
                SUCCESS_KEY: True,
                RESULT_KEY: {key: set1[key] for key in common},
                ERROR_KEY: None,
            }
        elif isinstance(set1, set) and isinstance(set2, dict):
            common = set1 & set2.keys()
            return {
                SUCCESS_KEY: True,
                RESULT_KEY: {key: set2[key] for key in common},
                ERROR_KEY: None,
            }
        elif isinstance(set1, dict) and isinstance(set2, dict):
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: "Intersection of two dictionaries is not supported",
            }
        else:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Invalid set types: {type(set1)} and {type(set2)}",
            }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error calculating intersection: {str(e)}",
        }


def union(
    set1: Union[Set[Any], Dict[Any, Any], List[Any], Tuple[Any, ...], Any],
    set2: Union[Set[Any], Dict[Any, Any], List[Any], Tuple[Any, ...], Any],
) -> Dict[str, Any]:
    """
    Calculate the union of two sets.
    
    Args:
        set1: First set (can be set, dict, list, tuple, or single element).
        set2: Second set (can be set, dict, list, tuple, or single element).
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - result: Union result (set).
            - error: Error message if operation failed (None if successful).
    """
    try:
        set1 = _create_set(set1)
        set2 = _create_set(set2)

        if isinstance(set1, set) and isinstance(set2, set):
            return {
                SUCCESS_KEY: True,
                RESULT_KEY: set1 | set2,
                ERROR_KEY: None,
            }
        else:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Invalid set types: {type(set1)} and {type(set2)}. Union requires both operands to be sets.",
            }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error calculating union: {str(e)}",
        }


def difference(
    set1: Union[Set[Any], Dict[Any, Any], List[Any], Tuple[Any, ...], Any],
    set2: Union[Set[Any], Dict[Any, Any], List[Any], Tuple[Any, ...], Any],
) -> Dict[str, Any]:
    """
    Calculate the difference of two sets (set1 - set2).
    
    For dictionaries, uses keys as the set elements. When set1 is a dict and set2 is a set,
    returns a dictionary with only the keys not in set2.
    
    Args:
        set1: First set (can be set, dict, list, tuple, or single element).
        set2: Second set (can be set, dict, list, tuple, or single element).
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - result: Difference result (set or dict).
            - error: Error message if operation failed (None if successful).
    """
    try:
        set1 = _create_set(set1)
        set2 = _create_set(set2)

        if isinstance(set1, set) and isinstance(set2, set):
            return {
                SUCCESS_KEY: True,
                RESULT_KEY: set1 - set2,
                ERROR_KEY: None,
            }
        elif isinstance(set1, dict) and isinstance(set2, set):
            return {
                SUCCESS_KEY: True,
                RESULT_KEY: {key: set1[key] for key in set1.keys() if key not in set2},
                ERROR_KEY: None,
            }
        else:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Invalid set types: {type(set1)} and {type(set2)}. Difference requires set1 to be a set or dict, and set2 to be a set.",
            }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error calculating difference: {str(e)}",
        }


def symmetric_difference(
    set1: Union[Set[Any], Dict[Any, Any], List[Any], Tuple[Any, ...], Any],
    set2: Union[Set[Any], Dict[Any, Any], List[Any], Tuple[Any, ...], Any],
) -> Dict[str, Any]:
    """
    Calculate the symmetric difference of two sets (elements in either set, but not both).
    
    Args:
        set1: First set (can be set, dict, list, tuple, or single element).
        set2: Second set (can be set, dict, list, tuple, or single element).
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - result: Symmetric difference result (set).
            - error: Error message if operation failed (None if successful).
    """
    try:
        set1 = _create_set(set1)
        set2 = _create_set(set2)

        if isinstance(set1, set) and isinstance(set2, set):
            return {
                SUCCESS_KEY: True,
                RESULT_KEY: set1 ^ set2,
                ERROR_KEY: None,
            }
        else:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Invalid set types: {type(set1)} and {type(set2)}. Symmetric difference requires both operands to be sets.",
            }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error calculating symmetric difference: {str(e)}",
        }


def subset(
    set1: Union[Set[Any], Dict[Any, Any], List[Any], Tuple[Any, ...], Any],
    set2: Union[Set[Any], Dict[Any, Any], List[Any], Tuple[Any, ...], Any],
) -> Dict[str, Any]:
    """
    Check if set1 is a subset of set2 (all elements of set1 are in set2).
    
    For dictionaries, uses keys as the set elements.
    
    Args:
        set1: First set (can be set, dict, list, tuple, or single element).
        set2: Second set (can be set, dict, list, tuple, or single element).
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - result: Boolean indicating if set1 is a subset of set2.
            - error: Error message if operation failed (None if successful).
    """
    try:
        set1 = _create_set(set1)
        set2 = _create_set(set2)

        if isinstance(set1, set) and isinstance(set2, set):
            return {
                SUCCESS_KEY: True,
                RESULT_KEY: set1 <= set2,
                ERROR_KEY: None,
            }
        elif isinstance(set1, dict) or isinstance(set2, dict):
            set1_keys = set(set1.keys()) if isinstance(set1, dict) else set1
            set2_keys = set(set2.keys()) if isinstance(set2, dict) else set2
            return {
                SUCCESS_KEY: True,
                RESULT_KEY: set1_keys <= set2_keys,
                ERROR_KEY: None,
            }
        else:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Invalid set types: {type(set1)} and {type(set2)}",
            }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error checking subset: {str(e)}",
        }


def superset(
    set1: Union[Set[Any], Dict[Any, Any], List[Any], Tuple[Any, ...], Any],
    set2: Union[Set[Any], Dict[Any, Any], List[Any], Tuple[Any, ...], Any],
) -> Dict[str, Any]:
    """
    Check if set1 is a superset of set2 (all elements of set2 are in set1).
    
    For dictionaries, uses keys as the set elements.
    
    Args:
        set1: First set (can be set, dict, list, tuple, or single element).
        set2: Second set (can be set, dict, list, tuple, or single element).
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - result: Boolean indicating if set1 is a superset of set2.
            - error: Error message if operation failed (None if successful).
    """
    try:
        set1 = _create_set(set1)
        set2 = _create_set(set2)

        if isinstance(set1, set) and isinstance(set2, set):
            return {
                SUCCESS_KEY: True,
                RESULT_KEY: set1 >= set2,
                ERROR_KEY: None,
            }
        elif isinstance(set1, dict) or isinstance(set2, dict):
            set1_keys = set(set1.keys()) if isinstance(set1, dict) else set1
            set2_keys = set(set2.keys()) if isinstance(set2, dict) else set2
            return {
                SUCCESS_KEY: True,
                RESULT_KEY: set1_keys >= set2_keys,
                ERROR_KEY: None,
            }
        else:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Invalid set types: {type(set1)} and {type(set2)}",
            }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error checking superset: {str(e)}",
        }