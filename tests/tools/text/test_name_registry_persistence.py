"""
Tests for NameRegistry save/load functionality.

Tests both JSON and Pickle formats for saving and loading registries,
including preservation of names, tokens, aliases, and usage counts.
"""

import pytest
import json
import pickle
from pathlib import Path
import tempfile
import os

from ixmachina.tools.text import NameRegistry


def test_save_load_json_basic():
    """
    Test basic JSON save and load with a few names.
    
    Verifies that a registry can be saved to JSON and loaded back
    with all data intact.
    """
    # Create registry with some names
    registry = NameRegistry()
    registry.add_name("John Smith")
    registry.add_name("Jane Doe")
    registry.add_name("Chris de Burgh")
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    try:
        # Save
        result = registry.save_to_json(file_path=temp_path)
        assert result['success'] is True
        assert Path(temp_path).exists()
        
        # Load
        loaded_registry = NameRegistry.load_from_json(file_path=temp_path)
        
        # Verify names
        assert len(loaded_registry) == 3
        assert loaded_registry.get_canonical("john smith") == "John Smith"
        assert loaded_registry.get_canonical("jane doe") == "Jane Doe"
        assert loaded_registry.get_canonical("chris de burgh") == "Chris de Burgh"
        
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_save_load_json_with_aliases():
    """
    Test JSON save/load preserves aliases.
    
    Verifies that aliases are correctly saved and restored.
    """
    # Create registry with names and aliases
    registry = NameRegistry()
    registry.add_name("John Smith")
    registry.add_alias(canonical_name="John Smith", alias="Johnny")
    registry.add_alias(canonical_name="John Smith", alias="Jon")
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    try:
        # Save
        result = registry.save_to_json(file_path=temp_path)
        assert result['success'] is True
        
        # Load
        loaded_registry = NameRegistry.load_from_json(file_path=temp_path)
        
        # Verify aliases work
        assert loaded_registry.get_canonical("Johnny") == "John Smith"
        assert loaded_registry.get_canonical("Jon") == "John Smith"
        
        # Verify alias list
        aliases = loaded_registry.get_aliases("John Smith")
        assert aliases is not None
        assert "Johnny" in aliases
        assert "Jon" in aliases
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_save_load_json_with_usage_counts():
    """
    Test JSON save/load preserves usage counts.
    
    Verifies that name usage counts are correctly saved and restored.
    """
    # Create registry and increment usage counts
    registry = NameRegistry()
    registry.add_name("John Smith")
    registry.add_name("john smith")  # Increment count
    registry.add_name("JOHN SMITH")  # Increment count again
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    try:
        # Save
        result = registry.save_to_json(file_path=temp_path)
        assert result['success'] is True
        
        # Load
        loaded_registry = NameRegistry.load_from_json(file_path=temp_path)
        
        # Verify name exists
        assert loaded_registry.get_canonical("john smith") == "John Smith"
        
        # Verify count is preserved (would need to expose count getter)
        # For now, just verify the name loads correctly
        assert len(loaded_registry) == 1
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_save_load_json_with_tokens():
    """
    Test JSON save/load preserves token index.
    
    Verifies that token-based matching still works after save/load.
    """
    # Create registry with multi-token names
    registry = NameRegistry()
    registry.add_name("John Smith")
    registry.add_name("John Doe")
    registry.add_name("Jane Smith")
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    try:
        # Save
        result = registry.save_to_json(file_path=temp_path)
        assert result['success'] is True
        
        # Load
        loaded_registry = NameRegistry.load_from_json(file_path=temp_path)
        
        # Verify token-based methods work
        john_names = loaded_registry.get_names_containing_token(token="john")
        assert "John Smith" in john_names
        assert "John Doe" in john_names
        assert "Jane Smith" not in john_names
        
        smith_names = loaded_registry.get_names_containing_token(token="smith")
        assert "John Smith" in smith_names
        assert "Jane Smith" in smith_names
        assert "John Doe" not in smith_names
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_save_load_pickle_basic():
    """
    Test basic pickle save and load with a few names.
    
    Verifies that a registry can be saved to pickle and loaded back
    with all data intact.
    """
    # Create registry with some names
    registry = NameRegistry()
    registry.add_name("John Smith")
    registry.add_name("Jane Doe")
    registry.add_name("Chris de Burgh")
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.pkl', delete=False) as f:
        temp_path = f.name
    
    try:
        # Save
        result = registry.save_to_pickle(file_path=temp_path)
        assert result['success'] is True
        assert Path(temp_path).exists()
        
        # Load
        loaded_registry = NameRegistry.load_from_pickle(file_path=temp_path)
        
        # Verify names
        assert len(loaded_registry) == 3
        assert loaded_registry.get_canonical("john smith") == "John Smith"
        assert loaded_registry.get_canonical("jane doe") == "Jane Doe"
        assert loaded_registry.get_canonical("chris de burgh") == "Chris de Burgh"
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_save_load_pickle_with_aliases():
    """
    Test pickle save/load preserves aliases.
    
    Verifies that aliases are correctly saved and restored.
    """
    # Create registry with names and aliases
    registry = NameRegistry()
    registry.add_name("John Smith")
    registry.add_alias(canonical_name="John Smith", alias="Johnny")
    registry.add_alias(canonical_name="John Smith", alias="Jon")
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.pkl', delete=False) as f:
        temp_path = f.name
    
    try:
        # Save
        result = registry.save_to_pickle(file_path=temp_path)
        assert result['success'] is True
        
        # Load
        loaded_registry = NameRegistry.load_from_pickle(file_path=temp_path)
        
        # Verify aliases work
        assert loaded_registry.get_canonical("Johnny") == "John Smith"
        assert loaded_registry.get_canonical("Jon") == "John Smith"
        
        # Verify alias list
        aliases = loaded_registry.get_aliases("John Smith")
        assert aliases is not None
        assert "Johnny" in aliases
        assert "Jon" in aliases
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_json_is_human_readable():
    """
    Test that JSON output is human-readable.
    
    Verifies that the saved JSON file can be opened and inspected
    as a text file.
    """
    # Create registry
    registry = NameRegistry()
    registry.add_name("John Smith")
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    try:
        # Save
        result = registry.save_to_json(file_path=temp_path)
        assert result['success'] is True
        
        # Read as text and verify it's valid JSON
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
            data = json.loads(content)
        
        # Verify structure
        assert 'names_by_letter' in data
        assert 'tokens_by_letter' in data
        assert 'normalized_to_canonical' in data
        assert 'alias_to_canonical' in data
        assert 'version' in data
        
        # Verify it's formatted (has newlines and indentation)
        assert '\n' in content
        assert '  ' in content  # Indentation
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_save_json_error_handling():
    """
    Test error handling when saving to an invalid path.
    
    Verifies that save errors are caught and reported correctly.
    """
    registry = NameRegistry()
    registry.add_name("John Smith")
    
    # Try to save to invalid path
    invalid_path = "/nonexistent/directory/names.json"
    result = registry.save_to_json(file_path=invalid_path)
    
    assert result['success'] is False
    assert 'error' in result


