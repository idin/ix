"""
SQL string escaping.
"""


def escape_sql_string(value: str) -> str:
    """Escape single quotes in SQL string values by doubling them."""
    return value.replace("'", "''")
