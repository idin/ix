"""
Utility functions for web tools.
"""

from .extract_domain import extract_domain
from .filter_by_domain import filter_by_domain
from .constants import BROWSER_USER_AGENT

__all__ = [
    "extract_domain",
    "filter_by_domain",
    "BROWSER_USER_AGENT",
]

