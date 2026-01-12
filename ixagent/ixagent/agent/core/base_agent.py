"""
Base Agent class for basic chatbot-style interactions with LLMs.
"""

import json
import os
from typing import List, Dict, Optional, Callable, Any, Union

from ...llm import LLM
from ...llm.tools import prepare_tools_for_provider
from ...tools.constants import RESULT_KEY, SUCCESS_KEY, ERROR_KEY
from ...utils.usage_tracker import UsageTracker
from ixutils import set_cache_path
from ..cognition.llm_management import (
    initialize_llms,
    get_llm_for_run,
    update_llm_special_objects,
)
from ..tool_management.tool_management import add_tools_to_agent
from ..tool_management.tool_execution import execute_tool, extract_tool_output_value
from ..tool_management.tool_processing import process_tool_call
from ..execution.run_loop import execute_iteration, get_final_result
from ..utils.verbose import (
    print_iteration,
    print_conversation_context,
    print_llm_response,
    print_tool_calls,
    print_tool_result,
)
from ..utils.return_modes import (
    CHAT_RESPONSE_MODES,
    TOOL_OUTPUT_VALUE_MODES,
    TOOL_FULL_OUTPUT_MODES,
    ALL_VALID_MODES,
)


class BaseAgent:
    """
    Basic Agent class that works like a chatbot.

    Maintains a single conversation history and allows repeated interactions
    through a single run() method. Each call adds to the conversation
    and returns a response. Supports function calling with tools.
    """

    def __init__(
        self,
        llm: Union[LLM, Dict[str, LLM]],
        default_llm: Optional[Union[LLM, str]] = None,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Callable]] = None,
        verbose: bool = True,
        default_return_mode: Optional[str] = None,
        working_directory: Optional[str] = None,
    ) -> None:
        """
        Initialize a BaseAgent.

        Args:
            llm: Either a single LLM instance, or a dictionary of LLMs (keyed by name).
            default_llm: The default LLM to use. Can be:
                - An LLM instance (if llm is a dict)
                - A string key to one of the LLMs in the dictionary
                - If not provided and llm is a single LLM, that LLM is used
                - If not provided and llm is a dict, the first LLM in the dict is used
            system_prompt: Optional system prompt for instructions.
            tools: Optional list of callable functions to use as tools.
            verbose: If True, print detailed information about agent's thinking process.
            default_return_mode: Default return mode to use if not specified in run().
            working_directory: Optional working directory path for agent's persistent data
                (cache, databases, etc.). If provided, creates the directory if it doesn't exist.
        """
        # Set up working directory (lazy creation - only created when first needed)
        if working_directory:
            self.working_directory = working_directory
            # Set cache path to working_directory/cache
            # Both working directory and cache directory will be created lazily when first used
            cache_path = os.path.join(working_directory, "cache")
            set_cache_path(cache_path)
        else:
            self.working_directory = None
        
        # Handle LLM initialization
        llm_config = initialize_llms(llm=llm, default_llm=default_llm)
        self.llms = llm_config["llms"]
        self.llm = llm_config["default_llm"]
        self.default_llm_key = llm_config["default_llm_key"]
        
        self.system_prompt = system_prompt
        self.verbose = verbose
        self.default_return_mode = default_return_mode.lower() if default_return_mode else None
        # Usage tracker
        self.usage_tracker = UsageTracker(include_conversation_id=False)
        
        # Store original functions for execution
        self.tool_functions: Dict[str, Callable] = {}
        # Store converted tools for LLM (provider-specific format)
        self.tools: Optional[List[Dict[str, Any]]] = None
        # Store schemas for type conversion
        self.tool_schemas: Dict[str, Dict[str, Any]] = {}
        
        # Basic system objects (just self and llm)
        self._system_objects: Dict[str, Any] = {'self': self, 'llm': self.llm}
        
        # Update special objects when default LLM changes
        self._update_llm_special_objects()
        
        # Initialize conversation history (single conversation)
        if self.system_prompt:
            self.conversation_history: List[Dict[str, str]] = [
                {"role": "system", "content": self.system_prompt}
            ]
        else:
            self.conversation_history: List[Dict[str, str]] = []
        
        if tools:
            # Build tool function mapping
            for tool in tools:
                tool_name = tool.__name__
                self.tool_functions[tool_name] = tool
            
            # Prepare tools for current provider (conversion happens outside Agent)
            provider = self.llm.provider
            prepared = prepare_tools_for_provider(tools, provider)
            self.tools = prepared["tools"]
            self.tool_schemas = prepared["schemas"]
    
    def _ensure_working_directory(self) -> None:
        """
        Ensure working directory exists, creating it if necessary.
        
        Called lazily when working directory is first needed.
        """
        if self.working_directory:
            os.makedirs(self.working_directory, exist_ok=True)
    
    def _update_llm_special_objects(self) -> None:
        """Update special objects for LLMs: 'llm' (default) and 'llm:name' for each LLM."""
        update_llm_special_objects(system_objects=self._system_objects, llm=self.llm)
        
        # Remove old llm: prefixed special objects
        keys_to_remove = [key for key in self._system_objects.keys() if key.startswith('llm:')]
        for key in keys_to_remove:
            del self._system_objects[key]
        
        # Add all LLMs as special objects with 'llm:' prefix
        for llm_key, llm_instance in self.llms.items():
            self._system_objects[f'llm:{llm_key}'] = llm_instance
    
    def _get_llm_for_run(
        self,
        llm_instance: Union[str, LLM],
    ) -> Dict[str, Any]:
        """
        Get the LLM instance to use for a run and its key.
        
        Args:
            llm_instance: Either a string key to one of the LLMs in self.llms,
                or an LLM instance from self.llms.
        
        Returns:
            Dictionary with keys:
                - "llm": LLM - The LLM instance to use
                - "llm_key": str - The key for the LLM instance
        
        Raises:
            KeyError: If the key or instance is not found in self.llms.
        """
        return get_llm_for_run(
            llms=self.llms,
            default_llm=self.llm,
            default_llm_key=self.default_llm_key,
            llm_instance=llm_instance,
        )
    
    def switch_default_llm(self, default_llm: Union[LLM, str]) -> None:
        """
        Switch the default LLM to use for queries.
        
        Args:
            default_llm: Either an LLM instance or a string key to one of the LLMs in self.llms.
        """
        if isinstance(default_llm, str):
            if default_llm not in self.llms:
                raise KeyError(
                    f"LLM key '{default_llm}' not found in llms dictionary. "
                    f"Available keys: {list(self.llms.keys())}"
                )
            self.llm = self.llms[default_llm]
            self.default_llm_key = default_llm
        else:
            # default_llm is an LLM instance - find it in the dictionary
            found = False
            for key, llm_instance in self.llms.items():
                if llm_instance is default_llm:
                    self.llm = default_llm
                    self.default_llm_key = key
                    found = True
                    break
            if not found:
                raise KeyError("LLM instance not found in llms dictionary")
        
        # Update special objects
        self._update_llm_special_objects()

    def add_tools(self, tools: List[Callable]) -> None:
        """
        Add tools to the agent mid-conversation.
        
        Args:
            tools: List of callable functions to add as tools.
        """
        self.tools, self.tool_schemas = add_tools_to_agent(
            tool_functions=self.tool_functions,
            tools=self.tools,
            tool_schemas=self.tool_schemas,
            new_tools=tools,
            provider=self.llm.provider,
        )
    
    def _execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        return_raw: bool = False,
    ) -> Any:
        """
        Execute a tool function with given arguments.

        Args:
            tool_name: Name of the tool to execute.
            arguments: Arguments to pass to the tool.
            return_raw: If True, return raw result; if False, return as string.

        Returns:
            Tool execution result as a string (default) or raw result.
        """
        return execute_tool(
            tool_functions=self.tool_functions,
            tool_name=tool_name,
            arguments=arguments,
            return_raw=return_raw,
        )

    def _extract_tool_output_value(self, tool_result: Any) -> Any:
        """
        Extract the output value from a tool result, removing metadata.
        
        Uses the standard RESULT_KEY from tool constants to extract the primary output.
        If RESULT_KEY is present, returns it directly (standardized output).
        Otherwise falls back to removing success/error metadata and returning the remaining fields.
        
        Args:
            tool_result: The raw tool result with metadata.
        
        Returns:
            The extracted output value without metadata.
        """
        return extract_tool_output_value(tool_result)

    def run(
        self,
        input_text: str,
        return_mode: Optional[str] = None,
        llm_instance: Union[str, LLM] = "default",
        max_iterations: int = 10,
    ) -> Any:
        """
        Process input and return response, maintaining conversation history.

        Supports function calling - if the LLM requests a function call,
        executes it and continues the conversation.

        Args:
            input_text: The user's input message.
            return_mode: What to return from the agent. Options:
                - "chat_response" (default): Return the LLM's text response.
                - "tool_output_value": Return the tool's output data only (removes "success" and "error" metadata).
                - "tool_full_output": Return the full tool output including "success" and "error" metadata fields.
            llm_instance: LLM instance to use for this run. Can be:
                - A string key to one of the LLMs in self.llms (default: "default")
                - An LLM instance from self.llms

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
                "Must be one of: 'chat_response' (or 'response'), "
                "'tool_output_value' (or 'tool_value', 'output_value', 'value'), "
                "'tool_full_output' (or 'tool_full', 'full_output', 'full')"
            )
        
        # Determine which LLM to use for this run
        llm_config = self._get_llm_for_run(llm_instance=llm_instance)
        run_llm = llm_config["llm"]
        llm_key = llm_config["llm_key"]
        
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": input_text})

        # Query LLM with full conversation history and tools
        # Tools are cached in __init__ to avoid repeated conversion
        iteration = 0
        accumulated_tool_results = []  # Accumulate results across iterations for tool return modes
        
        while iteration < max_iterations:
            iteration += 1
            
            should_continue, result = execute_iteration(
                iteration=iteration,
                max_iterations=max_iterations,
                run_llm=run_llm,
                conversation_history=self.conversation_history,
                tools=self.tools,
                usage_tracker=self.usage_tracker,
                llm_key=llm_key,
                return_mode=return_mode,
                process_tool_call=self._process_tool_call,
                accumulated_tool_results=accumulated_tool_results,
                verbose=self.verbose,
            )
            
            if not should_continue:
                return result
        
        # If we've exceeded max iterations, return accumulated tool results or error
        return get_final_result(
            return_mode=return_mode,
            accumulated_tool_results=accumulated_tool_results,
        )
    
    def _process_tool_call(
        self,
        tool_call: Dict[str, Any],
    ) -> Any:
        """
        Process a single tool call: extract, parse, convert types, execute.

        Args:
            tool_call: The tool call dictionary from the LLM response.

        Returns:
            Raw result from the tool execution.
        """
        return process_tool_call(
            tool_call=tool_call,
            tool_schemas=self.tool_schemas,
            execute_tool_func=self._execute_tool,
            conversation_history=self.conversation_history,
            verbose=self.verbose,
        )
    
    def reset_conversation(self) -> None:
        """
        Reset conversation, clearing all messages except system prompt.
        """
        if self.system_prompt:
            self.conversation_history = [
                {"role": "system", "content": self.system_prompt}
            ]
        else:
            self.conversation_history = []
    
    def get_total_usage(
        self,
        llm: Optional[str] = None,
    ) -> Dict[str, Optional[int]]:
        """
        Get total usage (tokens) optionally filtered by llm.
        
        Args:
            llm: Optional LLM identifier (key) to filter by. If None, includes all LLMs.
        
        Returns:
            Dictionary with "input_tokens", "output_tokens", and "total_tokens".
        """
        return self.usage_tracker.get_total_usage(llm=llm)
    
    def get_total_cost(
        self,
        llm: Optional[str] = None,
    ) -> Dict[str, Optional[float]]:
        """
        Get total cost optionally filtered by llm.
        
        Args:
            llm: Optional LLM identifier (key) to filter by. If None, includes all LLMs.
        
        Returns:
            Dictionary with "input_cost", "output_cost", and "total_cost".
        """
        return self.usage_tracker.get_total_cost(llm=llm)

