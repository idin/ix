"""
SQL literal conversion.
"""

from typing import Union

from .escape_sql_string import escape_sql_string


def sql_literal(value: Union[str, int]) -> str:
    """Convert a value to a SQL literal, quoting strings and leaving integers as-is."""
    if value is None:
        raise ValueError("Cannot convert None to SQL literal")
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return f"'{escape_sql_string(value)}'"
    raise TypeError(f"Expected str or int, got {type(value).__name__}")
