"""
Text memory for storing and searching text records with embeddings.
"""

from typing import Any, Dict, List, Optional
import json
import pickle
import sqlite3

from ixutils import utc_now


class TextMemory:
    """
    Memory for storing and searching text records with embeddings.
    
    Supports:
    - CRUD operations
    - Semantic search via embeddings
    - Tag-based filtering
    - Metadata queries
    
    Args:
        connection: SQLite database connection.
        auto_embed: Whether to automatically generate embeddings when saving.
        embedding_model: Name of the sentence-transformers model to use.
    """
    
    def __init__(
        self,
        connection: sqlite3.Connection,
        auto_embed: bool = True,
        embedding_model: str = 'all-MiniLM-L6-v2',
    ):
        self.connection = connection
        self.auto_embed = auto_embed
        self.embedding_model = embedding_model
        self._model = None  # Lazy loaded
    
    def _get_model(self):
        """Lazy load the embedding model."""
        if self._model is None:
            # Lazy import for performance (heavy library/conditional feature)
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.embedding_model)
        return self._model
    
    def _generate_embedding(self, text: str) -> Optional[bytes]:
        """Generate embedding for text."""
        try:
            model = self._get_model()
            embedding = model.encode(text)
            return pickle.dumps(embedding)
        except Exception:
            return None
    
    def _load_embedding(self, data: Optional[bytes]) -> Optional[List[float]]:
        """Load embedding from bytes."""
        if data is None:
            return None
        try:
            return pickle.loads(data).tolist()
        except Exception:
            return None
    
    def save(
        self,
        *,
        id: str,
        content: str,
        record_type_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        """
        Save a text record.
        
        Args:
            id: Unique identifier for the record.
            content: The text content.
            record_type_id: Type of record (e.g., "entity", "concept").
            tags: Optional list of tags.
            metadata: Optional metadata dictionary.
            embedding: Optional embedding bytes. If None and auto_embed is True,
                      generates one automatically.
        
        Returns:
            Dictionary with 'success' and saved data.
        """
        cursor = self.connection.cursor()
        now = utc_now()
        
        # Auto-generate embedding if needed
        if embedding is None and self.auto_embed:
            embedding = self._generate_embedding(content)
        
        tags_json = json.dumps(tags or [])
        metadata_json = json.dumps(metadata or {})
        
        cursor.execute("""
            INSERT OR REPLACE INTO texts 
            (id, record_type_id, content, tags, metadata, embedding, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?,
                COALESCE((SELECT created_at FROM texts WHERE id = ?), ?),
                ?)
        """, (id, record_type_id, content, tags_json, metadata_json, embedding, id, now, now))
        
        self.connection.commit()
        
        return {
            'success': True,
            'id': id,
            'content': content,
            'record_type_id': record_type_id,
            'tags': tags or [],
            'metadata': metadata or {},
        }
    
    def load(self, *, id: str) -> Optional[Dict[str, Any]]:
        """
        Load a text record by ID.
        
        Args:
            id: Record ID.
        
        Returns:
            Dictionary with record data, or None if not found.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT id, record_type_id, content, tags, metadata, embedding, created_at, updated_at
            FROM texts WHERE id = ?
        """, (id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return self._row_to_dict(row)
    
    def _row_to_dict(self, row: tuple) -> Dict[str, Any]:
        """Convert database row to dictionary."""
        tags = row[3]
        if isinstance(tags, str):
            tags = json.loads(tags)
        
        metadata = row[4]
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        
        return {
            'id': row[0],
            'record_type_id': row[1],
            'content': row[2],
            'tags': tags or [],
            'metadata': metadata or {},
            'embedding': self._load_embedding(row[5]),
            'created_at': row[6],
            'updated_at': row[7],
        }
    
    def delete(self, *, id: str) -> bool:
        """
        Delete a text record by ID.
        
        Args:
            id: Record ID.
        
        Returns:
            True if deleted, False if not found.
        """
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM texts WHERE id = ?", (id,))
        self.connection.commit()
        
        return cursor.rowcount > 0
    
    def list(
        self,
        *,
        record_type_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        List text records.
        
        Args:
            record_type_id: Optional filter by record type.
            limit: Maximum number of results.
            offset: Number of results to skip.
        
        Returns:
            List of record dictionaries.
        """
        cursor = self.connection.cursor()
        
        query = """
            SELECT id, record_type_id, content, tags, metadata, embedding, created_at, updated_at
            FROM texts
        """
        params: List[Any] = []
        
        if record_type_id is not None:
            query += " WHERE record_type_id = ?"
            params.append(record_type_id)
        
        query += " ORDER BY created_at DESC"
        
        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        
        cursor.execute(query, params)
        
        return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def search(
        self,
        *,
        query: str,
        limit: int = 10,
        record_type_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search text records by semantic similarity.
        
        Args:
            query: Search query text.
            limit: Maximum number of results.
            record_type_id: Optional filter by record type.
            tags: Optional filter by tags (records must have all specified tags).
        
        Returns:
            List of records sorted by similarity (most similar first).
        """
        # Generate query embedding
        query_embedding = self._generate_embedding(query)
        if query_embedding is None:
            return []
        
        query_vector = pickle.loads(query_embedding)
        
        # Fetch candidates
        cursor = self.connection.cursor()
        
        sql = """
            SELECT id, record_type_id, content, tags, metadata, embedding, created_at, updated_at
            FROM texts
            WHERE embedding IS NOT NULL
        """
        params: List[Any] = []
        
        if record_type_id is not None:
            sql += " AND record_type_id = ?"
            params.append(record_type_id)
        
        cursor.execute(sql, params)
        
        # Compute similarities
        results = []
        for row in cursor.fetchall():
            record = self._row_to_dict(row)
            
            # Filter by tags
            if tags:
                record_tags = set(record.get('tags', []))
                if not all(t in record_tags for t in tags):
                    continue
            
            # Compute cosine similarity
            if row[5] is not None:
                try:
                    record_vector = pickle.loads(row[5])
                    similarity = self._cosine_similarity(query_vector, record_vector)
                    record['similarity'] = similarity
                    results.append(record)
                except Exception:
                    pass
        
        # Sort by similarity (descending)
        results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        
        return results[:limit]
    
    def _cosine_similarity(self, vec1, vec2) -> float:
        """Compute cosine similarity between two vectors."""
        import numpy as np
        
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def find_by_tags(
        self,
        *,
        tags: List[str],
        match_all: bool = True,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Find records by tags.
        
        Args:
            tags: Tags to search for.
            match_all: If True, records must have all tags. If False, any tag matches.
            limit: Maximum number of results.
        
        Returns:
            List of matching records.
        """
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT id, record_type_id, content, tags, metadata, embedding, created_at, updated_at
            FROM texts
        """)
        
        results = []
        for row in cursor.fetchall():
            record = self._row_to_dict(row)
            record_tags = set(record.get('tags', []))
            
            if match_all:
                if all(t in record_tags for t in tags):
                    results.append(record)
            else:
                if any(t in record_tags for t in tags):
                    results.append(record)
        
        if limit is not None:
            results = results[:limit]
        
        return results
    
    def find_by_metadata(
        self,
        *,
        key: str,
        value: Any,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Find records by metadata key-value pair.
        
        Args:
            key: Metadata key to search.
            value: Value to match.
            limit: Maximum number of results.
        
        Returns:
            List of matching records.
        """
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT id, record_type_id, content, tags, metadata, embedding, created_at, updated_at
            FROM texts
        """)
        
        results = []
        for row in cursor.fetchall():
            record = self._row_to_dict(row)
            metadata = record.get('metadata', {})
            
            if metadata.get(key) == value:
                results.append(record)
        
        if limit is not None:
            results = results[:limit]
        
        return results
    
    # =========================================================================
    # Set/Member Operations
    # =========================================================================
    # A text can act as a "set" by having members attached to it.
    # Members are references to records in other tables (moments, numbers, texts).
    # This allows unified semantic search across both regular texts and sets.
    
    VALID_MEMBER_TABLES = {"moments", "numbers", "texts"}
    
    def add_member(
        self,
        *,
        text_id: str,
        member_id: str,
        member_table: str,
    ) -> Dict[str, Any]:
        """
        Add a member to a text (making it a set).
        
        A set is a text that has members attached. Members are references
        to records in other tables (moments, numbers, texts).
        
        Example:
            # Create a set for "Idin's toys"
            text_memory.save(
                id="idin_toys",
                record_type_id="toy_collection",
                content="Idin's favourite toys from childhood",
            )
            # Add members
            text_memory.add_member(
                text_id="idin_toys",
                member_id="teddy_bear",
                member_table="texts",
            )
        
        Args:
            text_id: ID of the text/set to add member to.
            member_id: ID of the member record.
            member_table: Table where member lives ("moments", "numbers", "texts").
        
        Returns:
            Dictionary with 'success' and member info.
        
        Raises:
            ValueError: If text_id doesn't exist or member_table is invalid.
        """
        # Validate member_table
        if member_table not in self.VALID_MEMBER_TABLES:
            raise ValueError(
                f"Invalid member_table: '{member_table}'. "
                f"Must be one of: {self.VALID_MEMBER_TABLES}"
            )
        
        cursor = self.connection.cursor()
        
        # Verify text exists
        cursor.execute("SELECT id FROM texts WHERE id = ?", (text_id,))
        if not cursor.fetchone():
            raise ValueError(f"Text with id '{text_id}' not found")
        
        now = utc_now()
        
        cursor.execute("""
            INSERT OR REPLACE INTO text_members (text_id, member_id, member_table, created_at)
            VALUES (?, ?, ?, ?)
        """, (text_id, member_id, member_table, now))
        
        self.connection.commit()
        
        return {
            'success': True,
            'text_id': text_id,
            'member_id': member_id,
            'member_table': member_table,
        }
    
    def remove_member(
        self,
        *,
        text_id: str,
        member_id: str,
        member_table: str,
    ) -> bool:
        """
        Remove a member from a text/set.
        
        Args:
            text_id: ID of the text/set.
            member_id: ID of the member to remove.
            member_table: Table where member lives.
        
        Returns:
            True if removed, False if not found.
        """
        cursor = self.connection.cursor()
        
        cursor.execute("""
            DELETE FROM text_members
            WHERE text_id = ? AND member_id = ? AND member_table = ?
        """, (text_id, member_id, member_table))
        
        self.connection.commit()
        
        return cursor.rowcount > 0
    
    def get_members(
        self,
        *,
        text_id: str,
        member_table: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all members of a text/set.
        
        Args:
            text_id: ID of the text/set.
            member_table: Optional filter by member table.
        
        Returns:
            List of member references (not resolved records).
        """
        cursor = self.connection.cursor()
        
        query = """
            SELECT text_id, member_id, member_table, created_at
            FROM text_members
            WHERE text_id = ?
        """
        params: List[Any] = [text_id]
        
        if member_table is not None:
            query += " AND member_table = ?"
            params.append(member_table)
        
        query += " ORDER BY created_at"
        
        cursor.execute(query, params)
        
        return [
            {
                'text_id': row[0],
                'member_id': row[1],
                'member_table': row[2],
                'created_at': row[3],
            }
            for row in cursor.fetchall()
        ]
    
    def clear_members(self, *, text_id: str) -> int:
        """
        Remove all members from a text/set.
        
        Args:
            text_id: ID of the text/set.
        
        Returns:
            Number of members removed.
        """
        cursor = self.connection.cursor()
        
        cursor.execute("DELETE FROM text_members WHERE text_id = ?", (text_id,))
        self.connection.commit()
        
        return cursor.rowcount
    
    def find_sets_containing(
        self,
        *,
        member_id: str,
        member_table: str,
    ) -> List[Dict[str, Any]]:
        """
        Find all texts/sets that contain a specific member.
        
        Args:
            member_id: ID of the member to search for.
            member_table: Table where member lives.
        
        Returns:
            List of text records that contain the member.
        """
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT t.id, t.record_type_id, t.content, t.tags, t.metadata, 
                   t.embedding, t.created_at, t.updated_at
            FROM texts t
            INNER JOIN text_members tm ON t.id = tm.text_id
            WHERE tm.member_id = ? AND tm.member_table = ?
        """, (member_id, member_table))
        
        return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def has_members(self, *, text_id: str) -> bool:
        """
        Check if a text has any members (is a set).
        
        Args:
            text_id: ID of the text.
        
        Returns:
            True if the text has members, False otherwise.
        """
        cursor = self.connection.cursor()
        
        cursor.execute(
            "SELECT 1 FROM text_members WHERE text_id = ? LIMIT 1",
            (text_id,)
        )
        
        return cursor.fetchone() is not None
    
    def count_members(self, *, text_id: str) -> int:
        """
        Count the number of members in a text/set.
        
        Args:
            text_id: ID of the text.
        
        Returns:
            Number of members.
        """
        cursor = self.connection.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM text_members WHERE text_id = ?",
            (text_id,)
        )
        
        return cursor.fetchone()[0]
