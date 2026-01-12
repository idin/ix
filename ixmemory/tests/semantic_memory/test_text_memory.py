"""Tests for TextMemory."""

import sqlite3
import pytest

from ixmemory.semantic_memory.database import initialize_database
from ixmemory.semantic_memory.text_memory import TextMemory


@pytest.fixture
def text_memory():
    """Create an in-memory TextMemory for testing (without auto-embed)."""
    connection = sqlite3.connect(":memory:")
    initialize_database(connection=connection)
    return TextMemory(connection=connection, auto_embed=False)


# =============================================================================
# Basic CRUD Tests
# =============================================================================

def test_save_and_load_text(text_memory):
    """Test saving and loading a text record."""
    result = text_memory.save(
        id="note1",
        content="This is a test note.",
        record_type_id="note",
    )
    
    assert result["success"] is True
    assert result["id"] == "note1"
    
    loaded = text_memory.load(id="note1")
    
    assert loaded is not None
    assert loaded["id"] == "note1"
    assert loaded["content"] == "This is a test note."
    assert loaded["record_type_id"] == "note"


def test_save_with_tags(text_memory):
    """Test saving a text with tags."""
    text_memory.save(
        id="tagged",
        content="Tagged content",
        tags=["important", "work"],
    )
    
    loaded = text_memory.load(id="tagged")
    
    assert "important" in loaded["tags"]
    assert "work" in loaded["tags"]


def test_save_with_metadata(text_memory):
    """Test saving a text with metadata."""
    text_memory.save(
        id="with_meta",
        content="Has metadata",
        metadata={"author": "Alice", "priority": 1},
    )
    
    loaded = text_memory.load(id="with_meta")
    
    assert loaded["metadata"]["author"] == "Alice"
    assert loaded["metadata"]["priority"] == 1


def test_load_nonexistent_text(text_memory):
    """Test loading a text that doesn't exist."""
    loaded = text_memory.load(id="nonexistent")
    assert loaded is None


def test_delete_text(text_memory):
    """Test deleting a text."""
    text_memory.save(id="to_delete", content="Delete me")
    
    deleted = text_memory.delete(id="to_delete")
    assert deleted is True
    
    loaded = text_memory.load(id="to_delete")
    assert loaded is None


def test_delete_nonexistent_text(text_memory):
    """Test deleting a text that doesn't exist."""
    deleted = text_memory.delete(id="nonexistent")
    assert deleted is False


def test_update_text(text_memory):
    """Test updating an existing text."""
    text_memory.save(id="updatable", content="Original content")
    
    text_memory.save(id="updatable", content="Updated content")
    
    loaded = text_memory.load(id="updatable")
    assert loaded["content"] == "Updated content"


# =============================================================================
# List Tests
# =============================================================================

def test_list_all_texts(text_memory):
    """Test listing all texts."""
    text_memory.save(id="t1", content="Text 1")
    text_memory.save(id="t2", content="Text 2")
    text_memory.save(id="t3", content="Text 3")
    
    texts = text_memory.list()
    
    assert len(texts) == 3


def test_list_with_limit(text_memory):
    """Test listing texts with limit."""
    text_memory.save(id="t1", content="Text 1")
    text_memory.save(id="t2", content="Text 2")
    text_memory.save(id="t3", content="Text 3")
    
    texts = text_memory.list(limit=2)
    
    assert len(texts) == 2


def test_list_by_record_type(text_memory):
    """Test listing texts filtered by record_type_id."""
    text_memory.save(id="note1", content="Note 1", record_type_id="note")
    text_memory.save(id="note2", content="Note 2", record_type_id="note")
    text_memory.save(id="doc1", content="Doc 1", record_type_id="document")
    
    notes = text_memory.list(record_type_id="note")
    
    assert len(notes) == 2
    assert all(t["record_type_id"] == "note" for t in notes)


# =============================================================================
# Find by Tags Tests
# =============================================================================

def test_find_by_tags_match_all(text_memory):
    """Test finding texts that have all specified tags."""
    text_memory.save(id="t1", content="T1", tags=["a", "b", "c"])
    text_memory.save(id="t2", content="T2", tags=["a", "b"])
    text_memory.save(id="t3", content="T3", tags=["a"])
    
    results = text_memory.find_by_tags(tags=["a", "b"], match_all=True)
    
    ids = {t["id"] for t in results}
    assert ids == {"t1", "t2"}


