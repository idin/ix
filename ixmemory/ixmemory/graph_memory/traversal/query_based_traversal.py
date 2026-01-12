"""
Graph traversal operations using CTE-based query builders.
"""

from typing import List, Dict, Any, Optional
import sqlite3
import json

from .query_builders import get_full_traversal_query


def traverse_with_queries(
    connection: sqlite3.Connection,
    start_node_id: str,
    max_depth: int = 1,
    relationship_type_whitelist: Optional[List[str]] = None,
    relationship_type_blacklist: Optional[List[str]] = None,
    direction: str = "outgoing",
) -> List[Dict[str, Any]]:
    """
    Traverse the graph from a starting node using CTE-based query builders.
    
    Args:
        connection: SQLite database connection.
        start_node_id: Starting node ID.
        max_depth: Maximum depth to traverse (0 = start node only, 1 = immediate neighbors).
        relationship_type_whitelist: Only traverse edges with these relationship types.
        relationship_type_blacklist: Exclude edges with these relationship types.
        direction: "outgoing", "incoming", or "both" (default: "outgoing").
    
    Returns:
        List of node dictionaries found within max_depth, including depth information.
        Each node dict includes: node_id, node_type, properties, depth
        
    Behavioural guarantees:
        - max_depth < 0 returns []
        - max_depth = 0 returns only the start node with depth 0
        - Duplicate nodes are deduplicated using minimum depth
    """
    if max_depth < 0:
        return []
    
    if direction not in ("outgoing", "incoming", "both"):
        raise ValueError(
            f"Invalid direction: {direction}. Must be 'outgoing', 'incoming', or 'both'."
        )
    
    cursor = connection.cursor()
    
    # Validate starting_node_ids exist in nodes
    requested_ids = {start_node_id}
    cursor.execute(
        "SELECT node_id FROM nodes WHERE node_id IN (?)",
        (start_node_id,),
    )
    found_ids = {row[0] for row in cursor.fetchall()}
    missing_ids = requested_ids - found_ids
    if missing_ids:
        raise ValueError(f"Unknown starting_node_ids: {sorted(missing_ids)}")
    
    # Build and execute traversal query using query builders
    # This handles all depths including 0
    query = get_full_traversal_query(
        max_depth=max_depth,
        direction=direction,
        starting_node_ids=[start_node_id],
        relationship_type_whitelist=relationship_type_whitelist,
        relationship_type_blacklist=relationship_type_blacklist,
    )
    
    cursor.execute(query)
    
    # Collect node_id -> min_depth from query results
    # Query now includes starting nodes at depth 0
    node_depths: Dict[str, int] = {}
    for row in cursor.fetchall():
        node_id = row[0]
        min_depth = row[1]
        node_depths[node_id] = min_depth
    
    # Fetch node details for all found nodes
    if not node_depths:
        return []
    
    placeholders = ','.join(['?'] * len(node_depths))
    cursor.execute(
        f"SELECT node_id, node_type, properties FROM nodes WHERE node_id IN ({placeholders})",
        list(node_depths.keys()),
    )
    
    # Build result list with node details and depths
    results: List[Dict[str, Any]] = []
    for row in cursor.fetchall():
        node_id = row[0]
        node_type = row[1]
        properties = _parse_properties(row[2])
        
        results.append({
            'node_id': node_id,
            'node_type': node_type,
            'properties': properties,
            'depth': node_depths[node_id],
        })
    
    # Sort by depth
    results.sort(key=lambda x: x['depth'])
    return results


def _parse_properties(properties_json: Optional[str]) -> Dict[str, Any]:
    """Parse JSON properties string, returning empty dict on failure."""
    if not properties_json:
        return {}
    try:
        return json.loads(properties_json)
    except (json.JSONDecodeError, TypeError):
        return {}
