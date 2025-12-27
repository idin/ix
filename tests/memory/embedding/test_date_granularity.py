"""
Tests for date granularity and distance calculations.

Verifies that:
- Year-only dates normalize to middle of year (July 1)
- Month-only dates normalize to middle of month (15th)
- Distance is 0 for dates within same year/month based on granularity
"""

from ixmachina.memory import MemoryStore


def test_year_granularity_normalization():
    """Test that year-only dates are normalized to middle of year."""
    store = MemoryStore(auto_embed=False)
    
    year_result = store.save_object(name='Year2010', value='2010', object_type='date')
    
    # All dates in 2010 should have distance 0
    store.save_object(name='Jan2010', value='2010-01-01', object_type='date')
    store.save_object(name='Jun2010', value='2010-06-30', object_type='date')
    store.save_object(name='Dec2010', value='2010-12-31', object_type='date')
    
    # Dates outside 2010 should have non-zero distance
    store.save_object(name='Dec2009', value='2009-12-31', object_type='date')
    store.save_object(name='Jan2011', value='2011-01-01', object_type='date')
    
    result = store.find_similar_objects(
        object_id=year_result['object_id'],
        limit=10,
        exclude_self=True,
    )
    
    assert result['success']
    similar = {obj['name']: obj['similarity'] for obj in result['similar_objects']}
    
    # All 2010 dates should have similarity 1.0 (distance 0)
    assert similar['Jan2010'] == 1.0
    assert similar['Jun2010'] == 1.0
    assert similar['Dec2010'] == 1.0
    
    # Non-2010 dates should have similarity < 1.0
    assert similar['Dec2009'] < 1.0
    assert similar['Jan2011'] < 1.0


def test_month_granularity_normalization():
    """Test that month-only dates are normalized to middle of month."""
    store = MemoryStore(auto_embed=False)
    
    month_result = store.save_object(name='June2010', value='2010-06', object_type='date')
    
    # All dates in June 2010 should have distance 0
    store.save_object(name='Jun1', value='2010-06-01', object_type='date')
    store.save_object(name='Jun15', value='2010-06-15', object_type='date')
    store.save_object(name='Jun30', value='2010-06-30', object_type='date')
    
    # Dates outside June 2010 should have non-zero distance
    store.save_object(name='May31', value='2010-05-31', object_type='date')
    store.save_object(name='Jul1', value='2010-07-01', object_type='date')
    
    result = store.find_similar_objects(
        object_id=month_result['object_id'],
        limit=10,
        exclude_self=True,
    )
    
    assert result['success']
    similar = {obj['name']: obj['similarity'] for obj in result['similar_objects']}
    
    # All June 2010 dates should have similarity 1.0 (distance 0)
    assert similar['Jun1'] == 1.0
    assert similar['Jun15'] == 1.0
    assert similar['Jun30'] == 1.0
    
    # Non-June dates should have similarity < 1.0
    assert similar['May31'] < 1.0
    assert similar['Jul1'] < 1.0


def test_day_granularity_exact_match():
    """Test that full dates use exact day-based distance."""
    store = MemoryStore(auto_embed=False)
    
    base_result = store.save_object(name='BaseDate', value='2010-06-15', object_type='date')
    
    # Create dates at various distances
    store.save_object(name='SameDay', value='2010-06-15', object_type='date')
    store.save_object(name='OneDayAfter', value='2010-06-16', object_type='date')
    store.save_object(name='OneWeekAfter', value='2010-06-22', object_type='date')
    store.save_object(name='OneMonthAfter', value='2010-07-15', object_type='date')
    
    result = store.find_similar_objects(
        object_id=base_result['object_id'],
        limit=10,
        exclude_self=True,
    )
    
    assert result['success']
    similar = {obj['name']: obj['similarity'] for obj in result['similar_objects']}
    
    # Same day should have highest similarity
    assert similar['SameDay'] == 1.0
    
    # Closer dates should have higher similarity
    assert similar['OneDayAfter'] > similar['OneWeekAfter']
    assert similar['OneWeekAfter'] > similar['OneMonthAfter']


def test_mixed_granularity_comparison():
    """Test comparison between dates with different granularities."""
    store = MemoryStore(auto_embed=False)
    
    # Year-only date
    year_result = store.save_object(name='Year2010', value='2010', object_type='date')
    
    # Month in that year
    store.save_object(name='June2010', value='2010-06', object_type='date')
    
    # Day in that year
    store.save_object(name='June15', value='2010-06-15', object_type='date')
    
    # Different year
    store.save_object(name='Year2011', value='2011', object_type='date')
    
    result = store.find_similar_objects(
        object_id=year_result['object_id'],
        limit=10,
        exclude_self=True,
    )
    
    assert result['success']
    similar = {obj['name']: obj['similarity'] for obj in result['similar_objects']}
    
    # All 2010 dates (regardless of granularity) should have distance 0
    assert similar['June2010'] == 1.0
    assert similar['June15'] == 1.0
    
    # Different year should have lower similarity
    assert similar['Year2011'] < similar['June2010']


def test_partial_date_year_to_complete_dates():
    """
    Test finding closest complete dates to a year-only date.
    
    All dates within 2010 should have similarity 1.0 (distance 0).
    """
    store = MemoryStore(auto_embed=False)
    
    year_result = store.save_object(name='Year2010', value='2010', object_type='date')
    
    # Create dates at boundaries and middle of 2010
    store.save_object(name='EndOf2009', value='2009-12-31', object_type='date')
    store.save_object(name='EarlyJan2010', value='2010-01-05', object_type='date')
    store.save_object(name='MidYear2010', value='2010-06-15', object_type='date')
    store.save_object(name='EndOf2010', value='2010-12-31', object_type='date')
    store.save_object(name='StartOf2011', value='2011-01-15', object_type='date')
    
    result = store.find_similar_objects(
        object_id=year_result['object_id'],
        limit=10,
        exclude_self=True,
    )
    
    assert result['success']
    similar = {obj['name']: obj['similarity'] for obj in result['similar_objects']}
    
    # All 2010 dates should have similarity 1.0
    assert similar['EarlyJan2010'] == 1.0
    assert similar['MidYear2010'] == 1.0
    assert similar['EndOf2010'] == 1.0
    
    # Non-2010 dates should have lower similarity
    assert similar['EndOf2009'] < 1.0
    assert similar['StartOf2011'] < 1.0

