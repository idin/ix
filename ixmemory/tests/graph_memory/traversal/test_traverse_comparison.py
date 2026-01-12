"""
Tests that compare all three traversal methods:
- graph_walk_traversal.traverse
- batched_bfs_traversal.traverse_batched_bfs
- query_based_traversal.traverse_with_queries

All implementations should produce the same nodes with the same depths.
"""

import pytest

from ixmemory.graph_memory.traversal import (
    traverse,
    traverse_batched_bfs,
    traverse_with_queries,
)


def _extract_node_depths(result):
    """Extract {node_id: depth} from traversal result."""
    return {node["node_id"]: node["depth"] for node in result}


def _extract_node_ids(result):
    """Extract set of node IDs from traversal result."""
    return {node["node_id"] for node in result}


# =============================================================================
# Paris outgoing comparisons
# =============================================================================

def test_paris_outgoing_depth_0_same_results(european_cities_db):
    """Both methods return the same result for Paris outgoing depth 0."""
    walk_result = traverse(
        connection=european_cities_db, start_node_id="paris", max_depth=0, direction="outgoing"
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="paris", max_depth=0, direction="outgoing"
    )
    
    assert _extract_node_depths(walk_result) == _extract_node_depths(query_result)


def test_paris_outgoing_depth_1_same_results(european_cities_db):
    """Both methods return the same result for Paris outgoing depth 1."""
    walk_result = traverse(
        connection=european_cities_db, start_node_id="paris", max_depth=1, direction="outgoing"
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="paris", max_depth=1, direction="outgoing"
    )
    
    assert _extract_node_depths(walk_result) == _extract_node_depths(query_result)


def test_paris_outgoing_depth_2_same_results(european_cities_db):
    """Both methods return the same result for Paris outgoing depth 2."""
    walk_result = traverse(
        connection=european_cities_db, start_node_id="paris", max_depth=2, direction="outgoing"
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="paris", max_depth=2, direction="outgoing"
    )
    
    assert _extract_node_depths(walk_result) == _extract_node_depths(query_result)


def test_paris_outgoing_depth_3_same_results(european_cities_db):
    """Both methods return the same result for Paris outgoing depth 3."""
    walk_result = traverse(
        connection=european_cities_db, start_node_id="paris", max_depth=3, direction="outgoing"
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="paris", max_depth=3, direction="outgoing"
    )
    
    assert _extract_node_depths(walk_result) == _extract_node_depths(query_result)


# =============================================================================
# Milan incoming comparisons
# =============================================================================

def test_milan_incoming_depth_0_same_results(european_cities_db):
    """Both methods return the same result for Milan incoming depth 0."""
    walk_result = traverse(
        connection=european_cities_db, start_node_id="milan", max_depth=0, direction="incoming"
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="milan", max_depth=0, direction="incoming"
    )
    
    assert _extract_node_depths(walk_result) == _extract_node_depths(query_result)


def test_milan_incoming_depth_1_same_results(european_cities_db):
    """Both methods return the same result for Milan incoming depth 1."""
    walk_result = traverse(
        connection=european_cities_db, start_node_id="milan", max_depth=1, direction="incoming"
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="milan", max_depth=1, direction="incoming"
    )
    
    assert _extract_node_depths(walk_result) == _extract_node_depths(query_result)


def test_milan_incoming_depth_2_same_results(european_cities_db):
    """Both methods return the same result for Milan incoming depth 2."""
    walk_result = traverse(
        connection=european_cities_db, start_node_id="milan", max_depth=2, direction="incoming"
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="milan", max_depth=2, direction="incoming"
    )
    
    assert _extract_node_depths(walk_result) == _extract_node_depths(query_result)


# =============================================================================
# Strasbourg both-direction comparisons
# =============================================================================

def test_strasbourg_both_depth_0_same_results(european_cities_db):
    """Both methods return the same result for Strasbourg both-direction depth 0."""
    walk_result = traverse(
        connection=european_cities_db, start_node_id="strasbourg", max_depth=0, direction="both"
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="strasbourg", max_depth=0, direction="both"
    )
    
    assert _extract_node_depths(walk_result) == _extract_node_depths(query_result)


def test_strasbourg_both_depth_1_same_results(european_cities_db):
    """Both methods return the same result for Strasbourg both-direction depth 1."""
    walk_result = traverse(
        connection=european_cities_db, start_node_id="strasbourg", max_depth=1, direction="both"
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="strasbourg", max_depth=1, direction="both"
    )
    
    assert _extract_node_depths(walk_result) == _extract_node_depths(query_result)


