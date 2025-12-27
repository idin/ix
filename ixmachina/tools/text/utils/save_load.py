"""
Save and load operations for NameRegistry.

Handles saving and loading registry data in JSON and Pickle formats.
"""

import json
import pickle
from pathlib import Path
from collections import defaultdict

from .first_letter_dict import FirstLetterDict


def save_to_json(registry, file_path: str) -> dict:
    """
    Save the registry to a JSON file.
    
    JSON format is human-readable and portable across Python versions.
    Good for inspection, debugging, and version control.
    
    Args:
        registry: NameRegistry instance to save.
        file_path: Path where the JSON file should be saved.
        
    Returns:
        Dictionary with success status and file path or error.
    """
    try:
        path = Path(file_path)
        
        # Convert FirstLetterDict to regular dict for JSON serialization
        def first_letter_dict_to_dict(fld: FirstLetterDict) -> dict:
            """Convert FirstLetterDict to regular dict."""
            return dict(fld.items())
        
        # Prepare data for JSON serialization
        data = {
            'names_by_letter': registry._names_by_letter,
            'tokens_by_letter': registry._tokens_by_letter,
            'normalized_to_canonical': first_letter_dict_to_dict(registry._normalized_to_canonical),
            'strict_to_canonical': first_letter_dict_to_dict(registry._strict_to_canonical),
            'concatenated_to_canonical': first_letter_dict_to_dict(registry._concatenated_to_canonical),
            'alias_to_canonical': first_letter_dict_to_dict(registry._alias_to_canonical),
            'total_lookups': registry._total_lookups,
            'version': '1.0'  # For future compatibility
        }
        
        # Save to JSON with pretty formatting
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return {
            'success': True,
            'file_path': str(path.resolve())
        }
        
    except Exception as e:
        return {
            'success': False,
            'file_path': file_path,
            'error': str(e)
        }


def load_from_json(file_path: str):
    """
    Load a registry from a JSON file.
    
    Args:
        file_path: Path to the JSON file to load.
        
    Returns:
        A new NameRegistry instance loaded from the file.
        
    Raises:
        FileNotFoundError: If the file doesn't exist.
        json.JSONDecodeError: If the file is not valid JSON.
        KeyError: If the file is missing required fields.
    """
    # Import here to avoid circular dependency
    from ..name_registry import NameRegistry
    
    path = Path(file_path)
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create new instance
    registry = NameRegistry()
    
    # Restore data structures
    registry._names_by_letter = defaultdict(dict, data['names_by_letter'])
    registry._tokens_by_letter = defaultdict(dict, data['tokens_by_letter'])
    registry._total_lookups = data.get('total_lookups', 0)
    
    # Efficiently restore FirstLetterDict instances using from_dict
    registry._normalized_to_canonical = FirstLetterDict.from_dict(data['normalized_to_canonical'])
    registry._strict_to_canonical = FirstLetterDict.from_dict(data['strict_to_canonical'])
    registry._concatenated_to_canonical = FirstLetterDict.from_dict(data['concatenated_to_canonical'])
    registry._alias_to_canonical = FirstLetterDict.from_dict(data['alias_to_canonical'])
    
    return registry


def save_to_pickle(registry, file_path: str) -> dict:
    """
    Save the registry to a pickle file.
    
    Pickle format is faster and simpler than JSON, but not human-readable.
    Use this for production when you don't need to inspect the file contents.
    
    Warning: Pickle files are Python version-dependent and can have security
    implications when loading untrusted data.
    
    Args:
        registry: NameRegistry instance to save.
        file_path: Path where the pickle file should be saved.
        
    Returns:
        Dictionary with success status and file path or error.
    """
    try:
        path = Path(file_path)
        
        # Save entire instance to pickle
        with open(path, 'wb') as f:
            pickle.dump(registry, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        return {
            'success': True,
            'file_path': str(path.resolve())
        }
        
    except Exception as e:
        return {
            'success': False,
            'file_path': file_path,
            'error': str(e)
        }


def load_from_pickle(file_path: str):
    """
    Load a registry from a pickle file.
    
    Warning: Only load pickle files from trusted sources, as pickle can
    execute arbitrary code during deserialization.
    
    Args:
        file_path: Path to the pickle file to load.
        
    Returns:
        A NameRegistry instance loaded from the file.
        
    Raises:
        FileNotFoundError: If the file doesn't exist.
        pickle.UnpicklingError: If the file is not a valid pickle.
    """
    # Import here to avoid circular dependency
    from ..name_registry import NameRegistry
    
    path = Path(file_path)
    
    with open(path, 'rb') as f:
        registry = pickle.load(f)
    
    # Verify it's a NameRegistry instance
    if not isinstance(registry, NameRegistry):
        raise TypeError(f"Loaded object is not a NameRegistry instance")
    
    return registry

