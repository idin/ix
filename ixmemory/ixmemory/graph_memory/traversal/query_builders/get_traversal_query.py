"""
Query builder for fixed-depth traversal.
"""

from typing import List

from .validate_identifier import validate_identifier


def get_traversal_query(
    max_depth: int,
    left_node_id_column: str = "left_node_id",
    right_node_id_column: str = "right_node_id",
    depth_column: str = "depth",
    edges_cte_name: str = "single_traversal",
    start_nodes_cte_name: str = "start_nodes",
    start_node_id_column: str = "node_id",
    output_node_id_column: str = "node_id",
) -> str:
    """
    Build a query for fixed-depth traversal using chained self-joins.
    
    Args:
        max_depth: Maximum depth to traverse (0 = start nodes only, 1 = one hop, etc.).
        left_node_id_column: Column name for the starting node in the edges CTE.
        right_node_id_column: Column name for the ending node in the edges CTE.
        depth_column: Output column name for the depth value.
        edges_cte_name: Name of the CTE containing edges.
        start_nodes_cte_name: Name of the CTE containing validated starting nodes.
        start_node_id_column: Column name for node ID in the start_nodes CTE.
        output_node_id_column: Column name for node ID in the output.
    
    Returns:
        SQL query string that produces output_node_id_column and min_depth columns,
        including starting nodes at depth 0.
    """
    if max_depth < 0:
        raise ValueError("max_depth must be non-negative")

    # Validate all identifiers
    for name, desc in [
        (left_node_id_column, "column name"),
        (right_node_id_column, "column name"),
        (depth_column, "column name"),
        (edges_cte_name, "CTE name"),
        (start_nodes_cte_name, "CTE name"),
        (start_node_id_column, "column name"),
        (output_node_id_column, "column name"),
    ]:
        validate_identifier(name, desc)

    edges = edges_cte_name
    start = start_nodes_cte_name
    start_col = start_node_id_column
    left = left_node_id_column
    right = right_node_id_column
    out = output_node_id_column

    selects: List[str] = []

    # Depth 0: validated starting nodes from start_nodes CTE
    selects.append(
        f"    SELECT s.{start_col} AS {out}, 0 AS {depth_column}\n"
        f"    FROM {start} s"
    )

    # Depth 1 to max_depth: chain joins anchored from start_nodes
    for d in range(1, max_depth + 1):
        if d == 1:
            # Depth 1: start_nodes joined with edges
            sql = (
                f"    SELECT e1.{right} AS {out}, 1 AS {depth_column}\n"
                f"    FROM {start} s\n"
                f"    JOIN {edges} e1 ON e1.{left} = s.{start_col}"
            )
        else:
            # Depth 2+: chain from start_nodes through edges
            joins = [
                f"    FROM {start} s",
                f"    JOIN {edges} e1 ON e1.{left} = s.{start_col}",
            ]
            for i in range(2, d + 1):
                joins.append(f"    JOIN {edges} e{i} ON e{i}.{left} = e{i-1}.{right}")
            
            sql = (
                f"    SELECT e{d}.{right} AS {out}, {d} AS {depth_column}\n"
                + "\n".join(joins)
            )
        selects.append(sql)

    unioned = "\n\n    UNION ALL\n\n".join(selects)

    return (
        f"SELECT\n"
        f"    {out},\n"
        f"    MIN({depth_column}) AS min_depth\n"
        f"FROM (\n"
        f"{unioned}\n"
        f")\n"
        f"GROUP BY {out}"
    )
