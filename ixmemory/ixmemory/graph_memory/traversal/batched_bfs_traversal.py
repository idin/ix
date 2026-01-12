"""
Graph traversal using level-synchronous BFS with batched queries.

This approach queries all neighbors of the entire frontier at once per depth level,
rather than querying per-node. More efficient for graphs with many nodes per level.
"""

from typing import List, Dict, Any, Optional, Set, Tuple
import sqlite3
import json
import re

# SQLite default parameter limit
_SQLITE_MAX_VARIABLE_NUMBER = 999

# Pattern for valid SQL identifiers
_IDENTIFIER_PATTERN = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def _validate_identifier(name: str, description: str = "identifier") -> None:
    """
    Validate that a string is a safe SQL identifier.
    
    Args:
        name: The identifier to validate.
        description: Description for error messages.
    
    Raises:
        ValueError: If the identifier is invalid.
    """
    if not _IDENTIFIER_PATTERN.match(name):
        raise ValueError(
            f"Invalid {description}: '{name}'. "
            f"Must match pattern {_IDENTIFIER_PATTERN.pattern}"
        )


def _chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of at most chunk_size."""
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def traverse_batched_bfs(
    connection: sqlite3.Connection,
    start_node_id: str,
    max_depth: int = 1,
    relationship_type_whitelist: Optional[List[str]] = None,
    relationship_type_blacklist: Optional[List[str]] = None,
    direction: str = "outgoing",
    # Configurable table/column names
    nodes_table: str = "nodes",
    edges_table: str = "edges",
    node_id_column: str = "node_id",
    node_type_column: str = "node_type",
    properties_column: str = "properties",
    source_node_id_column: str = "source_node_id",
    target_node_id_column: str = "target_node_id",
    relationship_type_column: str = "relationship_type",
) -> List[Dict[str, Any]]:
    """
    Traverse the graph using level-synchronous BFS with batch queries per depth.
    
    Queries all neighbors of the entire frontier in one SQL query per depth level,
    using IN clauses. Handles SQLite parameter limits by chunking large frontiers.
    
    Args:
        connection: SQLite database connection.
        start_node_id: Starting node ID.
        max_depth: Maximum depth to traverse (0 = start node only, 1 = immediate neighbors).
        relationship_type_whitelist: Only traverse edges with these relationship types.
        relationship_type_blacklist: Exclude edges with these relationship types.
        direction: "outgoing", "incoming", or "both" (default: "outgoing").
        nodes_table: Name of the nodes table.
        edges_table: Name of the edges table.
        node_id_column: Column name for node ID in nodes table.
        node_type_column: Column name for node type in nodes table.
        properties_column: Column name for properties in nodes table.
        source_node_id_column: Column name for source node ID in edges table.
        target_node_id_column: Column name for target node ID in edges table.
        relationship_type_column: Column name for relationship type in edges table.
    
    Returns:
        List of node dictionaries found within max_depth, sorted by depth.
        Each node dict includes: node_id, node_type, properties, depth, path
        
    Behavioural guarantees:
        - max_depth < 0 returns []
        - max_depth = 0 returns only the start node with depth 0
        - Duplicate nodes are deduplicated using minimum depth
        - Returned paths correspond to the minimum-depth path
        - Results are sorted by depth ascending
    
    Required indexes for performance:
        - edges(source_node_id, relationship_type)
        - edges(target_node_id, relationship_type)
        - nodes(node_id) (PK)
    """
    if max_depth < 0:
        return []
    
    if direction not in ("outgoing", "incoming", "both"):
        raise ValueError(
            f"Invalid direction: {direction}. Must be 'outgoing', 'incoming', or 'both'."
        )
    
    # Validate all identifiers
    for name, desc in [
        (nodes_table, "table name"),
        (edges_table, "table name"),
        (node_id_column, "column name"),
        (node_type_column, "column name"),
        (properties_column, "column name"),
        (source_node_id_column, "column name"),
        (target_node_id_column, "column name"),
        (relationship_type_column, "column name"),
    ]:
        _validate_identifier(name, desc)
    
    cursor = connection.cursor()
    
    # Validate start node exists
    cursor.execute(
        f"SELECT {node_id_column} FROM {nodes_table} WHERE {node_id_column} = ?",
        (start_node_id,),
    )
    if cursor.fetchone() is None:
        return []
    
    # Track visited nodes with their depth and parent (for path reconstruction)
    visited_depth: Dict[str, int] = {start_node_id: 0}
    parent: Dict[str, Optional[str]] = {start_node_id: None}
    
    if max_depth == 0:
        return _fetch_node_details(
            cursor, visited_depth, parent, start_node_id,
            nodes_table, node_id_column, node_type_column, properties_column,
        )
    
    # Level-synchronous BFS
    frontier: Set[str] = {start_node_id}
    
    for current_depth in range(1, max_depth + 1):
        if not frontier:
            break
        
        # Query all neighbors of the frontier in batch (handles chunking internally)
        candidates = _get_batch_neighbors(
            cursor,
            frontier,
            direction,
            relationship_type_whitelist,
            relationship_type_blacklist,
            edges_table,
            source_node_id_column,
            target_node_id_column,
            relationship_type_column,
        )
        
        # Deduplicate candidates: keep first occurrence (for consistent parent assignment)
        seen_candidates: Dict[str, str] = {}  # neighbor_id -> from_id
        for neighbor_id, from_id in candidates:
            if neighbor_id not in seen_candidates:
                seen_candidates[neighbor_id] = from_id
        
        # Filter to only new nodes
        new_frontier: Set[str] = set()
        for neighbor_id, from_id in seen_candidates.items():
            if neighbor_id not in visited_depth:
                visited_depth[neighbor_id] = current_depth
                parent[neighbor_id] = from_id
                new_frontier.add(neighbor_id)
        
        frontier = new_frontier
    
    return _fetch_node_details(
        cursor, visited_depth, parent, start_node_id,
        nodes_table, node_id_column, node_type_column, properties_column,
    )


def _get_batch_neighbors(
    cursor: sqlite3.Cursor,
    frontier: Set[str],
    direction: str,
    relationship_type_whitelist: Optional[List[str]],
    relationship_type_blacklist: Optional[List[str]],
    edges_table: str,
    source_node_id_column: str,
    target_node_id_column: str,
    relationship_type_column: str,
) -> List[Tuple[str, str]]:
    """
    Query all neighbors of the frontier nodes in batch, with chunking.
    
    Args:
        cursor: Database cursor.
        frontier: Set of node IDs to get neighbors for.
        direction: "outgoing", "incoming", or "both".
        relationship_type_whitelist: Only include edges with these relationship types.
        relationship_type_blacklist: Exclude edges with these relationship types.
        edges_table: Name of edges table.
        source_node_id_column: Column name for source node ID.
        target_node_id_column: Column name for target node ID.
        relationship_type_column: Column name for relationship type.
    
    Returns:
        List of (neighbor_id, from_id) tuples.
    """
    if not frontier:
        return []
    
    frontier_list = list(frontier)
    
    # Calculate chunk size accounting for relationship type params
    whitelist_count = len(relationship_type_whitelist) if relationship_type_whitelist else 0
    blacklist_count = len(relationship_type_blacklist) if relationship_type_blacklist else 0
    rel_params_count = whitelist_count + blacklist_count
    chunk_size = _SQLITE_MAX_VARIABLE_NUMBER - rel_params_count
    if chunk_size < 1:
        chunk_size = 1
    
    chunks = _chunk_list(frontier_list, chunk_size)
    
    results: List[Tuple[str, str]] = []
    
    for chunk in chunks:
        chunk_results = _query_neighbors_chunk(
            cursor, chunk, direction,
            relationship_type_whitelist, relationship_type_blacklist,
            edges_table, source_node_id_column, target_node_id_column,
            relationship_type_column,
        )
        results.extend(chunk_results)
    
    return results


def _query_neighbors_chunk(
    cursor: sqlite3.Cursor,
    frontier_chunk: List[str],
    direction: str,
    relationship_type_whitelist: Optional[List[str]],
    relationship_type_blacklist: Optional[List[str]],
    edges_table: str,
    source_node_id_column: str,
    target_node_id_column: str,
    relationship_type_column: str,
) -> List[Tuple[str, str]]:
    """
    Query neighbors for a single chunk of frontier nodes.
    """
    placeholders = ", ".join("?" for _ in frontier_chunk)
    
    # Build relationship type filter
    rel_filter = ""
    rel_params: List[str] = []
    
    if relationship_type_whitelist:
        rel_placeholders = ", ".join("?" for _ in relationship_type_whitelist)
        rel_filter += f" AND {relationship_type_column} IN ({rel_placeholders})"
        rel_params.extend(relationship_type_whitelist)
    
    if relationship_type_blacklist:
        rel_placeholders = ", ".join("?" for _ in relationship_type_blacklist)
        rel_filter += f" AND {relationship_type_column} NOT IN ({rel_placeholders})"
        rel_params.extend(relationship_type_blacklist)
    
    results: List[Tuple[str, str]] = []
    
    # Outgoing: source -> target
    if direction in ("outgoing", "both"):
        query = (
            f"SELECT {target_node_id_column}, {source_node_id_column} "
            f"FROM {edges_table} "
            f"WHERE {source_node_id_column} IN ({placeholders}){rel_filter}"
        )
        cursor.execute(query, frontier_chunk + rel_params)
        results.extend(cursor.fetchall())
    
    # Incoming: target -> source (reversed to get "from" perspective)
    if direction in ("incoming", "both"):
        query = (
            f"SELECT {source_node_id_column}, {target_node_id_column} "
            f"FROM {edges_table} "
            f"WHERE {target_node_id_column} IN ({placeholders}){rel_filter}"
        )
        cursor.execute(query, frontier_chunk + rel_params)
        results.extend(cursor.fetchall())
    
    return results


def _fetch_node_details(
    cursor: sqlite3.Cursor,
    visited_depth: Dict[str, int],
    parent: Dict[str, Optional[str]],
    start_node_id: str,
    nodes_table: str,
    node_id_column: str,
    node_type_column: str,
    properties_column: str,
) -> List[Dict[str, Any]]:
    """
    Fetch node details for all visited nodes and reconstruct paths.
    
    Args:
        cursor: Database cursor.
        visited_depth: Map of node_id -> depth.
        parent: Map of node_id -> parent_node_id.
        start_node_id: Starting node ID (for path reconstruction).
        nodes_table: Name of nodes table.
        node_id_column: Column name for node ID.
        node_type_column: Column name for node type.
        properties_column: Column name for properties.
    
    Returns:
        List of node dictionaries sorted by depth.
    """
    if not visited_depth:
        return []
    
    node_ids = list(visited_depth.keys())
    
    # Fetch all node details in chunked queries
    chunks = _chunk_list(node_ids, _SQLITE_MAX_VARIABLE_NUMBER)
    
    node_data: Dict[str, Dict[str, Any]] = {}
    for chunk in chunks:
        placeholders = ", ".join("?" for _ in chunk)
        cursor.execute(
            f"SELECT {node_id_column}, {node_type_column}, {properties_column} "
            f"FROM {nodes_table} "
            f"WHERE {node_id_column} IN ({placeholders})",
            chunk,
        )
        
        for row in cursor.fetchall():
            node_id = row[0]
            node_type = row[1]
            properties_json = row[2]
            
            # Safe JSON parsing
            properties = {}
            if properties_json:
                try:
                    properties = json.loads(properties_json)
                except (json.JSONDecodeError, TypeError):
                    properties = {}
            
            node_data[node_id] = {
                "node_id": node_id,
                "node_type": node_type,
                "properties": properties,
            }
    
    # Build result with depth and path
    result: List[Dict[str, Any]] = []
    for node_id, depth in visited_depth.items():
        if node_id not in node_data:
            continue
        
        node = node_data[node_id].copy()
        node["depth"] = depth
        node["path"] = _reconstruct_path(node_id, parent, start_node_id)
        result.append(node)
    
    # Sort by depth
    result.sort(key=lambda x: x["depth"])
    
    return result


def _reconstruct_path(
    node_id: str,
    parent: Dict[str, Optional[str]],
    start_node_id: str,
) -> List[str]:
    """
    Reconstruct the path from start to the given node by following parent pointers.
    
    Args:
        node_id: Target node ID.
        parent: Map of node_id -> parent_node_id.
        start_node_id: Starting node ID.
    
    Returns:
        List of node IDs from start to target, or [node_id] if path is invalid.
    """
    path: List[str] = []
    current: Optional[str] = node_id
    
    # Safety limit to prevent infinite loops
    max_iterations = len(parent) + 1
    iterations = 0
    
    while current is not None and iterations < max_iterations:
        path.append(current)
        current = parent.get(current)
        iterations += 1
    
    path.reverse()
    
    # Verify path reaches start_node_id
    if not path or path[0] != start_node_id:
        # Invalid path - return just the node itself
        return [node_id]
    
    return path
