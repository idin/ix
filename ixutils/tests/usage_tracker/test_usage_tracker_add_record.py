"""
Tests for UsageTracker add_record method.
"""

from ixutils import UsageTracker


def test_add_record_with_usage_only():
    """Test adding a record with only usage data."""
    tracker = UsageTracker(include_conversation_id=False)
    
    usage = {
        "input_tokens": 100,
        "output_tokens": 50,
        "total_tokens": 150,
    }
    
    tracker.add_record(usage=usage)
    
    assert len(tracker.records) == 1
    assert tracker.records[0]["input_tokens"] == 100
    assert tracker.records[0]["output_tokens"] == 50
    assert tracker.records[0]["total_tokens"] == 150
    assert tracker.records[0]["input_cost"] is None
    assert tracker.records[0]["output_cost"] is None
    assert tracker.records[0]["total_cost"] is None
    assert "llm" not in tracker.records[0]
    assert "conversation_id" not in tracker.records[0]


def test_add_record_with_cost_only():
    """Test adding a record with only cost data."""
    tracker = UsageTracker(include_conversation_id=False)
    
    cost = {
        "input_cost": 0.001,
        "output_cost": 0.002,
        "total_cost": 0.003,
    }
    
    tracker.add_record(cost=cost)
    
    assert len(tracker.records) == 1
    assert tracker.records[0]["input_tokens"] is None
    assert tracker.records[0]["output_tokens"] is None
    assert tracker.records[0]["total_tokens"] is None
    assert tracker.records[0]["input_cost"] == 0.001
    assert tracker.records[0]["output_cost"] == 0.002
    assert tracker.records[0]["total_cost"] == 0.003


def test_add_record_with_usage_and_cost():
    """Test adding a record with both usage and cost data."""
    tracker = UsageTracker(include_conversation_id=False)
    
    usage = {
        "input_tokens": 200,
        "output_tokens": 100,
        "total_tokens": 300,
    }
    
    cost = {
        "input_cost": 0.002,
        "output_cost": 0.001,
        "total_cost": 0.003,
    }
    
    tracker.add_record(usage=usage, cost=cost)
    
    assert len(tracker.records) == 1
    record = tracker.records[0]
    assert record["input_tokens"] == 200
    assert record["output_tokens"] == 100
    assert record["total_tokens"] == 300
    assert record["input_cost"] == 0.002
    assert record["output_cost"] == 0.001
    assert record["total_cost"] == 0.003


def test_add_record_with_llm():
    """Test adding a record with LLM identifier."""
    tracker = UsageTracker(include_conversation_id=False)
    
    usage = {"input_tokens": 50, "output_tokens": 25, "total_tokens": 75}
    
    tracker.add_record(usage=usage, llm="gpt-4")
    
    assert len(tracker.records) == 1
    assert tracker.records[0]["llm"] == "gpt-4"


def test_add_record_with_conversation_id():
    """Test adding a record with conversation_id when enabled."""
    tracker = UsageTracker(include_conversation_id=True)
    
    usage = {"input_tokens": 50, "output_tokens": 25, "total_tokens": 75}
    
    tracker.add_record(usage=usage, conversation_id="conv-1")
    
    assert len(tracker.records) == 1
    assert tracker.records[0]["conversation_id"] == "conv-1"


def test_add_record_without_conversation_id_when_not_enabled():
    """Test that conversation_id is not added when include_conversation_id is False."""
    tracker = UsageTracker(include_conversation_id=False)
    
    usage = {"input_tokens": 50, "output_tokens": 25, "total_tokens": 75}
    
    tracker.add_record(usage=usage, conversation_id="conv-1")
    
    assert len(tracker.records) == 1
    assert "conversation_id" not in tracker.records[0]


def test_add_record_with_missing_values():
    """Test adding a record with missing values in usage/cost dictionaries."""
    tracker = UsageTracker(include_conversation_id=False)
    
    usage = {"input_tokens": 100}  # Missing output_tokens and total_tokens
    cost = {"input_cost": 0.001}  # Missing output_cost and total_cost
    
    tracker.add_record(usage=usage, cost=cost)
    
    assert len(tracker.records) == 1
    assert tracker.records[0]["input_tokens"] == 100
    assert tracker.records[0]["output_tokens"] is None
    assert tracker.records[0]["total_tokens"] is None
    assert tracker.records[0]["input_cost"] == 0.001
    assert tracker.records[0]["output_cost"] is None
    assert tracker.records[0]["total_cost"] is None


def test_add_record_with_none_values():
    """Test adding a record with None for usage and cost."""
    tracker = UsageTracker(include_conversation_id=False)
    
    tracker.add_record(usage=None, cost=None)
    
    assert len(tracker.records) == 1
    assert tracker.records[0]["input_tokens"] is None
    assert tracker.records[0]["output_tokens"] is None
    assert tracker.records[0]["total_tokens"] is None
    assert tracker.records[0]["input_cost"] is None
    assert tracker.records[0]["output_cost"] is None
    assert tracker.records[0]["total_cost"] is None


def test_add_multiple_records():
    """Test adding multiple records."""
    tracker = UsageTracker(include_conversation_id=False)
    
    tracker.add_record(
        usage={"input_tokens": 100, "output_tokens": 50, "total_tokens": 150},
        cost={"input_cost": 0.001, "output_cost": 0.0005, "total_cost": 0.0015},
        llm="gpt-4",
    )
    
    tracker.add_record(
        usage={"input_tokens": 200, "output_tokens": 100, "total_tokens": 300},
        cost={"input_cost": 0.002, "output_cost": 0.001, "total_cost": 0.003},
        llm="gpt-4",
    )
    
    assert len(tracker.records) == 2
    assert tracker.records[0]["input_tokens"] == 100
    assert tracker.records[1]["input_tokens"] == 200

