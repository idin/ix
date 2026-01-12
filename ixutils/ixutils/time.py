"""
Unified time utilities for consistent timestamp handling across the codebase.
"""

import time
from datetime import datetime, timezone
from typing import Optional


def utc_now_iso() -> str:
    """
    Get current UTC time as ISO format string.
    
    Returns:
        ISO format string of current UTC time (e.g., "2024-01-15T10:30:45.123456+00:00").
    """
    return utc_now().isoformat()


def utc_now() -> datetime:
    """
    Get current UTC time as datetime object.
    
    Returns:
        datetime object with UTC timezone.
    """
    return datetime.now(timezone.utc)


def parse_iso(iso_string: str) -> datetime:
    """
    Parse an ISO format string to datetime object.
    
    Args:
        iso_string: ISO format datetime string.
    
    Returns:
        datetime object parsed from the ISO string.
    """
    return datetime.fromisoformat(iso_string)


def from_timestamp(timestamp: float) -> str:
    """
    Convert Unix timestamp to ISO format string.
    
    Args:
        timestamp: Unix timestamp (seconds since epoch).
    
    Returns:
        ISO format string.
    """
    return from_timestamp_datetime(timestamp).isoformat()


def from_timestamp_datetime(timestamp: float) -> datetime:
    """
    Convert Unix timestamp to datetime object.
    
    Args:
        timestamp: Unix timestamp (seconds since epoch).
    
    Returns:
        datetime object with UTC timezone.
    """
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def current_timestamp() -> float:
    """
    Get current Unix timestamp.
    
    Returns:
        Unix timestamp (seconds since epoch) as float.
    """
    return time.time()


def delay(seconds: float) -> None:
    """
    Sleep for the specified number of seconds.
    
    Args:
        seconds: Number of seconds to sleep (can be fractional).
    """
    time.sleep(seconds)


def strptime(date_string: str, format_string: str) -> datetime:
    """
    Parse a date string according to a format string.
    
    This is a wrapper around datetime.strptime for specialized date parsing.
    Use this instead of importing datetime directly.
    
    Args:
        date_string: String to parse.
        format_string: Format string (e.g., "%Y-%m-%d").
    
    Returns:
        datetime object parsed from the string.
    
    Raises:
        ValueError: If the string doesn't match the format.
    """
    return datetime.strptime(date_string, format_string)

