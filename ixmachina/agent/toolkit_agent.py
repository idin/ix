from .agent import Agent
from .file_system_agent import add_file_system_tools
from ..tools.web import (
    search_web,
    scrape_website,
    get_website_content,
    get_website_title,
    get_website_description,
    get_website_keywords,
    get_website_author,
)

from ..tools.text import (
    add_name_to_registry,
    remove_name_from_registry,
    get_name_registry,
    get_name_registry_contents,
    get_name_registry_status,
)

from .web_agent import add_web_tools as add_web_tools_func
from .file_system_agent import add_file_system_tools as add_file_system_tools_func

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
    
    def add_text_tools(self) -> None:
        """
        Add text processing tools to the agent.
        
        Note: Text tools may require NameRegistry context in the future.
        For now, they can be added directly.
        """
        text_tools = [
            add_name_to_registry,
            remove_name_from_registry,
            get_name_registry,
            get_name_registry_contents,
            get_name_registry_status,
        ]
        
        self.add_tools(text_tools)
