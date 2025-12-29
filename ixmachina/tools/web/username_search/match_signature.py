"""
Match a signature against existing and non-existing signatures.

Determines if a username exists by comparing its signature against
known existing and non-existing signatures using distinguishing factors.
"""

from typing import Dict, Any, List


def match_signature(
    signature: Dict[str, Any],
    existing_signature: Dict[str, Any],
    non_existing_signature: Dict[str, Any],
    distinguishing_factors: List[str],
) -> Dict[str, Any]:
    """
    Determine if a signature matches existing or non-existing signature.
    
    Compares the signature against existing and non-existing signatures
    using only the distinguishing factors to determine if the username exists.
    
    Args:
        signature: The signature to check (with status_code, error_type, content_keywords).
        existing_signature: The signature for existing usernames.
        non_existing_signature: The signature for non-existing usernames.
        distinguishing_factors: List of factors that distinguish existing from non-existing
                                (e.g., ["status_code", "content_keywords"]).
    
    Returns:
        Dictionary with:
            - exists: Boolean indicating if username exists (True/False/None)
            - error: Error message if undetermined (None if determined)
    """
    # Check each distinguishing factor
    matches_existing = True
    matches_non_existing = True
    
    for factor in distinguishing_factors:
        if factor == "status_code":
            if signature["status_code"] != existing_signature["status_code"]:
                matches_existing = False
            if signature["status_code"] != non_existing_signature["status_code"]:
                matches_non_existing = False
        elif factor == "error_type":
            if signature["error_type"] != existing_signature["error_type"]:
                matches_existing = False
            if signature["error_type"] != non_existing_signature["error_type"]:
                matches_non_existing = False
        elif factor == "content_keywords":
            if signature["content_keywords"] != existing_signature["content_keywords"]:
                matches_existing = False
            if signature["content_keywords"] != non_existing_signature["content_keywords"]:
                matches_non_existing = False
    
    # Determine existence based on matches
    if matches_existing and not matches_non_existing:
        return {
            "exists": True,
            "error": None,
        }
    elif matches_non_existing and not matches_existing:
        return {
            "exists": False,
            "error": None,
        }
    else:
        # Ambiguous - matches both or neither
        return {
            "exists": None,
            "error": (
                "Could not determine if username exists. "
                "Response matches both existing and non-existing signatures, or neither."
            ),
        }

