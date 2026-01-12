"""
Create tables in SQLite database.
"""

from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .connection import DatabaseConnection


def create_table(
    table_name: str,
    columns: Dict[str, str],
    database: Optional["DatabaseConnection"] = None,
) -> Dict[str, Any]:
    """
    Create a table in the database.
    
    Args:
        table_name: Name of the table to create.
        columns: Dictionary mapping column names to SQLite column types.
            Example: {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"}
        database: DatabaseConnection instance. If None, must be bound via agent.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - table_name: Name of the table.
            - error: Error message if operation failed (None if successful).
    """
    if database is None:
        return {
            "success": False,
            "table_name": table_name,
            "error": "Database connection is required. Pass database parameter or use with DatabaseAgent.",
        }
    
    try:
        # Validate table name (basic SQL injection prevention)
        if not table_name.replace("_", "").replace(" ", "").isalnum():
            return {
                "success": False,
                "table_name": table_name,
                "error": "Invalid table name. Table names should contain only alphanumeric characters, underscores, and spaces.",
            }
        
        # Build CREATE TABLE statement
        column_defs = [f"{name} {type_def}" for name, type_def in columns.items()]
        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)})"
        
        cursor = database.connection.cursor()
        cursor.execute(create_sql)
        database.commit()
        
        return {
            "success": True,
            "table_name": table_name,
            "error": None,
        }
    except Exception as e:
        database.rollback()
        return {
            "success": False,
            "table_name": table_name,
            "error": f"Error creating table: {str(e)}",
        }

