"""
Date parsing and distance calculation utilities for semantic memory.
"""

from typing import Any, Optional, Tuple

from ixutils import strptime


def parse_partial_date_with_granularity(
    date_value: Any
) -> Tuple[Optional[Any], Optional[str]]:
    """
    Parse a partial date and return both the date and its granularity.
    
    Supports formats:
    - "YYYY" (year only) → middle of year (July 1st)
    - "YYYY-MM" (year and month) → middle of month (15th)
    - "YYYY-MM-DD" (full date) → exact date
    
    Args:
        date_value: Date string to parse.
        
    Returns:
        Tuple of (datetime object, granularity) where granularity is
        "year", "month", or "day". Returns (None, None) if parsing fails.
    """
    if not isinstance(date_value, str):
        date_value = str(date_value)
    
    date_value = date_value.strip()
    
    # Try full date
    try:
        dt = strptime(date_value, "%Y-%m-%d")
        return (dt, "day")
    except ValueError:
        pass
    
    # Try year-month (use middle of month: 15th)
    try:
        dt = strptime(date_value + "-15", "%Y-%m-%d")
        return (dt, "month")
    except ValueError:
        pass
    
    # Try year only (use middle of year: July 1st)
    try:
        dt = strptime(date_value + "-07-01", "%Y-%m-%d")
        return (dt, "year")
    except ValueError:
        pass
    
    return (None, None)


def calculate_date_distance(
    date1: Any,
    granularity1: str,
    date2: Any,
    granularity2: str,
) -> int:
    """
    Calculate distance between two dates considering their granularity.
    
    Rules:
    - If both dates are same year/month (based on coarser granularity), distance is 0
    - Otherwise, calculate day-based distance between the normalized dates
    
    Args:
        date1: First datetime object.
        granularity1: Granularity of first date ("year", "month", "day").
        date2: Second datetime object.
        granularity2: Granularity of second date ("year", "month", "day").
        
    Returns:
        Distance in days.
    """
    # Use the coarser granularity
    if granularity1 == "year" or granularity2 == "year":
        # If either is year-only, check if same year
        if date1.year == date2.year:
            return 0
    elif granularity1 == "month" or granularity2 == "month":
        # If either is month-only, check if same year-month
        if date1.year == date2.year and date1.month == date2.month:
            return 0
    
    # Calculate actual day distance
    return abs((date1 - date2).days)

