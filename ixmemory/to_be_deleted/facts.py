"""
Fact operations for semantic memory.
"""

import json
import pickle
from typing import Any, Dict, Optional, List

from .fact import Fact
from ixutils import parse_iso


def save_fact(
    *,
    connection: Any,
    text: str,
    relationship_type: str,
    objects: List[Dict[str, str]],
    id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    embedding: Optional[list] = None,
    auto_embed: bool = True,
    embedding_generator: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Save a fact to the store.
    
    Args:
        connection: Database connection.
        text: Natural language statement.
        relationship_type: Type of relationship.
        objects: List of {"id": str, "role": str} dictionaries.
        fact_id: Optional unique identifier.
        metadata: Optional metadata dictionary.
        embedding: Optional embedding vector.
        auto_embed: Whether to auto-generate embeddings.
        embedding_generator: Embedding generator instance.
        
    Returns:
        Dictionary with success status and fact_id.
    """
    try:
        # Auto-generate embedding if enabled and not provided
        if auto_embed and embedding_generator and embedding is None and text:
            embedding = embedding_generator.embed(text=text)
        
        fact = Fact(
            text=text,
            relationship_type=relationship_type,
            objects=objects,
            id=id,
            metadata=metadata,
            embedding=embedding,
        )
        
        cursor = connection.cursor()
        
        # Save fact
        cursor.execute("""
            INSERT OR REPLACE INTO facts 
            (fact_id, text, relationship_type, metadata, embedding, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            fact.id,
            fact.text,
            fact.relationship_type,
            json.dumps(fact.metadata),
            pickle.dumps(fact.embedding) if fact.embedding else None,
            fact.created_at.isoformat(),
            fact.updated_at.isoformat(),
        ))
        
        # Delete old fact-record associations (for REPLACE)
        cursor.execute("""
            DELETE FROM fact_objects WHERE fact_id = ?
        """, (fact.id,))
        
        # Save fact-object associations
        for obj in fact.objects:
            cursor.execute("""
                INSERT INTO fact_objects (fact_id, object_id, role)
                VALUES (?, ?, ?)
            """, (
                fact.id,
                obj['id'],
                obj['role'],
            ))
        
        connection.commit()
        
        return {
            'success': True,
            'id': fact.id,
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }


def load_fact(
    *,
    connection: Any,
    id: str,
) -> Dict[str, Any]:
    """
    Load a fact from the store.
    
    Args:
        connection: Database connection.
        id: Universal ID of the fact to load.
        
    Returns:
        Dictionary with success status and fact data.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT * FROM facts WHERE fact_id = ?
        """, (id,))
        
        row = cursor.fetchone()
        
        if row is None:
            return {
                'success': False,
                'error': f"Fact '{id}' not found",
            }
        
        # Get associated objects
        cursor.execute("""
            SELECT object_id, role FROM fact_objects
            WHERE fact_id = ?
        """, (id,))
        
        objects = [
            {'id': obj_row['object_id'], 'role': obj_row['role']}  # Map DB column to 'id' in API
            for obj_row in cursor.fetchall()
        ]
        
        # Reconstruct Fact
        fact = Fact(
            text=row['text'],
            relationship_type=row['relationship_type'],
            objects=objects,
            id=row['fact_id'],
            metadata=json.loads(row['metadata']),
            embedding=pickle.loads(row['embedding']) if row['embedding'] else None,
        )
        
        # Restore timestamps
        fact.created_at = parse_iso(row['created_at'])
        fact.updated_at = parse_iso(row['updated_at'])
        
        return {
            'success': True,
            'fact': fact,
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }


def delete_fact(
    *,
    connection: Any,
    id: str,
) -> Dict[str, Any]:
    """
    Delete a fact from the store.
    
    Args:
        connection: Database connection.
        id: Universal ID of the fact to delete.
        
    Returns:
        Dictionary with success status.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""
            DELETE FROM facts WHERE fact_id = ?
        """, (id,))
        
        if cursor.rowcount == 0:
            return {
                'success': False,
                'error': f"Fact '{id}' not found",
            }
        
        connection.commit()
        
        return {
            'success': True,
            'id': id,
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }

