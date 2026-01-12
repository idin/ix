"""
Tests for GraphMemory traversal operations.
"""

from ixmemory.graph_memory import GraphMemory


def test_traverse_immediate_neighbors():
    """Test traversing immediate neighbors only."""
    graph = GraphMemory()
    
    graph.add_node(node_id="a", node_type="Node")
    graph.add_node(node_id="b", node_type="Node")
    graph.add_node(node_id="c", node_type="Node")
    
    graph.add_edge(source_node_id="a", target_node_id="b", relationship_type="connects")
    graph.add_edge(source_node_id="b", target_node_id="c", relationship_type="connects")
    
    nodes = graph.traverse(start_node_id="a", max_depth=1)
    
    node_ids = [node['node_id'] for node in nodes]
    assert "a" in node_ids  # Starting node
    assert "b" in node_ids  # Depth 1
    assert "c" not in node_ids  # Depth 2, not included
    
    graph.close()


def test_traverse_multiple_levels():
    """Test traversing multiple levels of depth."""
    graph = GraphMemory()
    
    graph.add_node(node_id="a", node_type="Node")
    graph.add_node(node_id="b", node_type="Node")
    graph.add_node(node_id="c", node_type="Node")
    graph.add_node(node_id="d", node_type="Node")
    
    graph.add_edge(source_node_id="a", target_node_id="b", relationship_type="connects")
    graph.add_edge(source_node_id="b", target_node_id="c", relationship_type="connects")
    graph.add_edge(source_node_id="c", target_node_id="d", relationship_type="connects")
    
    nodes = graph.traverse(start_node_id="a", max_depth=2)
    
    node_ids = [node['node_id'] for node in nodes]
    assert "a" in node_ids  # Depth 0
    assert "b" in node_ids  # Depth 1
    assert "c" in node_ids  # Depth 2
    assert "d" not in node_ids  # Depth 3, not included
    
    graph.close()


def test_traverse_includes_depth():
    """Test that traversal results include depth information."""
    graph = GraphMemory()
    
    graph.add_node(node_id="a", node_type="Node")
    graph.add_node(node_id="b", node_type="Node")
    graph.add_node(node_id="c", node_type="Node")
    
    graph.add_edge(source_node_id="a", target_node_id="b", relationship_type="connects")
    graph.add_edge(source_node_id="b", target_node_id="c", relationship_type="connects")
    
    nodes = graph.traverse(start_node_id="a", max_depth=2)
    
    # Find nodes by depth
    node_a = next(node for node in nodes if node['node_id'] == "a")
    node_b = next(node for node in nodes if node['node_id'] == "b")
    node_c = next(node for node in nodes if node['node_id'] == "c")
    
    assert node_a['depth'] == 0
    assert node_b['depth'] == 1
    assert node_c['depth'] == 2
    
    graph.close()


def test_traverse_includes_path():
    """Test that traversal results include path information."""
    graph = GraphMemory()
    
    graph.add_node(node_id="a", node_type="Node")
    graph.add_node(node_id="b", node_type="Node")
    graph.add_node(node_id="c", node_type="Node")
    
    graph.add_edge(source_node_id="a", target_node_id="b", relationship_type="connects")
    graph.add_edge(source_node_id="b", target_node_id="c", relationship_type="connects")
    
    nodes = graph.traverse(start_node_id="a", max_depth=2)
    
    node_c = next(node for node in nodes if node['node_id'] == "c")
    assert 'path' in node_c
    assert node_c['path'] == ["a", "b", "c"]
    
    graph.close()


def test_traverse_filtered_by_relationship():
    """Test traversing filtered by relationship types."""
    graph = GraphMemory()
    
    graph.add_node(node_id="a", node_type="Node")
    graph.add_node(node_id="b", node_type="Node")
    graph.add_node(node_id="c", node_type="Node")
    
    graph.add_edge(source_node_id="a", target_node_id="b", relationship_type="works_at")
    graph.add_edge(source_node_id="b", target_node_id="c", relationship_type="knows")
    
    nodes = graph.traverse(
        start_node_id="a",
        max_depth=2,
        relationship_type_whitelist=["works_at"],
    )
    
    node_ids = [node['node_id'] for node in nodes]
    assert "a" in node_ids
    assert "b" in node_ids  # Connected via "works_at"
    assert "c" not in node_ids  # Connected via "knows", filtered out
    
    graph.close()


def test_traverse_direction_incoming():
    """Test traversing in incoming direction."""
    graph = GraphMemory()
    
    graph.add_node(node_id="a", node_type="Node")
    graph.add_node(node_id="b", node_type="Node")
    graph.add_node(node_id="c", node_type="Node")
    
    graph.add_edge(source_node_id="a", target_node_id="b", relationship_type="connects")
    graph.add_edge(source_node_id="c", target_node_id="b", relationship_type="connects")
    
    nodes = graph.traverse(start_node_id="b", max_depth=1, direction="incoming")
    
    node_ids = [node['node_id'] for node in nodes]
    assert "b" in node_ids  # Starting node
    assert "a" in node_ids  # Incoming neighbor
    assert "c" in node_ids  # Incoming neighbor
    
    graph.close()

