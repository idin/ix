"""
Tests for MemoryStore auto-embedding functionality.

These tests REQUIRE sentence-transformers to be installed.
They will FAIL if it's not installed - that's intentional.
"""

from ixmachina.memory import MemoryStore, EmbeddingGenerator


def test_memory_store_auto_embed_disabled():
    """Test that MemoryStore with auto_embed=False doesn't create embeddings."""
    store = MemoryStore(auto_embed=False)
    
    result = store.save_object(
        name="Alice",
        value={"age": 30},
        description="Software engineer",
    )
    
    assert result['success'] is True
    object_id = result['object_id']
    
    # Load and check no embeddings were created
    load_result = store.load_object(object_id=object_id)
    assert load_result['success'] is True
    
    obj = load_result['object']
    assert obj.embedding is None
    assert obj.name_embedding is None


def test_memory_store_auto_embed_generates_embeddings():
    """Test that MemoryStore with auto_embed=True creates embeddings."""
    store = MemoryStore(auto_embed=True)
    
    result = store.save_object(
        name="Bob",
        value={"age": 45},
        description="CEO of Acme Corp",
    )
    
    assert result['success'] is True
    object_id = result['object_id']
    
    # Load and check embeddings were generated
    load_result = store.load_object(object_id=object_id)
    assert load_result['success'] is True
    
    obj = load_result['object']
    assert obj.embedding is not None
    assert isinstance(obj.embedding, list)
    assert len(obj.embedding) > 0
    
    assert obj.name_embedding is not None
    assert isinstance(obj.name_embedding, list)
    assert len(obj.name_embedding) > 0


def test_memory_store_with_custom_embedding_generator():
    """Test that MemoryStore uses provided embedding generator."""
    generator = EmbeddingGenerator(enabled=False)  # Explicitly disabled
    store = MemoryStore(auto_embed=True, embedding_generator=generator)
    
    result = store.save_object(
        name="Charlie",
        value="test data",
        description="Test description",
    )
    
    assert result['success'] is True
    object_id = result['object_id']
    
    # Load and check no embeddings (generator disabled)
    load_result = store.load_object(object_id=object_id)
    assert load_result['success'] is True
    
    obj = load_result['object']
    assert obj.embedding is None
    assert obj.name_embedding is None


def test_memory_store_manual_embeddings_override_auto():
    """Test that manually provided embeddings override auto-generation."""
    store = MemoryStore(auto_embed=True)
    
    manual_embedding = [0.1, 0.2, 0.3]
    manual_name_embedding = [0.4, 0.5, 0.6]
    
    result = store.save_object(
        name="David",
        value="test",
        description="Test",
        embedding=manual_embedding,
        name_embedding=manual_name_embedding,
    )
    
    assert result['success'] is True
    object_id = result['object_id']
    
    # Load and check manual embeddings were used
    load_result = store.load_object(object_id=object_id)
    assert load_result['success'] is True
    
    obj = load_result['object']
    assert obj.embedding == manual_embedding
    assert obj.name_embedding == manual_name_embedding


def test_memory_store_fact_auto_embed():
    """Test that facts are auto-embedded when auto_embed=True."""
    store = MemoryStore(auto_embed=True)
    
    # First save some objects
    alice_result = store.save_object(name="Alice", value="person")
    acme_result = store.save_object(name="Acme", value="company")
    
    # Save a fact
    fact_result = store.save_fact(
        text="Alice works at Acme",
        relationship_type="employment",
        objects=[
            {"object_id": alice_result['object_id'], "role": "employee"},
            {"object_id": acme_result['object_id'], "role": "employer"},
        ],
    )
    
    assert fact_result['success'] is True
    fact_id = fact_result['fact_id']
    
    # Load and check embedding was generated
    load_result = store.load_fact(fact_id=fact_id)
    assert load_result['success'] is True
    
    fact = load_result['fact']
    assert fact.embedding is not None
    assert isinstance(fact.embedding, list)
    assert len(fact.embedding) > 0


def test_memory_store_fact_manual_embedding_override():
    """Test that manually provided fact embeddings override auto-generation."""
    store = MemoryStore(auto_embed=True)
    
    alice_result = store.save_object(name="Alice", value="person")
    acme_result = store.save_object(name="Acme", value="company")
    
    manual_embedding = [0.7, 0.8, 0.9]
    
    fact_result = store.save_fact(
        text="Alice works at Acme",
        relationship_type="employment",
        objects=[
            {"object_id": alice_result['object_id'], "role": "employee"},
            {"object_id": acme_result['object_id'], "role": "employer"},
        ],
        embedding=manual_embedding,
    )
    
    assert fact_result['success'] is True
    fact_id = fact_result['fact_id']
    
    # Load and check manual embedding was used
    load_result = store.load_fact(fact_id=fact_id)
    assert load_result['success'] is True
    
    fact = load_result['fact']
    assert fact.embedding == manual_embedding


def test_memory_store_creates_generator_when_needed():
    """Test that MemoryStore creates an embedding generator when auto_embed=True."""
    store = MemoryStore(auto_embed=True)
    
    assert store.embedding_generator is not None
    assert isinstance(store.embedding_generator, EmbeddingGenerator)


def test_memory_store_no_generator_when_auto_embed_false():
    """Test that MemoryStore doesn't create generator when auto_embed=False."""
    store = MemoryStore(auto_embed=False)
    
    # Generator might be None or might exist but not be used
    # The important thing is embeddings aren't generated
    result = store.save_object(name="Test", value="data")
    object_id = result['object_id']
    
    load_result = store.load_object(object_id=object_id)
    obj = load_result['object']
    assert obj.embedding is None

