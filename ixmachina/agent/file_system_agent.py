"""
File system agent with file system tools and memory.
"""

from functools import partial

from .agent import Agent
from ..tools.file_system import (
    list_dir,
    list_dir_contents,
    get_file_status,
    change_file_path,
    move_file_into,
    clone_file_to_path,
    copy_file_into,
    change_dir_path,
    move_dir_into,
    clone_dir_to_path,
    copy_dir_into,
    change_path,
    move_into,
    clone_to_path,
    copy_into,
    delete_file,
    delete_dir,
    undelete,
    empty_dir,
    empty_recycle_bin,
    compare_files,
    compare_dirs,
)
from ..tools.file_system.memory import FileSystemMemory, undo


def add_file_system_tools(agent: Agent) -> None:
    # List of file system tool functions
        file_system_tool_functions = [
            list_dir,
            list_dir_contents,
            get_file_status,
            change_file_path,
            move_file_into,
            clone_file_to_path,
            copy_file_into,
            change_dir_path,
            move_dir_into,
            clone_dir_to_path,
            copy_dir_into,
            change_path,
            move_into,
            clone_to_path,
            copy_into,
            delete_file,
            delete_dir,
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
        file_system_tools = []
        for tool_func in file_system_tool_functions:
            tool = partial(tool_func, file_system_memory=agent._file_system_memory)
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

