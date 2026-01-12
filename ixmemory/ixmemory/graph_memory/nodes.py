"""
Node operations for GraphMemory.
"""

from typing import Any, Optional, Dict
import sqlite3
import json

from ixutils import utc_now_iso


def add_node(
    connection: sqlite3.Connection,
    node_id: str,
    node_type: str,
    properties: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Add a node to the graph.
    
    Args:
        connection: SQLite database connection.
        node_id: Unique identifier for the node.
        node_type: Type of the node (e.g., "Person", "Company").
        properties: Optional dictionary of node properties.
    """
    cursor = connection.cursor()
    now = utc_now_iso()
    properties_json = json.dumps(properties) if properties else None
    
    cursor.execute("""
        INSERT OR REPLACE INTO nodes 
        (node_id, node_type, properties, created_at, updated_at)
        VALUES (?, ?, ?, 
            COALESCE((SELECT created_at FROM nodes WHERE node_id = ?), ?),
            ?)
    """, (node_id, node_type, properties_json, node_id, now, now))
    
    connection.commit()


def get_node(
    connection: sqlite3.Connection,
    node_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Get a node by ID.
    
    Args:
        connection: SQLite database connection.
        node_id: ID of the node to retrieve.
    
    Returns:
        Dictionary with node data, or None if not found.
    """
    cursor = connection.cursor()
    cursor.execute("""
        SELECT node_id, node_type, properties, created_at, updated_at
        FROM nodes
        WHERE node_id = ?
    """, (node_id,))
    
    row = cursor.fetchone()
    if row is None:
        return None
    
    properties = json.loads(row['properties']) if row['properties'] else {}
    
    return {
        'node_id': row['node_id'],
        'node_type': row['node_type'],
        'properties': properties,
        'created_at': row['created_at'],
        'updated_at': row['updated_at'],
    }


def delete_node(
    connection: sqlite3.Connection,
    node_id: str,
) -> None:
    """
    Delete a node and all its edges.
    
    Args:
        connection: SQLite database connection.
        node_id: ID of the node to delete.
    """
    cursor = connection.cursor()
    cursor.execute("DELETE FROM nodes WHERE node_id = ?", (node_id,))
    # Edges are automatically deleted due to CASCADE
    connection.commit()
