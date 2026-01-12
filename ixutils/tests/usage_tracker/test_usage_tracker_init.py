"""
Tests for UsageTracker initialization.
"""

from ixutils import UsageTracker


def test_usage_tracker_init_without_conversation_id():
    """Test UsageTracker initialization without conversation_id."""
    tracker = UsageTracker(include_conversation_id=False)
    assert tracker.include_conversation_id is False
    assert tracker.records == []


def test_usage_tracker_init_with_conversation_id():
    """Test UsageTracker initialization with conversation_id."""
    tracker = UsageTracker(include_conversation_id=True)
    assert tracker.include_conversation_id is True
    assert tracker.records == []

