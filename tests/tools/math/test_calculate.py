"""
Tests for calculate function.
"""

import pytest
import math

from ixmachina.tools.math import calculate


def test_calculate_basic_addition():
    """Test basic addition."""
    result = calculate("2 + 3")
    assert result["success"] is True
    assert result["result"] == 5
    assert result["error"] is None


def test_calculate_basic_subtraction():
    """Test basic subtraction."""
    result = calculate("10 - 4")
    assert result["success"] is True
    assert result["result"] == 6
    assert result["error"] is None


def test_calculate_basic_multiplication():
    """Test basic multiplication."""
    result = calculate("3 * 4")
    assert result["success"] is True
    assert result["result"] == 12
    assert result["error"] is None


def test_calculate_basic_division():
    """Test basic division."""
    result = calculate("15 / 3")
    assert result["success"] is True
    assert result["result"] == 5.0
    assert result["error"] is None


def test_calculate_operator_precedence():
    """Test operator precedence (multiplication before addition)."""
    result = calculate("2 + 2 * 3")
    assert result["success"] is True
    assert result["result"] == 8  # 2 + (2 * 3) = 2 + 6 = 8, not (2 + 2) * 3 = 12


def test_calculate_parentheses():
    """Test parentheses override precedence."""
    result = calculate("(2 + 2) * 3")
    assert result["success"] is True
    assert result["result"] == 12  # (2 + 2) * 3 = 4 * 3 = 12


def test_calculate_nested_parentheses():
    """Test nested parentheses."""
    result = calculate("2 + (3 * 3 + 1)")
    assert result["success"] is True
    assert result["result"] == 12  # 2 + (9 + 1) = 2 + 10 = 12


def test_calculate_power():
    """Test power operation."""
    result = calculate("2 ** 3")
    assert result["success"] is True
    assert result["result"] == 8


def test_calculate_sqrt():
    """Test square root function."""
    result = calculate("sqrt(16)")
    assert result["success"] is True
    assert result["result"] == 4.0


def test_calculate_sin():
    """Test sine function."""
    result = calculate("sin(pi/2)")
    assert result["success"] is True
    assert abs(result["result"] - 1.0) < 0.0001


def test_calculate_cos():
    """Test cosine function."""
    result = calculate("cos(0)")
    assert result["success"] is True
    assert abs(result["result"] - 1.0) < 0.0001


def test_calculate_pi_constant():
    """Test pi constant."""
    result = calculate("pi")
    assert result["success"] is True
    assert abs(result["result"] - math.pi) < 0.0001


def test_calculate_e_constant():
    """Test e constant."""
    result = calculate("e")
    assert result["success"] is True
    assert abs(result["result"] - math.e) < 0.0001


def test_calculate_mean():
    """Test mean function with list."""
    result = calculate("mean([1,2,3,4,5])")
    assert result["success"] is True
    assert result["result"] == 3.0


def test_calculate_median():
    """Test median function with list."""
    result = calculate("median([1,2,3,4,5])")
    assert result["success"] is True
    assert result["result"] == 3
    
    result = calculate("median([1,2,3,4])")
    assert result["success"] is True
    assert result["result"] == 2.5


def test_calculate_std():
    """Test standard deviation function."""
    result = calculate("std([1,2,3,4,5])")
    assert result["success"] is True
    # Standard deviation of [1,2,3,4,5] ≈ 1.4142
    assert abs(result["result"] - 1.4142) < 0.01


def test_calculate_variance():
    """Test variance function."""
    result = calculate("variance([1,2,3,4,5])")
    assert result["success"] is True
    # Variance of [1,2,3,4,5] = 2.0
    assert abs(result["result"] - 2.0) < 0.01


def test_calculate_complex_expression():
    """Test complex expression with multiple operations."""
    result = calculate("sqrt(16) + sin(pi/2) * 2")
    assert result["success"] is True
    assert abs(result["result"] - 6.0) < 0.0001  # 4 + 1 * 2 = 4 + 2 = 6


def test_calculate_error_empty_expression():
    """Test error handling for empty expression."""
    result = calculate("")
    assert result["success"] is False
    assert result["result"] is None
    assert "empty" in result["error"].lower()


def test_calculate_error_invalid_syntax():
    """Test error handling for invalid syntax."""
    # Use a truly invalid syntax that Python AST cannot parse
    result = calculate("2 +")
    assert result["success"] is False
    assert result["result"] is None
    assert "syntax" in result["error"].lower() or "invalid" in result["error"].lower() or "parse" in result["error"].lower()


def test_calculate_error_unknown_function():
    """Test error handling for unknown function."""
    result = calculate("unknown_func(5)")
    assert result["success"] is False
    assert result["result"] is None
    assert "unknown" in result["error"].lower() or "Unknown function" in result["error"]


def test_calculate_error_division_by_zero():
    """Test error handling for division by zero."""
    result = calculate("10 / 0")
    assert result["success"] is False
    assert result["result"] is None
    assert "zero" in result["error"].lower() or "Division by zero" in result["error"]

