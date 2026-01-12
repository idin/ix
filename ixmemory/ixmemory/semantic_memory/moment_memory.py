"""
Moment memory for storing and searching temporal values.

Supports partial dates/times (e.g., "November", "2025", "3pm").
"""

from typing import Any, Dict, List, Optional
import sqlite3

from ixutils import utc_now


# Example record types for moments (for AI/developer hints)
MOMENT_RECORD_TYPES = [
    "birthdate",        # Date of birth
    "death_date",       # Date of death
    "start_date",       # Start of something (job, project, event)
    "end_date",         # End of something
    "event_date",       # Date of an event
    "deadline",         # Due date or deadline
    "created_date",     # Creation timestamp
    "modified_date",    # Last modification timestamp
    "anniversary",      # Recurring annual date
    "scheduled_time",   # Scheduled appointment/meeting time
    "publication_date", # Publication or release date
    "expiration_date",  # Expiration or end-of-life date
    "founding_date",    # When organization was founded
    "graduation_date",  # Academic graduation
    "hire_date",        # Employment start date
    "departure_date",   # Travel or leaving date
    "arrival_date",     # Travel or arrival date
    "meeting_time",     # Time of a meeting
    "historical_date",  # Historical event date
    "season",           # Season of year (partial: month range)
]


class MomentMemory:
    """
    Memory for storing and searching temporal values.
    
    Supports:
    - CRUD operations
    - Partial dates/times (year only, month only, etc.)
    - Record type categorization (birthdate, deadline, etc.)
    - Nearest moment search (optionally within same type)
    - Range queries
    
    Example record types:
        birthdate, death_date, start_date, end_date, event_date,
        deadline, created_date, anniversary, scheduled_time,
        publication_date, expiration_date, founding_date
    
    Args:
        connection: SQLite database connection.
    
    Example:
        >>> moments = MomentMemory(connection)
        >>> moments.save(id="alice_birth", year=1990, month=5, day=15, record_type="birthdate")
        >>> moments.save(id="project_deadline", year=2025, month=12, day=31, record_type="deadline")
        >>> moments.find_nearest(year=1992, record_type="birthdate")
    """
    
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
    
    def save(
        self,
        *,
        id: str,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
        hour: Optional[int] = None,
        minute: Optional[int] = None,
        second: Optional[int] = None,
        record_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Save a moment (temporal value).
        
        All temporal components are optional, allowing partial dates like
        "November" (month=11) or "2025" (year=2025).
        
        Args:
            id: Unique identifier for the moment.
            year: Year component (e.g., 2025).
            month: Month component (1-12).
            day: Day component (1-31).
            hour: Hour component (0-23).
            minute: Minute component (0-59).
            second: Second component (0-59).
            record_type: Type of moment (e.g., "birthdate", "deadline").
                        See MOMENT_RECORD_TYPES for examples.
        
        Returns:
            Dictionary with 'success' and saved data.
        """
        cursor = self.connection.cursor()
        now = utc_now()
        
        cursor.execute("""
            INSERT OR REPLACE INTO moments 
            (id, record_type, year, month, day, hour, minute, second, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?,
                COALESCE((SELECT created_at FROM moments WHERE id = ?), ?),
                ?)
        """, (id, record_type, year, month, day, hour, minute, second, id, now, now))
        
        self.connection.commit()
        
        return {
            'success': True,
            'id': id,
            'record_type': record_type,
            'year': year,
            'month': month,
            'day': day,
            'hour': hour,
            'minute': minute,
            'second': second,
        }
    
    def load(self, *, id: str) -> Optional[Dict[str, Any]]:
        """
        Load a moment by ID.
        
        Args:
            id: Moment ID.
        
        Returns:
            Dictionary with moment data, or None if not found.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT id, record_type, year, month, day, hour, minute, second, created_at, updated_at
            FROM moments WHERE id = ?
        """, (id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return {
            'id': row[0],
            'record_type': row[1],
            'year': row[2],
            'month': row[3],
            'day': row[4],
            'hour': row[5],
            'minute': row[6],
            'second': row[7],
            'created_at': row[8],
            'updated_at': row[9],
        }
    
    def delete(self, *, id: str) -> bool:
        """
        Delete a moment by ID.
        
        Args:
            id: Moment ID.
        
        Returns:
            True if deleted, False if not found.
        """
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM moments WHERE id = ?", (id,))
        self.connection.commit()
        
        return cursor.rowcount > 0
    
    def list(
        self,
        *,
        record_type: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        List moments.
        
        Args:
            record_type: Optional filter by record type (e.g., "birthdate").
            limit: Maximum number of results.
            offset: Number of results to skip.
        
        Returns:
            List of moment dictionaries.
        """
        cursor = self.connection.cursor()
        
        query = """
            SELECT id, record_type, year, month, day, hour, minute, second, created_at, updated_at
            FROM moments
        """
        conditions = []
        params: List[Any] = []
        
        if record_type is not None:
            conditions.append("record_type = ?")
            params.append(record_type)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY year, month, day, hour, minute, second"
        
        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        
        cursor.execute(query, params)
        
        return [
            {
                'id': row[0],
                'record_type': row[1],
                'year': row[2],
                'month': row[3],
                'day': row[4],
                'hour': row[5],
                'minute': row[6],
                'second': row[7],
                'created_at': row[8],
                'updated_at': row[9],
            }
            for row in cursor.fetchall()
        ]
    
    def _build_distance_expression(
        self,
        year: Optional[int],
        month: Optional[int],
        day: Optional[int],
        hour: Optional[int],
        minute: Optional[int],
        second: Optional[int],
    ) -> tuple[str, List[Any]]:
        """
        Build SQL expression for computing weighted distance.
        
        Returns:
            Tuple of (SQL expression, parameters list).
        """
        # Weights for each component (larger units = larger weight)
        weights = {
            'year': 365.0,
            'month': 30.0,
            'day': 1.0,
            'hour': 1.0 / 24.0,
            'minute': 1.0 / (24.0 * 60.0),
            'second': 1.0 / (24.0 * 60.0 * 60.0),
        }
        
        components = [
            ('year', year, weights['year']),
            ('month', month, weights['month']),
            ('day', day, weights['day']),
            ('hour', hour, weights['hour']),
            ('minute', minute, weights['minute']),
            ('second', second, weights['second']),
        ]
        
        terms = []
        params: List[Any] = []
        
        for column, target_value, weight in components:
            if target_value is not None:
                # CASE WHEN column IS NOT NULL THEN ABS(column - target) * weight ELSE large_value END
                terms.append(
                    f"CASE WHEN {column} IS NOT NULL THEN ABS({column} - ?) * ? ELSE 999999999 END"
                )
                params.extend([target_value, weight])
        
        if not terms:
            # No components specified, return constant large distance
            return "999999999", []
        
        # Sum all terms
        expression = " + ".join(terms)
        return expression, params
    
    def find_nearest(
        self,
        *,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
        hour: Optional[int] = None,
        minute: Optional[int] = None,
        second: Optional[int] = None,
        record_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Find moments nearest to target temporal values.
        
        Uses SQL-based distance computation for efficiency.
        Only compares components that are specified. For example,
        find_nearest(month=11) finds moments closest to November.
        
        Args:
            year: Target year.
            month: Target month (1-12).
            day: Target day (1-31).
            hour: Target hour (0-23).
            minute: Target minute (0-59).
            second: Target second (0-59).
            record_type: Optional filter by record type (e.g., "birthdate").
            limit: Maximum number of results.
        
        Returns:
            List of moments sorted by distance from target.
        """
        cursor = self.connection.cursor()
        
        # Build distance expression
        distance_expr, distance_params = self._build_distance_expression(
            year=year, month=month, day=day,
            hour=hour, minute=minute, second=second,
        )
        
        # Build query
        query = f"""
            SELECT id, record_type, year, month, day, hour, minute, second, 
                   created_at, updated_at, ({distance_expr}) AS distance
            FROM moments
        """
        params: List[Any] = list(distance_params)
        
        # Filter conditions
        conditions = []
        if record_type is not None:
            conditions.append("record_type = ?")
            params.append(record_type)
        
        # Only include records that have at least one of the searched components
        component_filters = []
        if year is not None:
            component_filters.append("year IS NOT NULL")
        if month is not None:
            component_filters.append("month IS NOT NULL")
        if day is not None:
            component_filters.append("day IS NOT NULL")
        if hour is not None:
            component_filters.append("hour IS NOT NULL")
        if minute is not None:
            component_filters.append("minute IS NOT NULL")
        if second is not None:
            component_filters.append("second IS NOT NULL")
        
        if component_filters:
            conditions.append("(" + " OR ".join(component_filters) + ")")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY distance LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        return [
            {
                'id': row[0],
                'record_type': row[1],
                'year': row[2],
                'month': row[3],
                'day': row[4],
                'hour': row[5],
                'minute': row[6],
                'second': row[7],
                'created_at': row[8],
                'updated_at': row[9],
                'distance': row[10],
            }
            for row in cursor.fetchall()
        ]
    
    def find_in_range(
        self,
        *,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        min_month: Optional[int] = None,
        max_month: Optional[int] = None,
        min_day: Optional[int] = None,
        max_day: Optional[int] = None,
        record_type: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Find moments within a range.
        
        Args:
            min_year: Minimum year (inclusive).
            max_year: Maximum year (inclusive).
            min_month: Minimum month (inclusive).
            max_month: Maximum month (inclusive).
            min_day: Minimum day (inclusive).
            max_day: Maximum day (inclusive).
            record_type: Optional filter by record type (e.g., "birthdate").
            limit: Maximum number of results.
        
        Returns:
            List of moments within the range.
        """
        cursor = self.connection.cursor()
        
        conditions = []
        params: List[Any] = []
        
        if record_type is not None:
            conditions.append("record_type = ?")
            params.append(record_type)
        
        if min_year is not None:
            conditions.append("(year IS NULL OR year >= ?)")
            params.append(min_year)
        
        if max_year is not None:
            conditions.append("(year IS NULL OR year <= ?)")
            params.append(max_year)
        
        if min_month is not None:
            conditions.append("(month IS NULL OR month >= ?)")
            params.append(min_month)
        
        if max_month is not None:
            conditions.append("(month IS NULL OR month <= ?)")
            params.append(max_month)
        
        if min_day is not None:
            conditions.append("(day IS NULL OR day >= ?)")
            params.append(min_day)
        
        if max_day is not None:
            conditions.append("(day IS NULL OR day <= ?)")
            params.append(max_day)
        
        query = """
            SELECT id, record_type, year, month, day, hour, minute, second, created_at, updated_at
            FROM moments
        """
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY year, month, day, hour, minute, second"
        
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        
        return [
            {
                'id': row[0],
                'record_type': row[1],
                'year': row[2],
                'month': row[3],
                'day': row[4],
                'hour': row[5],
                'minute': row[6],
                'second': row[7],
                'created_at': row[8],
                'updated_at': row[9],
            }
            for row in cursor.fetchall()
        ]
    
    def find_by_components(
        self,
        *,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
        hour: Optional[int] = None,
        minute: Optional[int] = None,
        second: Optional[int] = None,
        record_type: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Find moments with exact matching components.
        
        Only specified components are matched. For example,
        find_by_components(month=11) finds all moments where month=11.
        
        Args:
            year: Exact year to match.
            month: Exact month to match.
            day: Exact day to match.
            hour: Exact hour to match.
            minute: Exact minute to match.
            second: Exact second to match.
            record_type: Optional filter by record type (e.g., "birthdate").
            limit: Maximum number of results.
        
        Returns:
            List of matching moments.
        """
        cursor = self.connection.cursor()
        
        conditions = []
        params: List[Any] = []
        
        if record_type is not None:
            conditions.append("record_type = ?")
            params.append(record_type)
        
        if year is not None:
            conditions.append("year = ?")
            params.append(year)
        
        if month is not None:
            conditions.append("month = ?")
            params.append(month)
        
        if day is not None:
            conditions.append("day = ?")
            params.append(day)
        
        if hour is not None:
            conditions.append("hour = ?")
            params.append(hour)
        
        if minute is not None:
            conditions.append("minute = ?")
            params.append(minute)
        
        if second is not None:
            conditions.append("second = ?")
            params.append(second)
        
        query = """
            SELECT id, record_type, year, month, day, hour, minute, second, created_at, updated_at
            FROM moments
        """
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY year, month, day, hour, minute, second"
        
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        
        return [
            {
                'id': row[0],
                'record_type': row[1],
                'year': row[2],
                'month': row[3],
                'day': row[4],
                'hour': row[5],
                'minute': row[6],
                'second': row[7],
                'created_at': row[8],
                'updated_at': row[9],
            }
            for row in cursor.fetchall()
        ]
