"""Tests for NumberMemory."""

import sqlite3
import pytest

from ixmemory.semantic_memory.database import initialize_database
from ixmemory.semantic_memory.number_memory import NumberMemory


@pytest.fixture
def number_memory():
    """Create an in-memory NumberMemory for testing."""
    connection = sqlite3.connect(":memory:")
    initialize_database(connection=connection)
    return NumberMemory(connection=connection)


# =============================================================================
# Basic CRUD Tests
# =============================================================================

def test_save_and_load_integer(number_memory):
    """Test saving and loading an integer value."""
    result = number_memory.save(
        id="alice_age",
        value=32,
        record_type="age",
    )
    
    assert result["success"] is True
    assert result["id"] == "alice_age"
    
    loaded = number_memory.load(id="alice_age")
    
    assert loaded is not None
    assert loaded["id"] == "alice_age"
    assert loaded["value"] == 32
    assert loaded["number_type"] == "integer"
    assert loaded["record_type"] == "age"


def test_save_and_load_float(number_memory):
    """Test saving and loading a float value."""
    number_memory.save(
        id="item_price",
        value=19.99,
        record_type="price",
    )
    
    loaded = number_memory.load(id="item_price")
    
    assert loaded["value"] == 19.99
    assert loaded["number_type"] == "float"
    assert loaded["record_type"] == "price"


def test_save_float_with_integer_value(number_memory):
    """Test that float with integer value is stored as integer type."""
    number_memory.save(
        id="whole_float",
        value=100.0,
    )
    
    loaded = number_memory.load(id="whole_float")
    
    # Should be stored as integer since 100.0 is a whole number
    assert loaded["number_type"] == "integer"
    assert loaded["value"] == 100


def test_save_without_record_type(number_memory):
    """Test saving a number without record_type."""
    number_memory.save(
        id="untyped",
        value=42,
    )
    
    loaded = number_memory.load(id="untyped")
    
    assert loaded["record_type"] is None


def test_load_nonexistent_number(number_memory):
    """Test loading a number that doesn't exist."""
    loaded = number_memory.load(id="nonexistent")
    assert loaded is None


def test_delete_number(number_memory):
    """Test deleting a number."""
    number_memory.save(id="to_delete", value=99)
    
    deleted = number_memory.delete(id="to_delete")
    assert deleted is True
    
    loaded = number_memory.load(id="to_delete")
    assert loaded is None


def test_delete_nonexistent_number(number_memory):
    """Test deleting a number that doesn't exist."""
    deleted = number_memory.delete(id="nonexistent")
    assert deleted is False


def test_update_number(number_memory):
    """Test updating an existing number."""
    number_memory.save(id="updatable", value=10)
    
    number_memory.save(id="updatable", value=20)
    
    loaded = number_memory.load(id="updatable")
    assert loaded["value"] == 20


# =============================================================================
# List Tests
# =============================================================================

def test_list_all_numbers(number_memory):
    """Test listing all numbers."""
    number_memory.save(id="n1", value=10)
    number_memory.save(id="n2", value=20)
    number_memory.save(id="n3", value=30)
    
    numbers = number_memory.list()
    
    assert len(numbers) == 3


def test_list_with_limit(number_memory):
    """Test listing numbers with limit."""
    number_memory.save(id="n1", value=10)
    number_memory.save(id="n2", value=20)
    number_memory.save(id="n3", value=30)
    
    numbers = number_memory.list(limit=2)
    
    assert len(numbers) == 2


def test_list_by_record_type(number_memory):
    """Test listing numbers filtered by record_type."""
    number_memory.save(id="age1", value=25, record_type="age")
    number_memory.save(id="age2", value=30, record_type="age")
    number_memory.save(id="price1", value=9.99, record_type="price")
    
    ages = number_memory.list(record_type="age")
    
    assert len(ages) == 2
    assert all(n["record_type"] == "age" for n in ages)


# =============================================================================
# Find Nearest Tests
# =============================================================================

def test_find_nearest(number_memory):
    """Test finding numbers nearest to a target value."""
    number_memory.save(id="n10", value=10)
    number_memory.save(id="n20", value=20)
    number_memory.save(id="n30", value=30)
    
    nearest = number_memory.find_nearest(value=22, limit=2)
    
    assert len(nearest) == 2
    # 20 is closest to 22, then 30
    assert nearest[0]["id"] == "n20"
    assert nearest[1]["id"] == "n30"


