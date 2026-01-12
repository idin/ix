"""
Record wrapper with metadata and embeddings for semantic memory.
"""

from typing import Any, Optional, Dict, Literal
import json
import uuid

from ixutils import utc_now, parse_iso

ValueType = Literal["text", "number", "date"]


class Record:
    """
    Record wrapper for records stored in semantic memory.
    
    Contains name, description, metadata, tags, and embeddings for semantic search.
    
    Args:
        name: Name for this record (not necessarily unique).
        description: Human-readable description of the record.
        id: Optional unique identifier (auto-generated if not provided).
        record_type_id: Type of record (e.g., "entity", "concept", "event", "document"). Defaults to "entity".
        tags: Optional list of tags for categorization.
        metadata: Optional additional metadata dictionary.
        embedding: Optional primary embedding (name + description combined).
        name_embedding: Optional specialized embedding for name-only search.
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        id: Optional[str] = None,
        record_type_id: str = "entity",
        tags: Optional[list] = None,
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[list] = None,
        name_embedding: Optional[list] = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.record_type_id = record_type_id
        self.tags = tags or []
        self.metadata = metadata or {}
        self.embedding = embedding  # Primary: name + description (for text type)
        self.name_embedding = name_embedding  # Specialized: name only (for text type)
        
        # Auto-generated metadata
        self.created_at = utc_now()
        self.updated_at = utc_now()
        self.access_count = 0
        self.last_accessed = None
    
    def update_metadata(
        self,
        tags: Optional[list] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Update the record's metadata.
        
        Args:
            tags: New tags to add (appends to existing).
            metadata: Metadata dictionary to merge with existing.
        """
        if tags:
            self.tags.extend(tags)
        
        if metadata:
            self.metadata.update(metadata)
        
        self.updated_at = utc_now()
    
    def record_access(self) -> None:
        """Record that this record was accessed."""
        self.access_count += 1
        self.last_accessed = utc_now()
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get all metadata as a dictionary.
        
        Returns:
            Dictionary containing all metadata fields.
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'record_type_id': self.record_type_id,
            'value_type': self.value_type,
            'tags': self.tags,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'access_count': self.access_count,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
        }
    
    def get_embedding(self) -> Optional[list]:
        """
        Get the primary embedding vector (name + description).
        
        Returns:
            Embedding vector or None if not set.
        """
        return self.embedding
    
    def set_embedding(
        self,
        embedding: list,
        name_embedding: Optional[list] = None,
    ) -> None:
        """
        Set the embedding vectors.
        
        Args:
            embedding: Primary embedding vector (name + description).
            name_embedding: Optional specialized embedding for name-only search.
        """
        self.embedding = embedding
        if name_embedding is not None:
            self.name_embedding = name_embedding
        self.updated_at = utc_now()
    
    def get_name_embedding(self) -> Optional[list]:
        """
        Get the name-only embedding vector.
        
        Returns:
            Name embedding vector or None if not set.
        """
        return self.name_embedding
    
    def set_name_embedding(self, name_embedding: list) -> None:
        """
        Set the name-only embedding vector.
        
        Args:
            name_embedding: Embedding vector for name-only search.
        """
        self.name_embedding = name_embedding
        self.updated_at = utc_now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for serialization.
        
        Returns:
            Dictionary representation of the record.
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'record_type_id': self.record_type_id,
            'tags': self.tags,
            'metadata': self.metadata,
            'embedding': self.embedding,
            'name_embedding': self.name_embedding,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'access_count': self.access_count,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Record':
        """
        Create a Record from a dictionary.
        
        Args:
            data: Dictionary containing record data.
            
        Returns:
            New Record instance.
        """
        obj = cls(
            name=data['name'],
            description=data.get('description', ''),
            id=data.get('id'),
            value_type=data.get('value_type', 'text'),
            tags=data.get('tags', []),
            metadata=data.get('metadata', {}),
            embedding=data.get('embedding'),
            name_embedding=data.get('name_embedding'),
        )
        
        # Restore timestamps
        if 'created_at' in data:
            obj.created_at = parse_iso(data['created_at'])
        if 'updated_at' in data:
            obj.updated_at = parse_iso(data['updated_at'])
        if 'access_count' in data:
            obj.access_count = data['access_count']
        if data.get('last_accessed'):
            obj.last_accessed = parse_iso(data['last_accessed'])
        
        return obj
    
    def __repr__(self) -> str:
        return f"Record(id='{self.id[:8]}...', name='{self.name}', tags={self.tags})"

