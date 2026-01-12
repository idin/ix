"""
Tests for GraphMemory pathfinding operations.
"""

from ixmemory.graph_memory import GraphMemory


def test_find_path_direct():
    """Test finding a direct path between nodes."""
    graph = GraphMemory()
    
    graph.add_node(node_id="a", node_type="Node")
    graph.add_node(node_id="b", node_type="Node")
    
    graph.add_edge(source_node_id="a", target_node_id="b", relationship_type="connects")
    
    path = graph.find_path(start_node_id="a", end_node_id="b")
    assert path == ["a", "b"]
    
    graph.close()


def test_find_path_multi_hop():
    """Test finding a path through multiple nodes."""
    graph = GraphMemory()
    
    graph.add_node(node_id="a", node_type="Node")
    graph.add_node(node_id="b", node_type="Node")
    graph.add_node(node_id="c", node_type="Node")
    
    graph.add_edge(source_node_id="a", target_node_id="b", relationship_type="connects")
    graph.add_edge(source_node_id="b", target_node_id="c", relationship_type="connects")
    
    path = graph.find_path(start_node_id="a", end_node_id="c")
    assert path == ["a", "b", "c"]
    
    graph.close()


def test_find_path_no_path():
    """Test finding a path when none exists."""
    graph = GraphMemory()
    
    graph.add_node(node_id="a", node_type="Node")
    graph.add_node(node_id="b", node_type="Node")
    graph.add_node(node_id="c", node_type="Node")
    
    graph.add_edge(source_node_id="a", target_node_id="b", relationship_type="connects")
    # c is not connected
    
    path = graph.find_path(start_node_id="a", end_node_id="c")
    assert path is None
    
    graph.close()


def test_find_path_with_max_depth():
    """Test finding a path with max depth limit."""
    graph = GraphMemory()
    
    graph.add_node(node_id="a", node_type="Node")
    graph.add_node(node_id="b", node_type="Node")
    graph.add_node(node_id="c", node_type="Node")
    graph.add_node(node_id="d", node_type="Node")
    
    graph.add_edge(source_node_id="a", target_node_id="b", relationship_type="connects")
    graph.add_edge(source_node_id="b", target_node_id="c", relationship_type="connects")
    graph.add_edge(source_node_id="c", target_node_id="d", relationship_type="connects")
    
    # Path exists but exceeds max_depth
    path = graph.find_path(start_node_id="a", end_node_id="d", max_depth=2)
    assert path is None
    
    # Path exists within max_depth
    path = graph.find_path(start_node_id="a", end_node_id="c", max_depth=2)
    assert path == ["a", "b", "c"]
    
    graph.close()


def test_find_path_filtered_by_relationship():
    """Test finding a path filtered by relationship types."""
    graph = GraphMemory()
    
    graph.add_node(node_id="a", node_type="Node")
    graph.add_node(node_id="b", node_type="Node")
    graph.add_node(node_id="c", node_type="Node")
    
    graph.add_edge(source_node_id="a", target_node_id="b", relationship_type="works_at")
    graph.add_edge(source_node_id="b", target_node_id="c", relationship_type="knows")
    
    # Path exists but wrong relationship type
    path = graph.find_path(
        start_node_id="a",
        end_node_id="c",
        relationship_type_whitelist=["knows"],
    )
    assert path is None
    
    # Path exists with correct relationship type
    path = graph.find_path(
        start_node_id="a",
        end_node_id="b",
        relationship_type_whitelist=["works_at"],
    )
    assert path == ["a", "b"]
    
    graph.close()

