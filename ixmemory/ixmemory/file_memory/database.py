"""
Database initialization and management for FileMemory.
"""

import sqlite3


def initialize_database(connection: sqlite3.Connection) -> None:
    """
    Create tables and indexes if they don't exist.
    
    Args:
        connection: SQLite database connection.
    """
    cursor = connection.cursor()
    
    # Files table (handles all file types: text, binary, media, etc.)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id TEXT PRIMARY KEY,
            summary_record_id TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT NOT NULL,
            metadata TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (summary_record_id) REFERENCES records(id) ON DELETE CASCADE
        )
    """)
    
    # Indexes for efficient queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_files_summary_record 
        ON files(summary_record_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_files_file_path 
        ON files(file_path)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_files_file_type 
        ON files(file_type)
    """)
    
    connection.commit()

