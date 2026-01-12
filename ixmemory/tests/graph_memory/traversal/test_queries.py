"""
Tests for traversal query building functions.

All tests validate semantic correctness through execution, not string matching.
End-to-end traversal behaviour is the source of truth.
"""

import pytest

from ixmemory.graph_memory.traversal.query_builders import (
    get_nodes_and_edges_query,
    get_edges_query,
    get_traversal_query,
    get_full_traversal_query,
)

from tests.graph_memory.test_european_cities import (
    PARIS_OUTGOING_DEPTH_1,
    PARIS_OUTGOING_DEPTH_2,
    PARIS_OUTGOING_DEPTH_3,
    PARIS_OUTGOING_DEPTHS,
    MILAN_INCOMING_DEPTH_1,
    MILAN_INCOMING_DEPTH_2,
    MILAN_INCOMING_DEPTHS,
    STRASBOURG_BOTH_DEPTH_1,
    STRASBOURG_BOTH_DEPTH_2,
    STRASBOURG_BOTH_DEPTHS,
    EUROPEAN_CITIES_EDGES,
)


def _execute_full_query(connection, starting_node_id, **kwargs):
    """
    Execute a full traversal query and return dict of {node_id: min_depth}.
    
    Note: The SQL query does not return the starting node. Tests add it manually.
    """
    query = get_full_traversal_query(
        starting_node_ids=[starting_node_id],
        **kwargs,
    )
    cursor = connection.cursor()
    cursor.execute(query)
    
    # Query returns (node_id, min_depth)
    return {row[0]: row[1] for row in cursor.fetchall()}


def _execute_full_query_and_get_nodes(connection, starting_node_id, **kwargs):
    """
    Execute a full traversal query and return the set of node IDs reached.
    
    Adds the starting node since the query only returns reachable nodes.
    """
    result = _execute_full_query(connection, starting_node_id, **kwargs)
    result_nodes = set(result.keys())
    result_nodes.add(starting_node_id)
    return result_nodes


# =============================================================================
# Test get_nodes_and_edges_query - Execution-based
# =============================================================================

def test_get_nodes_and_edges_query_returns_all_edges(european_cities_db):
    """Query returns all edges with 5 columns matching schema."""
    query = get_nodes_and_edges_query()
    cursor = european_cities_db.cursor()
    cursor.execute(query)
    
    rows = cursor.fetchall()
    # Our fixture has exactly 28 edges (count from EUROPEAN_CITIES_EDGES)
    assert len(rows) == len(EUROPEAN_CITIES_EDGES)
    # Column structure: source_node_id, source_node_type, target_node_id, target_node_type, relationship_type
    assert len(rows[0]) == 5


def test_get_nodes_and_edges_query_relationship_filter_matches_all_returned(european_cities_db):
    """All returned edges have relationship_type matching the filter."""
    # Test with domestic filter
    query = get_nodes_and_edges_query(
        relationship_type_whitelist=["domestic"],
    )
    cursor = european_cities_db.cursor()
    cursor.execute(query)
    
    rows = cursor.fetchall()
    # Count domestic edges in fixture
    domestic_count = sum(1 for e in EUROPEAN_CITIES_EDGES if e["relationship_type"] == "domestic")
    assert len(rows) == domestic_count
    
    # Verify every row's relationship_type (column index 4) is "domestic"
    for row in rows:
        assert row[4] == "domestic", f"Expected 'domestic', got '{row[4]}'"


def test_get_nodes_and_edges_query_blacklist_excludes_relationship(european_cities_db):
    """Blacklisting 'domestic' excludes domestic edges, leaving only cross_border."""
    query = get_nodes_and_edges_query(
        relationship_type_blacklist=["domestic"],
    )
    cursor = european_cities_db.cursor()
    cursor.execute(query)
    
    rows = cursor.fetchall()
    # Count cross_border edges in fixture
    cross_border_count = sum(1 for e in EUROPEAN_CITIES_EDGES if e["relationship_type"] == "cross_border")
    assert len(rows) == cross_border_count
    
    # Verify no row has relationship_type "domestic"
    for row in rows:
        assert row[4] != "domestic", f"Expected no 'domestic', got '{row[4]}'"


def test_get_nodes_and_edges_query_nonexistent_relationship_returns_empty(european_cities_db):
    """Filtering by nonexistent relationship type returns no rows."""
    query = get_nodes_and_edges_query(
        relationship_type_whitelist=["nonexistent_type"],
    )
    cursor = european_cities_db.cursor()
    cursor.execute(query)
    
    rows = cursor.fetchall()
    assert len(rows) == 0


