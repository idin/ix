"""
Statistical functions for mathematical operations.
"""

import numpy as np
import pandas as pd


def mean(values):
    """Calculate mean of values."""
    if isinstance(values, (pd.Series, pd.DataFrame)):
        return values.mean()
    elif isinstance(values, np.ndarray):
        return float(np.mean(values))
    elif isinstance(values, (list, tuple)):
        return sum(values) / len(values) if len(values) > 0 else 0
    else:
        raise ValueError("mean requires a list, tuple, numpy array, or pandas Series/DataFrame")


def median(values):
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


def std(values):
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


def variance(values):
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

