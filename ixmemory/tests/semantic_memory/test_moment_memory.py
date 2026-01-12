"""Tests for MomentMemory."""

import sqlite3
import pytest

from ixmemory.semantic_memory.database import initialize_database
from ixmemory.semantic_memory.moment_memory import MomentMemory


@pytest.fixture
def moment_memory():
    """Create an in-memory MomentMemory for testing."""
    connection = sqlite3.connect(":memory:")
    initialize_database(connection=connection)
    return MomentMemory(connection=connection)


# =============================================================================
# Basic CRUD Tests
# =============================================================================

def test_save_and_load_full_moment(moment_memory):
    """Test saving and loading a moment with all components."""
    result = moment_memory.save(
        id="birthday_2025",
        year=2025,
        month=3,
        day=15,
        hour=14,
        minute=30,
        second=0,
        record_type="birthday",
    )
    
    assert result["success"] is True
    assert result["id"] == "birthday_2025"
    
    loaded = moment_memory.load(id="birthday_2025")
    
    assert loaded is not None
    assert loaded["id"] == "birthday_2025"
    assert loaded["year"] == 2025
    assert loaded["month"] == 3
    assert loaded["day"] == 15
    assert loaded["hour"] == 14
    assert loaded["minute"] == 30
    assert loaded["second"] == 0
    assert loaded["record_type"] == "birthday"


def test_save_partial_moment_year_only(moment_memory):
    """Test saving a partial moment with only year."""
    moment_memory.save(
        id="year_2025",
        year=2025,
    )
    
    loaded = moment_memory.load(id="year_2025")
    
    assert loaded["year"] == 2025
    assert loaded["month"] is None
    assert loaded["day"] is None
    assert loaded["hour"] is None


def test_save_partial_moment_month_only(moment_memory):
    """Test saving a partial moment with only month (November)."""
    moment_memory.save(
        id="november",
        month=11,
    )
    
    loaded = moment_memory.load(id="november")
    
    assert loaded["year"] is None
    assert loaded["month"] == 11
    assert loaded["day"] is None


def test_save_partial_moment_year_and_month(moment_memory):
    """Test saving a partial moment with year and month (November 2025)."""
    moment_memory.save(
        id="nov_2025",
        year=2025,
        month=11,
    )
    
    loaded = moment_memory.load(id="nov_2025")
    
    assert loaded["year"] == 2025
    assert loaded["month"] == 11
    assert loaded["day"] is None


def test_load_nonexistent_moment(moment_memory):
    """Test loading a moment that doesn't exist."""
    loaded = moment_memory.load(id="nonexistent")
    assert loaded is None


def test_delete_moment(moment_memory):
    """Test deleting a moment."""
    moment_memory.save(id="to_delete", year=2020)
    
    deleted = moment_memory.delete(id="to_delete")
    assert deleted is True
    
    loaded = moment_memory.load(id="to_delete")
    assert loaded is None


def test_delete_nonexistent_moment(moment_memory):
    """Test deleting a moment that doesn't exist."""
    deleted = moment_memory.delete(id="nonexistent")
    assert deleted is False


def test_update_moment(moment_memory):
    """Test updating an existing moment."""
    moment_memory.save(id="updatable", year=2020, month=1)
    
    moment_memory.save(id="updatable", year=2021, month=6)
    
    loaded = moment_memory.load(id="updatable")
    assert loaded["year"] == 2021
    assert loaded["month"] == 6


# =============================================================================
# List Tests
# =============================================================================

def test_list_all_moments(moment_memory):
    """Test listing all moments."""
    moment_memory.save(id="m1", year=2020)
    moment_memory.save(id="m2", year=2021)
    moment_memory.save(id="m3", year=2022)
    
    moments = moment_memory.list()
    
    assert len(moments) == 3


def test_list_with_limit(moment_memory):
    """Test listing moments with limit."""
    moment_memory.save(id="m1", year=2020)
    moment_memory.save(id="m2", year=2021)
    moment_memory.save(id="m3", year=2022)
    
    moments = moment_memory.list(limit=2)
    
    assert len(moments) == 2


def test_list_by_record_type(moment_memory):
    """Test listing moments filtered by record_type."""
    moment_memory.save(id="bd1", year=1990, record_type="birthdate")
    moment_memory.save(id="bd2", year=1985, record_type="birthdate")
    moment_memory.save(id="ev1", year=2020, record_type="event")
    
    birthdates = moment_memory.list(record_type="birthdate")
    
    assert len(birthdates) == 2
    assert all(m["record_type"] == "birthdate" for m in birthdates)


# =============================================================================
# Find Nearest Tests
# =============================================================================