def test_get_nodes_and_edges_query_node_type_filter_matches_schema(european_cities_db):
    """Node type filter only returns edges where both nodes match."""
    # All nodes in fixture are "city" type
    query = get_nodes_and_edges_query(
        node_type_whitelist=["city"],
    )
    cursor = european_cities_db.cursor()
    cursor.execute(query)
    
    rows = cursor.fetchall()
    assert len(rows) == len(EUROPEAN_CITIES_EDGES)
    
    # Verify all source and target node types are "city"
    for row in rows:
        assert row[1] == "city", f"Source node type should be 'city', got '{row[1]}'"
        assert row[3] == "city", f"Target node type should be 'city', got '{row[3]}'"


# =============================================================================
# Test get_edges_query - Execution-based with CTE
# =============================================================================

def test_get_edges_query_outgoing_with_cte(european_cities_db):
    """Outgoing edges from Paris via CTE returns correct neighbours."""
    # Build a complete query with CTE
    base_query = get_nodes_and_edges_query()
    edges_query = get_edges_query(
        direction="outgoing",
        left_node_id_whitelist=["paris"],
        common_table_expression_name="nodes_and_edges",
    )
    
    full_query = f"""
    WITH nodes_and_edges AS (
        {base_query}
    )
    {edges_query}
    """
    
    cursor = european_cities_db.cursor()
    cursor.execute(full_query)
    rows = cursor.fetchall()
    
    # Paris has 3 outgoing edges: Paris → Lille, Strasbourg, Lyon
    assert len(rows) == 3
    targets = {row[1] for row in rows}  # right_node_id is column 1
    assert targets == {"lille", "strasbourg", "lyon"}


def test_get_edges_query_incoming_with_cte(european_cities_db):
    """Incoming edges to Milan via CTE returns correct sources."""
    base_query = get_nodes_and_edges_query()
    edges_query = get_edges_query(
        direction="incoming",
        left_node_id_whitelist=["milan"],
        common_table_expression_name="nodes_and_edges",
    )
    
    full_query = f"""
    WITH nodes_and_edges AS (
        {base_query}
    )
    {edges_query}
    """
    
    cursor = european_cities_db.cursor()
    cursor.execute(full_query)
    rows = cursor.fetchall()
    
    # Milan has 3 incoming edges: Nice → Milan, Stuttgart → Milan, Munich → Milan
    assert len(rows) == 3
    sources = {row[1] for row in rows}  # right_node_id is the source for incoming
    assert sources == {"nice", "stuttgart", "munich"}


def test_get_edges_query_both_with_cte(european_cities_db):
    """Both-direction edges from Strasbourg returns outgoing and incoming."""
    base_query = get_nodes_and_edges_query()
    edges_query = get_edges_query(
        direction="both",
        left_node_id_whitelist=["strasbourg"],
        common_table_expression_name="nodes_and_edges",
    )
    
    full_query = f"""
    WITH nodes_and_edges AS (
        {base_query}
    )
    {edges_query}
    """
    
    cursor = european_cities_db.cursor()
    cursor.execute(full_query)
    rows = cursor.fetchall()
    
    # Strasbourg has:
    #   Outgoing: Strasbourg → Stuttgart, Frankfurt
    #   Incoming: Paris → Strasbourg
    assert len(rows) == 3
    neighbours = {row[1] for row in rows}
    assert neighbours == {"paris", "stuttgart", "frankfurt"}


# =============================================================================
# Test get_traversal_query - Error handling
# =============================================================================

def test_get_traversal_query_depth_0_returns_only_start_nodes():
    """Depth 0 returns only the starting nodes (from start_nodes CTE)."""
    query = get_traversal_query(max_depth=0)
    # Should contain a SELECT for depth 0 from start_nodes
    assert "start_nodes" in query
    assert "0 AS depth" in query


