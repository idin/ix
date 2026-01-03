"""
File system agent with file system tools and memory.
"""

import inspect
from functools import partial

from ..agent import Agent
from ...tools.file_system import (
    list_dir,
    list_dir_contents,
    get_file_status,
    change_path,
    copy_into,
    move_into,
    clone_to_path,
    delete,
    undelete,
    empty_dir,
    empty_recycle_bin,
    compare_files,
    compare_dirs,
)
from ...tools.file_system.memory import FileSystemMemory, undo


def add_file_system_tools(agent: Agent) -> None:
    # List of file system tool functions
        file_system_tool_functions = [
            list_dir,
            list_dir_contents,
            get_file_status,
            change_path,
            copy_into,
            move_into,
            clone_to_path,
            delete,
            undelete,
            empty_dir,
            empty_recycle_bin,
            compare_files,
            compare_dirs,
            undo,
        ]

        if not hasattr(agent, '_file_system_memory'):
            agent._file_system_memory = FileSystemMemory()
            agent._system_objects['file_system_memory'] = agent._file_system_memory
        
        # Bind file_system_memory to tools using functools.partial
        # Only bind to tools that accept file_system_memory parameter
        file_system_tools = []
        for tool_func in file_system_tool_functions:
            sig = inspect.signature(tool_func)
            if 'file_system_memory' in sig.parameters:
                # Tool accepts file_system_memory, bind it
                tool = partial(tool_func, file_system_memory=agent._file_system_memory)
            else:
                # Tool doesn't accept file_system_memory, use as-is
                tool = tool_func
            tool.__name__ = tool_func.__name__
            tool.__doc__ = tool_func.__doc__
            file_system_tools.append(tool)

        agent.add_tools(file_system_tools)


class FileSystemAgent(Agent):
    """
    Agent with file system tools and FileSystemMemory.
    
    Automatically sets up file system tools with memory tracking on initialization.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize FileSystemAgent with file system tools.
        
        Accepts all arguments from Agent.__init__.
        """
        super().__init__(*args, **kwargs)
        
        add_file_system_tools(agent=self)

