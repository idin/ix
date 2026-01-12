"""
Database schema and initialization for semantic memory.
"""

from typing import Any


def initialize_database(connection: Any) -> None:
    """
    Initialize the semantic memory database schema.
    
    Creates tables for:
    - ids: Tracks when each unique ID was created (entity birth)
    - id_tables: Junction table tracking which tables contain each ID
    - moments: Temporal values (dates, times, partial dates)
    - numbers: Numeric values
    - texts: Text records with embeddings
    - text_members: Members of sets (texts can have members from any table)
    
    Args:
        connection: SQLite database connection.
    """
    cursor = connection.cursor()
    
    # IDs table - tracks when each unique ID was created (entity birth)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ids (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL
        )
    """)
    
    # ID tables junction - tracks which tables contain each ID
    # table_name can be: moments, numbers, texts, graph_nodes, has_members, is_member
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS id_tables (
            id TEXT NOT NULL,
            table_name TEXT NOT NULL,
            added_at TEXT NOT NULL,
            PRIMARY KEY (id, table_name),
            FOREIGN KEY (id) REFERENCES ids(id) ON DELETE CASCADE
        )
    """)
    
    # Indexes for ID queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_id_tables_table_name ON id_tables(table_name)")
    
    # Moments table - temporal values with optional components
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS moments (
            id TEXT PRIMARY KEY,
            record_type TEXT,
            year INTEGER,
            month INTEGER,
            day INTEGER,
            hour INTEGER,
            minute INTEGER,
            second INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    # Indexes for moment queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_moments_year ON moments(year)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_moments_month ON moments(month)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_moments_day ON moments(day)")
    
    # Numbers table - numeric values
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS numbers (
            id TEXT PRIMARY KEY,
            value REAL NOT NULL,
            number_type TEXT NOT NULL,
            record_type TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    # Index for numeric proximity queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_numbers_value ON numbers(value)")
    
    # Texts table - text records with embeddings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS texts (
            id TEXT PRIMARY KEY,
            record_type_id TEXT,
            content TEXT NOT NULL,
            tags TEXT,
            metadata TEXT,
            embedding BLOB,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    # Indexes for text queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_texts_record_type_id ON texts(record_type_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_texts_created_at ON texts(created_at)")
    
    # Text members table - for sets (texts that contain references to other records)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS text_members (
            text_id TEXT NOT NULL,
            member_id TEXT NOT NULL,
            member_table TEXT NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY (text_id, member_id, member_table),
            FOREIGN KEY (text_id) REFERENCES texts(id) ON DELETE CASCADE
        )
    """)
    
    # Indexes for member queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_text_members_text_id ON text_members(text_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_text_members_member ON text_members(member_id, member_table)")
    
    connection.commit()
