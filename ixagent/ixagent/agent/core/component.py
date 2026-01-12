"""
Base component class for agent parts.

All agent components inherit from this class to ensure consistent structure.
"""


class AgentComponent:
    """
    Base class for all agent components.
    
    All parts of the agent (Memory, Cognition, Toolbox, etc.) should inherit
    from this class to ensure they follow the same structure and can be
    consistently managed by the Agent facade.
    """
    
    def __init__(self):
        """Initialize the component."""
        pass

