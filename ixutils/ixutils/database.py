"""
Database utilities for SQLite connections.
"""

import sqlite3
from typing import Optional, Callable


def create_database_connection(
    database_path: Optional[str] = None,
    initialize_tables: Optional[Callable[[sqlite3.Connection], None]] = None,
) -> sqlite3.Connection:
    """
    Create and configure a SQLite database connection.
    
    Args:
        database_path: Path to SQLite database file. If None, uses in-memory database.
        initialize_tables: Optional function to initialize tables. Called after connection is created.
    
    Returns:
        Configured SQLite connection with row_factory set to sqlite3.Row.
    """
    connection = sqlite3.connect(database_path or ':memory:')
    connection.row_factory = sqlite3.Row
    
    if initialize_tables is not None:
        initialize_tables(connection)
    
    return connection

