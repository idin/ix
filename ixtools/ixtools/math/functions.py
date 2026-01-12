"""
Mathematical functions (sqrt, log, exp) for operations.
"""

import math
import numpy as np
import pandas as pd


def sqrt(value):
    """Calculate square root of value(s)."""
    if isinstance(value, (pd.Series, pd.DataFrame)):
        return value.apply(math.sqrt)
    elif isinstance(value, np.ndarray):
        return np.sqrt(value)
    elif isinstance(value, (list, tuple)):
        return [math.sqrt(x) for x in value]
    else:
        return math.sqrt(value)


def log(value):
    """Calculate natural logarithm of value(s)."""
    if isinstance(value, (pd.Series, pd.DataFrame)):
        return value.apply(math.log)
    elif isinstance(value, np.ndarray):
        return np.log(value)
    elif isinstance(value, (list, tuple)):
        return [math.log(x) for x in value]
    else:
        return math.log(value)


def exp(value):
    """Calculate exponential of value(s)."""
    if isinstance(value, (pd.Series, pd.DataFrame)):
        return value.apply(math.exp)
    elif isinstance(value, np.ndarray):
        return np.exp(value)
    elif isinstance(value, (list, tuple)):
        return [math.exp(x) for x in value]
    else:
        return math.exp(value)

