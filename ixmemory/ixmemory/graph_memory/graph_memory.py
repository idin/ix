"""
Graph-based memory with SQLite backend for nodes and edges.
"""

from typing import Any, Optional, Dict, List
import sqlite3

from .nodes import add_node, get_node, delete_node
from .edges import add_edge, delete_edge
from .queries import get_neighbors, query_nodes
from .pathfinding import find_path
from .traversal import traverse, traverse_with_queries, traverse_batched_bfs


class GraphMemory:
    """
    Graph-based storage system for nodes and edges.
    
    Uses SQLite for persistent storage with support for:
    - Node storage with types and properties
    - Edge storage with relationships and properties
    - Path finding between nodes
    - Graph traversal and queries
    - Cross-referencing with SemanticMemory
    
    Args:
        connection: SQLite database connection (managed by parent Memory class).
    """
    
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
    
    def add_node(
        self,
        node_id: str,
        node_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add a node to the graph.
        
        Args:
            node_id: Unique identifier for the node.
            node_type: Type of the node (e.g., "Person", "Company").
            properties: Optional dictionary of node properties.
        """
        add_node(self.connection, node_id, node_type, properties)
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a node by ID.
        
        Args:
            node_id: ID of the node to retrieve.
        
        Returns:
            Dictionary with node data, or None if not found.
        """
        return get_node(self.connection, node_id)
    
    def add_edge(
        self,
        source_node_id: str,
        target_node_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None,
        edge_id: Optional[str] = None,
    ) -> str:
        """
        Add an edge between two nodes.
        
        Args:
            source_node_id: ID of the source node.
            target_node_id: ID of the target node.
            relationship_type: Type of relationship (e.g., "works_at", "knows").
            properties: Optional dictionary of edge properties.
            edge_id: Optional custom edge ID. If None, auto-generated.
        
        Returns:
            The edge ID (generated or provided).
        """
        return add_edge(
            self.connection,
            source_node_id,
            target_node_id,
            relationship_type,
            properties,
            edge_id,
        )
    
    def get_neighbors(
        self,
        node_id: str,
        relationship_type: Optional[str] = None,
        direction: str = "both",
    ) -> List[Dict[str, Any]]:
        """
        Get neighboring nodes.
        
        Args:
            node_id: ID of the node.
            relationship_type: Optional filter by relationship type.
            direction: "outgoing", "incoming", or "both" (default).
        
        Returns:
            List of neighbor node dictionaries.
        """
        return get_neighbors(self.connection, node_id, relationship_type, direction)
    
    def find_path(
        self,
        start_node_id: str,
        end_node_id: str,
        max_depth: int = 10,
        relationship_type_whitelist: Optional[List[str]] = None,
        relationship_type_blacklist: Optional[List[str]] = None,
    ) -> Optional[List[str]]:
        """
        Find a path between two nodes using BFS.
        
        Args:
            start_node_id: Starting node ID.
            end_node_id: Target node ID.
            max_depth: Maximum path length to search.
            relationship_type_whitelist: Only traverse edges with these relationship types.
            relationship_type_blacklist: Exclude edges with these relationship types.
        
        Returns:
            List of node IDs forming the path, or None if no path found.
        """
        return find_path(
            self.connection,
            start_node_id,
            end_node_id,
            max_depth,
            relationship_type_whitelist,
            relationship_type_blacklist,
        )
    
    def delete_node(self, node_id: str) -> None:
        """
        Delete a node and all its edges.
        
        Args:
            node_id: ID of the node to delete.
        """
        delete_node(self.connection, node_id)
    
    def delete_edge(self, edge_id: str) -> None:
        """
        Delete an edge.
        
        Args:
            edge_id: ID of the edge to delete.
        """
        delete_edge(self.connection, edge_id)
    
    def query_nodes(
        self,
        node_type: Optional[str] = None,
        properties_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query nodes by type and/or properties.
        
        Args:
            node_type: Optional node type to filter by.
            properties_filter: Optional dictionary of property key-value pairs to match.
        
        Returns:
            List of matching node dictionaries.
        """
        return query_nodes(self.connection, node_type, properties_filter)
    
    def traverse(
        self,
        start_node_id: str,
        max_depth: int = 1,
        relationship_type_whitelist: Optional[List[str]] = None,
        relationship_type_blacklist: Optional[List[str]] = None,
        direction: str = "outgoing",
        method: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Traverse the graph from a starting node, collecting all nodes within max_depth.
        
        Example: If a -> b -> c, calling traverse("a", max_depth=2) will return
        nodes a (depth 0), b (depth 1), and c (depth 2).
        
        Args:
            start_node_id: Starting node ID.
            max_depth: Maximum depth to traverse (1 = immediate neighbors only).
            relationship_type_whitelist: Only traverse edges with these relationship types.
            relationship_type_blacklist: Exclude edges with these relationship types.
            direction: "outgoing", "incoming", or "both" (default: "outgoing").
            method: Traversal method:
                   - "walk": Python BFS, one query per node (simple, includes path)
                   - "batched": Level-synchronous BFS, one query per depth (efficient, includes path)
                   - "query": SQL CTE-based (single query, no path)
                   If None, defaults to "batched".
        
        Returns:
            List of node dictionaries found within max_depth, including depth.
            Each node dict includes: node_id, node_type, properties, depth
            Note: "walk" and "batched" methods also include "path" key.
        """
        # Default to batched (best balance of efficiency and features)
        if method is None:
            method = "batched"
        
        if method == "walk":
            return traverse(
                connection=self.connection,
                start_node_id=start_node_id,
                max_depth=max_depth,
                relationship_type_whitelist=relationship_type_whitelist,
                relationship_type_blacklist=relationship_type_blacklist,
                direction=direction,
            )
        elif method == "batched":
            return traverse_batched_bfs(
                connection=self.connection,
                start_node_id=start_node_id,
                max_depth=max_depth,
                relationship_type_whitelist=relationship_type_whitelist,
                relationship_type_blacklist=relationship_type_blacklist,
                direction=direction,
            )
        elif method == "query":
            return traverse_with_queries(
                connection=self.connection,
                start_node_id=start_node_id,
                max_depth=max_depth,
                relationship_type_whitelist=relationship_type_whitelist,
                relationship_type_blacklist=relationship_type_blacklist,
                direction=direction,
            )
        else:
            raise ValueError(
                f"Invalid method: {method}. Must be 'walk', 'batched', 'query', or None."
            )
    
    def __repr__(self) -> str:
        return f"GraphMemory()"
