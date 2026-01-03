"""
Get schema information for a table.
"""

from typing import Dict, Any, Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .connection import DatabaseConnection


def get_table_schema(
    table_name: str,
    database: Optional["DatabaseConnection"] = None,
) -> Dict[str, Any]:
    """
    Get schema information for a table.
    
    Args:
        table_name: Name of the table.
        database: DatabaseConnection instance. If None, must be bound via agent.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - table_name: Name of the table.
            - columns: List of column information dictionaries with:
                - name: Column name
                - type: Column type
                - notnull: Whether column is NOT NULL
                - default_value: Default value (if any)
                - pk: Whether column is primary key
            - error: Error message if operation failed (None if successful).
    """
    if database is None:
        return {
            "success": False,
            "table_name": table_name,
            "columns": [],
            "error": "Database connection is required. Pass database parameter or use with DatabaseAgent.",
        }
    
    try:
        cursor = database.connection.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        rows = cursor.fetchall()
        
        if not rows:
            return {
                "success": False,
                "table_name": table_name,
                "columns": [],
                "error": f"Table '{table_name}' does not exist.",
            }
        
        columns = []
        for row in rows:
            columns.append({
                "name": row[1],  # cid, name, type, notnull, default_value, pk
                "type": row[2],
                "notnull": bool(row[3]),
                "default_value": row[4],
                "pk": bool(row[5]),
            })
        
        return {
            "success": True,
            "table_name": table_name,
            "columns": columns,
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "table_name": table_name,
            "columns": [],
            "error": f"Error getting table schema: {str(e)}",
        }

