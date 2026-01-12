"""
Edge operations for GraphMemory.
"""

from typing import Any, Optional, Dict
import sqlite3
import json
import uuid

from ixutils import utc_now_iso


def add_edge(
    connection: sqlite3.Connection,
    source_node_id: str,
    target_node_id: str,
    relationship_type: str,
    properties: Optional[Dict[str, Any]] = None,
    edge_id: Optional[str] = None,
) -> str:
    """
    Add an edge between two nodes.
    
    Args:
        connection: SQLite database connection.
        source_node_id: ID of the source node.
        target_node_id: ID of the target node.
        relationship_type: Type of relationship (e.g., "works_at", "knows").
        properties: Optional dictionary of edge properties.
        edge_id: Optional custom edge ID. If None, auto-generated.
    
    Returns:
        The edge ID (generated or provided).
    """
    if edge_id is None:
        edge_id = str(uuid.uuid4())
    
    cursor = connection.cursor()
    now = utc_now_iso()
    properties_json = json.dumps(properties) if properties else None
    
    cursor.execute("""
        INSERT OR REPLACE INTO edges 
        (edge_id, source_node_id, target_node_id, relationship_type, properties, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?,
            COALESCE((SELECT created_at FROM edges WHERE edge_id = ?), ?),
            ?)
    """, (edge_id, source_node_id, target_node_id, relationship_type, properties_json, edge_id, now, now))
    
    connection.commit()
    return edge_id


def delete_edge(
    connection: sqlite3.Connection,
    edge_id: str,
) -> None:
    """
    Delete an edge.
    
    Args:
        connection: SQLite database connection.
        edge_id: ID of the edge to delete.
    """
    cursor = connection.cursor()
    cursor.execute("DELETE FROM edges WHERE edge_id = ?", (edge_id,))
    connection.commit()