def test_find_by_tags_match_any(text_memory):
    """Test finding texts that have any specified tags."""
    text_memory.save(id="t1", content="T1", tags=["a"])
    text_memory.save(id="t2", content="T2", tags=["b"])
    text_memory.save(id="t3", content="T3", tags=["c"])
    
    results = text_memory.find_by_tags(tags=["a", "b"], match_all=False)
    
    ids = {t["id"] for t in results}
    assert ids == {"t1", "t2"}


def test_find_by_tags_with_limit(text_memory):
    """Test finding by tags with limit."""
    text_memory.save(id="t1", content="T1", tags=["common"])
    text_memory.save(id="t2", content="T2", tags=["common"])
    text_memory.save(id="t3", content="T3", tags=["common"])
    
    results = text_memory.find_by_tags(tags=["common"], limit=2)
    
    assert len(results) == 2


# =============================================================================
# Find by Metadata Tests
# =============================================================================

def test_find_by_metadata(text_memory):
    """Test finding texts by metadata key-value."""
    text_memory.save(id="t1", content="T1", metadata={"author": "Alice"})
    text_memory.save(id="t2", content="T2", metadata={"author": "Bob"})
    text_memory.save(id="t3", content="T3", metadata={"author": "Alice"})
    
    results = text_memory.find_by_metadata(key="author", value="Alice")
    
    ids = {t["id"] for t in results}
    assert ids == {"t1", "t3"}


def test_find_by_metadata_no_match(text_memory):
    """Test finding by metadata when nothing matches."""
    text_memory.save(id="t1", content="T1", metadata={"author": "Alice"})
    
    results = text_memory.find_by_metadata(key="author", value="Charlie")
    
    assert results == []


# =============================================================================
# Set/Member Operations Tests
# =============================================================================

def test_add_member(text_memory):
    """Test adding a member to a text (creating a set)."""
    text_memory.save(id="my_set", content="A collection of things")
    
    result = text_memory.add_member(
        text_id="my_set",
        member_id="item1",
        member_table="texts",
    )
    
    assert result["success"] is True
    assert result["text_id"] == "my_set"
    assert result["member_id"] == "item1"
    assert result["member_table"] == "texts"


def test_add_member_from_different_tables(text_memory):
    """Test adding members from different tables."""
    text_memory.save(id="my_set", content="Mixed collection")
    
    text_memory.add_member(text_id="my_set", member_id="text1", member_table="texts")
    text_memory.add_member(text_id="my_set", member_id="num1", member_table="numbers")
    text_memory.add_member(text_id="my_set", member_id="mom1", member_table="moments")
    
    members = text_memory.get_members(text_id="my_set")
    
    assert len(members) == 3
    tables = {m["member_table"] for m in members}
    assert tables == {"texts", "numbers", "moments"}


def test_add_member_invalid_table_raises_error(text_memory):
    """Test that adding member with invalid table raises ValueError."""
    text_memory.save(id="my_set", content="Test")
    
    with pytest.raises(ValueError, match="Invalid member_table"):
        text_memory.add_member(
            text_id="my_set",
            member_id="item",
            member_table="invalid_table",
        )


def test_add_member_to_nonexistent_text_raises_error(text_memory):
    """Test that adding member to non-existent text raises ValueError."""
    with pytest.raises(ValueError, match="not found"):
        text_memory.add_member(
            text_id="nonexistent",
            member_id="item",
            member_table="texts",
        )


def test_get_members(text_memory):
    """Test getting all members of a set."""
    text_memory.save(id="my_set", content="Test set")
    text_memory.add_member(text_id="my_set", member_id="a", member_table="texts")
    text_memory.add_member(text_id="my_set", member_id="b", member_table="texts")
    text_memory.add_member(text_id="my_set", member_id="c", member_table="numbers")
    
    members = text_memory.get_members(text_id="my_set")
    
    assert len(members) == 3


def test_get_members_filtered_by_table(text_memory):
    """Test getting members filtered by table."""
    text_memory.save(id="my_set", content="Test set")
    text_memory.add_member(text_id="my_set", member_id="a", member_table="texts")
    text_memory.add_member(text_id="my_set", member_id="b", member_table="numbers")
    
    text_members = text_memory.get_members(text_id="my_set", member_table="texts")
    
    assert len(text_members) == 1
    assert text_members[0]["member_id"] == "a"


