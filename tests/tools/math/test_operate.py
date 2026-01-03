"""
Tests for operate function.
"""

import pytest
import numpy as np
import pandas as pd
import math

from ixmachina.tools.math import operate


def test_operate_add_scalar():
    """Test addition with scalars."""
    result = operate(2, "+", 3)
    assert result["success"] is True
    assert result["result"] == 5
    assert result["error"] is None


def test_operate_add_list_scalar():
    """Test addition: list + scalar (broadcasting)."""
    result = operate([1, 2, 3], "+", 5)
    assert result["success"] is True
    assert result["result"] == [6, 7, 8]
    assert result["error"] is None


def test_operate_add_list_list():
    """Test addition: list + list (element-wise)."""
    result = operate([1, 2, 3], "+", [4, 5, 6])
    assert result["success"] is True
    assert result["result"] == [5, 7, 9]
    assert result["error"] is None


def test_operate_multiply_list_scalar():
    """Test multiplication: list * scalar."""
    result = operate([1, 2, 3], "*", 2)
    assert result["success"] is True
    assert result["result"] == [2, 4, 6]
    assert result["error"] is None


def test_operate_multiply_list_list():
    """Test multiplication: list * list (element-wise)."""
    result = operate([1, 2, 3], "multiply", [2, 3, 4])
    assert result["success"] is True
    assert result["result"] == [2, 6, 12]
    assert result["error"] is None


def test_operate_power():
    """Test power operation."""
    result = operate(10, "pow", 2)
    assert result["success"] is True
    assert result["result"] == 100


def test_operate_operation_aliases():
    """Test operation name aliases."""
    # Test "add" alias
    result1 = operate(2, "add", 3)
    result2 = operate(2, "+", 3)
    assert result1["result"] == result2["result"] == 5
    
    # Test "multiply" alias
    result1 = operate(2, "multiply", 3)
    result2 = operate(2, "*", 3)
    assert result1["result"] == result2["result"] == 6
    
    # Test "pow" alias
    result1 = operate(2, "pow", 3)
    result2 = operate(2, "power", 3)
    assert result1["result"] == result2["result"] == 8


def test_operate_mean():
    """Test mean statistical function."""
    result = operate([1, 2, 3, 4, 5], "mean")
    assert result["success"] is True
    assert result["result"] == 3.0


def test_operate_median():
    """Test median statistical function."""
    result = operate([1, 2, 3, 4, 5], "median")
    assert result["success"] is True
    assert result["result"] == 3
    
    result = operate([1, 2, 3, 4], "median")
    assert result["success"] is True
    assert result["result"] == 2.5


def test_operate_std():
    """Test standard deviation statistical function."""
    result = operate([1, 2, 3, 4, 5], "std")
    assert result["success"] is True
    assert abs(result["result"] - 1.4142) < 0.01


def test_operate_variance():
    """Test variance statistical function."""
    result = operate([1, 2, 3, 4, 5], "variance")
    assert result["success"] is True
    assert abs(result["result"] - 2.0) < 0.01


def test_operate_sin():
    """Test sine trigonometric function."""
    result = operate(math.pi / 2, "sin")
    assert result["success"] is True
    assert abs(result["result"] - 1.0) < 0.0001


def test_operate_cos():
    """Test cosine trigonometric function."""
    result = operate(0, "cos")
    assert result["success"] is True
    assert abs(result["result"] - 1.0) < 0.0001


def test_operate_sqrt():
    """Test square root function."""
    result = operate(16, "sqrt")
    assert result["success"] is True
    assert result["result"] == 4.0


def test_operate_sin_list():
    """Test sine function with list."""
    result = operate([0, math.pi/2, math.pi], "sin")
    assert result["success"] is True
    assert abs(result["result"][0] - 0.0) < 0.0001
    assert abs(result["result"][1] - 1.0) < 0.0001
    assert abs(result["result"][2] - 0.0) < 0.0001


def test_operate_numpy_array():
    """Test operate with numpy array."""
    values = np.array([1, 2, 3])
    result = operate(values, "+", 5)
    assert result["success"] is True
    assert isinstance(result["result"], np.ndarray)
    assert np.allclose(result["result"], [6, 7, 8])


def test_operate_pandas_series():
    """Test operate with pandas Series."""
    values = pd.Series([1, 2, 3])
    result = operate(values, "+", 5)
    assert result["success"] is True
    assert isinstance(result["result"], pd.Series)
    assert result["result"].tolist() == [6, 7, 8]


def test_operate_tuple_preserves_type():
    """Test that tuple input preserves tuple output."""
    result = operate((1, 2, 3), "+", 5)
    assert result["success"] is True
    assert isinstance(result["result"], tuple)
    assert result["result"] == (6, 7, 8)


def test_operate_error_unknown_operation():
    """Test error handling for unknown operation."""
    result = operate(5, "unknown_op", 3)
    assert result["success"] is False
    assert result["result"] is None
    assert "Unsupported operation" in result["error"] or "unknown" in result["error"].lower()


def test_operate_error_length_mismatch():
    """Test error handling for length mismatch in lists."""
    result = operate([1, 2, 3], "+", [4, 5])
    assert result["success"] is False
    assert result["result"] is None
    assert "length" in result["error"].lower() or "mismatch" in result["error"].lower() or "broadcast" in result["error"].lower() or "shape" in result["error"].lower()


def test_operate_error_division_by_zero():
    """Test error handling for division by zero."""
    result = operate(10, "/", 0)
    assert result["success"] is False
    assert result["result"] is None
    assert "zero" in result["error"].lower() or "Division by zero" in result["error"]

