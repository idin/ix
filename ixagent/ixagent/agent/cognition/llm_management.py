"""
LLM management utilities for BaseAgent.
"""

from typing import Dict, Optional, Union, Any

from ...llm import LLM


def initialize_llms(
    *,
    llm: Union[LLM, Dict[str, LLM]],
    default_llm: Optional[Union[LLM, str]],
) -> Dict[str, Any]:
    """
    Initialize LLM configuration for BaseAgent.
    
    Args:
        llm: Either a single LLM instance, or a dictionary of LLMs (keyed by name).
        default_llm: The default LLM to use.
    
    Returns:
        Dictionary with keys:
            - "llms": Dict[str, LLM] - Dictionary of all LLMs (normalized to dict format)
            - "default_llm": LLM - The default LLM instance
            - "default_llm_key": str - The key for the default LLM
    """
    if isinstance(llm, dict):
        # Multiple LLMs provided
        llms = llm
        
        # Determine default LLM
        if default_llm is None:
            # Use first LLM in dict as default
            default_key = next(iter(llms.keys()))
            default = llms[default_key]
        elif isinstance(default_llm, str):
            # default_llm is a key
            if default_llm not in llms:
                raise KeyError(f"Default LLM key '{default_llm}' not found in llms dictionary")
            default_key = default_llm
            default = llms[default_key]
        else:
            # default_llm is an LLM instance
            # Find which key it corresponds to
            default_key = None
            for key, llm_instance in llms.items():
                if llm_instance is default_llm:
                    default_key = key
                    break
            if default_key is None:
                raise KeyError("Default LLM instance not found in llms dictionary")
            default = default_llm
        
        return {
            "llms": llms,
            "default_llm": default,
            "default_llm_key": default_key,
        }
    else:
        # Single LLM provided - normalize to dict format
        return {
            "llms": {"default": llm},
            "default_llm": llm,
            "default_llm_key": "default",
        }


def get_llm_for_run(
    *,
    llms: Union[LLM, Dict[str, LLM]],
    default_llm: Optional[LLM],
    default_llm_key: Optional[str],
    llm_instance: Union[str, LLM],
) -> Dict[str, Any]:
    """
    Get the LLM instance to use for a run.
    
    Args:
        llms: Either a single LLM instance, or a dictionary of LLMs.
        default_llm: The default LLM instance.
        default_llm_key: The key for the default LLM (if using dict).
        llm_instance: LLM instance to use for this run.
    
    Returns:
        Dictionary with keys:
            - "llm": LLM - The LLM instance to use
            - "llm_key": str - The key for the LLM instance
    """
    if isinstance(llms, dict):
        # Multiple LLMs available
        if llm_instance == "default":
            return {
                "llm": default_llm,
                "llm_key": default_llm_key,
            }
        elif isinstance(llm_instance, str):
            # llm_instance is a key
            if llm_instance not in llms:
                raise KeyError(f"LLM key '{llm_instance}' not found in llms dictionary")
            return {
                "llm": llms[llm_instance],
                "llm_key": llm_instance,
            }
        else:
            # llm_instance is an LLM instance
            # Find which key it corresponds to
            for key, llm in llms.items():
                if llm is llm_instance:
                    return {
                        "llm": llm,
                        "llm_key": key,
                    }
            raise KeyError("LLM instance not found in llms dictionary")
    else:
        # Single LLM - always use it
        return {
            "llm": llms,
            "llm_key": "default",
        }


def update_llm_special_objects(
    *,
    system_objects: Dict[str, any],
    llm: LLM,
) -> None:
    """
    Update special objects dictionary with LLM reference.
    
    Args:
        system_objects: Dictionary of system objects to update.
        llm: The LLM instance to add.
    """
    system_objects['llm'] = llm

