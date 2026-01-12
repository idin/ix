"""
List all tables in SQLite database.
"""

from typing import Dict, Any, Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .connection import DatabaseConnection


def list_tables(
    database: Optional["DatabaseConnection"] = None,
) -> Dict[str, Any]:
    """
    List all tables in the database.
    
    Args:
        database: DatabaseConnection instance. If None, must be bound via agent.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - tables: List of table names.
            - error: Error message if operation failed (None if successful).
    """
    if database is None:
        return {
            "success": False,
            "tables": [],
            "error": "Database connection is required. Pass database parameter or use with DatabaseAgent.",
        }
    
    try:
        cursor = database.connection.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        rows = cursor.fetchall()
        tables = [row[0] for row in rows]
        
        return {
            "success": True,
            "tables": tables,
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "tables": [],
            "error": f"Error listing tables: {str(e)}",
        }

