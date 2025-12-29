"""
Tests for persist decorator ensuring function name is in cache path.
"""

import pytest
import shutil
from pathlib import Path
from ixmachina.utils.persist import persist


def test_function_name_appended_to_path():
    """Test that function name is appended when not already at end of path."""
    cache_base = ".cache/test_base"
    cache_path = Path(cache_base)
    
    if cache_path.exists():
        shutil.rmtree(cache_path)
    
    @persist(path=cache_base)
    def my_function(x: int) -> int:
        return x * 2
    
    result = my_function(5)
    assert result == 10
    
    # Function name should be appended to cache base
    expected_cache_dir = Path(cache_base) / "my_function"
    assert expected_cache_dir.exists()
    assert len(list(expected_cache_dir.iterdir())) == 1


def test_function_name_not_duplicated():
    """Test that function name is not duplicated if already at end of path."""
    cache_base = ".cache/test_base/my_function"
    cache_path = Path(cache_base)
    
    if cache_path.exists():
        shutil.rmtree(cache_path)
    
    @persist(path=cache_base)
    def my_function(x: int) -> int:
        return x * 2
    
    result = my_function(5)
    assert result == 10
    
    # Function name should not be duplicated
    expected_cache_dir = Path(cache_base)
    assert expected_cache_dir.exists()
    assert len(list(expected_cache_dir.iterdir())) == 1


def test_function_name_with_cache_path_parameter():
    """Test that function name is appended when using cache_path parameter."""
    cache_base = ".cache/test_param"
    cache_path = Path(cache_base)
    
    if cache_path.exists():
        shutil.rmtree(cache_path)
    
    @persist(path=".cache/default")
    def my_function(x: int) -> int:
        return x * 2
    
    # Call with override cache_path
    result = my_function(5, cache_path=cache_base)
    assert result == 10
    
    # Function name should be appended to override path
    expected_cache_dir = Path(cache_base) / "my_function"
    assert expected_cache_dir.exists()
    assert len(list(expected_cache_dir.iterdir())) == 1