def test_find_nearest_with_record_type_filter(number_memory):
    """Test finding nearest filtered by record_type."""
    number_memory.save(id="age25", value=25, record_type="age")
    number_memory.save(id="price24", value=24, record_type="price")
    number_memory.save(id="age35", value=35, record_type="age")
    
    nearest = number_memory.find_nearest(
        value=26,
        record_type="age",
        limit=1,
    )
    
    assert len(nearest) == 1
    assert nearest[0]["id"] == "age25"  # Closest age to 26


def test_find_nearest_returns_distance(number_memory):
    """Test that find_nearest returns distance in results."""
    number_memory.save(id="n100", value=100)
    
    nearest = number_memory.find_nearest(value=90, limit=1)
    
    assert "distance" in nearest[0]
    assert nearest[0]["distance"] == 10.0


def test_find_nearest_exact_match(number_memory):
    """Test finding exact match has distance 0."""
    number_memory.save(id="exact", value=50)
    
    nearest = number_memory.find_nearest(value=50, limit=1)
    
    assert nearest[0]["distance"] == 0.0


# =============================================================================
# Find in Range Tests
# =============================================================================

def test_find_in_range(number_memory):
    """Test finding numbers within a range."""
    number_memory.save(id="n10", value=10)
    number_memory.save(id="n20", value=20)
    number_memory.save(id="n30", value=30)
    number_memory.save(id="n40", value=40)
    
    in_range = number_memory.find_in_range(
        min_value=15,
        max_value=35,
    )
    
    assert len(in_range) == 2
    ids = {n["id"] for n in in_range}
    assert ids == {"n20", "n30"}


def test_find_in_range_with_record_type_filter(number_memory):
    """Test range search filtered by record_type."""
    number_memory.save(id="age25", value=25, record_type="age")
    number_memory.save(id="price28", value=28, record_type="price")
    number_memory.save(id="age35", value=35, record_type="age")
    
    in_range = number_memory.find_in_range(
        min_value=20,
        max_value=30,
        record_type="age",
    )
    
    assert len(in_range) == 1
    assert in_range[0]["id"] == "age25"


def test_find_in_range_inclusive(number_memory):
    """Test that range boundaries are inclusive."""
    number_memory.save(id="n10", value=10)
    number_memory.save(id="n20", value=20)
    
    in_range = number_memory.find_in_range(
        min_value=10,
        max_value=20,
    )
    
    assert len(in_range) == 2


def test_find_in_range_returns_empty_when_no_match(number_memory):
    """Test that range search returns empty list when nothing matches."""
    number_memory.save(id="n10", value=10)
    
    in_range = number_memory.find_in_range(min_value=100, max_value=200)
    
    assert in_range == []


def test_find_in_range_min_only(number_memory):
    """Test range search with only min_value."""
    number_memory.save(id="n10", value=10)
    number_memory.save(id="n50", value=50)
    number_memory.save(id="n100", value=100)
    
    in_range = number_memory.find_in_range(min_value=40)
    
    ids = {n["id"] for n in in_range}
    assert ids == {"n50", "n100"}


def test_find_in_range_max_only(number_memory):
    """Test range search with only max_value."""
    number_memory.save(id="n10", value=10)
    number_memory.save(id="n50", value=50)
    number_memory.save(id="n100", value=100)
    
    in_range = number_memory.find_in_range(max_value=60)
    
    ids = {n["id"] for n in in_range}
    assert ids == {"n10", "n50"}


# =============================================================================
# Edge Cases
# =============================================================================

def test_save_negative_number(number_memory):
    """Test saving negative numbers."""
    number_memory.save(id="temp", value=-15.5, record_type="temperature")
    
    loaded = number_memory.load(id="temp")
    
    assert loaded["value"] == -15.5


def test_save_zero(number_memory):
    """Test saving zero."""
    number_memory.save(id="zero", value=0)
    
    loaded = number_memory.load(id="zero")
    
    assert loaded["value"] == 0
    assert loaded["number_type"] == "integer"


def test_save_large_number(number_memory):
    """Test saving large numbers."""
    number_memory.save(id="large", value=10_000_000_000)
    
    loaded = number_memory.load(id="large")
    
    assert loaded["value"] == 10_000_000_000


def test_save_small_float(number_memory):
    """Test saving small float numbers."""
    number_memory.save(id="small", value=0.000001)
    
    loaded = number_memory.load(id="small")
    
    assert abs(loaded["value"] - 0.000001) < 1e-10
