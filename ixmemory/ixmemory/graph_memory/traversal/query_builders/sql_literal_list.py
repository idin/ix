"""
SQL literal list conversion.
"""

from typing import List, Union

from .sql_literal import sql_literal


def sql_literal_list(values: List[Union[str, int]]) -> str:
    """Convert a list of values to a comma-separated SQL literal list."""
    return ", ".join(sql_literal(v) for v in values)
