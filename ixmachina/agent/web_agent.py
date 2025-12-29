"""
Web agent with web tools.
"""

from .agent import Agent
from ..tools.web import (
    search_web,
    scrape_website,
    get_website_content,
    get_website_title,
    get_website_description,
    get_website_keywords,
    get_website_author,
)


def add_web_tools(agent: Agent) -> None:
    """
    Add web tools to an agent.
    
    Args:
        agent: The agent instance to add web tools to.
    """
    web_tools = [
        search_web,
        scrape_website,
        get_website_content,
        get_website_title,
        get_website_description,
        get_website_keywords,
        get_website_author,
    ]
    
    agent.add_tools(web_tools)


class WebAgent(Agent):
    """
    Agent with web tools.
    
    Automatically sets up web tools on initialization.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize WebAgent with web tools.
        
        Accepts all arguments from Agent.__init__.
        """
        super().__init__(*args, **kwargs)
        
        add_web_tools(agent=self)

