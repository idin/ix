"""
Similarity calculation utilities for semantic memory.
"""

import pickle
import math
from typing import Dict, Any, List

from .record import Record
from .date_utils import parse_partial_date_with_granularity, calculate_date_distance


def cosine_similarity(
    embedding_a: List[float],
    embedding_b: List[float],
) -> float:
    """
    Calculate cosine similarity between two embeddings.
    
    Args:
        embedding_a: First embedding vector.
        embedding_b: Second embedding vector.
        
    Returns:
        Cosine similarity score (0-1, where 1 is identical).
    """
    # Calculate dot product
    dot_product = sum(a * b for a, b in zip(embedding_a, embedding_b))
    
    # Calculate magnitudes
    magnitude_a = math.sqrt(sum(a * a for a in embedding_a))
    magnitude_b = math.sqrt(sum(b * b for b in embedding_b))
    
    # Avoid division by zero
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    
    # Calculate cosine similarity
    similarity = dot_product / (magnitude_a * magnitude_b)
    
    # Clamp to [0, 1] range (in case of floating point errors)
    return max(0.0, min(1.0, similarity))


def find_similar_text_records(
    *,
    connection: Any,
    query_record: Record,
    limit: int,
    exclude_self: bool,
) -> Dict[str, Any]:
    """
    Find similar text records using embedding similarity.
    
    Args:
        connection: Database connection.
        query_record: Record to find similar records for.
        limit: Maximum number of similar records to return.
        exclude_self: Whether to exclude the query record from results.
        
    Returns:
        Dictionary with success status and list of similar records with similarity scores.
    """
    if query_record.embedding is None:
        return {
            'success': False,
            'error': f"Record '{query_record.id}' has no embedding. Cannot find similar records.",
        }
    
    query_embedding = query_record.embedding
    
    # Get all text records with embeddings
    cursor = connection.cursor()
    cursor.execute("""
        SELECT object_id, name, description, value_type, embedding
        FROM objects
        WHERE embedding IS NOT NULL AND value_type = 'text'
    """)
    
    # Calculate similarities
    similarities = []
    
    for row in cursor.fetchall():
        other_id = row['object_id']
        
        # Skip self if requested
        if exclude_self and other_id == query_record.id:
            continue
        
        other_embedding = pickle.loads(row['embedding'])
        
        # Calculate cosine similarity
        similarity_score = cosine_similarity(
            embedding_a=query_embedding,
            embedding_b=other_embedding,
        )
        
        similarities.append({
            'id': other_id,
            'name': row['name'],
            'description': row['description'],
            'value_type': row['value_type'],
            'similarity': similarity_score,
        })
    
    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x['similarity'], reverse=True)
    
    # Limit results
    similarities = similarities[:limit]
    
    return {
        'success': True,
        'query_id': query_record.id,
        'similar_records': similarities,
        'count': len(similarities),
    }


