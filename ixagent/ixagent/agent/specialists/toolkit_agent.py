from typing import Optional

from .. import Agent
from .file_system_agent import add_file_system_tools
from .web_agent import add_web_tools as add_web_tools_func
from .database_agent import add_database_tools as add_database_tools_func

class ToolkitAgent(Agent):
    """
    Agent with composable tool sets.
    
    This agent provides methods to add different tool sets (file system, web, text, etc.)
    with their required context/memory. Each tool set can be added independently.
    
    Example:
        agent = ToolkitAgent(llm=my_llm)
        agent.add_file_system_tools()
        agent.add_web_tools()
        agent.add_text_tools()
    """

    def add_file_system_tools(self) -> None:
        """
        Add file system tools with FileSystemMemory to the agent.
        
        Creates a FileSystemMemory instance and binds it to all file system tools,
        then adds the tools to the agent.
        """
        add_file_system_tools(agent=self)
    
    def add_web_tools(self) -> None:
        """
        Add web tools to the agent.
        
        Web tools don't require special memory/context, so they can be added directly.
        """
        
        add_web_tools_func(agent=self)
    
    def add_database_tools(self, database_path: Optional[str] = None) -> None:
        """
        Add database tools with DatabaseConnection to the agent.
        
        Args:
            database_path: Path to SQLite database file. If None, uses agent's working_directory/database.db
                or in-memory database if no working_directory is set.
        """
        add_database_tools_func(agent=self, database_path=database_path)
    
    def add_text_tools(self) -> None:
        """
        Add text processing tools to the agent.
        
        Note: Text tools are not yet implemented. This method is a placeholder
        for future implementation when text tool functions are created.
        """
        raise NotImplementedError(
            "Text tools are not yet implemented. "
            "See ixmachina/tools/text/__init__.py for details on what needs to be created."
        )
