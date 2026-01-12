"""
Query builder for complete traversal with all CTEs.
"""

from typing import Optional, List, Literal, Union

from .validate_identifier import validate_identifier
from .sql_literal_list import sql_literal_list
from .get_nodes_and_edges_query import get_nodes_and_edges_query
from .get_edges_query import get_edges_query
from .get_traversal_query import get_traversal_query


def get_full_traversal_query(
    max_depth: int,
    # Table/column parameters for get_nodes_and_edges_query
    nodes_table: str = "nodes",
    edges_table: str = "edges",
    node_id_column: str = "node_id",
    source_node_id_column: str = "source_node_id",
    target_node_id_column: str = "target_node_id",
    source_node_type_column: str = "node_type",
    target_node_type_column: str = "node_type",
    relationship_type_column: str = "relationship_type",
    node_type_whitelist: Optional[List[str]] = None,
    node_type_blacklist: Optional[List[str]] = None,
    relationship_type_whitelist: Optional[List[str]] = None,
    relationship_type_blacklist: Optional[List[str]] = None,
    # Direction and filter parameters for get_edges_query
    direction: Literal["outgoing", "incoming", "both"] = "outgoing",
    starting_node_ids: Optional[Union[List[Union[str, int]], str, int]] = None,
    excluded_start_node_ids: Optional[Union[List[Union[str, int]], str, int]] = None,
    # CTE names and columns (overridable)
    start_nodes_cte_name: str = "start_nodes",
    start_node_id_column: str = "node_id",
    output_node_id_column: str = "node_id",
    left_node_id_column: str = "left_node_id",
    right_node_id_column: str = "right_node_id",
    nodes_and_edges_cte_name: str = "nodes_and_edges",
    single_traversal_cte_name: str = "single_traversal",
) -> str:
    """
    Build a complete traversal query that composes all helpers into one SQL string.
    
    The query structure is:
        WITH start_nodes AS (...),
             nodes_and_edges AS (...),
             single_traversal AS (...)
        SELECT node_id, min_depth FROM (... UNION ALL ...) GROUP BY node_id
    
    Args:
        max_depth: Maximum depth to traverse (0 = start nodes only, 1 = one hop, etc.).
        nodes_table: Name of the nodes table.
        edges_table: Name of the edges table.
        node_id_column: Column name for node ID in the nodes table.
        source_node_id_column: Column name for source node ID in edges table.
        target_node_id_column: Column name for target node ID in edges table.
        source_node_type_column: Column name for node type in nodes table (for source).
        target_node_type_column: Column name for node type in nodes table (for target).
        relationship_type_column: Column name for relationship type in edges table.
        node_type_whitelist: Only include edges where both nodes have these types.
        node_type_blacklist: Exclude edges where either node has these types.
        relationship_type_whitelist: Only include edges with these relationship types.
        relationship_type_blacklist: Exclude edges with these relationship types.
        direction: Edge direction - "outgoing", "incoming", or "both".
        starting_node_ids: Node IDs where traversal begins.
        excluded_start_node_ids: Node IDs to exclude from traversal origins.
        start_nodes_cte_name: Name for the CTE containing validated starting nodes.
        start_node_id_column: Column name for node ID in the start_nodes CTE.
        output_node_id_column: Column name for node ID in the output.
        left_node_id_column: Column name for left/source node in edges CTE.
        right_node_id_column: Column name for right/target node in edges CTE.
        nodes_and_edges_cte_name: Name for the CTE (nodes + edges join).
        single_traversal_cte_name: Name for the CTE (single hop edges).
    
    Returns:
        Complete SQL query string.
    """
    # Normalize starting_node_ids to a list
    if starting_node_ids is None:
        start_ids: List[Union[str, int]] = []
    elif isinstance(starting_node_ids, (str, int)):
        start_ids = [starting_node_ids]
    else:
        start_ids = list(starting_node_ids)
    
    # Normalize excluded_start_node_ids to a list
    if excluded_start_node_ids is None:
        excluded_ids: List[Union[str, int]] = []
    elif isinstance(excluded_start_node_ids, (str, int)):
        excluded_ids = [excluded_start_node_ids]
    else:
        excluded_ids = list(excluded_start_node_ids)
    
    # Validate all identifiers
    for name, desc in [
        (nodes_table, "table name"),
        (edges_table, "table name"),
        (node_id_column, "column name"),
        (source_node_id_column, "column name"),
        (target_node_id_column, "column name"),
        (source_node_type_column, "column name"),
        (target_node_type_column, "column name"),
        (relationship_type_column, "column name"),
        (start_nodes_cte_name, "CTE name"),
        (start_node_id_column, "column name"),
        (output_node_id_column, "column name"),
        (left_node_id_column, "column name"),
        (right_node_id_column, "column name"),
        (nodes_and_edges_cte_name, "CTE name"),
        (single_traversal_cte_name, "CTE name"),
    ]:
        validate_identifier(name, desc)
    
    # Build start_nodes CTE: validates starting_node_ids against nodes
    # Alias to start_node_id_column so get_traversal_query can reference it
    if start_ids:
        where_clauses = [f"{node_id_column} IN ({sql_literal_list(start_ids)})"]
        if excluded_ids:
            where_clauses.append(f"{node_id_column} NOT IN ({sql_literal_list(excluded_ids)})")
        
        start_nodes_query = (
            f"SELECT {node_id_column} AS {start_node_id_column}\n"
            f"FROM {nodes_table}\n"
            f"WHERE " + " AND ".join(where_clauses)
        )
    else:
        # Empty starting nodes - return empty result
        start_nodes_query = (
            f"SELECT {node_id_column} AS {start_node_id_column}\n"
            f"FROM {nodes_table}\n"
            f"WHERE 1=0"
        )
    
    # Build the base nodes+edges query
    nodes_and_edges_query = get_nodes_and_edges_query(
        nodes_table=nodes_table,
        edges_table=edges_table,
        node_id_column=node_id_column,
        source_node_id_column=source_node_id_column,
        target_node_id_column=target_node_id_column,
        source_node_type_column=source_node_type_column,
        target_node_type_column=target_node_type_column,
        relationship_type_column=relationship_type_column,
        node_type_whitelist=node_type_whitelist,
        node_type_blacklist=node_type_blacklist,
        relationship_type_whitelist=relationship_type_whitelist,
        relationship_type_blacklist=relationship_type_blacklist,
    )
    
    # Build the single-hop edges query (references nodes_and_edges CTE)
    # Do NOT filter by starting_node_ids here - multi-hop traversal needs all edges
    # Starting node filtering happens via start_nodes CTE join in get_traversal_query
    edges_query = get_edges_query(
        direction=direction,
        source_node_id_column=source_node_id_column,
        target_node_id_column=target_node_id_column,
        left_node_id_column=left_node_id_column,
        right_node_id_column=right_node_id_column,
        depth_column="depth",
        left_node_id_whitelist=None,
        left_node_id_blacklist=None,
        common_table_expression_name=nodes_and_edges_cte_name,
    )
    
    # Build the traversal query (references start_nodes and single_traversal CTEs)
    traversal_query = get_traversal_query(
        max_depth=max_depth,
        left_node_id_column=left_node_id_column,
        right_node_id_column=right_node_id_column,
        depth_column="depth",
        edges_cte_name=single_traversal_cte_name,
        start_nodes_cte_name=start_nodes_cte_name,
        start_node_id_column=start_node_id_column,
        output_node_id_column=output_node_id_column,
    )
    
    # Indent the sub-queries for readability
    start_nodes_indented = "\n    ".join(start_nodes_query.split("\n"))
    nodes_and_edges_indented = "\n    ".join(nodes_and_edges_query.split("\n"))
    edges_indented = "\n    ".join(edges_query.split("\n"))
    
    # Compose into final query with WITH clause
    return (
        f"WITH {start_nodes_cte_name} AS (\n"
        f"    {start_nodes_indented}\n"
        f"),\n"
        f"{nodes_and_edges_cte_name} AS (\n"
        f"    {nodes_and_edges_indented}\n"
        f"),\n"
        f"{single_traversal_cte_name} AS (\n"
        f"    {edges_indented}\n"
        f")\n"
        f"{traversal_query}"
    )
