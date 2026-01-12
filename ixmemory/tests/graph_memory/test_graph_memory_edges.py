"""
Tests for GraphMemory edge operations.
"""

from ixmemory.graph_memory import GraphMemory


def test_add_edge():
    """Test adding an edge between nodes."""
    graph = GraphMemory()
    
    graph.add_node(node_id="person_1", node_type="Person")
    graph.add_node(node_id="company_1", node_type="Company")
    
    edge_id = graph.add_edge(
        source_node_id="person_1",
        target_node_id="company_1",
        relationship_type="works_at",
        properties={"start_date": "2020-01-01"},
    )
    
    assert edge_id is not None
    
    neighbors = graph.get_neighbors(node_id="person_1")
    assert len(neighbors) == 1
    assert neighbors[0]['node_id'] == "company_1"
    
    graph.close()


def test_add_edge_without_properties():
    """Test adding an edge without properties."""
    graph = GraphMemory()
    
    graph.add_node(node_id="person_1", node_type="Person")
    graph.add_node(node_id="person_2", node_type="Person")
    
    edge_id = graph.add_edge(
        source_node_id="person_1",
        target_node_id="person_2",
        relationship_type="knows",
    )
    
    assert edge_id is not None
    
    neighbors = graph.get_neighbors(node_id="person_1")
    assert len(neighbors) == 1
    
    graph.close()


def test_get_neighbors_outgoing():
    """Test getting outgoing neighbors."""
    graph = GraphMemory()
    
    graph.add_node(node_id="a", node_type="Node")
    graph.add_node(node_id="b", node_type="Node")
    graph.add_node(node_id="c", node_type="Node")
    
    graph.add_edge(source_node_id="a", target_node_id="b", relationship_type="connects")
    graph.add_edge(source_node_id="b", target_node_id="c", relationship_type="connects")
    
    neighbors = graph.get_neighbors(node_id="a", direction="outgoing")
    assert len(neighbors) == 1
    assert neighbors[0]['node_id'] == "b"
    
    neighbors = graph.get_neighbors(node_id="b", direction="outgoing")
    assert len(neighbors) == 1
    assert neighbors[0]['node_id'] == "c"
    
    graph.close()


def test_get_neighbors_incoming():
    """Test getting incoming neighbors."""
    graph = GraphMemory()
    
    graph.add_node(node_id="a", node_type="Node")
    graph.add_node(node_id="b", node_type="Node")
    
    graph.add_edge(source_node_id="a", target_node_id="b", relationship_type="connects")
    
    neighbors = graph.get_neighbors(node_id="b", direction="incoming")
    assert len(neighbors) == 1
    assert neighbors[0]['node_id'] == "a"
    
    graph.close()


def test_get_neighbors_filtered_by_relationship():
    """Test getting neighbors filtered by relationship type."""
    graph = GraphMemory()
    
    graph.add_node(node_id="person_1", node_type="Person")
    graph.add_node(node_id="company_1", node_type="Company")
    graph.add_node(node_id="person_2", node_type="Person")
    
    graph.add_edge(source_node_id="person_1", target_node_id="company_1", relationship_type="works_at")
    graph.add_edge(source_node_id="person_1", target_node_id="person_2", relationship_type="knows")
    
    neighbors = graph.get_neighbors(node_id="person_1", relationship_type="works_at")
    assert len(neighbors) == 1
    assert neighbors[0]['node_id'] == "company_1"
    
    neighbors = graph.get_neighbors(node_id="person_1", relationship_type="knows")
    assert len(neighbors) == 1
    assert neighbors[0]['node_id'] == "person_2"
    
    graph.close()


def test_delete_edge():
    """Test deleting an edge."""
    graph = GraphMemory()
    
    graph.add_node(node_id="person_1", node_type="Person")
    graph.add_node(node_id="company_1", node_type="Company")
    
    edge_id = graph.add_edge(
        source_node_id="person_1",
        target_node_id="company_1",
        relationship_type="works_at",
    )
    
    neighbors = graph.get_neighbors(node_id="person_1")
    assert len(neighbors) == 1
    
    graph.delete_edge(edge_id=edge_id)
    
    neighbors = graph.get_neighbors(node_id="person_1")
    assert len(neighbors) == 0
    
    graph.close()

