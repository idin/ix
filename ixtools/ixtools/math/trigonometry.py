"""
Trigonometric functions for mathematical operations.
"""

import math
import numpy as np
import pandas as pd


def sin(value):
    """Calculate sine of value(s)."""
    if isinstance(value, (pd.Series, pd.DataFrame)):
        return value.apply(math.sin)
    elif isinstance(value, np.ndarray):
        return np.sin(value)
    elif isinstance(value, (list, tuple)):
        return [math.sin(x) for x in value]
    else:
        return math.sin(value)


def cos(value):
    """Calculate cosine of value(s)."""
    if isinstance(value, (pd.Series, pd.DataFrame)):
        return value.apply(math.cos)
    elif isinstance(value, np.ndarray):
        return np.cos(value)
    elif isinstance(value, (list, tuple)):
        return [math.cos(x) for x in value]
    else:
        return math.cos(value)


def tan(value):
    """Calculate tangent of value(s)."""
    if isinstance(value, (pd.Series, pd.DataFrame)):
        return value.apply(math.tan)
    elif isinstance(value, np.ndarray):
        return np.tan(value)
    elif isinstance(value, (list, tuple)):
        return [math.tan(x) for x in value]
    else:
        return math.tan(value)


def asin(value):
    """Calculate arcsine of value(s)."""
    if isinstance(value, (pd.Series, pd.DataFrame)):
        return value.apply(math.asin)
    elif isinstance(value, np.ndarray):
        return np.arcsin(value)
    elif isinstance(value, (list, tuple)):
        return [math.asin(x) for x in value]
    else:
        return math.asin(value)


def acos(value):
    """Calculate arccosine of value(s)."""
    if isinstance(value, (pd.Series, pd.DataFrame)):
        return value.apply(math.acos)
    elif isinstance(value, np.ndarray):
        return np.arccos(value)
    elif isinstance(value, (list, tuple)):
        return [math.acos(x) for x in value]
    else:
        return math.acos(value)


def atan(value):
    """Calculate arctangent of value(s)."""
    if isinstance(value, (pd.Series, pd.DataFrame)):
        return value.apply(math.atan)
    elif isinstance(value, np.ndarray):
        return np.arctan(value)
    elif isinstance(value, (list, tuple)):
        return [math.atan(x) for x in value]
    else:
        return math.atan(value)