def test_strasbourg_both_depth_2_same_results(european_cities_db):
    """Both methods return the same result for Strasbourg both-direction depth 2."""
    walk_result = traverse(
        connection=european_cities_db, start_node_id="strasbourg", max_depth=2, direction="both"
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="strasbourg", max_depth=2, direction="both"
    )
    
    assert _extract_node_depths(walk_result) == _extract_node_depths(query_result)


# =============================================================================
# Additional starting points
# =============================================================================

def test_berlin_outgoing_depth_2_same_results(european_cities_db):
    """Both methods return the same result for Berlin outgoing depth 2."""
    walk_result = traverse(
        connection=european_cities_db, start_node_id="berlin", max_depth=2, direction="outgoing"
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="berlin", max_depth=2, direction="outgoing"
    )
    
    assert _extract_node_depths(walk_result) == _extract_node_depths(query_result)


def test_rome_incoming_depth_3_same_results(european_cities_db):
    """Both methods return the same result for Rome incoming depth 3."""
    walk_result = traverse(
        connection=european_cities_db, start_node_id="rome", max_depth=3, direction="incoming"
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="rome", max_depth=3, direction="incoming"
    )
    
    assert _extract_node_depths(walk_result) == _extract_node_depths(query_result)


def test_frankfurt_both_depth_2_same_results(european_cities_db):
    """Both methods return the same result for Frankfurt both-direction depth 2."""
    walk_result = traverse(
        connection=european_cities_db, start_node_id="frankfurt", max_depth=2, direction="both"
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="frankfurt", max_depth=2, direction="both"
    )
    
    assert _extract_node_depths(walk_result) == _extract_node_depths(query_result)


def test_nice_both_depth_3_same_results(european_cities_db):
    """Both methods return the same result for Nice both-direction depth 3."""
    walk_result = traverse(
        connection=european_cities_db, start_node_id="nice", max_depth=3, direction="both"
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="nice", max_depth=3, direction="both"
    )
    
    assert _extract_node_depths(walk_result) == _extract_node_depths(query_result)


# =============================================================================
# Edge cases
# =============================================================================

def test_isolated_node_depth_1_same_results(european_cities_db):
    """Both methods return the same result for a node with no outgoing edges."""
    # Naples has no outgoing edges (it's a leaf in the outgoing direction)
    walk_result = traverse(
        connection=european_cities_db, start_node_id="naples", max_depth=1, direction="outgoing"
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="naples", max_depth=1, direction="outgoing"
    )
    
    assert _extract_node_depths(walk_result) == _extract_node_depths(query_result)


def test_leaf_node_incoming_depth_2_same_results(european_cities_db):
    """Both methods return the same result for leaf node with incoming traversal."""
    # Hamburg has no incoming edges in our graph
    walk_result = traverse(
        connection=european_cities_db, start_node_id="hamburg", max_depth=2, direction="incoming"
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="hamburg", max_depth=2, direction="incoming"
    )
    
    assert _extract_node_depths(walk_result) == _extract_node_depths(query_result)


def test_high_connectivity_node_depth_1_same_results(european_cities_db):
    """Both methods return the same result for highly connected node."""
    # Cologne has multiple outgoing edges
    walk_result = traverse(
        connection=european_cities_db, start_node_id="cologne", max_depth=1, direction="outgoing"
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="cologne", max_depth=1, direction="outgoing"
    )
    
    assert _extract_node_depths(walk_result) == _extract_node_depths(query_result)


# =============================================================================
# Node properties consistency
# =============================================================================

def test_node_properties_match(european_cities_db):
    """All methods return nodes with matching properties."""
    walk_result = traverse(
        connection=european_cities_db, start_node_id="paris", max_depth=2, direction="outgoing"
    )
    batched_result = traverse_batched_bfs(
        connection=european_cities_db, start_node_id="paris", max_depth=2, direction="outgoing"
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="paris", max_depth=2, direction="outgoing"
    )
    
    # Build dict of node_id -> (node_type, properties)
    walk_props = {
        node["node_id"]: (node["node_type"], node["properties"])
        for node in walk_result
    }
    batched_props = {
        node["node_id"]: (node["node_type"], node["properties"])
        for node in batched_result
    }
    query_props = {
        node["node_id"]: (node["node_type"], node["properties"])
        for node in query_result
    }
    
    assert walk_props == batched_props == query_props


# =============================================================================
# Batched BFS comparisons (all three methods)
# =============================================================================

