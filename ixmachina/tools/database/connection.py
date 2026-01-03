"""
Database connection management for SQLite.
"""

from typing import Optional
import sqlite3
import os


class DatabaseConnection:
    """
    Manages SQLite database connection and provides connection context.
    
    Args:
        database_path: Path to SQLite database file. If None, uses in-memory database.
    """
    
    def __init__(self, database_path: Optional[str] = None):
        """
        Initialize database connection.
        
        Args:
            database_path: Path to SQLite database file. If None, uses in-memory database.
        """
        self.database_path = database_path or ":memory:"
        self._connection: Optional[sqlite3.Connection] = None
        self._connect()
    
    def _connect(self) -> None:
        """Create or open database connection."""
        if self.database_path != ":memory:":
            # Create parent directory if it doesn't exist
            parent_dir = os.path.dirname(self.database_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
        
        self._connection = sqlite3.connect(self.database_path)
        self._connection.row_factory = sqlite3.Row  # Access columns by name
    
    @property
    def connection(self) -> sqlite3.Connection:
        """
        Get the database connection.
        
        Returns:
            SQLite connection object.
        """
        if self._connection is None:
            self._connect()
        return self._connection
    
    def close(self) -> None:
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def commit(self) -> None:
        """Commit pending transactions."""
        if self._connection:
            self._connection.commit()
    
    def rollback(self) -> None:
        """Rollback pending transactions."""
        if self._connection:
            self._connection.rollback()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()

