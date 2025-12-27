"""
Tests for number and date similarity using distance-based calculations.
"""

from ixmachina.memory import MemoryStore


def test_find_similar_numbers():
    """Test finding similar numbers using distance-based similarity."""
    store = MemoryStore(auto_embed=False)  # No embeddings needed for numbers
    
    # Create number objects
    numbers = {
        10: store.save_object(name="Ten", value=10, object_type="number"),
        20: store.save_object(name="Twenty", value=20, object_type="number"),
        25: store.save_object(name="TwentyFive", value=25, object_type="number"),
        30: store.save_object(name="Thirty", value=30, object_type="number"),
        100: store.save_object(name="Hundred", value=100, object_type="number"),
    }
    
    # Find similar to 25
    result = store.find_similar_objects(
        object_id=numbers[25]["object_id"],
        limit=4,
        exclude_self=True,
    )
    
    assert result["success"] is True
    similar = result["similar_objects"]
    
    print("\nSimilarity order to 25:")
    for i, item in enumerate(similar, 1):
        print(f"{i}. {item['name']} (similarity: {item['similarity']:.4f})")
    
    # Closest should be 20 and 30 (distance 5)
    # Then 10 (distance 15)
    # Then 100 (distance 75)
    names_in_order = [item["name"] for item in similar]
    
    # 20 and 30 should be most similar (positions 0 and 1, in either order)
    top_2 = set(names_in_order[:2])
    assert top_2 == {"Twenty", "Thirty"}, f"Expected Twenty and Thirty closest, got {top_2}"
    
    # 10 should be third
    assert names_in_order[2] == "Ten", f"Expected Ten third, got {names_in_order[2]}"
    
    # 100 should be last (farthest)
    assert names_in_order[3] == "Hundred", f"Expected Hundred last, got {names_in_order[3]}"


def test_find_similar_dates_full():
    """Test finding similar dates with full dates (YYYY-MM-DD)."""
    store = MemoryStore(auto_embed=False)
    
    # Create date objects
    dates = {
        "2020-01-01": store.save_object(name="NewYear2020", value="2020-01-01", object_type="date"),
        "2020-01-05": store.save_object(name="EarlyJan2020", value="2020-01-05", object_type="date"),
        "2020-06-15": store.save_object(name="MidJun2020", value="2020-06-15", object_type="date"),
        "2021-01-01": store.save_object(name="NewYear2021", value="2021-01-01", object_type="date"),
        "2025-01-01": store.save_object(name="NewYear2025", value="2025-01-01", object_type="date"),
    }
    
    # Find similar to 2020-01-01
    result = store.find_similar_objects(
        object_id=dates["2020-01-01"]["object_id"],
        limit=4,
        exclude_self=True,
    )
    
    assert result["success"] is True
    similar = result["similar_objects"]
    
    print("\nSimilarity order to 2020-01-01:")
    for i, item in enumerate(similar, 1):
        print(f"{i}. {item['name']} (similarity: {item['similarity']:.4f})")
    
    names_in_order = [item["name"] for item in similar]
    
    # EarlyJan2020 should be closest (4 days)
    assert names_in_order[0] == "EarlyJan2020"
    
    # MidJun2020 should be second (~165 days from 2020-01-01)
    assert names_in_order[1] == "MidJun2020"
    
    # NewYear2021 should be third (366 days, leap year)
    assert names_in_order[2] == "NewYear2021"
    
    # NewYear2025 should be last (farthest)
    assert names_in_order[3] == "NewYear2025"


def test_find_similar_dates_partial_year():
    """Test finding similar dates with partial dates (year only)."""
    store = MemoryStore(auto_embed=False)
    
    # Create date objects with year only
    dates = {
        "2015": store.save_object(name="Year2015", value="2015", object_type="date"),
        "2018": store.save_object(name="Year2018", value="2018", object_type="date"),
        "2020": store.save_object(name="Year2020", value="2020", object_type="date"),
        "2021": store.save_object(name="Year2021", value="2021", object_type="date"),
        "2025": store.save_object(name="Year2025", value="2025", object_type="date"),
    }
    
    # Find similar to 2020
    result = store.find_similar_objects(
        object_id=dates["2020"]["object_id"],
        limit=4,
        exclude_self=True,
    )
    
    assert result["success"] is True
    similar = result["similar_objects"]
    
    print("\nSimilarity order to 2020:")
    for i, item in enumerate(similar, 1):
        print(f"{i}. {item['name']} (similarity: {item['similarity']:.4f})")
    
    names_in_order = [item["name"] for item in similar]
    
    # 2021 should be closest (1 year = 365 days)
    assert names_in_order[0] == "Year2021"
    
    # 2018 should be second (2 years)
    assert names_in_order[1] == "Year2018"
    
    # Then either 2015 (5 years) or 2025 (5 years) - should be similar
    years_3_4 = set(names_in_order[2:4])
    assert years_3_4 == {"Year2015", "Year2025"}


