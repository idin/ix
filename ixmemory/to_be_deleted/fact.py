"""
Fact class for representing relationships between objects.
"""

from typing import List, Dict, Any, Optional
import uuid

from ixutils import utc_now, parse_iso


class Fact:
    """
    Represents a fact that connects objects with roles.
    
    Facts are first-class entities that connect multiple objects together,
    where each object has a specific role in the relationship.
    
    Example:
        Fact(
            text="Oxygen combined with Carbon produces CO2",
            relationship_type="chemical_reaction",
            objects=[
                {"id": "uuid-1", "role": "reactant_1"},
                {"id": "uuid-2", "role": "reactant_2"},
                {"id": "uuid-3", "role": "product"}
            ]
        )
    
    Args:
        text: Natural language statement describing the fact.
        relationship_type: Structured type for queries (e.g., "employment", "chemical_reaction").
        objects: List of dictionaries with "id" and "role" keys.
        id: Optional unique identifier (auto-generated if not provided).
        metadata: Optional additional metadata dictionary.
        embedding: Optional embedding vector for semantic search.
    """
    
    def __init__(
        self,
        text: str,
        relationship_type: str,
        objects: List[Dict[str, str]],
        id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[list] = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.text = text
        self.relationship_type = relationship_type
        self.objects = objects  # List of {"id": str, "role": str}
        self.metadata = metadata or {}
        self.embedding = embedding
        
        # Auto-generated metadata
        self.created_at = utc_now()
        self.updated_at = utc_now()
        
        # Validate objects format
        self._validate_objects()
    
    def _validate_objects(self) -> None:
        """
        Validate that objects list has correct format.
        
        Raises:
            ValueError: If objects format is invalid.
        """
        if not isinstance(self.objects, list):
            raise ValueError("objects must be a list")
        
        for obj in self.objects:
            if not isinstance(obj, dict):
                raise ValueError("Each object must be a dictionary")
            if 'id' not in obj or 'role' not in obj:
                raise ValueError("Each object must have 'id' and 'role' keys")
    
    def get_objects_by_role(self, role: str) -> List[str]:
        """
        Get all object IDs with a specific role.
        
        Args:
            role: The role to filter by.
            
        Returns:
            List of object IDs with that role.
        """
        return [
            obj['id']
            for obj in self.objects
            if obj['role'] == role
        ]
    
    def get_role_for_object(self, id: str) -> Optional[str]:
        """
        Get the role of a specific object in this fact.
        
        Args:
            id: Universal ID of the object (record).
            
        Returns:
            Role of the object, or None if object not in fact.
        """
        for obj in self.objects:
            if obj['id'] == id:
                return obj['role']
        return None
    
    def has_object(self, id: str) -> bool:
        """
        Check if this fact involves a specific object.
        
        Args:
            id: Universal ID of the object (record) to check.
            
        Returns:
            True if object is involved in this fact.
        """
        return any(obj['id'] == id for obj in self.objects)
    
    def update_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Update the fact's metadata.
        
        Args:
            metadata: Metadata dictionary to merge with existing.
        """
        self.metadata.update(metadata)
        self.updated_at = utc_now()
    
    def set_embedding(self, embedding: list) -> None:
        """
        Set the embedding vector.
        
        Args:
            embedding: Embedding vector for semantic search.
        """
        self.embedding = embedding
        self.updated_at = utc_now()
    
    def get_embedding(self) -> Optional[list]:
        """
        Get the embedding vector.
        
        Returns:
            Embedding vector or None if not set.
        """
        return self.embedding
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for serialization.
        
        Returns:
            Dictionary representation of the fact.
        """
        return {
            'id': self.id,
            'text': self.text,
            'relationship_type': self.relationship_type,
            'objects': self.objects,
            'metadata': self.metadata,
            'embedding': self.embedding,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Fact':
        """
        Create a Fact from a dictionary.
        
        Args:
            data: Dictionary containing fact data.
            
        Returns:
            New Fact instance.
        """
        fact = cls(
            text=data['text'],
            relationship_type=data['relationship_type'],
            objects=data['objects'],
            id=data.get('id'),
            metadata=data.get('metadata', {}),
            embedding=data.get('embedding'),
        )
        
        # Restore timestamps
        if 'created_at' in data:
            fact.created_at = parse_iso(data['created_at'])
        if 'updated_at' in data:
            fact.updated_at = parse_iso(data['updated_at'])
        
        return fact
    
    def __repr__(self) -> str:
        object_summary = ', '.join(
            f"{obj['id'][:8]}...({obj['role']})"
            for obj in self.objects
        )
        return f"Fact(type='{self.relationship_type}', objects=[{object_summary}])"

