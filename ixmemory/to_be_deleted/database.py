"""
Database initialization and management for SemanticMemory.
"""

import sqlite3


def initialize_database(connection: sqlite3.Connection) -> None:
    """
    Create tables and indexes if they don't exist.
    
    Args:
        connection: SQLite database connection.
    """
    cursor = connection.cursor()
    
    # Record types lookup table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS record_types (
            record_type_id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        )
    """)
    
    # Insert default record types if they don't exist
    default_types = [
        ("entity", "Entity", "Concrete things like people, companies, places, objects"),
        ("concept", "Concept", "Abstract ideas and concepts"),
        ("event", "Event", "Things that happened or will happen"),
        ("document", "Document", "Text documents, articles, files"),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO record_types (record_type_id, name, description)
        VALUES (?, ?, ?)
    """, default_types)
    
    # Records table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id TEXT PRIMARY KEY,
            record_type_id TEXT NOT NULL,
            name TEXT,
            description TEXT,
            tags TEXT,
            metadata TEXT,
            embedding BLOB,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (record_type_id) REFERENCES record_types(record_type_id)
        )
    """)
    
    # Indexes
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_records_name 
        ON records(name)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_records_record_type 
        ON records(record_type_id)
    """)
    
    # Facts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facts (
            fact_id TEXT PRIMARY KEY,
            text TEXT,
            relationship_type TEXT,
            metadata TEXT,
            embedding BLOB,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    
    # Fact-record associations with roles
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fact_records (
            fact_id TEXT,
            record_id TEXT,
            role TEXT,
            PRIMARY KEY (fact_id, record_id, role),
            FOREIGN KEY (fact_id) REFERENCES facts(fact_id) ON DELETE CASCADE,
            FOREIGN KEY (record_id) REFERENCES records(id) ON DELETE CASCADE
        )
    """)
    
    # Create indexes for efficient queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_fact_records_record 
        ON fact_records(record_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_fact_records_fact 
        ON fact_records(fact_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_facts_type 
        ON facts(relationship_type)
    """)
    
    connection.commit()