def test_find_similar_dates_partial_year_month():
    """Test finding similar dates with year-month."""
    store = MemoryStore(auto_embed=False)
    
    # Create date objects with year-month
    dates = {
        "2020-01": store.save_object(name="Jan2020", value="2020-01", object_type="date"),
        "2020-02": store.save_object(name="Feb2020", value="2020-02", object_type="date"),
        "2020-06": store.save_object(name="Jun2020", value="2020-06", object_type="date"),
        "2021-01": store.save_object(name="Jan2021", value="2021-01", object_type="date"),
    }
    
    # Find similar to 2020-01
    result = store.find_similar_objects(
        object_id=dates["2020-01"]["object_id"],
        limit=3,
        exclude_self=True,
    )
    
    assert result["success"] is True
    similar = result["similar_objects"]
    
    print("\nSimilarity order to 2020-01:")
    for i, item in enumerate(similar, 1):
        print(f"{i}. {item['name']} (similarity: {item['similarity']:.4f})")
    
    names_in_order = [item["name"] for item in similar]
    
    # Feb2020 should be closest (1 month)
    assert names_in_order[0] == "Feb2020"
    
    # Jun2020 should be second (5 months)
    assert names_in_order[1] == "Jun2020"
    
    # Jan2021 should be last (12 months)
    assert names_in_order[2] == "Jan2021"


def test_mixed_types_only_same_type_compared():
    """Test that only objects of the same type are compared."""
    store = MemoryStore(auto_embed=True)
    
    # Create objects of different types
    text_obj = store.save_object(name="Paris", value="city", description="Capital of France", object_type="text")
    num_obj = store.save_object(name="TwentyFive", value=25, object_type="number")
    date_obj = store.save_object(name="Year2020", value="2020", object_type="date")
    
    # Find similar to text object
    result = store.find_similar_objects(
        object_id=text_obj["object_id"],
        limit=10,
        exclude_self=True,
    )
    
    assert result["success"] is True
    # Should find no similar objects (no other text objects)
    assert result["count"] == 0
    
    # Find similar to number object
    result = store.find_similar_objects(
        object_id=num_obj["object_id"],
        limit=10,
        exclude_self=True,
    )
    
    assert result["success"] is True
    # Should find no similar objects (no other number objects)
    assert result["count"] == 0
    
    # Find similar to date object
    result = store.find_similar_objects(
        object_id=date_obj["object_id"],
        limit=10,
        exclude_self=True,
    )
    
    assert result["success"] is True
    # Should find no similar objects (no other date objects)
    assert result["count"] == 0


def test_number_similarity_scores():
    """Test that number similarity scores are properly normalized."""
    store = MemoryStore(auto_embed=False)
    
    # Create numbers with varying distances
    store.save_object(name="Zero", value=0, object_type="number")
    store.save_object(name="Five", value=5, object_type="number")
    mid_result = store.save_object(name="Ten", value=10, object_type="number")
    store.save_object(name="Fifteen", value=15, object_type="number")
    store.save_object(name="Twenty", value=20, object_type="number")
    
    result = store.find_similar_objects(
        object_id=mid_result["object_id"],
        limit=4,
        exclude_self=True,
    )
    
    assert result["success"] is True
    similar = result["similar_objects"]
    
    # All similarities should be between 0 and 1
    for item in similar:
        assert 0 <= item["similarity"] <= 1
    
    # Objects closer in value should have higher similarity
    five_sim = [item for item in similar if item["name"] == "Five"][0]["similarity"]
    zero_sim = [item for item in similar if item["name"] == "Zero"][0]["similarity"]
    
    assert five_sim > zero_sim  # 5 is closer to 10 than 0 is

