"""
Tests for UsageTracker get_total_usage method.
"""

from ixutils import UsageTracker


def test_get_total_usage_all_records():
    """Test get_total_usage with no filters."""
    tracker = UsageTracker(include_conversation_id=False)
    
    tracker.add_record(
        usage={"input_tokens": 100, "output_tokens": 50, "total_tokens": 150},
        llm="gpt-4",
    )
    
    tracker.add_record(
        usage={"input_tokens": 200, "output_tokens": 100, "total_tokens": 300},
        llm="gpt-4",
    )
    
    total = tracker.get_total_usage()
    
    assert total["input_tokens"] == 300
    assert total["output_tokens"] == 150
    assert total["total_tokens"] == 450


def test_get_total_usage_filtered_by_llm():
    """Test get_total_usage filtered by LLM."""
    tracker = UsageTracker(include_conversation_id=False)
    
    tracker.add_record(
        usage={"input_tokens": 100, "output_tokens": 50, "total_tokens": 150},
        llm="gpt-4",
    )
    
    tracker.add_record(
        usage={"input_tokens": 200, "output_tokens": 100, "total_tokens": 300},
        llm="gpt-3.5",
    )
    
    total_gpt4 = tracker.get_total_usage(llm="gpt-4")
    assert total_gpt4["input_tokens"] == 100
    assert total_gpt4["output_tokens"] == 50
    assert total_gpt4["total_tokens"] == 150
    
    total_gpt35 = tracker.get_total_usage(llm="gpt-3.5")
    assert total_gpt35["input_tokens"] == 200
    assert total_gpt35["output_tokens"] == 100
    assert total_gpt35["total_tokens"] == 300


def test_get_total_usage_filtered_by_conversation():
    """Test get_total_usage filtered by conversation_id."""
    tracker = UsageTracker(include_conversation_id=True)
    
    tracker.add_record(
        usage={"input_tokens": 100, "output_tokens": 50, "total_tokens": 150},
        conversation_id="conv1",
    )
    
    tracker.add_record(
        usage={"input_tokens": 200, "output_tokens": 100, "total_tokens": 300},
        conversation_id="conv2",
    )
    
    total_conv1 = tracker.get_total_usage(conversation_id="conv1")
    assert total_conv1["input_tokens"] == 100
    assert total_conv1["total_tokens"] == 150
    
    total_conv2 = tracker.get_total_usage(conversation_id="conv2")
    assert total_conv2["input_tokens"] == 200
    assert total_conv2["total_tokens"] == 300


def test_get_total_usage_filtered_by_llm_and_conversation():
    """Test get_total_usage filtered by both LLM and conversation_id."""
    tracker = UsageTracker(include_conversation_id=True)
    
    tracker.add_record(
        usage={"input_tokens": 100, "output_tokens": 50, "total_tokens": 150},
        llm="gpt-4",
        conversation_id="conv1",
    )
    
    tracker.add_record(
        usage={"input_tokens": 200, "output_tokens": 100, "total_tokens": 300},
        llm="gpt-4",
        conversation_id="conv1",
    )
    
    tracker.add_record(
        usage={"input_tokens": 50, "output_tokens": 25, "total_tokens": 75},
        llm="gpt-4",
        conversation_id="conv2",
    )
    
    total = tracker.get_total_usage(llm="gpt-4", conversation_id="conv1")
    assert total["input_tokens"] == 300
    assert total["output_tokens"] == 150
    assert total["total_tokens"] == 450


def test_get_total_usage_no_records():
    """Test get_total_usage with no records."""
    tracker = UsageTracker(include_conversation_id=False)
    
    total = tracker.get_total_usage()
    
    assert total["input_tokens"] is None
    assert total["output_tokens"] is None
    assert total["total_tokens"] is None


def test_get_total_usage_with_none_values():
    """Test get_total_usage when some records have None values."""
    tracker = UsageTracker(include_conversation_id=False)
    
    tracker.add_record(
        usage={"input_tokens": 100, "output_tokens": None, "total_tokens": 150},
        llm="gpt-4",
    )
    
    tracker.add_record(
        usage={"input_tokens": 200, "output_tokens": 100, "total_tokens": 300},
        llm="gpt-4",
    )
    
    total = tracker.get_total_usage()
    
    assert total["input_tokens"] == 300
    assert total["output_tokens"] == 100  # Only the non-None value is summed
    assert total["total_tokens"] == 450

