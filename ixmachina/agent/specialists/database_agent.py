"""
Database agent with database tools and connection.
"""

from typing import Optional
from functools import partial

from ..agent import Agent
from ...tools.database import (
    execute_query,
    create_table,
    list_tables,
    get_table_schema,
)
from ...tools.database.connection import DatabaseConnection


def add_database_tools(agent: Agent, database_path: Optional[str] = None) -> None:
    """
    Add database tools with DatabaseConnection to the agent.
    
    Args:
        agent: The agent instance to add database tools to.
        database_path: Path to SQLite database file. If None, uses agent's working_directory/database.db
            or in-memory database if no working_directory is set.
    """
    import os
    
    # Use working_directory if database_path not provided
    if database_path is None:
        if hasattr(agent, 'working_directory') and agent.working_directory:
            # Ensure working directory exists (lazy creation)
            agent._ensure_working_directory()
            database_path = os.path.join(agent.working_directory, "database.db")
        else:
            database_path = ":memory:"
    
    database_tool_functions = [
        execute_query,
        create_table,
        list_tables,
        get_table_schema,
    ]
    
    if not hasattr(agent, '_database'):
        agent._database = DatabaseConnection(database_path=database_path)
        agent._system_objects['database'] = agent._database
    
    # Bind database to tools using functools.partial
    database_tools = []
    for tool_func in database_tool_functions:
        tool = partial(tool_func, database=agent._database)
        tool.__name__ = tool_func.__name__
        tool.__doc__ = tool_func.__doc__
        database_tools.append(tool)
    
    agent.add_tools(database_tools)


class DatabaseAgent(Agent):
    """
    Agent with database tools and DatabaseConnection.
    
    Automatically sets up database tools with connection on initialization.
    """
    
    def __init__(self, database_path: Optional[str] = None, *args, **kwargs):
        """
        Initialize DatabaseAgent with database tools.
        
        Args:
            database_path: Path to SQLite database file. If None, uses agent's working_directory/database.db
                or in-memory database if no working_directory is set.
            *args: Additional arguments passed to Agent.__init__.
            **kwargs: Additional keyword arguments passed to Agent.__init__.
        """
        super().__init__(*args, **kwargs)
        
        add_database_tools(agent=self, database_path=database_path)

