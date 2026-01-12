"""
Pytest fixtures for graph_memory tests.
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path

from tests.graph_memory.test_european_cities import (
    EUROPEAN_CITIES_NODES,
    EUROPEAN_CITIES_EDGES,
)


@pytest.fixture(scope="session")
def european_cities_db():
    """
    Create a temporary SQLite database with European cities graph data.
    
    This fixture is session-scoped, so the database is created once
    and shared across all tests that use it.
    
    Yields:
        sqlite3.Connection: Connection to the temporary database.
    """
    # Create a temporary file for the database
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as temp_file:
        db_path = Path(temp_file.name)
    
    # Build the database
    connection = sqlite3.connect(str(db_path))
    connection.execute("PRAGMA foreign_keys = ON;")
    
    cursor = connection.cursor()
    
    # Create tables matching the graph_memory schema
    cursor.execute("""
        CREATE TABLE nodes (
            node_id TEXT PRIMARY KEY,
            node_type TEXT,
            properties TEXT
        );
    """)
    
    cursor.execute("""
        CREATE TABLE edges (
            edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_node_id TEXT NOT NULL,
            target_node_id TEXT NOT NULL,
            relationship_type TEXT,
            properties TEXT,
            FOREIGN KEY (source_node_id) REFERENCES nodes(node_id),
            FOREIGN KEY (target_node_id) REFERENCES nodes(node_id)
        );
    """)
    
    # Create indexes for traversal performance
    cursor.execute("CREATE INDEX idx_edges_source ON edges(source_node_id);")
    cursor.execute("CREATE INDEX idx_edges_target ON edges(target_node_id);")
    
    # Insert nodes (mapping test data fields to schema fields)
    cursor.executemany(
        "INSERT INTO nodes(node_id, node_type, properties) VALUES (?, ?, ?);",
        [
            (
                node["id"],
                "city",  # All are cities
                f'{{"label": "{node["label"]}", "colour": "{node["colour"]}"}}',
            )
            for node in EUROPEAN_CITIES_NODES
        ],
    )
    
    # Insert edges
    cursor.executemany(
        "INSERT INTO edges(source_node_id, target_node_id, relationship_type, properties) VALUES (?, ?, ?, ?);",
        [
            (
                edge["source_id"],
                edge["target_id"],
                edge["relationship_type"],
                f'{{"colour": "{edge["colour"]}"}}',
            )
            for edge in EUROPEAN_CITIES_EDGES
        ],
    )
    
    connection.commit()
    
    yield connection
    
    # Cleanup
    connection.close()
    db_path.unlink(missing_ok=True)
