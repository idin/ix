"""
Query builder for nodes and edges.
"""

from typing import Optional, List

from .validate_identifier import validate_identifier
from .sql_literal_list import sql_literal_list


def get_nodes_and_edges_query(
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
) -> str:
    """
    Return a query that produces a table with columns:
        source_node_id, source_node_type, target_node_id, target_node_type, relationship_type
    
    Args:
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
    
    Returns:
        SQL query string.
    """
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
    ]:
        validate_identifier(name, desc)
    
    where_clauses = []
    
    if node_type_whitelist:
        where_clauses.append(f"n1.{source_node_type_column} IN ({sql_literal_list(node_type_whitelist)})")
        where_clauses.append(f"n2.{target_node_type_column} IN ({sql_literal_list(node_type_whitelist)})")
    
    if node_type_blacklist:
        where_clauses.append(f"n1.{source_node_type_column} NOT IN ({sql_literal_list(node_type_blacklist)})")
        where_clauses.append(f"n2.{target_node_type_column} NOT IN ({sql_literal_list(node_type_blacklist)})")
    
    if relationship_type_whitelist:
        where_clauses.append(f"e.{relationship_type_column} IN ({sql_literal_list(relationship_type_whitelist)})")
    
    if relationship_type_blacklist:
        where_clauses.append(f"e.{relationship_type_column} NOT IN ({sql_literal_list(relationship_type_blacklist)})")
    
    where_sql = ""
    if where_clauses:
        where_sql = "\nWHERE " + "\n  AND ".join(where_clauses)
    
    return (
        f"SELECT\n"
        f"    e.{source_node_id_column} AS source_node_id,\n"
        f"    n1.{source_node_type_column} AS source_node_type,\n"
        f"    e.{target_node_id_column} AS target_node_id,\n"
        f"    n2.{target_node_type_column} AS target_node_type,\n"
        f"    e.{relationship_type_column} AS relationship_type\n"
        f"FROM {edges_table} e\n"
        f"JOIN {nodes_table} n1 ON e.{source_node_id_column} = n1.{node_id_column}\n"
        f"JOIN {nodes_table} n2 ON e.{target_node_id_column} = n2.{node_id_column}"
        f"{where_sql}"
    )
