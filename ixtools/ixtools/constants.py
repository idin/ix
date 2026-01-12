"""
Constants for tool return dictionaries.

All tools should use these constants for consistent return structure.
The primary output/result should always be in RESULT_KEY.
"""

# Standard return keys - ALL tools must use these
SUCCESS_KEY = "success"
ERROR_KEY = "error"
RESULT_KEY = "result"  # Primary output/result of the tool
METADATA_KEY = "metadata"  # Tool-specific metadata (like file paths)
