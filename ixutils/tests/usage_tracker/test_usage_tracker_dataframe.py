"""
Tests for UsageTracker DataFrame methods.
"""

from ixutils import UsageTracker


def test_get_dataframe_empty():
    """Test getting DataFrame from empty tracker."""
    tracker = UsageTracker(include_conversation_id=False)
    
    df = tracker.get_dataframe()
    
    assert len(df) == 0
    assert "input_tokens" in df.columns
    assert "output_tokens" in df.columns
    assert "total_tokens" in df.columns
    assert "input_cost" in df.columns
    assert "output_cost" in df.columns
    assert "total_cost" in df.columns
    assert "llm" in df.columns


def test_get_dataframe_with_records():
    """Test getting DataFrame with records."""
    tracker = UsageTracker(include_conversation_id=False)
    
    tracker.add_record(
        usage={"input_tokens": 100, "output_tokens": 50, "total_tokens": 150},
        cost={"input_cost": 0.001, "output_cost": 0.0005, "total_cost": 0.0015},
        llm="gpt-4",
    )
    
    df = tracker.get_dataframe()
    
    assert len(df) == 1
    assert df.iloc[0]["input_tokens"] == 100
    assert df.iloc[0]["output_tokens"] == 50
    assert df.iloc[0]["total_tokens"] == 150
    assert df.iloc[0]["input_cost"] == 0.001
    assert df.iloc[0]["output_cost"] == 0.0005
    assert df.iloc[0]["total_cost"] == 0.0015
    assert df.iloc[0]["llm"] == "gpt-4"


def test_get_dataframe_with_conversation_id():
    """Test getting DataFrame with conversation_id column."""
    tracker = UsageTracker(include_conversation_id=True)
    
    tracker.add_record(
        usage={"input_tokens": 100, "output_tokens": 50, "total_tokens": 150},
        conversation_id="conv-1",
    )
    
    df = tracker.get_dataframe()
    
    assert "conversation_id" in df.columns
    assert df.iloc[0]["conversation_id"] == "conv-1"

