"""
Unit conversion tool.

Converts values from one unit to another using a base unit system.
Each unit category has a base unit, and all conversions go through the base unit.
"""

from typing import Dict, Any, Union, List, Tuple, Optional
import numpy as np
import pandas as pd

from ..constants import SUCCESS_KEY, RESULT_KEY, ERROR_KEY


# Unit conversion factors: each unit maps to its conversion factor to the base unit
# To convert from unit A to unit B: value * (factor_A / factor_B)
_UNIT_CONVERSIONS = {
    # Length (base: meter)
    "length": {
        "meter": 1.0,
        "metre": 1.0,  # British spelling
        "m": 1.0,
        "kilometer": 1000.0,
        "kilometre": 1000.0,
        "km": 1000.0,
        "centimeter": 0.01,
        "centimetre": 0.01,
        "cm": 0.01,
        "millimeter": 0.001,
        "millimetre": 0.001,
        "mm": 0.001,
        "mile": 1609.344,
        "mi": 1609.344,
        "yard": 0.9144,
        "yd": 0.9144,
        "foot": 0.3048,
        "feet": 0.3048,
        "ft": 0.3048,
        "inch": 0.0254,
        "in": 0.0254,
        "nautical_mile": 1852.0,
        "nmi": 1852.0,
    },
    # Mass (base: kilogram)
    "mass": {
        "kilogram": 1.0,
        "kg": 1.0,
        "gram": 0.001,
        "g": 0.001,
        "milligram": 0.000001,
        "mg": 0.000001,
        "pound": 0.453592,
        "lb": 0.453592,
        "ounce": 0.0283495,
        "oz": 0.0283495,
        "metric_ton": 1000.0,  # Metric ton
        "short_ton": 907.18474,  # US ton (2000 pounds)
        "long_ton": 1016.0469088,  # UK ton (2240 pounds)
    },
    # Temperature (special case - needs offset)
    "temperature": {
        "celsius": ("celsius", 1.0, 0.0),
        "c": ("celsius", 1.0, 0.0),
        "fahrenheit": ("celsius", 5.0/9.0, -32.0),
        "f": ("celsius", 5.0/9.0, -32.0),
        "kelvin": ("celsius", 1.0, -273.15),
        "k": ("celsius", 1.0, -273.15),
    },
    # Time (base: second)
    "time": {
        "second": 1.0,
        "sec": 1.0,
        "s": 1.0,
        "minute": 60.0,
        "min": 60.0,
        "hour": 3600.0,
        "hr": 3600.0,
        "h": 3600.0,
        "day": 86400.0,
        "d": 86400.0,
        "week": 604800.0,
        "wk": 604800.0,
        "month": 2592000.0,  # 30 days
        "year": 31536000.0,  # 365 days
        "yr": 31536000.0,
    },
    # Volume (base: liter)
    "volume": {
        "liter": 1.0,
        "litre": 1.0,
        "l": 1.0,
        "milliliter": 0.001,
        "millilitre": 0.001,
        "ml": 0.001,
        "gallon": 3.78541,
        "gal": 3.78541,
        "quart": 0.946353,
        "qt": 0.946353,
        "pint": 0.473176,
        "pt": 0.473176,
        "cup": 0.236588,
        "fluid_ounce": 0.0295735,
        "fl_oz": 0.0295735,
        "cubic_meter": 1000.0,
        "m3": 1000.0,
        "cubic_centimeter": 0.001,
        "cm3": 0.001,
    },
    # Energy (base: joule)
    "energy": {
        "joule": 1.0,
        "j": 1.0,
        "kilojoule": 1000.0,
        "kj": 1000.0,
        "calorie": 4.184,
        "cal": 4.184,
        "kilocalorie": 4184.0,
        "kcal": 4184.0,
        "british_thermal_unit": 1055.06,
        "btu": 1055.06,
        "kilowatt_hour": 3600000.0,
        "kwh": 3600000.0,
    },
    # Speed (base: meter per second)
    "speed": {
        "meter_per_second": 1.0,
        "mps": 1.0,
        "m/s": 1.0,
        "kilometer_per_hour": 0.277778,
        "kmh": 0.277778,
        "km/h": 0.277778,
        "mile_per_hour": 0.44704,
        "mph": 0.44704,
        "knot": 0.514444,
        "kt": 0.514444,
    },
}


def _normalize_unit_name(unit: str) -> str:
    """Normalize unit name to lowercase with underscores."""
    return unit.strip().lower().replace(" ", "_").replace("-", "_")


def _find_unit_category(unit: str) -> Optional[str]:
    """Find which category a unit belongs to."""
    normalized = _normalize_unit_name(unit)
    for category, units in _UNIT_CONVERSIONS.items():
        if normalized in units:
            return category
    return None


