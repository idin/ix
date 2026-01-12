"""
Graph traversal using BFS with iterative queries.

This approach walks the graph step by step, querying for edges at each depth level.
"""

from typing import List, Dict, Any, Optional, Set
import sqlite3
import json


def traverse(
    connection: sqlite3.Connection,
    start_node_id: str,
    max_depth: int = 1,
    relationship_type_whitelist: Optional[List[str]] = None,
    relationship_type_blacklist: Optional[List[str]] = None,
    direction: str = "outgoing",
) -> List[Dict[str, Any]]:
    """
    Traverse the graph from a starting node using BFS with iterative queries.
    
    At each depth level, queries for edges from the current frontier nodes,
    then advances to the next depth.
    
    Args:
        connection: SQLite database connection.
        start_node_id: Starting node ID.
        max_depth: Maximum depth to traverse (0 = start node only, 1 = immediate neighbors).
        relationship_type_whitelist: Only traverse edges with these relationship types.
        relationship_type_blacklist: Exclude edges with these relationship types.
        direction: "outgoing", "incoming", or "both" (default: "outgoing").
    
    Returns:
        List of node dictionaries found within max_depth, including depth information.
        Each node dict includes: node_id, node_type, properties, depth, path
        
    Behavioural guarantees:
        - max_depth < 0 returns []
        - max_depth = 0 returns only the start node with depth 0
        - Duplicate nodes are deduplicated using minimum depth
        - Returned paths correspond to the minimum-depth path
    """
    if max_depth < 0:
        return []
    
    if direction not in ("outgoing", "incoming", "both"):
        raise ValueError(
            f"Invalid direction: {direction}. Must be 'outgoing', 'incoming', or 'both'."
        )
    
    cursor = connection.cursor()
    
    # Get start node details
    start_node = _get_node(cursor, start_node_id)
    if start_node is None:
        return []
    
    # Track visited nodes with their minimum depth and path
    # node_id -> {node_id, node_type, properties, depth, path}
    visited: Dict[str, Dict[str, Any]] = {
        start_node_id: {
            'node_id': start_node_id,
            'node_type': start_node['node_type'],
            'properties': start_node['properties'],
            'depth': 0,
            'path': [start_node_id],
        }
    }
    
    if max_depth == 0:
        return list(visited.values())
    
    # BFS: frontier is the set of node IDs at the current depth
    frontier: Set[str] = {start_node_id}
    
    for current_depth in range(1, max_depth + 1):
        if not frontier:
            break
        
        # Get all edges from frontier nodes
        next_frontier: Set[str] = set()
        
        for node_id in frontier:
            # Get neighbors via edges
            neighbors = _get_neighbors(
                cursor=cursor,
                node_id=node_id,
                direction=direction,
                relationship_type_whitelist=relationship_type_whitelist,
                relationship_type_blacklist=relationship_type_blacklist,
            )
            
            for neighbor_id in neighbors:
                if neighbor_id not in visited:
                    # Get neighbor node details
                    neighbor_node = _get_node(cursor, neighbor_id)
                    if neighbor_node is None:
                        continue
                    
                    # Build path from parent
                    parent_path = visited[node_id]['path']
                    new_path = parent_path + [neighbor_id]
                    
                    visited[neighbor_id] = {
                        'node_id': neighbor_id,
                        'node_type': neighbor_node['node_type'],
                        'properties': neighbor_node['properties'],
                        'depth': current_depth,
                        'path': new_path,
                    }
                    next_frontier.add(neighbor_id)
        
        frontier = next_frontier
    
    # Sort by depth
    results = sorted(visited.values(), key=lambda x: x['depth'])
    return results


def _get_node(cursor: sqlite3.Cursor, node_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a single node by ID."""
    cursor.execute(
        "SELECT node_id, node_type, properties FROM nodes WHERE node_id = ?",
        (node_id,),
    )
    row = cursor.fetchone()
    if row is None:
        return None
    
    return {
        'node_id': row[0],
        'node_type': row[1],
        'properties': _parse_properties(row[2]),
    }


def _get_neighbors(
    cursor: sqlite3.Cursor,
    node_id: str,
    direction: str,
    relationship_type_whitelist: Optional[List[str]] = None,
    relationship_type_blacklist: Optional[List[str]] = None,
) -> List[str]:
    """
    Get neighbor node IDs connected to the given node.
    
    Args:
        cursor: Database cursor.
        node_id: The node to find neighbors for.
        direction: "outgoing", "incoming", or "both".
        relationship_type_whitelist: Only include edges with these relationship types.
        relationship_type_blacklist: Exclude edges with these relationship types.
    
    Returns:
        List of neighbor node IDs.
    """
    neighbors: List[str] = []
    
    # Build relationship type filter
    rel_filter = ""
    params: List[Any] = [node_id]
    
    if relationship_type_whitelist:
        placeholders = ','.join(['?'] * len(relationship_type_whitelist))
        rel_filter += f" AND relationship_type IN ({placeholders})"
        params.extend(relationship_type_whitelist)
    
    if relationship_type_blacklist:
        placeholders = ','.join(['?'] * len(relationship_type_blacklist))
        rel_filter += f" AND relationship_type NOT IN ({placeholders})"
        params.extend(relationship_type_blacklist)
    
    if direction in ("outgoing", "both"):
        query = f"SELECT target_node_id FROM edges WHERE source_node_id = ?{rel_filter}"
        cursor.execute(query, params)
        neighbors.extend(row[0] for row in cursor.fetchall())
    
    if direction in ("incoming", "both"):
        query = f"SELECT source_node_id FROM edges WHERE target_node_id = ?{rel_filter}"
        cursor.execute(query, params)
        neighbors.extend(row[0] for row in cursor.fetchall())
    
    return neighbors


def _parse_properties(properties_json: Optional[str]) -> Dict[str, Any]:
    """Parse JSON properties string, returning empty dict on failure."""
    if not properties_json:
        return {}
    try:
        return json.loads(properties_json)
    except (json.JSONDecodeError, TypeError):
        return {}