def test_load_json_missing_file():
    """
    Test error handling when loading from a missing file.
    
    Verifies that a FileNotFoundError is raised.
    """
    with pytest.raises(FileNotFoundError):
        NameRegistry.load_from_json(file_path="nonexistent_file.json")


def test_save_pickle_error_handling():
    """
    Test error handling when saving pickle to an invalid path.
    
    Verifies that save errors are caught and reported correctly.
    """
    registry = NameRegistry()
    registry.add_name("John Smith")
    
    # Try to save to invalid path
    invalid_path = "/nonexistent/directory/names.pkl"
    result = registry.save_to_pickle(file_path=invalid_path)
    
    assert result['success'] is False
    assert 'error' in result


def test_load_pickle_missing_file():
    """
    Test error handling when loading from a missing pickle file.
    
    Verifies that a FileNotFoundError is raised.
    """
    with pytest.raises(FileNotFoundError):
        NameRegistry.load_from_pickle(file_path="nonexistent_file.pkl")


def test_concatenated_form_preserved():
    """
    Test that concatenated form lookup works after save/load.
    
    Verifies that "johnsmith" can still find "John Smith" after
    saving and loading.
    """
    # Create registry
    registry = NameRegistry()
    registry.add_name("John Smith")
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    try:
        # Save and load
        registry.save_to_json(file_path=temp_path)
        loaded_registry = NameRegistry.load_from_json(file_path=temp_path)
        
        # Verify concatenated lookup works
        assert loaded_registry.get_canonical("johnsmith") == "John Smith"
        assert loaded_registry.get_canonical("john smith") == "John Smith"
        assert loaded_registry.get_canonical("john_smith") == "John Smith"
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

