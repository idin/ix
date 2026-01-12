"""
Number memory for storing and searching numeric values.
"""

from typing import Any, Dict, List, Optional, Union, Literal
import sqlite3

from ixutils import utc_now


# Example record types for numbers (for AI/developer hints)
NUMBER_RECORD_TYPES = [
    "age",              # Person's age (integer, 0-150)
    "count",            # Count of items (integer, >= 0)
    "price",            # Monetary amount (float, >= 0)
    "temperature",      # Temperature reading (float, can be negative)
    "percentage",       # Percentage value (float, 0-100)
    "weight",           # Weight measurement (float, >= 0)
    "height",           # Height measurement (float, >= 0)
    "distance",         # Distance measurement (float, >= 0)
    "score",            # Score or points (integer or float)
    "rating",           # Rating value (float, often 0-5 or 0-10)
    "quantity",         # Quantity amount (integer or float, >= 0)
    "duration_seconds", # Duration in seconds (float, >= 0)
    "year",             # Year as number (integer)
    "rank",             # Ranking position (integer, >= 1)
    "index",            # Index or position (integer, >= 0)
    "currency_amount",  # Money amount (float)
    "latitude",         # Geographic latitude (float, -90 to 90)
    "longitude",        # Geographic longitude (float, -180 to 180)
]


