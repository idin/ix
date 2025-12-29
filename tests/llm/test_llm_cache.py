"""
Tests for LLM caching functionality.
"""

from pathlib import Path
from tests.conftest import DEFAULT_TEST_MODEL
from tests.api_keys import get_openai_api_key
import shutil

from ixmachina.llm import LLM
from ixmachina.utils.persist import set_cache_path, get_cache_path


def test_llm_cache_disabled_by_default():
    """Test that LLM caching is disabled by default."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL)
    
    assert llm.use_cache is False


def test_llm_cache_enabled_when_use_cache_true():
    """Test that LLM caching can be enabled."""
    api_key = get_openai_api_key()
    llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL, use_cache=True)
    
    assert llm.use_cache is True


def test_llm_cache_returns_cached_result():
    """Test that LLM returns cached result on second identical query."""
    api_key = get_openai_api_key()

    # Set up test cache directory
    cache_dir = Path(".cache/ix_test/llm_cache")
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    
    # Save original cache path
    original_cache_path = get_cache_path()
    
    try:
        # Set cache path for test
        set_cache_path(cache_dir)
        
        llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL, use_cache=True)
        
        # First query - should make API call
        response1 = llm.query(user_prompt="Say hello in exactly one word")
        assert isinstance(response1, str)
        assert len(response1) > 0
        
        # Second identical query - should return from cache
        response2 = llm.query(user_prompt="Say hello in exactly one word")
        
        # Should be the same response
        assert response1 == response2
        
        # Verify cache file exists
        cache_key = f"llm_query:{DEFAULT_TEST_MODEL}"
        cache_files = list((cache_dir / cache_key).glob("*.cache"))
        assert len(cache_files) > 0
        
    finally:
        # Restore original cache path
        set_cache_path(original_cache_path)
        # Clean up test cache
        if cache_dir.exists():
            shutil.rmtree(cache_dir)


def test_llm_cache_different_queries_not_cached():
    """Test that different queries do not use the same cache."""
    api_key = get_openai_api_key()

    # Set up test cache directory
    cache_dir = Path(".cache/ix_test/llm_cache")
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    
    # Save original cache path
    original_cache_path = get_cache_path()
    
    try:
        # Set cache path for test
        set_cache_path(cache_dir)
        
        llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL, use_cache=True)
        
        # First query
        response1 = llm.query(user_prompt="Say hello")
        assert isinstance(response1, str)
        
        # Second different query - should make new API call
        response2 = llm.query(user_prompt="Say goodbye")
        assert isinstance(response2, str)
        
        # Responses should be different (unless by coincidence)
        # But more importantly, both should be valid responses
        
        # Verify multiple cache files exist
        cache_key = f"llm_query:{DEFAULT_TEST_MODEL}"
        cache_files = list((cache_dir / cache_key).glob("*.cache"))
        assert len(cache_files) >= 2
        
    finally:
        # Restore original cache path
        set_cache_path(original_cache_path)
        # Clean up test cache
        if cache_dir.exists():
            shutil.rmtree(cache_dir)


def test_llm_cache_disabled_no_caching():
    """Test that when use_cache=False, no caching occurs."""
    api_key = get_openai_api_key()

    # Set up test cache directory
    cache_dir = Path(".cache/ix_test/llm_cache")
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    
    # Save original cache path
    original_cache_path = get_cache_path()
    
    try:
        # Set cache path for test
        set_cache_path(cache_dir)
        
        llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL, use_cache=False)
        
        # Make a query
        response1 = llm.query(user_prompt="Say hello")
        assert isinstance(response1, str)
        
        # Verify no cache files were created
        cache_key = f"llm_query:{DEFAULT_TEST_MODEL}"
        cache_path = cache_dir / cache_key
        if cache_path.exists():
            cache_files = list(cache_path.glob("*.cache"))
            assert len(cache_files) == 0
        
    finally:
        # Restore original cache path
        set_cache_path(original_cache_path)
        # Clean up test cache
        if cache_dir.exists():
            shutil.rmtree(cache_dir)


def test_llm_cache_with_different_parameters():
    """Test that queries with different parameters use different cache entries."""
    api_key = get_openai_api_key()

    # Set up test cache directory
    cache_dir = Path(".cache/ix_test/llm_cache")
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    
    # Save original cache path
    original_cache_path = get_cache_path()
    
    try:
        # Set cache path for test
        set_cache_path(cache_dir)
        
        llm = LLM(api_key=api_key, model_name=DEFAULT_TEST_MODEL, use_cache=True)
        
        # Query with temperature
        response1 = llm.query(user_prompt="Say hello", temperature=0.5)
        assert isinstance(response1, str)
        
        # Same query with different temperature - should be different cache entry
        response2 = llm.query(user_prompt="Say hello", temperature=0.9)
        assert isinstance(response2, str)
        
        # Verify multiple cache files exist
        cache_key = f"llm_query:{DEFAULT_TEST_MODEL}"
        cache_files = list((cache_dir / cache_key).glob("*.cache"))
        assert len(cache_files) >= 2
        
    finally:
        # Restore original cache path
        set_cache_path(original_cache_path)
        # Clean up test cache
        if cache_dir.exists():
            shutil.rmtree(cache_dir)