def _convert_temperature(value: Any, from_unit: str, to_unit: str) -> Any:
    """Convert temperature values (special case with offset)."""
    from_norm = _normalize_unit_name(from_unit)
    to_norm = _normalize_unit_name(to_unit)
    
    from_info = _UNIT_CONVERSIONS["temperature"][from_norm]
    to_info = _UNIT_CONVERSIONS["temperature"][to_norm]
    
    # Convert from source to celsius
    from_base, from_factor, from_offset = from_info[1], from_info[1], from_info[2]
    # Convert from celsius to target
    to_base, to_factor, to_offset = to_info[1], to_info[1], to_info[2]
    
    # Formula: (value * from_factor + from_offset) * (to_factor / from_factor) - to_offset
    # Simplified: value * (to_factor / from_factor) + (from_offset * to_factor / from_factor) - to_offset
    # Actually, let's do it step by step:
    # 1. Convert to celsius: celsius = (value + from_offset) * from_factor
    # 2. Convert from celsius: result = celsius / to_factor - to_offset
    
    if isinstance(value, (pd.Series, pd.DataFrame)):
        celsius = (value + from_offset) * from_factor
        return celsius / to_factor - to_offset
    elif isinstance(value, np.ndarray):
        celsius = (value + from_offset) * from_factor
        return (celsius / to_factor - to_offset)
    elif isinstance(value, (list, tuple)):
        return [(v + from_offset) * from_factor / to_factor - to_offset for v in value]
    else:
        celsius = (value + from_offset) * from_factor
        return celsius / to_factor - to_offset


def _convert_standard(value: Any, from_unit: str, to_unit: str, category: str) -> Any:
    """Convert standard units (using conversion factors)."""
    from_norm = _normalize_unit_name(from_unit)
    to_norm = _normalize_unit_name(to_unit)
    
    from_factor = _UNIT_CONVERSIONS[category][from_norm]
    to_factor = _UNIT_CONVERSIONS[category][to_norm]
    
    # Convert: value * (from_factor / to_factor)
    conversion_factor = from_factor / to_factor
    
    if isinstance(value, (pd.Series, pd.DataFrame)):
        return value * conversion_factor
    elif isinstance(value, np.ndarray):
        return value * conversion_factor
    elif isinstance(value, (list, tuple)):
        return [v * conversion_factor for v in value]
    else:
        return value * conversion_factor


def convert_units(
    values: Union[float, int, List[float], Tuple[float, ...], Any],
    from_unit: str,
    to_unit: str,
) -> Dict[str, Any]:
    """
    Convert values from one unit to another.
    
    Supports conversion of:
    - Scalars (single numbers)
    - Lists/tuples
    - numpy arrays
    - pandas Series/DataFrames
    
    Supported unit categories:
    - Length: meter, kilometer, mile, foot, inch, etc.
    - Mass: kilogram, gram, pound, ounce, etc.
    - Temperature: celsius, fahrenheit, kelvin
    - Time: second, minute, hour, day, etc.
    - Volume: liter, gallon, quart, etc.
    - Energy: joule, calorie, btu, etc.
    - Speed: meter_per_second, kilometer_per_hour, mile_per_hour, etc.
    
    Args:
        values: Value(s) to convert. Can be scalar, list, tuple, numpy array, or pandas Series/DataFrame.
        from_unit: Source unit name (e.g., "meter", "kilogram", "celsius").
        to_unit: Target unit name (e.g., "foot", "pound", "fahrenheit").
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if conversion succeeded.
            - result: Converted value(s) if successful, None otherwise.
            - error: Error message if conversion failed, None if successful.
    
    Examples:
        >>> convert_units(1000, "meter", "kilometer")
        {"success": True, "result": 1.0, "error": None}
        
        >>> convert_units([32, 212], "fahrenheit", "celsius")
        {"success": True, "result": [0.0, 100.0], "error": None}
        
        >>> convert_units(5, "kilogram", "pound")
        {"success": True, "result": 11.0231..., "error": None}
    """
    try:
        # Normalize unit names
        from_norm = _normalize_unit_name(from_unit)
        to_norm = _normalize_unit_name(to_unit)
        
        # Find unit categories
        from_category = _find_unit_category(from_unit)
        to_category = _find_unit_category(to_unit)
        
        if from_category is None:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Unknown source unit: {from_unit}",
            }
        
        if to_category is None:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Unknown target unit: {to_unit}",
            }
        
        if from_category != to_category:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: f"Cannot convert between different unit categories: {from_category} to {to_category}",
            }
        
        # Perform conversion
        if from_category == "temperature":
            result = _convert_temperature(values, from_unit, to_unit)
        else:
            result = _convert_standard(values, from_unit, to_unit, from_category)
        
        # Convert result back to original type if needed
        if isinstance(values, (list, tuple)) and isinstance(result, np.ndarray):
            result = result.tolist()
        elif isinstance(values, tuple) and isinstance(result, list):
            result = tuple(result)
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: result,
            ERROR_KEY: None,
        }
    
    except KeyError as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Unit conversion error: {str(e)}",
        }
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Unexpected error: {str(e)}",
        }

