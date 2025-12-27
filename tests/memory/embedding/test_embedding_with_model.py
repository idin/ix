"""
Tests for EmbeddingGenerator with actual sentence-transformers model.

These tests REQUIRE sentence-transformers to be installed.
They will FAIL if it's not installed - that's intentional.
"""

from ixmachina.memory import EmbeddingGenerator


def test_embed_text_with_model():
    """Test embedding text with actual model."""
    generator = EmbeddingGenerator()
    
    result = generator.embed(text="Hello world")
    
    assert result is not None
    assert isinstance(result, list)
    assert len(result) > 0  # Should have embedding dimensions
    assert all(isinstance(x, float) for x in result)  # All elements should be floats


def test_embed_same_text_gives_same_embedding():
    """Test that embedding the same text twice gives the same result."""
    generator = EmbeddingGenerator()
    
    result1 = generator.embed(text="Test text")
    result2 = generator.embed(text="Test text")
    
    assert result1 is not None
    assert result2 is not None
    assert len(result1) == len(result2)
    
    # Should be very close (allowing for tiny floating point differences)
    for v1, v2 in zip(result1, result2):
        assert abs(v1 - v2) < 1e-6


def test_embed_different_texts_give_different_embeddings():
    """Test that different texts give different embeddings."""
    generator = EmbeddingGenerator()
    
    result1 = generator.embed(text="The cat sat on the mat")
    result2 = generator.embed(text="Quantum physics is fascinating")
    
    assert result1 is not None
    assert result2 is not None
    assert len(result1) == len(result2)  # Same dimensions
    assert result1 != result2  # Different values


def test_embed_similar_texts_have_similar_embeddings():
    """Test that similar texts have similar embeddings (high cosine similarity)."""
    generator = EmbeddingGenerator()
    
    result1 = generator.embed(text="The cat is sleeping")
    result2 = generator.embed(text="A cat is asleep")
    result3 = generator.embed(text="Quantum mechanics")
    
    assert result1 is not None
    assert result2 is not None
    assert result3 is not None
    
    # Calculate cosine similarity
    def cosine_similarity(a, b):
        import math
        dot_product = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x * x for x in a))
        mag_b = math.sqrt(sum(x * x for x in b))
        return dot_product / (mag_a * mag_b)
    
    sim_1_2 = cosine_similarity(result1, result2)  # Similar texts
    sim_1_3 = cosine_similarity(result1, result3)  # Different texts
    
    # Similar texts should have higher similarity than different texts
    assert sim_1_2 > sim_1_3
    assert sim_1_2 > 0.7  # Should be quite similar


def test_embed_object_combines_name_and_description():
    """Test that embed_object properly combines name and description."""
    generator = EmbeddingGenerator()
    
    # Test with description
    result_combined = generator.embed_object(
        name="Alice",
        description="Software engineer",
    )
    
    # Test name only
    result_name_only = generator.embed_object(
        name="Alice",
        description="",
    )
    
    assert result_combined is not None
    assert result_name_only is not None
    assert len(result_combined) == len(result_name_only)
    assert result_combined != result_name_only  # Should be different


def test_embed_batch_with_model():
    """Test batch embedding with actual model."""
    generator = EmbeddingGenerator()
    
    texts = ["First text", "Second text", "Third text"]
    result = generator.embed_batch(texts=texts)
    
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 3
    assert all(isinstance(emb, list) for emb in result)
    assert all(len(emb) > 0 for emb in result)


def test_model_loaded_once():
    """Test that model is loaded only once even with multiple embed calls."""
    generator = EmbeddingGenerator()
    
    assert generator._model is None
    assert generator._tried_loading is False
    
    # First embed call
    generator.embed(text="First text")
    
    assert generator._tried_loading is True
    assert generator._model is not None
    model_instance = generator._model
    
    # Second embed call
    generator.embed(text="Second text")
    
    # Should be the same model instance
    assert generator._model is model_instance


def test_embedding_dimensions():
    """Test that embeddings have expected dimensions for all-MiniLM-L6-v2."""
    generator = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
    
    result = generator.embed(text="Test")
    
    assert result is not None
    # all-MiniLM-L6-v2 produces 384-dimensional embeddings
    assert len(result) == 384