def test_all_three_paris_outgoing_depth_2(european_cities_db):
    """All three methods return same nodes for Paris outgoing depth 2."""
    walk_result = traverse(
        connection=european_cities_db, start_node_id="paris", max_depth=2, direction="outgoing"
    )
    batched_result = traverse_batched_bfs(
        connection=european_cities_db, start_node_id="paris", max_depth=2, direction="outgoing"
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="paris", max_depth=2, direction="outgoing"
    )
    
    walk_depths = _extract_node_depths(walk_result)
    batched_depths = _extract_node_depths(batched_result)
    query_depths = _extract_node_depths(query_result)
    
    assert walk_depths == batched_depths == query_depths


def test_all_three_milan_incoming_depth_2(european_cities_db):
    """All three methods return same nodes for Milan incoming depth 2."""
    walk_result = traverse(
        connection=european_cities_db, start_node_id="milan", max_depth=2, direction="incoming"
    )
    batched_result = traverse_batched_bfs(
        connection=european_cities_db, start_node_id="milan", max_depth=2, direction="incoming"
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="milan", max_depth=2, direction="incoming"
    )
    
    walk_depths = _extract_node_depths(walk_result)
    batched_depths = _extract_node_depths(batched_result)
    query_depths = _extract_node_depths(query_result)
    
    assert walk_depths == batched_depths == query_depths


def test_all_three_strasbourg_both_depth_2(european_cities_db):
    """All three methods return same nodes for Strasbourg both-direction depth 2."""
    walk_result = traverse(
        connection=european_cities_db, start_node_id="strasbourg", max_depth=2, direction="both"
    )
    batched_result = traverse_batched_bfs(
        connection=european_cities_db, start_node_id="strasbourg", max_depth=2, direction="both"
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="strasbourg", max_depth=2, direction="both"
    )
    
    walk_depths = _extract_node_depths(walk_result)
    batched_depths = _extract_node_depths(batched_result)
    query_depths = _extract_node_depths(query_result)
    
    assert walk_depths == batched_depths == query_depths


def test_all_three_nice_both_depth_3(european_cities_db):
    """All three methods return same nodes for Nice both-direction depth 3."""
    walk_result = traverse(
        connection=european_cities_db, start_node_id="nice", max_depth=3, direction="both"
    )
    batched_result = traverse_batched_bfs(
        connection=european_cities_db, start_node_id="nice", max_depth=3, direction="both"
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="nice", max_depth=3, direction="both"
    )
    
    walk_depths = _extract_node_depths(walk_result)
    batched_depths = _extract_node_depths(batched_result)
    query_depths = _extract_node_depths(query_result)
    
    assert walk_depths == batched_depths == query_depths


def test_all_three_depth_0(european_cities_db):
    """All three methods return same result for depth 0."""
    walk_result = traverse(
        connection=european_cities_db, start_node_id="paris", max_depth=0, direction="outgoing"
    )
    batched_result = traverse_batched_bfs(
        connection=european_cities_db, start_node_id="paris", max_depth=0, direction="outgoing"
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="paris", max_depth=0, direction="outgoing"
    )
    
    walk_depths = _extract_node_depths(walk_result)
    batched_depths = _extract_node_depths(batched_result)
    query_depths = _extract_node_depths(query_result)
    
    assert walk_depths == batched_depths == query_depths
    assert walk_depths == {"paris": 0}


# =============================================================================
# Batched BFS specific tests (path reconstruction)
# =============================================================================

def test_batched_includes_path(european_cities_db):
    """Batched BFS includes path in results."""
    result = traverse_batched_bfs(
        connection=european_cities_db, start_node_id="paris", max_depth=2, direction="outgoing"
    )
    
    # All nodes should have a path
    for node in result:
        assert "path" in node
        assert isinstance(node["path"], list)
        assert len(node["path"]) > 0
        # Path should start with paris
        assert node["path"][0] == "paris"
        # Path should end with the node itself
        assert node["path"][-1] == node["node_id"]


def test_batched_path_length_matches_depth(european_cities_db):
    """Path length should be depth + 1."""
    result = traverse_batched_bfs(
        connection=european_cities_db, start_node_id="paris", max_depth=3, direction="outgoing"
    )
    
    for node in result:
        expected_length = node["depth"] + 1
        assert len(node["path"]) == expected_length, (
            f"Node {node['node_id']} at depth {node['depth']} "
            f"has path length {len(node['path'])}, expected {expected_length}"
        )


# =============================================================================
# Blacklist tests - verify blacklist reduces results
# =============================================================================
# The test data has two relationship types:
#   - "domestic": within-country edges
#   - "cross_border": between-country edges
# Paris has only domestic outgoing edges (to Lille, Strasbourg, Lyon)
# Strasbourg has domestic (from Paris) and cross_border (to Stuttgart, Frankfurt)

def test_walk_blacklist_cross_border_reduces_results(european_cities_db):
    """Blacklisting cross_border should reduce nodes found."""
    # Without blacklist - should reach German cities via Strasbourg
    result_no_blacklist = traverse(
        connection=european_cities_db, start_node_id="paris", max_depth=2, direction="outgoing"
    )
    
    # With blacklist - exclude cross_border edges
    result_with_blacklist = traverse(
        connection=european_cities_db, start_node_id="paris", max_depth=2, direction="outgoing",
        relationship_type_blacklist=["cross_border"],
    )
    
    # Without blacklist includes Stuttgart, Frankfurt (via Strasbourg cross_border)
    no_blacklist_nodes = _extract_node_ids(result_no_blacklist)
    assert "stuttgart" in no_blacklist_nodes
    assert "frankfurt" in no_blacklist_nodes
    
    # With blacklist excludes cross_border destinations
    blacklist_nodes = _extract_node_ids(result_with_blacklist)
    assert "stuttgart" not in blacklist_nodes
    assert "frankfurt" not in blacklist_nodes
    
    # Should still have domestic destinations
    assert "lille" in blacklist_nodes
    assert "strasbourg" in blacklist_nodes
    assert "lyon" in blacklist_nodes


def test_batched_blacklist_cross_border_reduces_results(european_cities_db):
    """Blacklisting cross_border should reduce nodes found."""
    result_no_blacklist = traverse_batched_bfs(
        connection=european_cities_db, start_node_id="paris", max_depth=2, direction="outgoing"
    )
    result_with_blacklist = traverse_batched_bfs(
        connection=european_cities_db, start_node_id="paris", max_depth=2, direction="outgoing",
        relationship_type_blacklist=["cross_border"],
    )
    
    no_blacklist_nodes = _extract_node_ids(result_no_blacklist)
    blacklist_nodes = _extract_node_ids(result_with_blacklist)
    
    # Cross-border destinations excluded
    assert "stuttgart" in no_blacklist_nodes
    assert "stuttgart" not in blacklist_nodes


def test_query_blacklist_cross_border_reduces_results(european_cities_db):
    """Blacklisting cross_border should reduce nodes found."""
    result_no_blacklist = traverse_with_queries(
        connection=european_cities_db, start_node_id="paris", max_depth=2, direction="outgoing"
    )
    result_with_blacklist = traverse_with_queries(
        connection=european_cities_db, start_node_id="paris", max_depth=2, direction="outgoing",
        relationship_type_blacklist=["cross_border"],
    )
    
    no_blacklist_nodes = _extract_node_ids(result_no_blacklist)
    blacklist_nodes = _extract_node_ids(result_with_blacklist)
    
    # Cross-border destinations excluded
    assert "stuttgart" in no_blacklist_nodes
    assert "stuttgart" not in blacklist_nodes


def test_walk_blacklist_domestic_leaves_only_cross_border(european_cities_db):
    """Blacklisting domestic from Strasbourg should only allow cross_border."""
    # Strasbourg has: incoming domestic from Paris, outgoing cross_border to Stuttgart/Frankfurt
    result = traverse(
        connection=european_cities_db, start_node_id="strasbourg", max_depth=1, direction="outgoing",
        relationship_type_blacklist=["domestic"],
    )
    
    nodes = _extract_node_ids(result)
    # Should have strasbourg and cross_border destinations
    assert nodes == {"strasbourg", "stuttgart", "frankfurt"}


# =============================================================================
# Blacklist comparison tests - all three methods should agree
# =============================================================================

def test_all_three_blacklist_cross_border_same_results(european_cities_db):
    """All three methods with cross_border blacklist should return same nodes."""
    blacklist = ["cross_border"]
    
    walk_result = traverse(
        connection=european_cities_db, start_node_id="paris", max_depth=2, direction="outgoing",
        relationship_type_blacklist=blacklist,
    )
    batched_result = traverse_batched_bfs(
        connection=european_cities_db, start_node_id="paris", max_depth=2, direction="outgoing",
        relationship_type_blacklist=blacklist,
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="paris", max_depth=2, direction="outgoing",
        relationship_type_blacklist=blacklist,
    )
    
    walk_depths = _extract_node_depths(walk_result)
    batched_depths = _extract_node_depths(batched_result)
    query_depths = _extract_node_depths(query_result)
    
    assert walk_depths == batched_depths == query_depths


