"""
Tests for UsageTracker class.
"""

import pytest
from ixmachina.utils.usage_tracker import UsageTracker


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


def test_get_aggregated_dataframe_no_grouping():
    """Test getting aggregated DataFrame with no grouping."""
    tracker = UsageTracker(include_conversation_id=False)
    
    tracker.add_record(
        usage={"input_tokens": 100, "output_tokens": 50, "total_tokens": 150},
        cost={"input_cost": 0.001, "output_cost": 0.0005, "total_cost": 0.0015},
    )
    
    tracker.add_record(
        usage={"input_tokens": 200, "output_tokens": 100, "total_tokens": 300},
        cost={"input_cost": 0.002, "output_cost": 0.001, "total_cost": 0.003},
    )
    
    df = tracker.get_aggregated_dataframe(group_by=[])
    
    assert len(df) == 1
    assert df.iloc[0]["input_tokens"] == 300
    assert df.iloc[0]["output_tokens"] == 150
    assert df.iloc[0]["total_tokens"] == 450
    assert abs(df.iloc[0]["input_cost"] - 0.003) < 0.0001
    assert abs(df.iloc[0]["output_cost"] - 0.0015) < 0.0001
    assert abs(df.iloc[0]["total_cost"] - 0.0045) < 0.0001


def test_get_aggregated_dataframe_by_llm():
    """Test getting aggregated DataFrame grouped by LLM."""
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
    
    tracker.add_record(
        usage={"input_tokens": 50, "output_tokens": 25, "total_tokens": 75},
        cost={"input_cost": 0.0005, "output_cost": 0.00025, "total_cost": 0.00075},
        llm="gpt-3.5",
    )
    
    df = tracker.get_aggregated_dataframe(group_by=["llm"])
    
    assert len(df) == 2
    gpt4_row = df[df["llm"] == "gpt-4"].iloc[0]
    assert gpt4_row["input_tokens"] == 300
    assert gpt4_row["output_tokens"] == 150
    assert gpt4_row["total_tokens"] == 450
    
    gpt35_row = df[df["llm"] == "gpt-3.5"].iloc[0]
    assert gpt35_row["input_tokens"] == 50
    assert gpt35_row["output_tokens"] == 25
    assert gpt35_row["total_tokens"] == 75


def test_get_aggregated_dataframe_by_llm_and_conversation():
    """Test getting aggregated DataFrame grouped by LLM and conversation_id."""
    tracker = UsageTracker(include_conversation_id=True)
    
    tracker.add_record(
        usage={"input_tokens": 100, "output_tokens": 50, "total_tokens": 150},
        cost={"input_cost": 0.001, "output_cost": 0.0005, "total_cost": 0.0015},
        llm="gpt-4",
        conversation_id="conv-1",
    )
    
    tracker.add_record(
        usage={"input_tokens": 200, "output_tokens": 100, "total_tokens": 300},
        cost={"input_cost": 0.002, "output_cost": 0.001, "total_cost": 0.003},
        llm="gpt-4",
        conversation_id="conv-1",
    )
    
    tracker.add_record(
        usage={"input_tokens": 50, "output_tokens": 25, "total_tokens": 75},
        cost={"input_cost": 0.0005, "output_cost": 0.00025, "total_cost": 0.00075},
        llm="gpt-4",
        conversation_id="conv-2",
    )
    
    df = tracker.get_aggregated_dataframe(group_by=["llm", "conversation_id"])
    
    assert len(df) == 2
    conv1_row = df[(df["llm"] == "gpt-4") & (df["conversation_id"] == "conv-1")].iloc[0]
    assert conv1_row["input_tokens"] == 300
    assert conv1_row["output_tokens"] == 150
    
    conv2_row = df[(df["llm"] == "gpt-4") & (df["conversation_id"] == "conv-2")].iloc[0]
    assert conv2_row["input_tokens"] == 50
    assert conv2_row["output_tokens"] == 25


def test_get_aggregated_dataframe_default_grouping():
    """Test getting aggregated DataFrame with default grouping."""
    tracker = UsageTracker(include_conversation_id=True)
    
    tracker.add_record(
        usage={"input_tokens": 100, "output_tokens": 50, "total_tokens": 150},
        llm="gpt-4",
        conversation_id="conv-1",
    )
    
    tracker.add_record(
        usage={"input_tokens": 200, "output_tokens": 100, "total_tokens": 300},
        llm="gpt-4",
        conversation_id="conv-1",
    )
    
    df = tracker.get_aggregated_dataframe()
    
    assert len(df) == 1
    assert df.iloc[0]["llm"] == "gpt-4"
    assert df.iloc[0]["conversation_id"] == "conv-1"
    assert df.iloc[0]["input_tokens"] == 300
    assert df.iloc[0]["output_tokens"] == 150



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
