"""
Advanced Agent class for chatbot-style interactions with LLMs.
"""

import os
from typing import List, Dict, Optional, Callable, Any, Union

from ...llm import LLM
from ...llm.tools import prepare_tools_for_provider
from ixutils import set_cache_path
from .initialization import enhance_system_prompt, initialize_agent_components
from .conversation_management import (
    start_conversation as start_conversation_helper,
    get_conversation as get_conversation_helper,
    reset_conversation as reset_conversation_helper,
    forget_conversation as forget_conversation_helper,
)
from .object_saving import save_objects_to_agent
from ..memory.memory import Memory
from ..memory.references import ObjectReferenceResolver
from ..memory.save_objects import (
    ObjectToSave,
    MultipleObjectsToSave,
    save_as,
)
from ..cognition.cognition import Cognition
from ..tool_management.agent_tool_execution import (
    execute_tool as execute_tool_helper,
    process_tool_call as process_tool_call_helper,
    convert_arguments_to_types as convert_arguments_to_types_helper,
)
from ..tool_management.tool_execution import extract_tool_output_value
from ..utils.return_modes import ALL_VALID_MODES
from ..execution.agent_run_loop import run_agent
from .exceptions import SpecialObjectKeyError


class Agent:
    """
    Advanced Agent class that works like a chatbot.
    
    Uses modular architecture with Memory and Cognition components.
    """

    def __init__(
        self,
        llm: Union[LLM, Dict[str, LLM]],
        default_llm: Optional[Union[LLM, str]] = None,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Callable]] = None,
        system_object_prefix: str = "sys:",
        global_object_prefix: str = "obj:",
        conversation_object_prefix: str = "conv_obj:",
        tool_call_object_prefix: str = "tool_obj:",
        verbose: bool = True,
        default_return_mode: Optional[str] = None,
        working_directory: Optional[str] = None,
    ) -> None:
        """
        Initialize an Agent.
        
        Args:
            llm: Either a single LLM instance, or a dictionary of LLMs (keyed by name).
            default_llm: The default LLM to use. Can be:
                - An LLM instance (if llm is a dict)
                - A string key to one of the LLMs in the dictionary
                - If not provided and llm is a single LLM, that LLM is used
                - If not provided and llm is a dict, the first LLM in the dict is used
            system_prompt: Optional system prompt for instructions.
            tools: Optional list of callable functions to use as tools.
            system_object_prefix: Prefix for system object references in tool arguments (default: "sys:").
                References must be wrapped in angle brackets: <sys:key>. Examples: <sys:self>, <sys:llm>.
            global_object_prefix: Prefix for global saved object references in tool arguments (default: "obj:").
                References must be wrapped in angle brackets: <obj:object_name> for global objects.
            conversation_object_prefix: Prefix for conversation-scoped saved object references (default: "conv_obj:").
                References must be wrapped in angle brackets: <conv_obj:conversation_id:object_name>.
            tool_call_object_prefix: Prefix for tool call result references in tool arguments (default: "tool_obj:").
                References must be wrapped in angle brackets: <tool_obj:conversation_id:tool_call_id>.
            verbose: If True, print detailed information about agent's thinking process.
            working_directory: Optional working directory path for agent's persistent data
                (cache, databases, etc.). If provided, creates the directory if it doesn't exist.
        """
        # Set up working directory
        if working_directory:
            self.working_directory = working_directory
            cache_path = os.path.join(working_directory, "cache")
            set_cache_path(cache_path)
        else:
            self.working_directory = None
        
        # Enhance system prompt with memory guidance
        enhanced_system_prompt = enhance_system_prompt(system_prompt)
        self.system_prompt = enhanced_system_prompt
        self.verbose = verbose
        self.default_return_mode = default_return_mode.lower() if default_return_mode else None
        
        # Initialize Cognition component (LLMs, usage tracking, system objects)
        self.cognition = Cognition(
            llm=llm,
            default_llm=default_llm,
            include_conversation_id=True,
            agent_self=self,
        )
        
        # Initialize Memory component
        self.memory = Memory(
            system_object_prefix=system_object_prefix,
            global_object_prefix=global_object_prefix,
            conversation_object_prefix=conversation_object_prefix,
            tool_call_object_prefix=tool_call_object_prefix,
        )
        
        # Current conversation ID (defaults to "default")
        self.current_conversation_id = "default"
        
        # Object prefixes (normalized)
        self.system_object_prefix = system_object_prefix.lower()
        self.global_object_prefix = global_object_prefix.lower()
        self.conversation_object_prefix = conversation_object_prefix.lower()
        self.tool_call_object_prefix = tool_call_object_prefix.lower()
        
        # Reference resolver will be initialized lazily via property
        self._reference_resolver: Optional[ObjectReferenceResolver] = None
        
        # Initialize tool management (temporary - until Toolbox is created)
        self.tool_functions: Dict[str, Callable] = {}
        self.tools: Optional[List[Dict[str, Any]]] = None
        self.tool_schemas: Dict[str, Dict[str, Any]] = {}
        
        # Initialize agent components (tools, schemas)
        initialize_agent_components(
            agent_instance=self,
            system_object_prefix=system_object_prefix,
            global_object_prefix=global_object_prefix,
            conversation_object_prefix=conversation_object_prefix,
            tool_call_object_prefix=tool_call_object_prefix,
            default_return_mode=default_return_mode,
            tools=tools,
            memory=self.memory,
            current_conversation_id_getter=lambda: self.current_conversation_id,
            llm_provider=self.cognition.llm.provider,
        )
        
        # Initialize default conversation
        self.start_conversation()
    
    @property
    def _reference_resolver_instance(self) -> ObjectReferenceResolver:
        """
        Get or create the object reference resolver.
        
        Returns:
            ObjectReferenceResolver instance.
        """
        if self._reference_resolver is None:
            self._reference_resolver = ObjectReferenceResolver(
                memory=self.memory,
                system_objects=self.cognition.system_objects,
                system_object_prefix=self.system_object_prefix,
                global_object_prefix=self.global_object_prefix,
                conversation_object_prefix=self.conversation_object_prefix,
                tool_call_object_prefix=self.tool_call_object_prefix,
            )
        return self._reference_resolver
    
    def _convert_arguments_to_types(
        self,
        arguments: Dict[str, Any],
        tool_schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Convert function arguments to appropriate Python types based on schema.
        
        Args:
            arguments: Parsed JSON arguments dictionary.
            tool_schema: Tool schema in provider-specific format.
        
        Returns:
            Arguments dictionary with properly typed values.
        """
        return convert_arguments_to_types_helper(
            arguments=arguments,
            tool_schema=tool_schema,
        )
    
    def _process_tool_call(
        self,
        tool_call: Dict[str, Any],
        conversation_id: Optional[str] = None,
    ) -> Any:
        """
        Process a single tool call: extract, parse, convert types, execute, and track.
        
        Args:
            tool_call: The tool call dictionary from the LLM response.
            conversation_id: ID of the conversation.
        
        Returns:
            Raw result from the tool execution.
        """
        if conversation_id is None:
            conversation_id = self.current_conversation_id
        
        file_system_memory = getattr(self, '_file_system_memory', None)
        
        return process_tool_call_helper(
            tool_call=tool_call,
            tool_schemas=self.tool_schemas,
            tool_functions=self.tool_functions,
            reference_resolver=self._reference_resolver_instance,
            memory=self.memory,
            current_conversation_id=self.current_conversation_id,
            file_system_memory=file_system_memory,
            verbose=self.verbose,
            convert_arguments_to_types_func=self._convert_arguments_to_types,
        )
    
    def _extract_tool_output_value(self, tool_result: Any) -> Any:
        """
        Extract the output value from a tool result, removing metadata.
        
        Args:
            tool_result: The raw tool result with metadata.
        
        Returns:
            The extracted output value without metadata.
        """
        return extract_tool_output_value(tool_result)
    
    def save_as(
        self,
        *,
        name: Optional[str] = None,
        obj: Optional[Any] = None,
        conversation_scoped: bool = False,
        conversation_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Union[ObjectToSave, MultipleObjectsToSave]:
        """
        Save an object or multiple objects as saved objects that can be referenced later.
        
        When called on an agent instance, actually saves the object(s) to the agent's storage.
        Can be called in two ways:
        1. Single object: save_as(name="key", obj=obj)
        2. Multiple objects: save_as(key1=obj1, key2=obj2, ...)
        
        Args:
            name: Name to save the object under (for single save).
            obj: The object to save (for single save).
            conversation_scoped: If True, save as conversation-scoped object.
                              If False, save as global object (default).
            conversation_id: Conversation ID for conversation-scoped objects.
                           Uses current conversation if not provided.
            **kwargs: Named objects to save (for multiple save). conversation_scoped applies to all.
        
        Returns:
            ObjectToSave wrapper for single save, or ObjectsToSave for multiple save.
        """
        result = save_as(name=name, obj=obj, conversation_scoped=conversation_scoped, **kwargs)
        
        # Use current conversation ID if not provided for conversation-scoped objects
        if conversation_id is None:
            conversation_id = self.current_conversation_id
        
        # Actually save the object(s) to agent storage
        save_objects_to_agent(
            result=result,
            memory=self.memory,
            conversation_id=conversation_id,
        )
        
        return result
    
    def switch_default_llm(self, default_llm: Union[LLM, str]) -> None:
        """
        Switch the default LLM to use for queries.
        
        Args:
            default_llm: Either an LLM instance or a string key to one of the LLMs in self.cognition.llms.
        """
        self.cognition.switch_default_llm(default_llm=default_llm)
    
    def start_conversation(self, conversation_id: Optional[str] = None) -> None:
        """
        Start a new conversation with the given ID.
        
        Initializes the conversation with the system prompt if available.
        Sets this conversation as the current one.
        
        Args:
            conversation_id: Optional conversation ID. Uses current_conversation_id if not provided.
        """
        self.current_conversation_id = start_conversation_helper(
            conversation_id=conversation_id,
            current_conversation_id=self.current_conversation_id,
            memory=self.memory,
            system_prompt=self.system_prompt,
        )
    
    def _get_conversation(self, conversation_id: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Get conversation history for a given ID.
        
        Args:
            conversation_id: Optional conversation ID. Uses current_conversation_id if not provided.
        
        Returns:
            List of conversation messages.
        
        Raises:
            ValueError: If conversation doesn't exist.
        """
        return get_conversation_helper(
            conversation_id=conversation_id,
            current_conversation_id=self.current_conversation_id,
            memory=self.memory,
        )
    
    def reset_conversation(self, conversation_id: Optional[str] = None) -> None:
        """
        Reset a conversation, clearing all messages except system prompt.
        
        Args:
            conversation_id: Optional conversation ID. Uses current_conversation_id if not provided.
        """
        reset_conversation_helper(
            conversation_id=conversation_id,
            current_conversation_id=self.current_conversation_id,
            memory=self.memory,
            system_prompt=self.system_prompt,
        )
    
    def forget_conversation(self, conversation_id: Optional[str] = None) -> None:
        """
        Forget a conversation completely, or all conversations if no ID provided.
        
        Note: Usage tracking and tool call tracking for deleted conversations are preserved.
        
        Args:
            conversation_id: Optional conversation ID. If None, forgets all conversations.
        """
        new_current_id = forget_conversation_helper(
            conversation_id=conversation_id,
            current_conversation_id=self.current_conversation_id,
            memory=self.memory,
        )
        if new_current_id is not None:
            self.current_conversation_id = new_current_id
    
    def run(
        self,
        input_text: str,
        conversation_id: Optional[str] = None,
        return_mode: Optional[str] = None,
        llm_instance: Union[str, LLM] = "default",
        max_iterations: int = 10,
    ) -> Any:
        """
        Process input and return response, maintaining conversation history.
        
        Args:
            input_text: The user's input message.
            conversation_id: Optional conversation ID. Uses default if not provided.
            return_mode: What to return from the agent. Options:
                - "chat_response" (default): Return the LLM's text response.
                - "tool_output_value": Return the tool's output data only (removes "success" and "error" metadata).
                - "tool_full_output": Return the full tool output including "success" and "error" metadata fields.
            llm_instance: LLM instance to use for this run. Can be:
                - A string key to one of the LLMs in self.cognition.llms (default: "default")
                - An LLM instance from self.cognition.llms
        
        Returns:
            The agent's response based on return_mode:
                - "chat_response": The LLM's text response (default).
                - "tool_output_value": Tool output data only (without success/error metadata).
                - "tool_full_output": Full tool output with success/error metadata.
        """
        return_mode = return_mode or self.default_return_mode or "chat_response"
        
        # Validate return_mode
        if return_mode not in ALL_VALID_MODES:
            raise ValueError(
                f"Invalid return_mode: {return_mode}. "
                "Must be one of: 'chat_response' (or 'response', 'chat'), "
                "'tool_output_value' (or 'tool_value', 'output_value', 'value'), "
                "'tool_full_output' (or 'tool_full', 'full_output', 'full')"
            )
        
        # Determine which LLM to use for this run
        llm_config = self.cognition.get_llm_for_run(llm_instance=llm_instance)
        run_llm = llm_config["llm"]
        llm_key = llm_config["llm_key"]
        
        # Set as current conversation for tool execution context
        # (Built-in tools like load/remember use current_conversation_id)
        if conversation_id is not None:
            self.current_conversation_id = conversation_id
        
        return run_agent(
            input_text=input_text,
            memory=self.memory,
            current_conversation_id=self.current_conversation_id,
            conversation_id=conversation_id,
            return_mode=return_mode,
            run_llm=run_llm,
            llm_key=llm_key,
            tools=self.tools,
            usage_tracker=self.cognition.usage_tracker,
            process_tool_call_func=self._process_tool_call,
            extract_tool_output_value_func=self._extract_tool_output_value,
            verbose=self.verbose,
            max_iterations=max_iterations,
        )
    
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
        return self.cognition.get_total_usage(llm=llm, conversation_id=conversation_id)
    
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
        return self.cognition.get_total_cost(llm=llm, conversation_id=conversation_id)