def test_remove_member(text_memory):
    """Test removing a member from a set."""
    text_memory.save(id="my_set", content="Test set")
    text_memory.add_member(text_id="my_set", member_id="item", member_table="texts")
    
    removed = text_memory.remove_member(
        text_id="my_set",
        member_id="item",
        member_table="texts",
    )
    
    assert removed is True
    
    members = text_memory.get_members(text_id="my_set")
    assert len(members) == 0


def test_remove_nonexistent_member(text_memory):
    """Test removing a member that doesn't exist."""
    text_memory.save(id="my_set", content="Test set")
    
    removed = text_memory.remove_member(
        text_id="my_set",
        member_id="nonexistent",
        member_table="texts",
    )
    
    assert removed is False


def test_clear_members(text_memory):
    """Test clearing all members from a set."""
    text_memory.save(id="my_set", content="Test set")
    text_memory.add_member(text_id="my_set", member_id="a", member_table="texts")
    text_memory.add_member(text_id="my_set", member_id="b", member_table="texts")
    text_memory.add_member(text_id="my_set", member_id="c", member_table="texts")
    
    count = text_memory.clear_members(text_id="my_set")
    
    assert count == 3
    assert text_memory.get_members(text_id="my_set") == []


def test_find_sets_containing(text_memory):
    """Test finding sets that contain a specific member."""
    text_memory.save(id="set1", content="Set 1")
    text_memory.save(id="set2", content="Set 2")
    text_memory.save(id="set3", content="Set 3")
    
    text_memory.add_member(text_id="set1", member_id="item_x", member_table="texts")
    text_memory.add_member(text_id="set2", member_id="item_x", member_table="texts")
    # set3 does not contain item_x
    
    sets = text_memory.find_sets_containing(
        member_id="item_x",
        member_table="texts",
    )
    
    ids = {s["id"] for s in sets}
    assert ids == {"set1", "set2"}


def test_has_members_true(text_memory):
    """Test has_members returns True when text has members."""
    text_memory.save(id="my_set", content="Test")
    text_memory.add_member(text_id="my_set", member_id="item", member_table="texts")
    
    assert text_memory.has_members(text_id="my_set") is True


def test_has_members_false(text_memory):
    """Test has_members returns False when text has no members."""
    text_memory.save(id="not_a_set", content="Test")
    
    assert text_memory.has_members(text_id="not_a_set") is False


def test_count_members(text_memory):
    """Test counting members in a set."""
    text_memory.save(id="my_set", content="Test")
    text_memory.add_member(text_id="my_set", member_id="a", member_table="texts")
    text_memory.add_member(text_id="my_set", member_id="b", member_table="texts")
    text_memory.add_member(text_id="my_set", member_id="c", member_table="numbers")
    
    count = text_memory.count_members(text_id="my_set")
    
    assert count == 3


def test_count_members_empty_set(text_memory):
    """Test counting members in empty set returns 0."""
    text_memory.save(id="empty_set", content="Test")
    
    count = text_memory.count_members(text_id="empty_set")
    
    assert count == 0


# =============================================================================
# Set Use Case: "Idin's Toys" Example
# =============================================================================

def test_set_use_case_idins_toys(text_memory):
    """Test creating and using a set like 'Idin's toys'."""
    # Create the set
    text_memory.save(
        id="idin_toys",
        content="Idin's favourite toys from childhood",
        record_type_id="toy_collection",
        tags=["personal", "nostalgia"],
    )
    
    # Add members (would be from different tables in real use)
    text_memory.add_member(text_id="idin_toys", member_id="teddy_bear", member_table="texts")
    text_memory.add_member(text_id="idin_toys", member_id="toy_car", member_table="texts")
    text_memory.add_member(text_id="idin_toys", member_id="car_price", member_table="numbers")
    text_memory.add_member(text_id="idin_toys", member_id="purchase_date", member_table="moments")
    
    # Verify the set
    loaded = text_memory.load(id="idin_toys")
    assert loaded["content"] == "Idin's favourite toys from childhood"
    assert "personal" in loaded["tags"]
    
    # Verify members
    members = text_memory.get_members(text_id="idin_toys")
    assert len(members) == 4
    
    # Verify we can find the set by the teddy bear
    sets = text_memory.find_sets_containing(
        member_id="teddy_bear",
        member_table="texts",
    )
    assert len(sets) == 1
    assert sets[0]["id"] == "idin_toys"
