"""
Tests for GraphMemory node operations.
"""

from ixmemory.graph_memory import GraphMemory


def test_add_node():
    """Test adding a node to the graph."""
    graph = GraphMemory()
    
    graph.add_node(
        node_id="person_1",
        node_type="Person",
        properties={"name": "Alice", "age": 30},
    )
    
    node = graph.get_node(node_id="person_1")
    assert node is not None
    assert node['node_id'] == "person_1"
    assert node['node_type'] == "Person"
    assert node['properties']['name'] == "Alice"
    assert node['properties']['age'] == 30
    
    graph.close()


def test_get_node_not_found():
    """Test getting a node that doesn't exist."""
    graph = GraphMemory()
    
    node = graph.get_node(node_id="nonexistent")
    assert node is None
    
    graph.close()


def test_add_node_without_properties():
    """Test adding a node without properties."""
    graph = GraphMemory()
    
    graph.add_node(
        node_id="company_1",
        node_type="Company",
    )
    
    node = graph.get_node(node_id="company_1")
    assert node is not None
    assert node['node_id'] == "company_1"
    assert node['node_type'] == "Company"
    assert node['properties'] == {}
    
    graph.close()


def test_delete_node():
    """Test deleting a node."""
    graph = GraphMemory()
    
    graph.add_node(
        node_id="person_1",
        node_type="Person",
    )
    
    node = graph.get_node(node_id="person_1")
    assert node is not None
    
    graph.delete_node(node_id="person_1")
    
    node = graph.get_node(node_id="person_1")
    assert node is None
    
    graph.close()


def test_query_nodes_by_label():
    """Test querying nodes by label."""
    graph = GraphMemory()
    
    graph.add_node(node_id="person_1", node_type="Person", properties={"name": "Alice"})
    graph.add_node(node_id="person_2", node_type="Person", properties={"name": "Bob"})
    graph.add_node(node_id="company_1", node_type="Company", properties={"name": "TechCorp"})
    
    persons = graph.query_nodes(node_type="Person")
    assert len(persons) == 2
    assert all(node['node_type'] == "Person" for node in persons)
    
    companies = graph.query_nodes(node_type="Company")
    assert len(companies) == 1
    assert companies[0]['node_type'] == "Company"
    
    graph.close()


def test_query_nodes_by_properties():
    """Test querying nodes by properties."""
    graph = GraphMemory()
    
    graph.add_node(node_id="person_1", node_type="Person", properties={"name": "Alice", "age": 30})
    graph.add_node(node_id="person_2", node_type="Person", properties={"name": "Bob", "age": 25})
    graph.add_node(node_id="person_3", node_type="Person", properties={"name": "Charlie", "age": 30})
    
    results = graph.query_nodes(properties_filter={"age": 30})
    assert len(results) == 2
    assert all(node['properties']['age'] == 30 for node in results)
    
    results = graph.query_nodes(properties_filter={"name": "Alice"})
    assert len(results) == 1
    assert results[0]['properties']['name'] == "Alice"
    
    graph.close()

