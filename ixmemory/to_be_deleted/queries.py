"""
Query operations for semantic memory.
"""

from typing import Any, Dict, Optional

from .facts import load_fact


def find_facts_by_object(
    *,
    connection: Any,
    id: str,
    role: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Find all facts involving a specific record (by universal ID).
    
    Args:
        connection: Database connection.
        id: Universal ID of the record.
        role: Optional role filter.
        
    Returns:
        Dictionary with success status and list of facts.
    """
    try:
        cursor = connection.cursor()
        
        if role:
            cursor.execute("""
                SELECT DISTINCT f.fact_id 
                FROM facts f
                JOIN fact_objects fo ON f.fact_id = fo.fact_id
                WHERE fo.object_id = ? AND fo.role = ?
            """, (id, role))
        else:
            cursor.execute("""
                SELECT DISTINCT f.fact_id 
                FROM facts f
                JOIN fact_objects fo ON f.fact_id = fo.fact_id
                WHERE fo.object_id = ?
            """, (id,))
        
        fact_ids = [row['fact_id'] for row in cursor.fetchall()]
        
        # Load each fact
        facts = []
        for fact_id in fact_ids:
            result = load_fact(connection=connection, id=fact_id)
            if result['success']:
                facts.append(result['fact'])
        
        return {
            'success': True,
            'facts': facts,
            'count': len(facts),
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }


def find_records_by_fact(
    *,
    connection: Any,
    id: str,
    role: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Find all records in a specific fact.
    
    Args:
        connection: Database connection.
        id: Universal ID of the fact.
        role: Optional role filter.
        
    Returns:
        Dictionary with success status and list of records with their info.
    """
    try:
        cursor = connection.cursor()
        
        if role:
            cursor.execute("""
                SELECT fo.object_id, o.name, o.description, fo.role 
                FROM fact_objects fo
                JOIN objects o ON fo.object_id = o.object_id
                WHERE fo.fact_id = ? AND fo.role = ?
            """, (id, role))
        else:
            cursor.execute("""
                SELECT fo.object_id, o.name, o.description, fo.role 
                FROM fact_objects fo
                JOIN objects o ON fo.object_id = o.object_id
                WHERE fo.fact_id = ?
            """, (id,))
        
        records = [
            {
                'id': row['object_id'],
                'name': row['name'],
                'description': row['description'],
                'role': row['role'],
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


def find_facts_by_type(
    *,
    connection: Any,
    relationship_type: str,
) -> Dict[str, Any]:
    """
    Find all facts of a specific type.
    
    Args:
        connection: Database connection.
        relationship_type: Type of relationship to find.
        
    Returns:
        Dictionary with success status and list of facts.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT fact_id FROM facts
            WHERE relationship_type = ?
        """, (relationship_type,))
        
        fact_ids = [row['fact_id'] for row in cursor.fetchall()]
        
        # Load each fact
        facts = []
        for fact_id in fact_ids:
            result = load_fact(connection=connection, id=fact_id)
            if result['success']:
                facts.append(result['fact'])
        
        return {
            'success': True,
            'facts': facts,
            'count': len(facts),
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }


def find_records_by_role(
    *,
    connection: Any,
    relationship_type: str,
    role: str,
) -> Dict[str, Any]:
    """
    Find all records with a specific role in a relationship type.
    
    Example: Find all "employers" in "employment" relationships.
    
    Args:
        connection: Database connection.
        relationship_type: Type of relationship.
        role: Role to filter by.
        
    Returns:
        Dictionary with success status and list of records with their info.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT DISTINCT fo.object_id, o.name, o.description
            FROM fact_objects fo
            JOIN facts f ON fo.fact_id = f.fact_id
            JOIN objects o ON fo.object_id = o.object_id
            WHERE f.relationship_type = ? AND fo.role = ?
        """, (relationship_type, role))
        
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

