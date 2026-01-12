"""
Tests for graph traversal using European cities data.
"""

from ixmemory.graph_memory.traversal import traverse

from tests.graph_memory.test_european_cities import (
    PARIS_OUTGOING_DEPTH_0,
    PARIS_OUTGOING_DEPTH_1,
    PARIS_OUTGOING_DEPTH_2,
    PARIS_OUTGOING_DEPTH_3,
    MILAN_INCOMING_DEPTH_0,
    MILAN_INCOMING_DEPTH_1,
    MILAN_INCOMING_DEPTH_2,
    STRASBOURG_BOTH_DEPTH_0,
    STRASBOURG_BOTH_DEPTH_1,
    STRASBOURG_BOTH_DEPTH_2,
)


def _extract_node_ids(result):
    """Extract node IDs from traversal result."""
    return {node["node_id"] for node in result}


# =============================================================================
# Outgoing traversal from Paris
# =============================================================================

def test_paris_outgoing_depth_0(european_cities_db):
    """Test depth 0 returns only the start node."""
    result = traverse(
        connection=european_cities_db,
        start_node_id="paris",
        max_depth=0,
        direction="outgoing",
    )
    assert _extract_node_ids(result) == PARIS_OUTGOING_DEPTH_0


def test_paris_outgoing_depth_1(european_cities_db):
    """Test depth 1 returns Paris and its direct outgoing neighbours."""
    result = traverse(
        connection=european_cities_db,
        start_node_id="paris",
        max_depth=1,
        direction="outgoing",
    )
    assert _extract_node_ids(result) == PARIS_OUTGOING_DEPTH_1


def test_paris_outgoing_depth_2(european_cities_db):
    """Test depth 2 returns nodes reachable in 2 hops from Paris."""
    result = traverse(
        connection=european_cities_db,
        start_node_id="paris",
        max_depth=2,
        direction="outgoing",
    )
    assert _extract_node_ids(result) == PARIS_OUTGOING_DEPTH_2


def test_paris_outgoing_depth_3(european_cities_db):
    """Test depth 3 returns nodes reachable in 3 hops from Paris."""
    result = traverse(
        connection=european_cities_db,
        start_node_id="paris",
        max_depth=3,
        direction="outgoing",
    )
    assert _extract_node_ids(result) == PARIS_OUTGOING_DEPTH_3


# =============================================================================
# Incoming traversal from Milan
# =============================================================================

def test_milan_incoming_depth_0(european_cities_db):
    """Test depth 0 returns only the start node."""
    result = traverse(
        connection=european_cities_db,
        start_node_id="milan",
        max_depth=0,
        direction="incoming",
    )
    assert _extract_node_ids(result) == MILAN_INCOMING_DEPTH_0


def test_milan_incoming_depth_1(european_cities_db):
    """Test depth 1 returns Milan and nodes that point to it."""
    result = traverse(
        connection=european_cities_db,
        start_node_id="milan",
        max_depth=1,
        direction="incoming",
    )
    assert _extract_node_ids(result) == MILAN_INCOMING_DEPTH_1


def test_milan_incoming_depth_2(european_cities_db):
    """Test depth 2 returns nodes reachable in 2 incoming hops to Milan."""
    result = traverse(
        connection=european_cities_db,
        start_node_id="milan",
        max_depth=2,
        direction="incoming",
    )
    assert _extract_node_ids(result) == MILAN_INCOMING_DEPTH_2


# =============================================================================
# Both-direction traversal from Strasbourg
# =============================================================================

def test_strasbourg_both_depth_0(european_cities_db):
    """Test depth 0 returns only the start node."""
    result = traverse(
        connection=european_cities_db,
        start_node_id="strasbourg",
        max_depth=0,
        direction="both",
    )
    assert _extract_node_ids(result) == STRASBOURG_BOTH_DEPTH_0


def test_strasbourg_both_depth_1(european_cities_db):
    """Test depth 1 returns Strasbourg and nodes connected in either direction."""
    result = traverse(
        connection=european_cities_db,
        start_node_id="strasbourg",
        max_depth=1,
        direction="both",
    )
    assert _extract_node_ids(result) == STRASBOURG_BOTH_DEPTH_1


def test_strasbourg_both_depth_2(european_cities_db):
    """Test depth 2 returns nodes reachable in 2 hops in either direction."""
    result = traverse(
        connection=european_cities_db,
        start_node_id="strasbourg",
        max_depth=2,
        direction="both",
    )
    assert _extract_node_ids(result) == STRASBOURG_BOTH_DEPTH_2
