"""
Semantic memory with SQLite backend for objects and facts.
"""

from typing import Any, Optional, Dict, List

from .record import Record, ValueType
from .embeddings import EmbeddingGenerator
from .database import initialize_database
from .date_utils import parse_partial_date_with_granularity
from .similarity import find_similar_text_records, find_similar_number_records, find_similar_date_records
from .storage import save_record, load_record, delete_record, list_records, find_records_by_name
from .facts import save_fact, load_fact, delete_fact
from .queries import find_facts_by_object, find_records_by_fact, find_facts_by_type, find_records_by_role
from ixutils import create_database_connection


class SemanticMemory:
    """
    Storage system for records and facts with relationships.
    
    Uses SQLite for persistent storage with support for:
    - Record storage with metadata and embeddings
    - Fact-based relationships with roles (n-ary relationships)
    - Graph traversal to find related objects
    - Semantic search using embeddings
    
    Args:
        database_path: Path to SQLite database file. If None, uses in-memory database.
        auto_embed: Whether to automatically generate embeddings when saving objects/facts.
        embedding_generator: Custom embedding generator. If None, uses default.
    """
    
    def __init__(
        self,
        database_path: Optional[str] = None,
        auto_embed: bool = True,
        embedding_generator: Optional[EmbeddingGenerator] = None,
    ):
        self.database_path = database_path or ':memory:'
        self.auto_embed = auto_embed
        self.embedding_generator = embedding_generator
        
        # If auto_embed is True but no generator provided, create one
        if self.auto_embed and self.embedding_generator is None:
            self.embedding_generator = EmbeddingGenerator()
        
        self.connection = create_database_connection(
            database_path=self.database_path,
            initialize_tables=initialize_database,
        )
    
    # ============================================================================
    # Record operations
    # ============================================================================
    
    def save_record(
        self,
        name: str,
        value: Any,
        description: str = "",
        id: Optional[str] = None,
        value_type: ValueType = "text",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[list] = None,
        name_embedding: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Save a record to the store.
        
        If auto_embed is enabled and embeddings are not provided, they will be
        generated automatically for text records:
        - Primary embedding: name + description combined
        - Name embedding: name only (if name is not empty)
        
        For number and date records, embeddings are not used; similarity is based
        on distance.
        
        Args:
            name: Name for the record (not necessarily unique).
            value: The value to store.
            description: Human-readable description of the record.
            id: Optional universal identifier (auto-generated if not provided).
                This ID can be used across all memory systems.
            value_type: Type of value. Must be "text", "number", or "date". Defaults to "text".
            tags: Optional list of tags.
            metadata: Optional metadata dictionary.
            embedding: Optional primary embedding vector (name + description).
            name_embedding: Optional name-only embedding vector.
            
        Returns:
            Dictionary with success status and id.
        """
        return save_record(
            connection=self.connection,
            name=name,
            value=value,
            description=description,
            id=id,
            value_type=value_type,
            tags=tags,
            metadata=metadata,
            embedding=embedding,
            name_embedding=name_embedding,
            auto_embed=self.auto_embed,
            embedding_generator=self.embedding_generator,
        )
    
    def load_record(self, id: str) -> Dict[str, Any]:
        """
        Load a record from the store by ID.
        
        Args:
            id: Universal ID of the record to load.
            
        Returns:
            Dictionary with success status and record data.
        """
        return load_record(
            connection=self.connection,
            id=id,
        )
    
    def delete_record(self, id: str) -> Dict[str, Any]:
        """
        Delete a record from the store.
        
        Args:
            id: Universal ID of the record to delete.
            
        Returns:
            Dictionary with success status.
        """
        return delete_record(
            connection=self.connection,
            id=id,
        )
    
    def list_records(self) -> Dict[str, Any]:
        """
        List all records in the store with basic info.
        
        Returns:
            Dictionary with success status and list of records (id, name, description, type).
        """
        return list_records(connection=self.connection)
    
    def find_records_by_name(self, name: str) -> Dict[str, Any]:
        """
        Find all records with a specific name.
        
        Args:
            name: Name to search for.
            
        Returns:
            Dictionary with success status and list of matching records.
        """
        return find_records_by_name(
            connection=self.connection,
            name=name,
        )
    
    # ============================================================================
    # Fact operations
    # ============================================================================
    
    def save_fact(
        self,
        text: str,
        relationship_type: str,
        objects: List[Dict[str, str]],
        id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Save a fact to the store.
        
        If auto_embed is enabled and embedding is not provided, it will be
        generated automatically from the fact text.
        
        Args:
            text: Natural language statement.
            relationship_type: Type of relationship.
            objects: List of {"id": str, "role": str} dictionaries.
            id: Optional unique identifier (auto-generated if not provided).
                This ID can be used across all memory systems.
            metadata: Optional metadata dictionary.
            embedding: Optional embedding vector.
            
        Returns:
            Dictionary with success status and id.
        """
        return save_fact(
            connection=self.connection,
            text=text,
            relationship_type=relationship_type,
            objects=objects,
            id=id,
            metadata=metadata,
            embedding=embedding,
            auto_embed=self.auto_embed,
            embedding_generator=self.embedding_generator,
        )
    
    def load_fact(self, id: str) -> Dict[str, Any]:
        """
        Load a fact from the store by ID.
        
        Args:
            id: Universal ID of the fact to load.
            
        Returns:
            Dictionary with success status and fact data.
        """
        return load_fact(
            connection=self.connection,
            id=id,
        )
    
    def delete_fact(self, id: str) -> Dict[str, Any]:
        """
        Delete a fact from the store.
        
        Args:
            id: Universal ID of the fact to delete.
            
        Returns:
            Dictionary with success status.
        """
        return delete_fact(
            connection=self.connection,
            id=id,
        )
    
    # ============================================================================
    # Query operations
    # ============================================================================
    
    def find_facts_by_object(
        self,
        id: str,
        role: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Find all facts involving a specific record (by universal ID).
        
        Args:
            id: Universal ID of the record.
            role: Optional role filter.
            
        Returns:
            Dictionary with success status and list of facts.
        """
        return find_facts_by_object(
            connection=self.connection,
            id=id,
            role=role,
        )
    
    def find_records_by_fact(
        self,
        id: str,
        role: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Find all records in a specific fact.
        
        Args:
            id: Universal ID of the fact.
            role: Optional role filter.
            
        Returns:
            Dictionary with success status and list of records with their info.
        """
        return find_records_by_fact(
            connection=self.connection,
            id=id,
            role=role,
        )
    
    def find_facts_by_type(
        self,
        relationship_type: str,
    ) -> Dict[str, Any]:
        """
        Find all facts of a specific type.
        
        Args:
            relationship_type: Type of relationship to find.
            
        Returns:
            Dictionary with success status and list of facts.
        """
        return find_facts_by_type(
            connection=self.connection,
            relationship_type=relationship_type,
        )
    
    def find_records_by_role(
        self,
        relationship_type: str,
        role: str,
    ) -> Dict[str, Any]:
        """
        Find all records with a specific role in a relationship type.
        
        Example: Find all "employers" in "employment" relationships.
        
        Args:
            relationship_type: Type of relationship.
            role: Role to filter by.
            
        Returns:
            Dictionary with success status and list of records with their info.
        """
        return find_records_by_role(
            connection=self.connection,
            relationship_type=relationship_type,
            role=role,
        )
    
    # ============================================================================
    # Semantic search
    # ============================================================================
    
    def find_similar_by_query(
        self,
        query_value: Any,
        value_type: ValueType = 'text',
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Find objects similar to a query value (without saving it first).
        
        Args:
            query_value: The value to search for (text, number, or date string).
            value_type: Type of value ('text', 'number', 'date').
            limit: Maximum number of similar records to return.
            
        Returns:
            Dictionary with keys:
            - success: Whether the operation succeeded.
            - query_value: The original query value.
            - similar_records: List of similar records with similarity scores.
            - count: Number of similar records returned.
            - error: Error message if operation failed (None if successful).
        """
        # Create a temporary Record for the query (without saving)
        temp_query_record = Record(
            id='__temp_query__',
            name='__temp__',
            value=query_value,
            value_type=value_type,
        )
        
        # Auto-embed if needed
        if self.auto_embed and value_type == 'text':
            embedding = self.embedding_generator.embed(str(query_value))
            temp_query_record.embedding = embedding
        
        # Route to appropriate similarity function
        if value_type == 'text':
            result = find_similar_text_records(
                connection=self.connection,
                query_record=temp_query_record,
                limit=limit,
                exclude_self=False,  # No "self" to exclude for temp record
            )
        elif value_type == 'number':
            result = find_similar_number_records(
                connection=self.connection,
                query_record=temp_query_record,
                limit=limit,
                exclude_self=False,
            )
        elif value_type == 'date':
            result = find_similar_date_records(
                connection=self.connection,
                query_record=temp_query_record,
                limit=limit,
                exclude_self=False,
            )
        else:
            return {
                'success': False,
                'error': f"Unsupported value_type: {value_type}",
            }
        
        # Replace query_id with query_value in result
        if result.get('success'):
            result['query_value'] = query_value
            result.pop('query_id', None)
        
        return result
    
    def find_similar_records(
        self,
        id: str,
        limit: int = 10,
        exclude_self: bool = True,
    ) -> Dict[str, Any]:
        """
        Find records similar to a given record.
        
        Similarity method depends on record type:
        - text: cosine similarity between embeddings
        - number: distance-based (inverse of absolute difference)
        - date: distance-based (inverse of time difference)
        
        Args:
            id: Universal ID of the query record.
            limit: Maximum number of similar records to return.
            exclude_self: Whether to exclude the query record from results.
            
        Returns:
            Dictionary with success status and list of similar records.
            Each result includes: id, name, description, value_type, similarity (0-1).
        """
        try:
            # Load the query record
            query_result = self.load_record(id=id)
            if not query_result['success']:
                return query_result
            
            query_record = query_result['record']
            value_type = query_record.value_type
            
            # Handle based on value type
            if value_type == "text":
                return find_similar_text_records(
                    connection=self.connection,
                    query_record=query_record,
                    limit=limit,
                    exclude_self=exclude_self,
                )
            elif value_type == "number":
                return find_similar_number_records(
                    connection=self.connection,
                    query_record=query_record,
                    limit=limit,
                    exclude_self=exclude_self,
                )
            elif value_type == "date":
                return find_similar_date_records(
                    connection=self.connection,
                    query_record=query_record,
                    limit=limit,
                    exclude_self=exclude_self,
                )
            else:
                return {
                    'success': False,
                    'error': f"Unknown value type: {value_type}",
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }
    
    
    def _parse_partial_date(self, date_value: Any) -> Optional[Any]:
        """
        Parse a partial date (year, year-month, or full date).
        
        DEPRECATED: Use parse_partial_date_with_granularity instead.
        This method is kept for backward compatibility.
        
        Args:
            date_value: Date string to parse.
            
        Returns:
            datetime object, or None if parsing fails.
        """
        result = parse_partial_date_with_granularity(date_value)
        return result[0] if result[0] is not None else None
    
    # ============================================================================
    # Utility methods
    # ============================================================================
    
    def close(self) -> None:
        """Close the database connection."""
        self.connection.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __repr__(self) -> str:
        return f"SemanticMemory(database_path='{self.database_path}')"