def find_similar_number_records(
    *,
    connection: Any,
    query_record: Record,
    limit: int,
    exclude_self: bool,
) -> Dict[str, Any]:
    """
    Find similar number records using distance-based similarity.
    
    Similarity is calculated as the inverse of the distance between numeric values,
    normalized to a 0-1 scale.
    
    Args:
        connection: Database connection.
        query_record: Record with a numeric value to find similar records for.
        limit: Maximum number of similar records to return.
        exclude_self: Whether to exclude the query record from results.
        
    Returns:
        Dictionary with success status and list of similar records with similarity scores.
    """
    try:
        query_value = float(query_record.value)
    except (ValueError, TypeError):
        return {
            'success': False,
            'error': f"Record value is not a valid number: {query_record.value}",
        }
    
    # Get all number records
    cursor = connection.cursor()
    cursor.execute("""
        SELECT object_id, name, description, value_type, value
        FROM objects
        WHERE value_type = 'number'
    """)
    
    # Calculate similarities
    similarities = []
    distances = []
    
    for row in cursor.fetchall():
        other_id = row['object_id']
        
        # Skip self if requested
        if exclude_self and other_id == query_record.id:
            continue
        
        try:
            other_value = float(pickle.loads(row['value']))
            distance = abs(query_value - other_value)
            distances.append(distance)
            
            similarities.append({
                'id': other_id,
                'name': row['name'],
                'description': row['description'],
                'value_type': row['value_type'],
                'distance': distance,
            })
        except (ValueError, TypeError):
            # Skip records with invalid number values
            continue
    
    if not similarities:
        return {
            'success': True,
            'query_id': query_record.id,
            'similar_records': [],
            'count': 0,
        }
    
    # Normalize distances to similarity scores (0-1)
    max_distance = max(distances) if distances else 1.0
    if max_distance == 0:
        max_distance = 1.0  # Avoid division by zero
    
    for item in similarities:
        # Similarity = 1 - (distance / max_distance)
        item['similarity'] = 1.0 - (item['distance'] / max_distance)
        del item['distance']  # Remove intermediate distance field
    
    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x['similarity'], reverse=True)
    
    # Limit results
    similarities = similarities[:limit]
    
    return {
        'success': True,
        'query_id': query_record.id,
        'similar_records': similarities,
        'count': len(similarities),
    }


def find_similar_date_records(
    *,
    connection: Any,
    query_record: Record,
    limit: int,
    exclude_self: bool,
) -> Dict[str, Any]:
    """
    Find similar date records using distance-based similarity.
    
    Supports partial dates (YYYY, YYYY-MM, YYYY-MM-DD) and calculates similarity
    based on temporal distance, considering date granularity.
    
    Args:
        connection: Database connection.
        query_record: Record with a date value to find similar records for.
        limit: Maximum number of similar records to return.
        exclude_self: Whether to exclude the query record from results.
        
    Returns:
        Dictionary with success status and list of similar records with similarity scores.
    """
    
    # Parse query date (supports "YYYY", "YYYY-MM", "YYYY-MM-DD")
    query_date, query_granularity = parse_partial_date_with_granularity(query_record.value)
    if query_date is None:
        return {
            'success': False,
            'error': f"Record value is not a valid date: {query_record.value}",
        }
    
    # Get all date records
    cursor = connection.cursor()
    cursor.execute("""
        SELECT object_id, name, description, value_type, value
        FROM objects
        WHERE value_type = 'date'
    """)
    
    # Calculate similarities
    similarities = []
    distances = []  # In days
    
    for row in cursor.fetchall():
        other_id = row['object_id']
        
        # Skip self if requested
        if exclude_self and other_id == query_record.id:
            continue
        
        other_value = pickle.loads(row['value'])
        other_date, other_granularity = parse_partial_date_with_granularity(other_value)
        
        if other_date is None:
            continue
        
        # Calculate distance considering granularity
        distance = calculate_date_distance(
            date1=query_date,
            granularity1=query_granularity,
            date2=other_date,
            granularity2=other_granularity,
        )
        distances.append(distance)
        
        similarities.append({
            'id': other_id,
            'name': row['name'],
            'description': row['description'],
            'value_type': row['value_type'],
            'distance': distance,
        })
    
    if not similarities:
        return {
            'success': True,
            'query_id': query_record.id,
            'similar_records': [],
            'count': 0,
        }
    
    # Normalize distances to similarity scores (0-1)
    max_distance = max(distances) if distances else 1.0
    if max_distance == 0:
        max_distance = 1.0  # Avoid division by zero
    
    for item in similarities:
        # Similarity = 1 - (distance / max_distance)
        item['similarity'] = 1.0 - (item['distance'] / max_distance)
        del item['distance']  # Remove intermediate distance field
    
    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x['similarity'], reverse=True)
    
    # Limit results
    similarities = similarities[:limit]
    
    return {
        'success': True,
        'query_id': query_record.id,
        'similar_records': similarities,
        'count': len(similarities),
    }

