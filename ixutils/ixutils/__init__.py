"""
Shared utilities package for the ix ecosystem.

Provides common utilities used across multiple packages:
- persist: Caching decorator for function results
- time: Time utilities (UTC timestamps, ISO parsing, etc.)
- database: SQLite database connection helpers
- usage_tracker: Usage and cost tracking for LLMs and agents
- json_parser: JSON and Python literal parsing utilities
- fuzzy_match: String fuzzy matching utilities
"""

from .persist import persist, set_cache_path, get_cache_path
from .time import (
    utc_now_iso,
    utc_now,
    parse_iso,
    from_timestamp,
    from_timestamp_datetime,
    current_timestamp,
    delay,
    strptime,
)
from .database import create_database_connection
from .usage_tracker import UsageTracker
from .json_parser import repair_json, parse_json_robust, parse_json_or_python_literal
from .fuzzy_match import fuzzy_match
from .env_var import EnvVar

__all__ = [
    # Persist
    "persist",
    "set_cache_path",
    "get_cache_path",
    # Time
    "utc_now_iso",
    "utc_now",
    "parse_iso",
    "from_timestamp",
    "from_timestamp_datetime",
    "current_timestamp",
    "delay",
    "strptime",
    # Database
    "create_database_connection",
    # Usage Tracker
    "UsageTracker",
    # JSON Parser
    "repair_json",
    "parse_json_robust",
    "parse_json_or_python_literal",
    # Fuzzy Match
    "fuzzy_match",
    # Environment Variables
    "EnvVar",
]

