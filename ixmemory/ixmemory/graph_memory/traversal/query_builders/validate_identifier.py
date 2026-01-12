"""
SQL identifier validation.
"""

import re


# Pattern for valid SQL identifiers (table names, column names)
_IDENTIFIER_PATTERN = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def validate_identifier(name: str, description: str = "identifier") -> None:
    """
    Validate that a string is a safe SQL identifier.
    
    Args:
        name: The identifier to validate.
        description: Description for error messages (e.g., "table name", "column name").
    
    Raises:
        ValueError: If the identifier is invalid.
    """
    if not _IDENTIFIER_PATTERN.match(name):
        raise ValueError(
            f"Invalid {description}: '{name}'. "
            f"Must match pattern {_IDENTIFIER_PATTERN.pattern}"
        )
