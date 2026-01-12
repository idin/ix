"""
Pathfinding operations for GraphMemory.
"""

import json
from typing import Optional, List, Set
from collections import deque
import sqlite3

from .queries import get_neighbors


def find_path(
    connection: sqlite3.Connection,
    start_node_id: str,
    end_node_id: str,
    max_depth: int = 10,
    relationship_type_whitelist: Optional[List[str]] = None,
    relationship_type_blacklist: Optional[List[str]] = None,
) -> Optional[List[str]]:
    """
    Find a path between two nodes using BFS.
    
    Args:
        connection: SQLite database connection (passed to get_neighbors).
        start_node_id: Starting node ID.
        end_node_id: Target node ID.
        max_depth: Maximum path length to search.
        relationship_type_whitelist: Only traverse edges with these relationship types.
        relationship_type_blacklist: Exclude edges with these relationship types.
    
    Returns:
        List of node IDs forming the path, or None if no path found.
    """
    if start_node_id == end_node_id:
        return [start_node_id]
    
    # Convert to sets for efficient lookup
    whitelist: Optional[Set[str]] = set(relationship_type_whitelist) if relationship_type_whitelist else None
    blacklist: Set[str] = set(relationship_type_blacklist) if relationship_type_blacklist else set()
    
    # BFS to find shortest path
    queue = deque([(start_node_id, [start_node_id])])
    visited = {start_node_id}
    
    while queue:
        current_node, path = queue.popleft()
        
        if len(path) > max_depth:
            continue
        
        # Get neighbors with relationship type filtering
        neighbors = _get_filtered_neighbors(
            connection, current_node, whitelist, blacklist
        )
        
        for neighbor in neighbors:
            neighbor_id = neighbor['node_id']
            
            if neighbor_id == end_node_id:
                return path + [neighbor_id]
            
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                queue.append((neighbor_id, path + [neighbor_id]))
    
    return None


def _get_filtered_neighbors(
    connection: sqlite3.Connection,
    node_id: str,
    whitelist: Optional[Set[str]],
    blacklist: Set[str],
) -> List[dict]:
    """
    Get neighbors filtered by relationship type whitelist/blacklist.
    
    Args:
        connection: SQLite database connection.
        node_id: The node to find neighbors for.
        whitelist: Only include these relationship types (None = all).
        blacklist: Exclude these relationship types.
    
    Returns:
        List of neighbor dictionaries.
    """
    if whitelist:
        # Query each whitelisted type and combine
        neighbors = []
        seen_ids: Set[str] = set()
        for rel_type in whitelist:
            if rel_type in blacklist:
                continue
            for neighbor in get_neighbors(
                connection=connection,
                node_id=node_id,
                relationship_type=rel_type,
                direction="outgoing",
            ):
                if neighbor['node_id'] not in seen_ids:
                    neighbors.append(neighbor)
                    seen_ids.add(neighbor['node_id'])
        return neighbors
    elif blacklist:
        # Get all neighbors and filter out blacklisted
        # Note: This requires querying edges directly to check relationship_type
        cursor = connection.cursor()
        placeholders = ','.join(['?'] * len(blacklist))
        cursor.execute(f"""
            SELECT DISTINCT n.node_id, n.node_type, n.properties, n.created_at, n.updated_at
            FROM nodes n
            JOIN edges e ON n.node_id = e.target_node_id
            WHERE e.source_node_id = ?
              AND e.relationship_type NOT IN ({placeholders})
        """, (node_id, *blacklist))
        
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
    else:
        # No filtering
        return get_neighbors(
            connection=connection,
            node_id=node_id,
            direction="outgoing",
        )

