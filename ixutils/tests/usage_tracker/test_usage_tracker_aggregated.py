"""
Tests for UsageTracker aggregated DataFrame methods.
"""

from ixutils import UsageTracker


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

