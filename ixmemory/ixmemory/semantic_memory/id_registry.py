"""
ID Registry for tracking all IDs across semantic memory tables.

Two tables:
- ids: When each unique ID was created (entity birth)
- id_tables: Which tables contain each ID (junction table)

This ensures ID uniqueness across the entire system and tracks
the history of when IDs were added to different tables.
"""

import uuid
import sqlite3
from typing import Any, Dict, List, Optional, Set

from ixutils import utc_now


# Valid table names that can be tracked
# Semantic memory: moments, numbers, texts
# Graph memory: graph_nodes
# Other memory: files, conversations
VALID_TABLE_NAMES = {
    "moments",
    "numbers", 
    "texts",
    "graph_nodes",
    "files",
    "conversations",
}


class IdRegistry:
    """
    Registry for tracking all IDs across semantic memory tables.
    
    Uses two tables:
    - ids: Stores each unique ID with its creation timestamp
    - id_tables: Junction table mapping IDs to tables they exist in
    
    Example:
        >>> registry = IdRegistry(connection)
        >>> 
        >>> # Create a new ID
        >>> alice_id = registry.create_id(prefix="alice")
        >>> 
        >>> # Add to tables
        >>> registry.add_to_table(id=alice_id, table_name="texts")
        >>> registry.add_to_table(id=alice_id, table_name="graph_nodes")
        >>> 
        >>> # Query
        >>> tables = registry.get_tables(id=alice_id)
        >>> # ["texts", "graph_nodes"]
    
    Args:
        connection: SQLite database connection.
    """
    
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
    
    def generate_id(self, prefix: Optional[str] = None) -> str:
        """
        Generate a unique ID string (does NOT register it).
        
        Uses UUID4 for guaranteed uniqueness. Optionally adds a prefix
        for human readability.
        
        Args:
            prefix: Optional prefix (e.g., "alice" produces "alice_a1b2c3d4").
        
        Returns:
            Unique ID string.
        """
        unique_part = uuid.uuid4().hex[:12]
        
        if prefix:
            return f"{prefix}_{unique_part}"
        return unique_part
    
    def create_id(self, prefix: Optional[str] = None) -> str:
        """
        Generate AND register a new unique ID.
        
        Args:
            prefix: Optional prefix for human readability.
        
        Returns:
            The newly created and registered ID.
        """
        new_id = self.generate_id(prefix=prefix)
        self.register(id=new_id)
        return new_id
    
    def exists(self, *, id: str) -> bool:
        """
        Check if an ID exists in the registry.
        
        Args:
            id: ID to check.
        
        Returns:
            True if ID exists, False otherwise.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT 1 FROM ids WHERE id = ?", (id,))
        return cursor.fetchone() is not None
    
    def register(self, *, id: str) -> Dict[str, Any]:
        """
        Register an ID in the registry (create the entity).
        
        If ID already exists, does nothing (idempotent).
        
        Args:
            id: ID to register.
        
        Returns:
            Dictionary with 'success', 'id', and 'created' (True if new).
        """
        if self.exists(id=id):
            return {'success': True, 'id': id, 'created': False}
        
        cursor = self.connection.cursor()
        now = utc_now()
        
        cursor.execute(
            "INSERT INTO ids (id, created_at) VALUES (?, ?)",
            (id, now)
        )
        self.connection.commit()
        
        return {'success': True, 'id': id, 'created': True}
    
    def add_to_table(self, *, id: str, table_name: str) -> Dict[str, Any]:
        """
        Add an ID to a table (record that this ID exists in this table).
        
        If ID doesn't exist yet, registers it first.
        If already in this table, does nothing (idempotent).
        
        Args:
            id: ID to add.
            table_name: Table name (moments, numbers, texts, graph_nodes,
                       has_members, is_member).
        
        Returns:
            Dictionary with 'success' and 'added' (True if newly added).
        
        Raises:
            ValueError: If table_name is invalid.
        """
        if table_name not in VALID_TABLE_NAMES:
            raise ValueError(
                f"Invalid table_name: '{table_name}'. "
                f"Must be one of: {VALID_TABLE_NAMES}"
            )
        
        # Ensure ID exists
        self.register(id=id)
        
        cursor = self.connection.cursor()
        
        # Check if already in this table
        cursor.execute(
            "SELECT 1 FROM id_tables WHERE id = ? AND table_name = ?",
            (id, table_name)
        )
        if cursor.fetchone():
            return {'success': True, 'id': id, 'table_name': table_name, 'added': False}
        
        # Add to table
        now = utc_now()
        cursor.execute(
            "INSERT INTO id_tables (id, table_name, added_at) VALUES (?, ?, ?)",
            (id, table_name, now)
        )
        self.connection.commit()
        
        return {'success': True, 'id': id, 'table_name': table_name, 'added': True}
    
    def remove_from_table(self, *, id: str, table_name: str) -> bool:
        """
        Remove an ID from a table.
        
        Does NOT delete the ID itself - just removes the table association.
        
        Args:
            id: ID to remove.
            table_name: Table to remove from.
        
        Returns:
            True if removed, False if wasn't in that table.
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "DELETE FROM id_tables WHERE id = ? AND table_name = ?",
            (id, table_name)
        )
        self.connection.commit()
        
        return cursor.rowcount > 0
    
    def get_tables(self, *, id: str) -> List[str]:
        """
        Get all tables that contain an ID.
        
        Args:
            id: ID to look up.
        
        Returns:
            List of table names, empty if ID not found or not in any table.
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT table_name FROM id_tables WHERE id = ? ORDER BY added_at",
            (id,)
        )
        return [row[0] for row in cursor.fetchall()]
    
    def get(self, *, id: str) -> Optional[Dict[str, Any]]:
        """
        Get full info for an ID.
        
        Args:
            id: ID to look up.
        
        Returns:
            Dictionary with id, created_at, and tables list. None if not found.
        """
        cursor = self.connection.cursor()
        
        # Get creation info
        cursor.execute("SELECT id, created_at FROM ids WHERE id = ?", (id,))
        row = cursor.fetchone()
        if not row:
            return None
        
        # Get tables
        tables = self.get_tables(id=id)
        
        return {
            'id': row[0],
            'created_at': row[1],
            'tables': tables,
        }
    
    def delete(self, *, id: str) -> bool:
        """
        Delete an ID completely from the registry.
        
        Removes the ID and all its table associations.
        
        Args:
            id: ID to delete.
        
        Returns:
            True if deleted, False if not found.
        """
        cursor = self.connection.cursor()
        
        # Delete from id_tables first (foreign key)
        cursor.execute("DELETE FROM id_tables WHERE id = ?", (id,))
        
        # Delete from ids
        cursor.execute("DELETE FROM ids WHERE id = ?", (id,))
        self.connection.commit()
        
        return cursor.rowcount > 0
    
    def is_in_table(self, *, id: str, table_name: str) -> bool:
        """
        Check if an ID is in a specific table.
        
        Args:
            id: ID to check.
            table_name: Table to check.
        
        Returns:
            True if ID is in the table, False otherwise.
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT 1 FROM id_tables WHERE id = ? AND table_name = ?",
            (id, table_name)
        )
        return cursor.fetchone() is not None
    
    def find_by_table(
        self,
        *,
        table_name: str,
        limit: Optional[int] = None,
    ) -> List[str]:
        """
        Find all IDs in a specific table.
        
        Args:
            table_name: Table to search.
            limit: Maximum number of results.
        
        Returns:
            List of IDs in the table.
        """
        cursor = self.connection.cursor()
        
        query = "SELECT id FROM id_tables WHERE table_name = ? ORDER BY added_at DESC"
        params: List[Any] = [table_name]
        
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        return [row[0] for row in cursor.fetchall()]
    
    def find_by_tables(
        self,
        *,
        table_names: List[str],
        match_all: bool = True,
    ) -> List[str]:
        """
        Find IDs that are in specified tables.
        
        Args:
            table_names: List of table names to search.
            match_all: If True, ID must be in ALL tables. If False, any table.
        
        Returns:
            List of matching IDs.
        """
        if not table_names:
            return []
        
        cursor = self.connection.cursor()
        
        if match_all:
            # ID must be in all specified tables
            placeholders = ",".join("?" for _ in table_names)
            cursor.execute(f"""
                SELECT id FROM id_tables
                WHERE table_name IN ({placeholders})
                GROUP BY id
                HAVING COUNT(DISTINCT table_name) = ?
            """, (*table_names, len(table_names)))
        else:
            # ID can be in any of the specified tables
            placeholders = ",".join("?" for _ in table_names)
            cursor.execute(f"""
                SELECT DISTINCT id FROM id_tables
                WHERE table_name IN ({placeholders})
            """, table_names)
        
        return [row[0] for row in cursor.fetchall()]
    
    def find_in_multiple_tables(self) -> List[Dict[str, Any]]:
        """
        Find IDs that exist in more than one table.
        
        Returns:
            List of dicts with 'id' and 'tables' for IDs in multiple tables.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT id FROM id_tables
            GROUP BY id
            HAVING COUNT(DISTINCT table_name) > 1
        """)
        
        results = []
        for row in cursor.fetchall():
            id = row[0]
            tables = self.get_tables(id=id)
            results.append({'id': id, 'tables': tables})
        
        return results
    
    def list_all(
        self,
        *,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        List all registered IDs.
        
        Args:
            limit: Maximum number of results.
            offset: Number of results to skip.
        
        Returns:
            List of dicts with 'id', 'created_at', and 'tables'.
        """
        cursor = self.connection.cursor()
        
        query = "SELECT id, created_at FROM ids ORDER BY created_at DESC"
        params: List[Any] = []
        
        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            id = row[0]
            tables = self.get_tables(id=id)
            results.append({
                'id': id,
                'created_at': row[1],
                'tables': tables,
            })
        
        return results
    
    def count(self) -> int:
        """
        Get total count of registered IDs.
        
        Returns:
            Number of IDs in the registry.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM ids")
        return cursor.fetchone()[0]
    
    def count_by_table(self, *, table_name: str) -> int:
        """
        Get count of IDs in a specific table.
        
        Args:
            table_name: Table to count.
        
        Returns:
            Number of IDs in the table.
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM id_tables WHERE table_name = ?",
            (table_name,)
        )
        return cursor.fetchone()[0]
