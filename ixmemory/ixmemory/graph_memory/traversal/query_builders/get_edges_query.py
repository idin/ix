"""
Query builder for edges with direction.
"""

from typing import Optional, List, Literal, Union

from .validate_identifier import validate_identifier
from .sql_literal_list import sql_literal_list


def get_edges_query(
    direction: Literal["outgoing", "incoming", "both"] = "outgoing",
    source_node_id_column: str = "source_node_id",
    target_node_id_column: str = "target_node_id",
    left_node_id_column: str = "left_node_id",
    right_node_id_column: str = "right_node_id",
    depth_column: str = "depth",
    left_node_id_whitelist: Optional[Union[List[Union[str, int]], str, int]] = None,
    left_node_id_blacklist: Optional[Union[List[Union[str, int]], str, int]] = None,
    common_table_expression_name: str = "edges",
) -> str:
    """
    Build a query that selects edges from a CTE, producing: left_node_id, right_node_id, depth.
    
    Note: This query references the CTE named by common_table_expression_name but does not
    define it. The caller must wrap this in a WITH clause or ensure the CTE exists.
    
    Args:
        direction: Edge direction - "outgoing", "incoming", or "both".
        source_node_id_column: Column name for source node ID in the CTE.
        target_node_id_column: Column name for target node ID in the CTE.
        left_node_id_column: Output column name for the starting node.
        right_node_id_column: Output column name for the ending node.
        depth_column: Output column name for the depth value.
        common_table_expression_name: Name of the CTE to select from.
        left_node_id_whitelist: Only include edges starting from these node IDs.
        left_node_id_blacklist: Exclude edges starting from these node IDs.
    
    Returns:
        SQL query string (without WITH clause).
    """
    if isinstance(left_node_id_whitelist, (str, int)):
        left_node_id_whitelist = [left_node_id_whitelist]
    if isinstance(left_node_id_blacklist, (str, int)):
        left_node_id_blacklist = [left_node_id_blacklist]

    # Validate all identifiers
    for name, desc in [
        (source_node_id_column, "column name"),
        (target_node_id_column, "column name"),
        (left_node_id_column, "column name"),
        (right_node_id_column, "column name"),
        (depth_column, "column name"),
        (common_table_expression_name, "CTE name"),
    ]:
        validate_identifier(name, desc)

    cte = common_table_expression_name

    if direction in {"outgoing", "both"}:
        outgoing_query = (
            f"SELECT\n"
            f"        {source_node_id_column} AS {left_node_id_column},\n"
            f"        {target_node_id_column} AS {right_node_id_column},\n"
            f"        1 AS {depth_column}\n"
            f"    FROM {cte}"
        )

        where_clauses = []
        if left_node_id_whitelist:
            where_clauses.append(f"{source_node_id_column} IN ({sql_literal_list(left_node_id_whitelist)})")
        if left_node_id_blacklist:
            where_clauses.append(f"{source_node_id_column} NOT IN ({sql_literal_list(left_node_id_blacklist)})")
        if where_clauses:
            outgoing_query += f"\n    WHERE {' AND '.join(where_clauses)}"
    else:
        outgoing_query = ''

    if direction in {"incoming", "both"}:
        incoming_query = (
            f"SELECT\n"
            f"        {target_node_id_column} AS {left_node_id_column},\n"
            f"        {source_node_id_column} AS {right_node_id_column},\n"
            f"        1 AS {depth_column}\n"
            f"    FROM {cte}"
        )

        where_clauses = []
        if left_node_id_whitelist:
            where_clauses.append(f"{target_node_id_column} IN ({sql_literal_list(left_node_id_whitelist)})")
        if left_node_id_blacklist:
            where_clauses.append(f"{target_node_id_column} NOT IN ({sql_literal_list(left_node_id_blacklist)})")
        if where_clauses:
            incoming_query += f"\n    WHERE {' AND '.join(where_clauses)}"
    else:
        incoming_query = ''

    # Combine queries with UNION ALL, then apply DISTINCT to remove duplicates
    if direction == "both":
        query = (
            f"SELECT DISTINCT *\n"
            f"FROM (\n"
            f"    {outgoing_query}\n"
            f"    UNION ALL\n"
            f"    {incoming_query}\n"
            f")"
        )
    elif direction == "outgoing":
        query = (
            f"SELECT DISTINCT *\n"
            f"FROM (\n"
            f"    {outgoing_query}\n"
            f")"
        )
    elif direction == "incoming":
        query = (
            f"SELECT DISTINCT *\n"
            f"FROM (\n"
            f"    {incoming_query}\n"
            f")"
        )
    else:
        raise ValueError(f"Invalid direction: {direction}")

    return query