def test_find_nearest_by_year(moment_memory):
    """Test finding moments nearest to a target year."""
    moment_memory.save(id="y2020", year=2020)
    moment_memory.save(id="y2022", year=2022)
    moment_memory.save(id="y2025", year=2025)
    
    nearest = moment_memory.find_nearest(year=2021, limit=2)
    
    assert len(nearest) == 2
    # 2020 and 2022 are both distance 1 from 2021
    ids = {m["id"] for m in nearest}
    assert "y2020" in ids or "y2022" in ids


def test_find_nearest_by_month(moment_memory):
    """Test finding moments nearest to a target month."""
    moment_memory.save(id="jan", month=1)
    moment_memory.save(id="jun", month=6)
    moment_memory.save(id="dec", month=12)
    
    nearest = moment_memory.find_nearest(month=5, limit=1)
    
    assert len(nearest) == 1
    assert nearest[0]["id"] == "jun"  # June (6) is closest to May (5)


def test_find_nearest_by_year_and_month(moment_memory):
    """Test finding nearest with multiple components."""
    moment_memory.save(id="jan_2020", year=2020, month=1)
    moment_memory.save(id="dec_2020", year=2020, month=12)
    moment_memory.save(id="jan_2021", year=2021, month=1)
    
    nearest = moment_memory.find_nearest(year=2020, month=6, limit=1)
    
    # jan_2020: year diff=0, month diff=5 -> 0*365 + 5*30 = 150
    # dec_2020: year diff=0, month diff=6 -> 0*365 + 6*30 = 180
    # jan_2021: year diff=1, month diff=5 -> 1*365 + 5*30 = 515
    # jan_2020 is closest
    assert nearest[0]["id"] == "jan_2020"


def test_find_nearest_with_record_type_filter(moment_memory):
    """Test finding nearest filtered by record_type."""
    moment_memory.save(id="bd1990", year=1990, record_type="birthdate")
    moment_memory.save(id="ev1991", year=1991, record_type="event")
    moment_memory.save(id="bd2000", year=2000, record_type="birthdate")
    
    nearest = moment_memory.find_nearest(
        year=1992,
        record_type="birthdate",
        limit=1,
    )
    
    assert len(nearest) == 1
    assert nearest[0]["id"] == "bd1990"  # Closest birthdate to 1992


def test_find_nearest_returns_distance(moment_memory):
    """Test that find_nearest returns distance in results."""
    moment_memory.save(id="y2020", year=2020)
    
    nearest = moment_memory.find_nearest(year=2025, limit=1)
    
    assert "distance" in nearest[0]
    # Distance should be 5 years * 365 weight = 1825
    assert nearest[0]["distance"] == 5 * 365.0


# =============================================================================
# Find in Range Tests
# =============================================================================

def test_find_in_range_year(moment_memory):
    """Test finding moments within a year range."""
    moment_memory.save(id="y2018", year=2018)
    moment_memory.save(id="y2020", year=2020)
    moment_memory.save(id="y2022", year=2022)
    moment_memory.save(id="y2025", year=2025)
    
    in_range = moment_memory.find_in_range(
        min_year=2019,
        max_year=2023,
    )
    
    assert len(in_range) == 2
    ids = {m["id"] for m in in_range}
    assert ids == {"y2020", "y2022"}


def test_find_in_range_month(moment_memory):
    """Test finding moments within a month range."""
    moment_memory.save(id="jan", month=1)
    moment_memory.save(id="apr", month=4)
    moment_memory.save(id="jul", month=7)
    moment_memory.save(id="oct", month=10)
    
    in_range = moment_memory.find_in_range(
        min_month=3,
        max_month=8,
    )
    
    ids = {m["id"] for m in in_range}
    assert ids == {"apr", "jul"}


def test_find_in_range_with_record_type_filter(moment_memory):
    """Test range search filtered by record_type."""
    moment_memory.save(id="bd1990", year=1990, record_type="birthdate")
    moment_memory.save(id="ev1995", year=1995, record_type="event")
    moment_memory.save(id="bd2000", year=2000, record_type="birthdate")
    
    in_range = moment_memory.find_in_range(
        min_year=1985,
        max_year=1999,
        record_type="birthdate",
    )
    
    assert len(in_range) == 1
    assert in_range[0]["id"] == "bd1990"


def test_find_in_range_returns_empty_when_no_match(moment_memory):
    """Test that range search returns empty list when nothing matches."""
    moment_memory.save(id="y2020", year=2020)
    
    in_range = moment_memory.find_in_range(min_year=2025, max_year=2030)
    
    assert in_range == []
