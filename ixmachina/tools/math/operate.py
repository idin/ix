"""
Unified mathematical operations on various data types.

Supports operations on scalars, lists, tuples, numpy arrays, and pandas Series/DataFrames.
Handles element-wise operations and broadcasting automatically.
"""

from typing import Dict, Any, Union, List, Tuple, Optional
import operator
import math
import numpy as np
import pandas as pd

from ..constants import SUCCESS_KEY, RESULT_KEY, ERROR_KEY


# Statistical functions (unary operations)
def _mean(values):
    """Calculate mean of values."""
    if isinstance(values, (pd.Series, pd.DataFrame)):
        return values.mean()
    elif isinstance(values, np.ndarray):
        return float(np.mean(values))
    elif isinstance(values, (list, tuple)):
        return sum(values) / len(values) if len(values) > 0 else 0
    else:
        raise ValueError("mean requires a list, tuple, numpy array, or pandas Series/DataFrame")

def _median(values):
    """Calculate median of values."""
    if isinstance(values, (pd.Series, pd.DataFrame)):
        return values.median()
    elif isinstance(values, np.ndarray):
        return float(np.median(values))
    elif isinstance(values, (list, tuple)):
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        if n == 0:
            return 0
        if n % 2 == 1:
            return sorted_vals[n // 2]
        else:
            return (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2
    else:
        raise ValueError("median requires a list, tuple, numpy array, or pandas Series/DataFrame")

def _std(values):
    """Calculate standard deviation of values."""
    if isinstance(values, (pd.Series, pd.DataFrame)):
        return values.std()
    elif isinstance(values, np.ndarray):
        return float(np.std(values))
    elif isinstance(values, (list, tuple)):
        if len(values) == 0:
            return 0
        mean_val = sum(values) / len(values)
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        return variance ** 0.5
    else:
        raise ValueError("std requires a list, tuple, numpy array, or pandas Series/DataFrame")

def _variance(values):
    """Calculate variance of values."""
    if isinstance(values, (pd.Series, pd.DataFrame)):
        return values.var()
    elif isinstance(values, np.ndarray):
        return float(np.var(values))
    elif isinstance(values, (list, tuple)):
        if len(values) == 0:
            return 0
        mean_val = sum(values) / len(values)
        return sum((x - mean_val) ** 2 for x in values) / len(values)
    else:
        raise ValueError("variance requires a list, tuple, numpy array, or pandas Series/DataFrame")

# Trigonometric functions (unary operations)
def _sin(value):
    """Calculate sine of value(s)."""
    if isinstance(value, (pd.Series, pd.DataFrame)):
        return value.apply(math.sin)
    elif isinstance(value, np.ndarray):
        return np.sin(value)
    elif isinstance(value, (list, tuple)):
        return [math.sin(x) for x in value]
    else:
        return math.sin(value)

def _cos(value):
    """Calculate cosine of value(s)."""
    if isinstance(value, (pd.Series, pd.DataFrame)):
        return value.apply(math.cos)
    elif isinstance(value, np.ndarray):
        return np.cos(value)
    elif isinstance(value, (list, tuple)):
        return [math.cos(x) for x in value]
    else:
        return math.cos(value)

def _tan(value):
    """Calculate tangent of value(s)."""
    if isinstance(value, (pd.Series, pd.DataFrame)):
        return value.apply(math.tan)
    elif isinstance(value, np.ndarray):
        return np.tan(value)
    elif isinstance(value, (list, tuple)):
        return [math.tan(x) for x in value]
    else:
        return math.tan(value)

def _asin(value):
    """Calculate arcsine of value(s)."""
    if isinstance(value, (pd.Series, pd.DataFrame)):
        return value.apply(math.asin)
    elif isinstance(value, np.ndarray):
        return np.arcsin(value)
    elif isinstance(value, (list, tuple)):
        return [math.asin(x) for x in value]
    else:
        return math.asin(value)

def _acos(value):
    """Calculate arccosine of value(s)."""
    if isinstance(value, (pd.Series, pd.DataFrame)):
        return value.apply(math.acos)
    elif isinstance(value, np.ndarray):
        return np.arccos(value)
    elif isinstance(value, (list, tuple)):
        return [math.acos(x) for x in value]
    else:
        return math.acos(value)

def _atan(value):
    """Calculate arctangent of value(s)."""
    if isinstance(value, (pd.Series, pd.DataFrame)):
        return value.apply(math.atan)
    elif isinstance(value, np.ndarray):
        return np.arctan(value)
    elif isinstance(value, (list, tuple)):
        return [math.atan(x) for x in value]
    else:
        return math.atan(value)

def _sqrt(value):
    """Calculate square root of value(s)."""
    if isinstance(value, (pd.Series, pd.DataFrame)):
        return value.apply(math.sqrt)
    elif isinstance(value, np.ndarray):
        return np.sqrt(value)
    elif isinstance(value, (list, tuple)):
        return [math.sqrt(x) for x in value]
    else:
        return math.sqrt(value)

def _log(value):
    """Calculate natural logarithm of value(s)."""
    if isinstance(value, (pd.Series, pd.DataFrame)):
        return value.apply(math.log)
    elif isinstance(value, np.ndarray):
        return np.log(value)
    elif isinstance(value, (list, tuple)):
        return [math.log(x) for x in value]
    else:
        return math.log(value)

def _exp(value):
    """Calculate exponential (e^x) of value(s)."""
    if isinstance(value, (pd.Series, pd.DataFrame)):
        return value.apply(math.exp)
    elif isinstance(value, np.ndarray):
        return np.exp(value)
    elif isinstance(value, (list, tuple)):
        return [math.exp(x) for x in value]
    else:
        return math.exp(value)

# Operation mapping: normalize operation names to operator functions
_OPERATION_MAP = {
    # Addition
    "+": operator.add,
    "add": operator.add,
    "plus": operator.add,
    # Subtraction
    "-": operator.sub,
    "sub": operator.sub,
    "subtract": operator.sub,
    "minus": operator.sub,
    # Multiplication
    "*": operator.mul,
    "mul": operator.mul,
    "multiply": operator.mul,
    "times": operator.mul,
    # Division
    "/": operator.truediv,
    "div": operator.truediv,
    "divide": operator.truediv,
    # Floor division
    "//": operator.floordiv,
    "floordiv": operator.floordiv,
    # Modulo
    "%": operator.mod,
    "mod": operator.mod,
    "modulo": operator.mod,
    # Power
    "**": operator.pow,
    "pow": operator.pow,
    "power": operator.pow,
    # Statistical functions (unary)
    "mean": _mean,
    "median": _median,
    "std": _std,
    "std_dev": _std,
    "variance": _variance,
    # Trigonometric functions (unary)
    "sin": _sin,
    "cos": _cos,
    "tan": _tan,
    "asin": _asin,
    "acos": _acos,
    "atan": _atan,
    # Other math functions (unary)
    "sqrt": _sqrt,
    "log": _log,
    "exp": _exp,
}


def _normalize_operation(operation: str) -> Any:
    """
    Normalize operation string to operator function.
    
    Args:
        operation: Operation string (e.g., "add", "+", "multiply", "*").
    
    Returns:
        Operator function.
    
    Raises:
        ValueError: If operation is not supported.
    """
    operation = operation.strip().lower()
    if operation not in _OPERATION_MAP:
        raise ValueError(
            f"Unsupported operation: {operation}. "
            f"Supported operations: {', '.join(sorted(set(_OPERATION_MAP.keys())))}"
        )
    return _OPERATION_MAP[operation]


def _convert_to_best_type(values: Any) -> Any:
    """
    Convert values to the most capable type (pandas > numpy > list).
    
    Args:
        values: Input values (scalar, list, tuple, numpy array, pandas Series/DataFrame).
    
    Returns:
        Values in the best available type.
    """
    if isinstance(values, (pd.Series, pd.DataFrame)):
        return values
    if isinstance(values, np.ndarray):
        return values
    if isinstance(values, (list, tuple)):
        return np.array(values)
    # Scalar - return as-is
    return values


def _perform_operation(
    values: Any,
    operation_func: Any,
    other_values: Optional[Any] = None,
) -> Any:
    """
    Perform operation on values using numpy/pandas for efficiency.
    
    Args:
        values: First operand (scalar, list, numpy array, pandas Series/DataFrame).
        operation_func: Operator function (from operator module or statistical function).
        other_values: Second operand (optional for unary operations like mean, median).
    
    Returns:
        Result of the operation (in numpy/pandas form, not converted back).
    """
    # Check if this is a unary operation (statistical, trigonometric, or other math functions)
    # Unary functions are callable but not from operator module
    unary_functions = (_mean, _median, _std, _variance, _sin, _cos, _tan, _asin, _acos, _atan, _sqrt, _log, _exp)
    is_unary = other_values is None or operation_func in unary_functions
    
    if is_unary:
        # Unary operation (statistical functions)
        # Don't convert - statistical functions handle type conversion internally
        return operation_func(values)
    
    # Binary operation - convert to best type for operations
    values = _convert_to_best_type(values)
    other_values = _convert_to_best_type(other_values)
    
    # Perform operation - numpy/pandas handle broadcasting automatically
    return operation_func(values, other_values)


def operate(
    values: Union[float, int, List[float], Tuple[float, ...], Any],
    operation: str,
    other_values: Optional[Union[float, int, List[float], Tuple[float, ...], Any]] = None,
) -> Dict[str, Any]:
    """
    Perform a mathematical operation on values.
    
    Supports operations on:
    - Scalars (single numbers)
    - Lists/tuples
    - numpy arrays (if numpy is installed)
    - pandas Series/DataFrames (if pandas is installed)
    
    Operations can be specified as:
    - Symbols: "+", "-", "*", "/", "**", "%", "//"
    - Full names: "add", "subtract", "multiply", "divide", "power", "modulo"
    - Short aliases: "sub", "mul", "div", "pow", "mod"
    - Unary functions: "mean", "median", "std", "variance", "sin", "cos", "tan", "sqrt", "log", "exp"
    
    Behavior:
    - Scalar + Scalar → Scalar result
    - List + Scalar → List (broadcasting)
    - List + List (same length) → List (element-wise)
    - numpy array + numpy array → numpy array (element-wise or broadcasting)
    - pandas Series + pandas Series → pandas Series (element-wise)
    - DataFrame + DataFrame → DataFrame (element-wise)
    - mean/median/std/variance on List/Array/Series → Scalar result
    
    Args:
        values: First operand. Can be scalar, list, tuple, numpy array, or pandas Series/DataFrame.
        operation: Operation to perform (e.g., "add", "+", "multiply", "*", "mean", "median").
        other_values: Second operand (optional for unary operations like mean, median, std, variance).
                     Required for binary operations. Same types as values.
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if operation succeeded.
            - result: The operation result if successful, None otherwise.
            - error: Error message if operation failed, None if successful.
    
    Examples:
        >>> operate([1, 2, 3], "+", 5)
        {"success": True, "result": [6, 7, 8], "error": None}
        
        >>> operate([1, 2, 3], "multiply", [2, 3, 4])
        {"success": True, "result": [2, 6, 12], "error": None}
        
        >>> operate(10, "pow", 2)
        {"success": True, "result": 100, "error": None}
        
        >>> operate([1, 2, 3], "add", [4, 5])  # Length mismatch
        {"success": False, "result": None, "error": "Length mismatch: 3 vs 2..."}
        
        >>> operate([1, 2, 3, 4, 5], "mean")
        {"success": True, "result": 3.0, "error": None}
        
        >>> operate([1, 2, 3, 4, 5], "median")
        {"success": True, "result": 3, "error": None}
        
        >>> operate(pi/2, "sin")
        {"success": True, "result": 1.0, "error": None}
        
        >>> operate([0, pi/2, pi], "cos")
        {"success": True, "result": [1.0, 0.0, -1.0], "error": None}
    """
    try:
        # Normalize operation
        operation_func = _normalize_operation(operation)
        
        # Create type flags for original types
        def get_type_flag(value):
            if isinstance(value, pd.DataFrame):
                return "dataframe"
            elif isinstance(value, pd.Series):
                return "series"
            elif isinstance(value, np.ndarray):
                return "numpy"
            elif isinstance(value, list):
                return "list"
            elif isinstance(value, tuple):
                return "tuple"
            else:
                return "scalar"
        
        values_type_flag = get_type_flag(values)
        other_type_flag = get_type_flag(other_values) if other_values is not None else None
        
        # Perform operation in general form (using numpy/pandas)
        result = _perform_operation(values, operation_func, other_values)
        
        # Convert back based on type flags
        # Priority: pandas (dataframe/series) > numpy > list/tuple > scalar
        if values_type_flag in ("dataframe", "series") or other_type_flag in ("dataframe", "series"):
            # Result is already pandas, keep it
            pass
        elif values_type_flag == "numpy" or other_type_flag == "numpy":
            # Result is numpy, keep it
            pass
        elif values_type_flag == "list" or (other_type_flag == "list" and values_type_flag != "tuple"):
            # Convert back to list
            if isinstance(result, np.ndarray):
                result = result.tolist()
        elif values_type_flag == "tuple" or other_type_flag == "tuple":
            # Convert back to tuple
            if isinstance(result, np.ndarray):
                result = tuple(result.tolist())
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: result,
            ERROR_KEY: None,
        }
    
    except ValueError as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: str(e),
        }
    except ZeroDivisionError as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Division by zero: {str(e)}",
        }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Unexpected error: {str(e)}",
        }

