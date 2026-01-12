"""
Core foundation package providing LLM connections, utilities, and output formatting.
"""

from .llm import LLM
from .format_output import format_output

__all__ = ["LLM", "format_output"]

