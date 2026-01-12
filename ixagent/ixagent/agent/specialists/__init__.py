"""
Specialist agent classes with pre-configured tool sets.
"""

from .file_system_agent import FileSystemAgent, add_file_system_tools
from .web_agent import WebAgent, add_web_tools
from .database_agent import DatabaseAgent, add_database_tools
from .toolkit_agent import ToolkitAgent

__all__ = [
    'FileSystemAgent',
    'WebAgent',
    'DatabaseAgent',
    'ToolkitAgent',
    'add_file_system_tools',
    'add_web_tools',
    'add_database_tools',
]

