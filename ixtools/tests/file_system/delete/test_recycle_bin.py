"""
Tests for recycle bin utility functions.
"""

import os
import pytest

from ixtools.file_system.delete.recycle_bin import (
    get_recycle_bin_path,
    set_recycle_bin_path,
    get_recycle_bin_index_path,
    ensure_recycle_bin_exists,
)
from ixtools.file_system.constants import DEFAULT_RECYCLE_BIN_NAME
from ixtools.file_system.path_utils import path_exists
from ixtools.file_system.delete import delete


def test_get_recycle_bin_path_default():
    """Test get_recycle_bin_path returns default path when no override is set."""
    # Reset to default first
    set_recycle_bin_path(path=None)
    
    home_dir = os.path.expanduser("~")
    expected_path = os.path.join(home_dir, DEFAULT_RECYCLE_BIN_NAME)
    
    actual_path = get_recycle_bin_path()
    
    assert actual_path == expected_path


def test_set_recycle_bin_path_custom():
    """Test set_recycle_bin_path sets a custom path."""
    # Save original path
    original_path = get_recycle_bin_path()
    
    try:
        # Set custom path
        custom_path = "/tmp/test_recycle_bin_custom"
        set_recycle_bin_path(path=custom_path)
        
        # Verify get_recycle_bin_path returns the custom path
        assert get_recycle_bin_path() == custom_path
    finally:
        # Reset to original
        set_recycle_bin_path(path=None)


def test_set_recycle_bin_path_reset_to_default():
    """Test set_recycle_bin_path(None) resets to default."""
    # Set a custom path first
    custom_path = "/tmp/test_recycle_bin_reset"
    set_recycle_bin_path(path=custom_path)
    assert get_recycle_bin_path() == custom_path
    
    # Reset to default
    set_recycle_bin_path(path=None)
    
    # Verify it's back to default
    home_dir = os.path.expanduser("~")
    expected_path = os.path.join(home_dir, DEFAULT_RECYCLE_BIN_NAME)
    assert get_recycle_bin_path() == expected_path


def test_get_recycle_bin_index_path_uses_custom_path():
    """Test get_recycle_bin_index_path uses the custom recycle bin path when set."""
    # Save original path
    original_path = get_recycle_bin_path()
    
    try:
        # Set custom path
        custom_path = "/tmp/test_recycle_bin_index"
        set_recycle_bin_path(path=custom_path)
        
        # Get index path
        index_path = get_recycle_bin_index_path()
        
        # Verify it uses the custom path
        expected_index_path = os.path.join(custom_path, ".index.json")
        assert index_path == expected_index_path
    finally:
        # Reset to original
        set_recycle_bin_path(path=None)


def test_get_recycle_bin_index_path_uses_default_path():
    """Test get_recycle_bin_index_path uses default path when no override is set."""
    # Reset to default first
    set_recycle_bin_path(path=None)
    
    # Get index path
    index_path = get_recycle_bin_index_path()
    
    # Verify it uses the default path
    home_dir = os.path.expanduser("~")
    expected_index_path = os.path.join(home_dir, DEFAULT_RECYCLE_BIN_NAME, ".index.json")
    assert index_path == expected_index_path


def test_ensure_recycle_bin_exists_uses_custom_path():
    """Test ensure_recycle_bin_exists uses custom path when set."""
    # Save original path
    original_path = get_recycle_bin_path()
    
    try:
        # Set custom path
        custom_path = "/tmp/test_recycle_bin_ensure"
        set_recycle_bin_path(path=custom_path)
        
        # Ensure recycle bin exists
        created_path = ensure_recycle_bin_exists()
        
        # Verify it returns the custom path
        assert created_path == custom_path
        
        # Verify directory was created
        assert path_exists(custom_path)
        assert os.path.isdir(custom_path)
        
        # Clean up
        if path_exists(custom_path):
            delete(paths=custom_path)
    finally:
        # Reset to original
        set_recycle_bin_path(path=None)


def test_ensure_recycle_bin_exists_uses_default_path():
    """Test ensure_recycle_bin_exists uses default path when no override is set."""
    # Reset to default first
    set_recycle_bin_path(path=None)
    
    # Ensure recycle bin exists
    created_path = ensure_recycle_bin_exists()
    
    # Verify it returns the default path
    home_dir = os.path.expanduser("~")
    expected_path = os.path.join(home_dir, DEFAULT_RECYCLE_BIN_NAME)
    assert created_path == expected_path
    
    # Verify directory was created
    assert path_exists(expected_path)
    assert os.path.isdir(expected_path)


def test_set_recycle_bin_path_multiple_changes():
    """Test set_recycle_bin_path can be changed multiple times."""
    # Save original path
    original_path = get_recycle_bin_path()
    
    try:
        # Set first custom path
        path1 = "/tmp/test_recycle_bin_1"
        set_recycle_bin_path(path=path1)
        assert get_recycle_bin_path() == path1
        
        # Change to second custom path
        path2 = "/tmp/test_recycle_bin_2"
        set_recycle_bin_path(path=path2)
        assert get_recycle_bin_path() == path2
        
        # Change back to first
        set_recycle_bin_path(path=path1)
        assert get_recycle_bin_path() == path1
    finally:
        # Reset to original
        set_recycle_bin_path(path=None)

