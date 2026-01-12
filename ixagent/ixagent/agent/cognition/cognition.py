"""
Cognition component for agent - manages LLM models, usage tracking, and system objects.
"""

from typing import Dict, Optional, Union, Any

from ...llm import LLM
from ...utils.usage_tracker import UsageTracker
from .llm_management import (
    initialize_llms,
    get_llm_for_run,
    update_llm_special_objects,
)
from ..core.component import AgentComponent


class Cognition(AgentComponent):
    """
    Cognition component for agent - handles LLM management and system references.
    
    Manages:
    - LLM registry (multiple LLMs)
    - Default LLM selection
    - Usage tracking (tokens, costs)
    - System objects (self, llm, llm:name references)
    """
    
    def __init__(
        self,
        llm: Union[LLM, Dict[str, LLM]],
        default_llm: Optional[Union[LLM, str]] = None,
        include_conversation_id: bool = True,
        agent_self: Optional[Any] = None,
    ):
        """
        Initialize Cognition component.
        
        Args:
            llm: Either a single LLM instance, or a dictionary of LLMs (keyed by name).
            default_llm: The default LLM to use. Can be:
                - An LLM instance (if llm is a dict)
                - A string key to one of the LLMs in the dictionary
                - If not provided and llm is a single LLM, that LLM is used
                - If not provided and llm is a dict, the first LLM in the dict is used
            include_conversation_id: If True, usage tracker includes conversation_id.
            agent_self: Optional agent instance reference for system objects.
        """
        # Initialize LLMs
        llm_config = initialize_llms(
            llm=llm,
            default_llm=default_llm,
        )
        self.llms: Dict[str, LLM] = llm_config["llms"]
        self.llm: LLM = llm_config["default_llm"]
        self.default_llm_key: str = llm_config["default_llm_key"]
        
        # Usage tracker
        self.usage_tracker = UsageTracker(include_conversation_id=include_conversation_id)
        
        # System objects (self, llm, llm:name references)
        self._system_objects: Dict[str, Any] = {}
        if agent_self is not None:
            self._system_objects['self'] = agent_self
        self._system_objects['llm'] = self.llm
        
        # Update LLM special objects
        self._update_llm_special_objects()
    
    def _update_llm_special_objects(self) -> None:
        """Update special objects for LLMs: 'llm' (default) and 'llm:name' for each LLM."""
        update_llm_special_objects(system_objects=self._system_objects, llm=self.llm)
        
        # Add llm:name references for all LLMs
        for key, llm_instance in self.llms.items():
            self._system_objects[f'llm:{key}'] = llm_instance
    
    def switch_default_llm(self, default_llm: Union[LLM, str]) -> None:
        """
        Switch the default LLM to use for queries.
        
        Args:
            default_llm: Either an LLM instance or a string key to one of the LLMs in self.llms.
        
        Raises:
            KeyError: If default_llm is a string key that doesn't exist in self.llms.
            KeyError: If default_llm is an LLM instance that's not in self.llms.
        """
        if isinstance(default_llm, str):
            # default_llm is a key
            if default_llm not in self.llms:
                raise KeyError(f"Default LLM key '{default_llm}' not found in llms dictionary")
            self.llm = self.llms[default_llm]
            self.default_llm_key = default_llm
        else:
            # default_llm is an LLM instance
            # Find which key it corresponds to
            found_key = None
            for key, llm_instance in self.llms.items():
                if llm_instance is default_llm:
                    found_key = key
                    break
            if found_key is None:
                raise KeyError("Default LLM instance not found in llms dictionary")
            self.llm = default_llm
            self.default_llm_key = found_key
        
        # Update system objects
        self._update_llm_special_objects()
    
    def get_llm_for_run(self, llm_instance: Union[str, LLM] = "default") -> Dict[str, Any]:
        """
        Get the LLM instance to use for a run.
        
        Args:
            llm_instance: LLM instance to use for this run. Can be:
                - A string key to one of the LLMs in self.llms (default: "default")
                - An LLM instance from self.llms
        
        Returns:
            Dictionary with keys:
                - "llm": LLM - The LLM instance to use
                - "llm_key": str - The key for the LLM instance
        
        Raises:
            KeyError: If llm_instance is a string key that doesn't exist in self.llms.
            KeyError: If llm_instance is an LLM instance that's not in self.llms.
        """
        return get_llm_for_run(
            llms=self.llms,
            default_llm=self.llm,
            default_llm_key=self.default_llm_key,
            llm_instance=llm_instance,
        )
    
    def get_system_object(self, key: str) -> Any:
        """
        Get a system object by key.
        
        Args:
            key: System object key.
        
        Returns:
            The system object.
        
        Raises:
            KeyError: If the system object is not found.
        """
        return self._system_objects[key]
    
    def add_system_object(self, key: str, value: Any) -> None:
        """
        Add a system object.
        
        Args:
            key: System object key.
            value: The object to store.
        """
        self._system_objects[key.strip()] = value
    
    def get_total_usage(
        self,
        llm: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Optional[int]]:
        """
        Get total usage (tokens) optionally filtered by llm and/or conversation_id.
        
        Args:
            llm: Optional LLM identifier (key) to filter by. If None, includes all LLMs.
            conversation_id: Optional conversation ID to filter by. If None, includes all conversations.
        
        Returns:
            Dictionary with "input_tokens", "output_tokens", and "total_tokens".
        """
        return self.usage_tracker.get_total_usage(llm=llm, conversation_id=conversation_id)
    
    def get_total_cost(
        self,
        llm: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Optional[float]]:
        """
        Get total cost optionally filtered by llm and/or conversation_id.
        
        Args:
            llm: Optional LLM identifier (key) to filter by. If None, includes all LLMs.
            conversation_id: Optional conversation ID to filter by. If None, includes all conversations.
        
        Returns:
            Dictionary with "input_cost", "output_cost", and "total_cost".
        """
        return self.usage_tracker.get_total_cost(llm=llm, conversation_id=conversation_id)
    
    @property
    def system_objects(self) -> Dict[str, Any]:
        """
        Get system objects dictionary.
        
        Returns:
            Dictionary of system objects.
        """
        return self._system_objects

