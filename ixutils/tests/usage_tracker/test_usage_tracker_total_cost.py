"""
Tests for UsageTracker get_total_cost method.
"""

from ixutils import UsageTracker


def test_get_total_cost_all_records():
    """Test get_total_cost with no filters."""
    tracker = UsageTracker(include_conversation_id=False)
    
    tracker.add_record(
        cost={"input_cost": 0.001, "output_cost": 0.0005, "total_cost": 0.0015},
        llm="gpt-4",
    )
    
    tracker.add_record(
        cost={"input_cost": 0.002, "output_cost": 0.001, "total_cost": 0.003},
        llm="gpt-4",
    )
    
    total = tracker.get_total_cost()
    
    assert abs(total["input_cost"] - 0.003) < 0.0001
    assert abs(total["output_cost"] - 0.0015) < 0.0001
    assert abs(total["total_cost"] - 0.0045) < 0.0001


def test_get_total_cost_filtered_by_llm():
    """Test get_total_cost filtered by LLM."""
    tracker = UsageTracker(include_conversation_id=False)
    
    tracker.add_record(
        cost={"input_cost": 0.001, "output_cost": 0.0005, "total_cost": 0.0015},
        llm="gpt-4",
    )
    
    tracker.add_record(
        cost={"input_cost": 0.002, "output_cost": 0.001, "total_cost": 0.003},
        llm="gpt-3.5",
    )
    
    total_gpt4 = tracker.get_total_cost(llm="gpt-4")
    assert abs(total_gpt4["input_cost"] - 0.001) < 0.0001
    assert abs(total_gpt4["output_cost"] - 0.0005) < 0.0001
    
    total_gpt35 = tracker.get_total_cost(llm="gpt-3.5")
    assert abs(total_gpt35["input_cost"] - 0.002) < 0.0001
    assert abs(total_gpt35["output_cost"] - 0.001) < 0.0001


def test_get_total_cost_filtered_by_conversation():
    """Test get_total_cost filtered by conversation_id."""
    tracker = UsageTracker(include_conversation_id=True)
    
    tracker.add_record(
        cost={"input_cost": 0.001, "output_cost": 0.0005, "total_cost": 0.0015},
        conversation_id="conv1",
    )
    
    tracker.add_record(
        cost={"input_cost": 0.002, "output_cost": 0.001, "total_cost": 0.003},
        conversation_id="conv2",
    )
    
    total_conv1 = tracker.get_total_cost(conversation_id="conv1")
    assert abs(total_conv1["input_cost"] - 0.001) < 0.0001
    
    total_conv2 = tracker.get_total_cost(conversation_id="conv2")
    assert abs(total_conv2["input_cost"] - 0.002) < 0.0001


def test_get_total_cost_no_records():
    """Test get_total_cost with no records."""
    tracker = UsageTracker(include_conversation_id=False)
    
    total = tracker.get_total_cost()
    
    assert total["input_cost"] is None
    assert total["output_cost"] is None
    assert total["total_cost"] is None


def test_get_total_cost_with_none_values():
    """Test get_total_cost when some records have None values."""
    tracker = UsageTracker(include_conversation_id=False)
    
    tracker.add_record(
        cost={"input_cost": 0.001, "output_cost": None, "total_cost": 0.0015},
        llm="gpt-4",
    )
    
    tracker.add_record(
        cost={"input_cost": 0.002, "output_cost": 0.001, "total_cost": 0.003},
        llm="gpt-4",
    )
    
    total = tracker.get_total_cost()
    
    assert abs(total["input_cost"] - 0.003) < 0.0001
    assert abs(total["output_cost"] - 0.001) < 0.0001  # Only the non-None value is summed
    assert abs(total["total_cost"] - 0.0045) < 0.0001