class NumberMemory:
    """
    Memory for storing and searching numeric values.
    
    Supports:
    - CRUD operations
    - Integer vs float type tracking
    - Record type categorization (age, price, count, etc.)
    - Nearest value search (optionally within same type)
    - Range queries
    
    Example record types:
        age, count, price, temperature, percentage, weight, height,
        distance, score, rating, quantity, duration_seconds, year,
        rank, index, currency_amount, latitude, longitude
    
    Args:
        connection: SQLite database connection.
    
    Example:
        >>> numbers = NumberMemory(connection)
        >>> numbers.save(id="alice_age", value=32, record_type="age")
        >>> numbers.save(id="item_price", value=19.99, record_type="price")
        >>> numbers.find_nearest(value=30, record_type="age")
    """
    
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
    
    def _determine_number_type(self, value: Union[int, float]) -> str:
        """Determine if value is integer or float."""
        if isinstance(value, int):
            return "integer"
        elif isinstance(value, float) and value.is_integer():
            return "integer"
        else:
            return "float"
    
    def _convert_value(self, value: float, number_type: str) -> Union[int, float]:
        """Convert value back to original type."""
        if number_type == "integer":
            return int(value)
        return value
    
    def save(
        self,
        *,
        id: str,
        value: Union[int, float],
        record_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Save a numeric value.
        
        Args:
            id: Unique identifier for the number.
            value: The numeric value (int or float).
            record_type: Type of number (e.g., "age", "price", "count").
                        See NUMBER_RECORD_TYPES for examples.
        
        Returns:
            Dictionary with 'success' and saved data.
        """
        cursor = self.connection.cursor()
        now = utc_now()
        number_type = self._determine_number_type(value)
        
        cursor.execute("""
            INSERT OR REPLACE INTO numbers 
            (id, value, number_type, record_type, created_at, updated_at)
            VALUES (?, ?, ?, ?,
                COALESCE((SELECT created_at FROM numbers WHERE id = ?), ?),
                ?)
        """, (id, float(value), number_type, record_type, id, now, now))
        
        self.connection.commit()
        
        return {
            'success': True,
            'id': id,
            'value': value,
            'number_type': number_type,
            'record_type': record_type,
        }
    
    def load(self, *, id: str) -> Optional[Dict[str, Any]]:
        """
        Load a number by ID.
        
        Args:
            id: Number ID.
        
        Returns:
            Dictionary with number data, or None if not found.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT id, value, number_type, record_type, created_at, updated_at 
            FROM numbers WHERE id = ?
        """, (id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return {
            'id': row[0],
            'value': self._convert_value(row[1], row[2]),
            'number_type': row[2],
            'record_type': row[3],
            'created_at': row[4],
            'updated_at': row[5],
        }
    
    def delete(self, *, id: str) -> bool:
        """
        Delete a number by ID.
        
        Args:
            id: Number ID.
        
        Returns:
            True if deleted, False if not found.
        """
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM numbers WHERE id = ?", (id,))
        self.connection.commit()
        
        return cursor.rowcount > 0
    
    def list(
        self,
        *,
        record_type: Optional[str] = None,
        number_type: Optional[Literal["integer", "float"]] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        List numbers.
        
        Args:
            record_type: Optional filter by record type (e.g., "age", "price").
            number_type: Optional filter by number type ("integer" or "float").
            limit: Maximum number of results.
            offset: Number of results to skip.
        
        Returns:
            List of number dictionaries.
        """
        cursor = self.connection.cursor()
        
        query = "SELECT id, value, number_type, record_type, created_at, updated_at FROM numbers"
        conditions = []
        params: List[Any] = []
        
        if record_type is not None:
            conditions.append("record_type = ?")
            params.append(record_type)
        
        if number_type is not None:
            conditions.append("number_type = ?")
            params.append(number_type)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY value"
        
        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        
        cursor.execute(query, params)
        
        return [
            {
                'id': row[0],
                'value': self._convert_value(row[1], row[2]),
                'number_type': row[2],
                'record_type': row[3],
                'created_at': row[4],
                'updated_at': row[5],
            }
            for row in cursor.fetchall()
        ]
    
    def find_nearest(
        self,
        *,
        value: Union[int, float],
        record_type: Optional[str] = None,
        number_type: Optional[Literal["integer", "float"]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Find numbers nearest to a target value.
        
        Args:
            value: Target value to search near.
            record_type: Optional filter by record type (e.g., "age", "price").
            number_type: Optional filter by number type ("integer" or "float").
            limit: Maximum number of results.
        
        Returns:
            List of numbers sorted by distance from target.
        """
        cursor = self.connection.cursor()
        
        query = """
            SELECT id, value, number_type, record_type, created_at, updated_at, 
                   ABS(value - ?) AS distance
            FROM numbers
        """
        conditions = []
        params: List[Any] = [float(value)]
        
        if record_type is not None:
            conditions.append("record_type = ?")
            params.append(record_type)
        
        if number_type is not None:
            conditions.append("number_type = ?")
            params.append(number_type)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY distance LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        return [
            {
                'id': row[0],
                'value': self._convert_value(row[1], row[2]),
                'number_type': row[2],
                'record_type': row[3],
                'created_at': row[4],
                'updated_at': row[5],
                'distance': row[6],
            }
            for row in cursor.fetchall()
        ]
    
    def find_in_range(
        self,
        *,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        record_type: Optional[str] = None,
        number_type: Optional[Literal["integer", "float"]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Find numbers within a range.
        
        Args:
            min_value: Minimum value (inclusive). None for no lower bound.
            max_value: Maximum value (inclusive). None for no upper bound.
            record_type: Optional filter by record type (e.g., "age", "price").
            number_type: Optional filter by number type ("integer" or "float").
            limit: Maximum number of results.
        
        Returns:
            List of numbers within the range, sorted by value.
        """
        cursor = self.connection.cursor()
        
        conditions = []
        params: List[Any] = []
        
        if min_value is not None:
            conditions.append("value >= ?")
            params.append(float(min_value))
        
        if max_value is not None:
            conditions.append("value <= ?")
            params.append(float(max_value))
        
        if record_type is not None:
            conditions.append("record_type = ?")
            params.append(record_type)
        
        if number_type is not None:
            conditions.append("number_type = ?")
            params.append(number_type)
        
        query = "SELECT id, value, number_type, record_type, created_at, updated_at FROM numbers"
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY value"
        
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        
        return [
            {
                'id': row[0],
                'value': self._convert_value(row[1], row[2]),
                'number_type': row[2],
                'record_type': row[3],
                'created_at': row[4],
                'updated_at': row[5],
            }
            for row in cursor.fetchall()
        ]
