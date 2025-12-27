"""
Tests for semantic search using embeddings.
"""

from ixmachina.memory import MemoryStore


def test_find_similar_objects_to_city():
    """
    Test finding objects similar to Berlin.
    
    Objects: Paris, London, Frankfurt, Berlin, Ice Cream, Computer
    
    Expected similarity order to Berlin:
    1. Frankfurt (German city, geographically close)
    2. Paris or London (European capitals)
    3. Paris or London (the other one)
    4. Ice Cream or Computer (unrelated items)
    5. Ice Cream or Computer (the other unrelated item)
    """
    store = MemoryStore(auto_embed=True)
    
    # Create objects
    objects = {
        "Paris": store.save_object(name="Paris", value="city", description="Capital of France"),
        "London": store.save_object(name="London", value="city", description="Capital of United Kingdom"),
        "Frankfurt": store.save_object(name="Frankfurt", value="city", description="Major city in Germany"),
        "Berlin": store.save_object(name="Berlin", value="city", description="Capital of Germany"),
        "Ice Cream": store.save_object(name="Ice Cream", value="food", description="Frozen dessert"),
        "Computer": store.save_object(name="Computer", value="device", description="Electronic computing device"),
    }
    
    berlin_id = objects["Berlin"]["object_id"]
    
    # Find similar objects to Berlin (excluding Berlin itself)
    result = store.find_similar_objects(
        object_id=berlin_id,
        limit=5,
        exclude_self=True,
    )
    
    assert result["success"] is True
    assert "similar_objects" in result
    similar = result["similar_objects"]
    
    # Should return 5 objects (all except Berlin)
    assert len(similar) == 5
    
    # Each result should have object info and similarity score
    for item in similar:
        assert "object_id" in item
        assert "name" in item
        assert "similarity" in item
        assert 0 <= item["similarity"] <= 1  # Cosine similarity in [0, 1]
    
    # Extract names in order
    names_in_order = [item["name"] for item in similar]
    
    print("\nSimilarity order to Berlin:")
    for i, item in enumerate(similar, 1):
        print(f"{i}. {item['name']} (similarity: {item['similarity']:.4f})")
    
    # Frankfurt should be most similar (position 0)
    assert names_in_order[0] == "Frankfurt", f"Expected Frankfurt first, got {names_in_order[0]}"
    
    # Paris and London should be positions 1 and 2 (in either order)
    cities_2_3 = set(names_in_order[1:3])
    assert cities_2_3 == {"Paris", "London"}, f"Expected Paris and London in positions 2-3, got {cities_2_3}"
    
    # Ice Cream and Computer should be positions 3 and 4 (in either order)
    unrelated_4_5 = set(names_in_order[3:5])
    assert unrelated_4_5 == {"Ice Cream", "Computer"}, f"Expected Ice Cream and Computer in positions 4-5, got {unrelated_4_5}"
    
    # Frankfurt should be significantly more similar than unrelated items
    frankfurt_similarity = similar[0]["similarity"]
    computer_similarity = [item["similarity"] for item in similar if item["name"] == "Computer"][0]
    ice_cream_similarity = [item["similarity"] for item in similar if item["name"] == "Ice Cream"][0]
    
    assert frankfurt_similarity > computer_similarity + 0.1  # At least 0.1 difference
    assert frankfurt_similarity > ice_cream_similarity + 0.1


def test_find_similar_objects_with_limit():
    """Test limiting the number of similar objects returned."""
    store = MemoryStore(auto_embed=True)
    
    # Create several objects
    for i in range(10):
        store.save_object(name=f"Object{i}", value=f"data{i}", description=f"Test object {i}")
    
    # Get first object
    all_objects = store.list_objects()
    first_id = all_objects["objects"][0]["object_id"]
    
    # Find top 3 similar objects
    result = store.find_similar_objects(
        object_id=first_id,
        limit=3,
        exclude_self=True,
    )
    
    assert result["success"] is True
    assert len(result["similar_objects"]) == 3


def test_find_similar_objects_include_self():
    """Test finding similar objects including the query object itself."""
    store = MemoryStore(auto_embed=True)
    
    alice_result = store.save_object(
        name="Alice",
        value="person",
        description="Software engineer",
    )
    store.save_object(name="Bob", value="person", description="Data scientist")
    store.save_object(name="Charlie", value="person", description="Product manager")
    
    # Find similar with self included
    result = store.find_similar_objects(
        object_id=alice_result["object_id"],
        limit=3,
        exclude_self=False,
    )
    
    assert result["success"] is True
    similar = result["similar_objects"]
    
    # Alice should be first (similarity ~1.0 with itself)
    assert similar[0]["name"] == "Alice"
    assert abs(similar[0]["similarity"] - 1.0) < 0.0001  # Allow tiny floating-point error


def test_find_similar_objects_with_similar_descriptions():
    """Test that objects with similar descriptions have higher similarity."""
    store = MemoryStore(auto_embed=True)
    
    result1 = store.save_object(
        name="Object1",
        value="data",
        description="A red apple sitting on a wooden table",
    )
    store.save_object(
        name="Object2",
        value="data",
        description="A green apple on a wooden surface",
    )
    store.save_object(
        name="Object3",
        value="data",
        description="A quantum computer processing algorithms",
    )
    
    # Find similar to Object1
    result = store.find_similar_objects(
        object_id=result1["object_id"],
        limit=2,
        exclude_self=True,
    )
    
    assert result["success"] is True
    similar = result["similar_objects"]
    
    # Object2 (similar apple description) should be more similar than Object3 (computer)
    assert similar[0]["name"] == "Object2"
    assert similar[1]["name"] == "Object3"
    
    # Similarity should be significantly higher for the similar description
    assert similar[0]["similarity"] > similar[1]["similarity"] + 0.1


def test_find_similar_objects_no_embedding():
    """Test error when trying to find similar objects for an object without embedding."""
    store = MemoryStore(auto_embed=False)  # No auto-embedding
    
    result = store.save_object(name="Test", value="data")
    object_id = result["object_id"]
    
    # Should fail because object has no embedding
    result = store.find_similar_objects(object_id=object_id, limit=5)
    
    assert result["success"] is False
    assert "error" in result
    assert "no embedding" in result["error"].lower()