def test_get_traversal_query_negative_depth_raises_value_error():
    """Negative depth raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        get_traversal_query(max_depth=-1)
    assert "max_depth" in str(exc_info.value)


# =============================================================================
# Test get_full_traversal_query - Node membership
# =============================================================================

def test_full_query_paris_outgoing_depth_1(european_cities_db):
    """Paris outgoing depth 1 reaches Lille, Strasbourg, Lyon."""
    result = _execute_full_query_and_get_nodes(
        connection=european_cities_db,
        starting_node_id="paris",
        max_depth=1,
        direction="outgoing",
    )
    assert result == PARIS_OUTGOING_DEPTH_1


def test_full_query_paris_outgoing_depth_2(european_cities_db):
    """Paris outgoing depth 2 reaches German and French cities via Lille/Strasbourg/Lyon."""
    result = _execute_full_query_and_get_nodes(
        connection=european_cities_db,
        starting_node_id="paris",
        max_depth=2,
        direction="outgoing",
    )
    assert result == PARIS_OUTGOING_DEPTH_2


def test_full_query_paris_outgoing_depth_3(european_cities_db):
    """Paris outgoing depth 3 reaches Munich, Milan, Genoa."""
    result = _execute_full_query_and_get_nodes(
        connection=european_cities_db,
        starting_node_id="paris",
        max_depth=3,
        direction="outgoing",
    )
    assert result == PARIS_OUTGOING_DEPTH_3


def test_full_query_milan_incoming_depth_1(european_cities_db):
    """Milan incoming depth 1 finds Nice, Stuttgart, Munich (nodes pointing to Milan)."""
    result = _execute_full_query_and_get_nodes(
        connection=european_cities_db,
        starting_node_id="milan",
        max_depth=1,
        direction="incoming",
    )
    assert result == MILAN_INCOMING_DEPTH_1


def test_full_query_milan_incoming_depth_2(european_cities_db):
    """Milan incoming depth 2 finds nodes pointing to Nice/Stuttgart/Munich."""
    result = _execute_full_query_and_get_nodes(
        connection=european_cities_db,
        starting_node_id="milan",
        max_depth=2,
        direction="incoming",
    )
    assert result == MILAN_INCOMING_DEPTH_2


def test_full_query_strasbourg_both_depth_1(european_cities_db):
    """Strasbourg both depth 1 finds Paris (incoming) and Stuttgart/Frankfurt (outgoing)."""
    result = _execute_full_query_and_get_nodes(
        connection=european_cities_db,
        starting_node_id="strasbourg",
        max_depth=1,
        direction="both",
    )
    assert result == STRASBOURG_BOTH_DEPTH_1


def test_full_query_strasbourg_both_depth_2(european_cities_db):
    """Strasbourg both depth 2 expands in all directions."""
    result = _execute_full_query_and_get_nodes(
        connection=european_cities_db,
        starting_node_id="strasbourg",
        max_depth=2,
        direction="both",
    )
    assert result == STRASBOURG_BOTH_DEPTH_2


# =============================================================================
# Test get_full_traversal_query - Minimum depth correctness
# =============================================================================

def test_paris_outgoing_depths_are_correct(european_cities_db):
    """
    Verify minimum depths for Paris outgoing traversal.
    
    Human explanation:
    - Lille, Strasbourg, Lyon are 1 hop from Paris (direct edges)
    - Cologne, Düsseldorf are 2 hops (via Lille)
    - Stuttgart, Frankfurt are 2 hops (via Strasbourg)
    - Marseille, Nice are 2 hops (via Lyon)
    - Munich, Milan, Genoa are 3 hops
    """
    result = _execute_full_query(
        connection=european_cities_db,
        starting_node_id="paris",
        max_depth=3,
        direction="outgoing",
    )
    
    for node_id, expected_depth in PARIS_OUTGOING_DEPTHS.items():
        assert node_id in result, f"{node_id} should be reachable from Paris"
        assert result[node_id] == expected_depth, (
            f"{node_id} should be at depth {expected_depth}, got {result[node_id]}"
        )


def test_milan_incoming_depths_are_correct(european_cities_db):
    """
    Verify minimum depths for Milan incoming traversal.
    
    Human explanation:
    - Nice, Stuttgart, Munich are 1 hop (they have edges to Milan)
    - Lyon, Marseille are 2 hops (they point to Nice)
    - Frankfurt, Strasbourg are 2 hops (they point to Stuttgart)
    """
    result = _execute_full_query(
        connection=european_cities_db,
        starting_node_id="milan",
        max_depth=2,
        direction="incoming",
    )
    
    for node_id, expected_depth in MILAN_INCOMING_DEPTHS.items():
        assert node_id in result, f"{node_id} should reach Milan via incoming"
        assert result[node_id] == expected_depth, (
            f"{node_id} should be at depth {expected_depth}, got {result[node_id]}"
        )


def test_strasbourg_both_depths_are_correct(european_cities_db):
    """
    Verify minimum depths for Strasbourg both-direction traversal.
    
    Human explanation:
    - Paris is 1 hop (Paris → Strasbourg, so incoming)
    - Stuttgart, Frankfurt are 1 hop (Strasbourg → them, outgoing)
    - Lille, Lyon are 2 hops (from Paris)
    - Munich, Milan are 2 hops (from Stuttgart)
    - Cologne is 2 hops (into Frankfurt)
    """
    result = _execute_full_query(
        connection=european_cities_db,
        starting_node_id="strasbourg",
        max_depth=2,
        direction="both",
    )
    
    for node_id, expected_depth in STRASBOURG_BOTH_DEPTHS.items():
        assert node_id in result, f"{node_id} should be reachable from Strasbourg"
        assert result[node_id] == expected_depth, (
            f"{node_id} should be at depth {expected_depth}, got {result[node_id]}"
        )


# =============================================================================
# Negative tests - Nodes that must NOT appear at certain depths
# =============================================================================

def test_paris_outgoing_milan_not_reachable_in_2_hops(european_cities_db):
    """
    Milan is NOT reachable from Paris in 2 hops (outgoing).
    
    Human explanation:
    - Paris → Strasbourg → Stuttgart → Milan is 3 hops
    - Paris → Lyon → Nice → Milan is 3 hops
    - There is no 2-hop path from Paris to Milan
    """
    result = _execute_full_query(
        connection=european_cities_db,
        starting_node_id="paris",
        max_depth=2,
        direction="outgoing",
    )
    
    assert "milan" not in result, "Milan should NOT be reachable from Paris in 2 hops"
    
    # But at depth 3, Milan IS reachable
    result_depth_3 = _execute_full_query(
        connection=european_cities_db,
        starting_node_id="paris",
        max_depth=3,
        direction="outgoing",
    )
    assert "milan" in result_depth_3, "Milan should be reachable from Paris in 3 hops"
    assert result_depth_3["milan"] == 3


def test_milan_incoming_paris_not_reachable_in_2_hops(european_cities_db):
    """
    Paris does NOT reach Milan via incoming traversal within 2 hops.
    
    Human explanation:
    - Paris → Strasbourg → Stuttgart → Milan would need 3 incoming hops
    - Paris itself has no outgoing edge directly to Milan
    """
    result = _execute_full_query(
        connection=european_cities_db,
        starting_node_id="milan",
        max_depth=2,
        direction="incoming",
    )
    
    assert "paris" not in result, "Paris should NOT reach Milan in 2 incoming hops"


def test_strasbourg_both_rome_not_reachable_in_2_hops(european_cities_db):
    """
    Rome is NOT reachable from Strasbourg in 2 hops (either direction).
    
    Human explanation:
    - Rome is deep in Italy: Milan → Bologna → Florence → Rome
    - Strasbourg can reach Milan in 2 hops (via Stuttgart)
    - But Milan → Rome requires 3 more hops through Italy
    """
    result = _execute_full_query(
        connection=european_cities_db,
        starting_node_id="strasbourg",
        max_depth=2,
        direction="both",
    )
    
    assert "rome" not in result, "Rome should NOT be reachable from Strasbourg in 2 hops"


def test_paris_outgoing_berlin_not_reachable_in_3_hops(european_cities_db):
    """
    Berlin is NOT reachable from Paris outgoing in 3 hops.
    
    Human explanation:
    - Berlin is only reachable via Hamburg → Berlin
    - Paris → Lille → Cologne → ? There's no path from Cologne to Berlin
    - Paris → Strasbourg → Frankfurt → ? No path to Hamburg or Berlin
    """
    result = _execute_full_query(
        connection=european_cities_db,
        starting_node_id="paris",
        max_depth=3,
        direction="outgoing",
    )
    
    assert "berlin" not in result, "Berlin should NOT be reachable from Paris in 3 hops"


# =============================================================================
# Test deduplication uses minimum depth
# =============================================================================

def test_deduplication_uses_minimum_depth_nice_from_paris(european_cities_db):
    """
    Nice has only one path from Paris and appears at depth 2.
    
    Human explanation:
    - Paris → Lyon → Nice is the only path (depth 2)
    """
    result = _execute_full_query(
        connection=european_cities_db,
        starting_node_id="paris",
        max_depth=3,
        direction="outgoing",
    )
    
    assert "nice" in result
    assert result["nice"] == 2, "Nice should appear at minimum depth 2"


def test_deduplication_genoa_minimum_depth_from_paris(european_cities_db):
    """
    Genoa can be reached from Paris via multiple paths, minimum is 3.
    
    Human explanation:
    - Paris → Lyon → Marseille → Genoa (depth 3)
    - Paris → Lyon → Nice → Genoa (depth 3)
    - Both are depth 3, so min_depth = 3
    """
    result = _execute_full_query(
        connection=european_cities_db,
        starting_node_id="paris",
        max_depth=3,
        direction="outgoing",
    )
    
    assert "genoa" in result
    assert result["genoa"] == 3, "Genoa should appear at minimum depth 3"
