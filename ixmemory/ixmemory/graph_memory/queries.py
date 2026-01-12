"""
Graph query operations for GraphMemory.
"""

from typing import Any, Optional, Dict, List
import sqlite3
import json


def get_neighbors(
    connection: sqlite3.Connection,
    node_id: str,
    relationship_type: Optional[str] = None,
    direction: str = "both",
) -> List[Dict[str, Any]]:
    """
    Get neighboring nodes.
    
    Args:
        connection: SQLite database connection.
        node_id: ID of the node.
        relationship_type: Optional filter by relationship type.
        direction: "outgoing", "incoming", or "both" (default).
    
    Returns:
        List of neighbor node dictionaries.
    """
    cursor = connection.cursor()
    
    if direction == "outgoing":
        if relationship_type:
            cursor.execute("""
                SELECT DISTINCT n.node_id, n.node_type, n.properties, n.created_at, n.updated_at
                FROM nodes n
                JOIN edges e ON n.node_id = e.target_node_id
                WHERE e.source_node_id = ? AND e.relationship_type = ?
            """, (node_id, relationship_type))
        else:
            cursor.execute("""
                SELECT DISTINCT n.node_id, n.node_type, n.properties, n.created_at, n.updated_at
                FROM nodes n
                JOIN edges e ON n.node_id = e.target_node_id
                WHERE e.source_node_id = ?
            """, (node_id,))
    elif direction == "incoming":
        if relationship_type:
            cursor.execute("""
                SELECT DISTINCT n.node_id, n.node_type, n.properties, n.created_at, n.updated_at
                FROM nodes n
                JOIN edges e ON n.node_id = e.source_node_id
                WHERE e.target_node_id = ? AND e.relationship_type = ?
            """, (node_id, relationship_type))
        else:
            cursor.execute("""
                SELECT DISTINCT n.node_id, n.node_type, n.properties, n.created_at, n.updated_at
                FROM nodes n
                JOIN edges e ON n.node_id = e.source_node_id
                WHERE e.target_node_id = ?
            """, (node_id,))
    else:  # both
        if relationship_type:
            cursor.execute("""
                SELECT DISTINCT n.node_id, n.node_type, n.properties, n.created_at, n.updated_at
                FROM nodes n
                JOIN edges e ON (
                    (n.node_id = e.target_node_id AND e.source_node_id = ?) OR
                    (n.node_id = e.source_node_id AND e.target_node_id = ?)
                )
                WHERE e.relationship_type = ?
            """, (node_id, node_id, relationship_type))
        else:
            cursor.execute("""
                SELECT DISTINCT n.node_id, n.node_type, n.properties, n.created_at, n.updated_at
                FROM nodes n
                JOIN edges e ON (
                    (n.node_id = e.target_node_id AND e.source_node_id = ?) OR
                    (n.node_id = e.source_node_id AND e.target_node_id = ?)
                )
            """, (node_id, node_id))
    
    neighbors = []
    for row in cursor.fetchall():
        properties = json.loads(row['properties']) if row['properties'] else {}
        neighbors.append({
            'node_id': row['node_id'],
            'node_type': row['node_type'],
            'properties': properties,
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
        })
    
    return neighbors


def query_nodes(
    connection: sqlite3.Connection,
    node_type: Optional[str] = None,
    properties_filter: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Query nodes by type and/or properties.
    
    Args:
        connection: SQLite database connection.
        node_type: Optional node type to filter by.
        properties_filter: Optional dictionary of property key-value pairs to match.
    
    Returns:
        List of matching node dictionaries.
    """
    cursor = connection.cursor()
    
    if node_type and properties_filter:
        # Filter by both type and properties
        query = "SELECT node_id, node_type, properties, created_at, updated_at FROM nodes WHERE node_type = ?"
        params = [node_type]
        
        nodes = []
        for row in cursor.execute(query, params):
            node_properties = json.loads(row['properties']) if row['properties'] else {}
            
            # Check if all filter properties match
            if all(node_properties.get(k) == v for k, v in properties_filter.items()):
                nodes.append({
                    'node_id': row['node_id'],
                    'node_type': row['node_type'],
                    'properties': node_properties,
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                })
        
        return nodes
    elif node_type:
        cursor.execute("""
            SELECT node_id, node_type, properties, created_at, updated_at
            FROM nodes
            WHERE node_type = ?
        """, (node_type,))
    elif properties_filter:
        # Filter by properties only (requires scanning all nodes)
        cursor.execute("""
            SELECT node_id, node_type, properties, created_at, updated_at
            FROM nodes
        """)
    else:
        # No filters - return all nodes
        cursor.execute("""
            SELECT node_id, node_type, properties, created_at, updated_at
            FROM nodes
        """)
    
    nodes = []
    for row in cursor.fetchall():
        node_properties = json.loads(row['properties']) if row['properties'] else {}
        
        # If properties_filter provided, check if all match
        if properties_filter:
            if not all(node_properties.get(k) == v for k, v in properties_filter.items()):
                continue
        
        nodes.append({
            'node_id': row['node_id'],
            'node_type': row['node_type'],
            'properties': node_properties,
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
        })
    
    return nodes
