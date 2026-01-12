"""
Database initialization and management for GraphMemory.
"""

import sqlite3


def initialize_database(connection: sqlite3.Connection) -> None:
    """
    Create tables and indexes if they don't exist.
    
    Args:
        connection: SQLite database connection.
    """
    cursor = connection.cursor()
    
    # Nodes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nodes (
            node_id TEXT PRIMARY KEY,
            node_type TEXT,
            properties TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    
    # Edges table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS edges (
            edge_id TEXT PRIMARY KEY,
            source_node_id TEXT,
            target_node_id TEXT,
            relationship_type TEXT,
            properties TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (source_node_id) REFERENCES nodes(node_id) ON DELETE CASCADE,
            FOREIGN KEY (target_node_id) REFERENCES nodes(node_id) ON DELETE CASCADE
        )
    """)
    
    # Indexes for efficient queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_edges_source 
        ON edges(source_node_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_edges_target 
        ON edges(target_node_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_edges_relationship 
        ON edges(relationship_type)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_nodes_type 
        ON nodes(node_type)
    """)
    
    connection.commit()

