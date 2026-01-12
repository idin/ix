"""
Record storage operations for semantic memory.
"""

import json
import pickle
from typing import Any, Dict, Optional, List

from .record import Record, ValueType
from ixutils import parse_iso


def save_record(
    *,
    connection: Any,
    name: str,
    value: Any,
    description: str = "",
    id: Optional[str] = None,
    value_type: ValueType = "text",
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    embedding: Optional[list] = None,
    name_embedding: Optional[list] = None,
    auto_embed: bool = True,
    embedding_generator: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Save a record to the store.
    
    Args:
        connection: Database connection.
        name: Name for the record.
        value: The value to store.
        description: Human-readable description.
        id: Optional unique identifier (universal ID across all memory systems).
        value_type: Type of value ("text", "number", "date").
        tags: Optional list of tags.
        metadata: Optional metadata dictionary.
        embedding: Optional primary embedding vector.
        name_embedding: Optional name-only embedding vector.
        auto_embed: Whether to auto-generate embeddings.
        embedding_generator: Embedding generator instance.
        
    Returns:
        Dictionary with success status and id.
    """
    try:
        # Auto-generate embeddings only for text records
        if value_type == "text" and auto_embed and embedding_generator:
            if embedding is None:
                embedding = embedding_generator.embed_object(
                    name=name,
                    description=description,
                )
            
            if name_embedding is None and name:
                name_embedding = embedding_generator.embed(text=name)
        
        record = Record(
            name=name,
            value=value,
            description=description,
            id=id,
            value_type=value_type,
            tags=tags,
            metadata=metadata,
            embedding=embedding,
            name_embedding=name_embedding,
        )
        
        cursor = connection.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO objects 
            (object_id, name, description, value, value_type, tags, metadata, embedding, 
             name_embedding, created_at, updated_at, access_count, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.id,
            record.name,
            record.description,
            pickle.dumps(record.value),
            record.value_type,
            json.dumps(record.tags),
            json.dumps(record.metadata),
            pickle.dumps(record.embedding) if record.embedding else None,
            pickle.dumps(record.name_embedding) if record.name_embedding else None,
            record.created_at.isoformat(),
            record.updated_at.isoformat(),
            record.access_count,
            record.last_accessed.isoformat() if record.last_accessed else None,
        ))
        
        connection.commit()
        
        return {
            'success': True,
            'id': record.id,
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }


def load_record(
    *,
    connection: Any,
    id: str,
) -> Dict[str, Any]:
    """
    Load a record from the store by ID.
    
    Args:
        connection: Database connection.
        id: Universal ID of the record to load.
        
    Returns:
        Dictionary with success status and record data.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT * FROM objects WHERE object_id = ?
        """, (id,))
        
        row = cursor.fetchone()
        
        if row is None:
            return {
                'success': False,
                'error': f"Record with ID '{id}' not found",
            }
        
        # Reconstruct Record
        record = Record(
            name=row['name'],
            value=pickle.loads(row['value']),
            description=row['description'],
            id=row['object_id'],
            value_type=row.get('value_type', 'text'),
            tags=json.loads(row['tags']),
            metadata=json.loads(row['metadata']),
            embedding=pickle.loads(row['embedding']) if row['embedding'] else None,
            name_embedding=pickle.loads(row['name_embedding']) if row['name_embedding'] else None,
        )
        
        # Restore timestamps
        record.created_at = parse_iso(row['created_at'])
        record.updated_at = parse_iso(row['updated_at'])
        record.access_count = row['access_count']
        if row['last_accessed']:
            record.last_accessed = parse_iso(row['last_accessed'])
        
        # Record access
        record.record_access()
        
        # Update access count in database
        cursor.execute("""
            UPDATE objects 
            SET access_count = ?, last_accessed = ?
            WHERE object_id = ?
        """, (
            record.access_count,
            record.last_accessed.isoformat(),
            id,
        ))
        connection.commit()
        
        return {
            'success': True,
            'record': record,
            'id': record.id,
            'value': record.value,
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }


def delete_record(
    *,
    connection: Any,
    id: str,
) -> Dict[str, Any]:
    """
    Delete a record from the store.
    
    Args:
        connection: Database connection.
        id: Universal ID of the record to delete.
        
    Returns:
        Dictionary with success status.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""
            DELETE FROM objects WHERE object_id = ?
        """, (id,))
        
        if cursor.rowcount == 0:
            return {
                'success': False,
                'error': f"Record with ID '{id}' not found",
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


def list_records(
    *,
    connection: Any,
) -> Dict[str, Any]:
    """
    List all records in the store with basic info.
    
    Args:
        connection: Database connection.
        
    Returns:
        Dictionary with success status and list of records.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT object_id, name, description, value_type FROM objects")
        
        records = [
            {
                'id': row['object_id'],
                'name': row['name'],
                'description': row['description'],
                'value_type': row['value_type'] if 'value_type' in row.keys() else 'text',
            }
            for row in cursor.fetchall()
        ]
        
        return {
            'success': True,
            'records': records,
            'count': len(records),
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }


def find_records_by_name(
    *,
    connection: Any,
    name: str,
) -> Dict[str, Any]:
    """
    Find all records with a specific name.
    
    Args:
        connection: Database connection.
        name: Name to search for.
        
    Returns:
        Dictionary with success status and list of matching records.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT object_id, name, description FROM objects
            WHERE name = ?
        """, (name,))
        
        records = [
            {
                'id': row['object_id'],
                'name': row['name'],
                'description': row['description'],
            }
            for row in cursor.fetchall()
        ]
        
        return {
            'success': True,
            'records': records,
            'count': len(records),
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }

