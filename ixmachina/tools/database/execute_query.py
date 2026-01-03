"""
Execute SQL queries on SQLite database.
"""

from typing import Dict, Any, Optional, List, TYPE_CHECKING
import sqlite3

if TYPE_CHECKING:
    from .connection import DatabaseConnection


def execute_query(
    query: str,
    parameters: Optional[tuple] = None,
    database: Optional["DatabaseConnection"] = None,
) -> Dict[str, Any]:
    """
    Execute a SQL query on the database.
    
    Args:
        query: SQL query to execute (SELECT, INSERT, UPDATE, DELETE, etc.).
        parameters: Optional tuple of parameters for parameterized queries.
        database: DatabaseConnection instance. If None, must be bound via agent.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - query: The executed query.
            - results: List of result rows (for SELECT queries) or None.
            - rowcount: Number of rows affected (for INSERT/UPDATE/DELETE).
            - error: Error message if operation failed (None if successful).
    """
    if database is None:
        return {
            "success": False,
            "query": query,
            "results": None,
            "rowcount": 0,
            "error": "Database connection is required. Pass database parameter or use with DatabaseAgent.",
        }
    
    try:
        cursor = database.connection.cursor()
        
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)
        
        # Check if this is a SELECT query
        query_upper = query.strip().upper()
        is_select = query_upper.startswith("SELECT")
        
        if is_select:
            # Fetch all results
            rows = cursor.fetchall()
            # Convert Row objects to dictionaries
            results = [dict(row) for row in rows]
        else:
            # For INSERT/UPDATE/DELETE, commit and return rowcount
            database.commit()
            results = None
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "rowcount": cursor.rowcount,
            "error": None,
        }
    except sqlite3.Error as e:
        database.rollback()
        return {
            "success": False,
            "query": query,
            "results": None,
            "rowcount": 0,
            "error": f"Database error: {str(e)}",
        }
    except Exception as e:
        database.rollback()
        return {
            "success": False,
            "query": query,
            "results": None,
            "rowcount": 0,
            "error": f"Error executing query: {str(e)}",
        }