def test_all_three_blacklist_domestic_same_results(european_cities_db):
    """All three methods with domestic blacklist should return same nodes."""
    blacklist = ["domestic"]
    
    walk_result = traverse(
        connection=european_cities_db, start_node_id="strasbourg", max_depth=1, direction="outgoing",
        relationship_type_blacklist=blacklist,
    )
    batched_result = traverse_batched_bfs(
        connection=european_cities_db, start_node_id="strasbourg", max_depth=1, direction="outgoing",
        relationship_type_blacklist=blacklist,
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="strasbourg", max_depth=1, direction="outgoing",
        relationship_type_blacklist=blacklist,
    )
    
    walk_depths = _extract_node_depths(walk_result)
    batched_depths = _extract_node_depths(batched_result)
    query_depths = _extract_node_depths(query_result)
    
    assert walk_depths == batched_depths == query_depths
    # Should only have strasbourg and cross_border destinations
    assert _extract_node_ids(walk_result) == {"strasbourg", "stuttgart", "frankfurt"}


def test_all_three_blacklist_nonexistent_type_same_as_no_blacklist(european_cities_db):
    """Blacklisting a nonexistent relationship type should have no effect."""
    blacklist = ["nonexistent_relationship_type"]
    
    walk_blacklist = traverse(
        connection=european_cities_db, start_node_id="paris", max_depth=2, direction="outgoing",
        relationship_type_blacklist=blacklist,
    )
    batched_blacklist = traverse_batched_bfs(
        connection=european_cities_db, start_node_id="paris", max_depth=2, direction="outgoing",
        relationship_type_blacklist=blacklist,
    )
    query_blacklist = traverse_with_queries(
        connection=european_cities_db, start_node_id="paris", max_depth=2, direction="outgoing",
        relationship_type_blacklist=blacklist,
    )
    
    walk_no_filter = traverse(
        connection=european_cities_db, start_node_id="paris", max_depth=2, direction="outgoing",
    )
    batched_no_filter = traverse_batched_bfs(
        connection=european_cities_db, start_node_id="paris", max_depth=2, direction="outgoing",
    )
    query_no_filter = traverse_with_queries(
        connection=european_cities_db, start_node_id="paris", max_depth=2, direction="outgoing",
    )
    
    assert _extract_node_depths(walk_blacklist) == _extract_node_depths(walk_no_filter)
    assert _extract_node_depths(batched_blacklist) == _extract_node_depths(batched_no_filter)
    assert _extract_node_depths(query_blacklist) == _extract_node_depths(query_no_filter)


def test_all_three_blacklist_incoming_same_results(european_cities_db):
    """All three methods with blacklist on incoming direction should agree."""
    # Milan has incoming cross_border from Nice, Stuttgart, Munich
    blacklist = ["cross_border"]
    
    walk_result = traverse(
        connection=european_cities_db, start_node_id="milan", max_depth=1, direction="incoming",
        relationship_type_blacklist=blacklist,
    )
    batched_result = traverse_batched_bfs(
        connection=european_cities_db, start_node_id="milan", max_depth=1, direction="incoming",
        relationship_type_blacklist=blacklist,
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="milan", max_depth=1, direction="incoming",
        relationship_type_blacklist=blacklist,
    )
    
    walk_depths = _extract_node_depths(walk_result)
    batched_depths = _extract_node_depths(batched_result)
    query_depths = _extract_node_depths(query_result)
    
    assert walk_depths == batched_depths == query_depths
    # With cross_border blacklisted, only milan remains (no domestic incoming)
    assert walk_depths == {"milan": 0}


def test_all_three_blacklist_both_direction_same_results(european_cities_db):
    """All three methods with blacklist on both direction should agree."""
    # Strasbourg: incoming domestic from Paris, outgoing cross_border to Stuttgart/Frankfurt
    blacklist = ["domestic"]
    
    walk_result = traverse(
        connection=european_cities_db, start_node_id="strasbourg", max_depth=1, direction="both",
        relationship_type_blacklist=blacklist,
    )
    batched_result = traverse_batched_bfs(
        connection=european_cities_db, start_node_id="strasbourg", max_depth=1, direction="both",
        relationship_type_blacklist=blacklist,
    )
    query_result = traverse_with_queries(
        connection=european_cities_db, start_node_id="strasbourg", max_depth=1, direction="both",
        relationship_type_blacklist=blacklist,
    )
    
    walk_depths = _extract_node_depths(walk_result)
    batched_depths = _extract_node_depths(batched_result)
    query_depths = _extract_node_depths(query_result)
    
    assert walk_depths == batched_depths == query_depths
    # Domestic blacklisted: no Paris (incoming), but Stuttgart/Frankfurt (outgoing cross_border)
    assert _extract_node_ids(walk_result) == {"strasbourg", "stuttgart", "frankfurt"}
