"""
Tests for EmbeddingGenerator class.
"""

from ixmachina.memory import EmbeddingGenerator


def test_create_embedding_generator_with_defaults():
    """Create an embedding generator with default settings."""
    generator = EmbeddingGenerator()
    
    assert generator.model_name == "all-MiniLM-L6-v2"
    assert generator.enabled is True
    assert generator._model is None  # Not loaded yet
    assert generator._tried_loading is False


def test_create_embedding_generator_with_custom_model():
    """Create an embedding generator with a custom model name."""
    generator = EmbeddingGenerator(model_name="custom-model")
    
    assert generator.model_name == "custom-model"


def test_create_embedding_generator_disabled():
    """Create an embedding generator with embedding disabled."""
    generator = EmbeddingGenerator(enabled=False)
    
    assert generator.enabled is False


def test_embed_empty_string():
    """Embedding an empty string should return None."""
    generator = EmbeddingGenerator()
    
    result = generator.embed(text="")
    
    assert result is None


def test_embed_returns_none_when_disabled():
    """Embedding should return None when generator is disabled."""
    generator = EmbeddingGenerator(enabled=False)
    
    result = generator.embed(text="Hello world")
    
    assert result is None


def test_embed_batch_empty_list():
    """Embedding an empty list should return None."""
    generator = EmbeddingGenerator()
    
    result = generator.embed_batch(texts=[])
    
    assert result is None


def test_embed_batch_returns_none_when_disabled():
    """Batch embedding should return None when generator is disabled."""
    generator = EmbeddingGenerator(enabled=False)
    
    result = generator.embed_batch(texts=["Hello", "World"])
    
    assert result is None

