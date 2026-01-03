"""
Tests for convert_units function.
"""

import pytest
import numpy as np
import pandas as pd

from ixmachina.tools.math.convert_units import convert_units


def test_convert_units_length_meter_to_kilometer():
    """Test converting meters to kilometers."""
    result = convert_units(1000, "meter", "kilometer")
    assert result["success"] is True
    assert result["result"] == 1.0
    assert result["error"] is None


def test_convert_units_length_round_trip():
    """Test round-trip conversion: meter -> kilometer -> meter."""
    original = 1000.0
    result1 = convert_units(original, "meter", "kilometer")
    assert result1["success"] is True
    
    result2 = convert_units(result1["result"], "kilometer", "meter")
    assert result2["success"] is True
    assert abs(result2["result"] - original) < 0.0001


def test_convert_units_length_mile_to_foot():
    """Test converting miles to feet (explicit value check)."""
    result = convert_units(1, "mile", "foot")
    assert result["success"] is True
    # 1 mile = 5280 feet
    assert abs(result["result"] - 5280.0) < 0.1


def test_convert_units_length_list():
    """Test converting a list of length values."""
    result = convert_units([1000, 2000, 3000], "meter", "kilometer")
    assert result["success"] is True
    assert result["result"] == [1.0, 2.0, 3.0]
    assert result["error"] is None


def test_convert_units_mass_kilogram_to_pound():
    """Test converting kilograms to pounds (explicit value check)."""
    result = convert_units(1, "kilogram", "pound")
    assert result["success"] is True
    # 1 kg ≈ 2.20462 pounds
    assert abs(result["result"] - 2.20462) < 0.01


def test_convert_units_mass_round_trip():
    """Test round-trip conversion: kilogram -> pound -> kilogram."""
    original = 5.0
    result1 = convert_units(original, "kilogram", "pound")
    assert result1["success"] is True
    
    result2 = convert_units(result1["result"], "pound", "kilogram")
    assert result2["success"] is True
    assert abs(result2["result"] - original) < 0.0001


def test_convert_units_temperature_fahrenheit_to_celsius():
    """Test converting Fahrenheit to Celsius (explicit value check)."""
    # 32°F = 0°C
    result = convert_units(32, "fahrenheit", "celsius")
    assert result["success"] is True
    assert abs(result["result"] - 0.0) < 0.01
    
    # 212°F = 100°C
    result = convert_units(212, "fahrenheit", "celsius")
    assert result["success"] is True
    assert abs(result["result"] - 100.0) < 0.01


def test_convert_units_temperature_celsius_to_fahrenheit():
    """Test converting Celsius to Fahrenheit (explicit value check)."""
    # 0°C = 32°F
    result = convert_units(0, "celsius", "fahrenheit")
    assert result["success"] is True
    assert abs(result["result"] - 32.0) < 0.01
    
    # 100°C = 212°F
    result = convert_units(100, "celsius", "fahrenheit")
    assert result["success"] is True
    assert abs(result["result"] - 212.0) < 0.01


def test_convert_units_temperature_round_trip_fahrenheit():
    """Test round-trip conversion: fahrenheit -> celsius -> fahrenheit."""
    original = 32.0
    result1 = convert_units(original, "fahrenheit", "celsius")
    assert result1["success"] is True
    
    result2 = convert_units(result1["result"], "celsius", "fahrenheit")
    assert result2["success"] is True
    assert abs(result2["result"] - original) < 0.0001


def test_convert_units_temperature_round_trip_celsius():
    """Test round-trip conversion: celsius -> fahrenheit -> celsius."""
    original = 100.0
    result1 = convert_units(original, "celsius", "fahrenheit")
    assert result1["success"] is True
    
    result2 = convert_units(result1["result"], "fahrenheit", "celsius")
    assert result2["success"] is True
    assert abs(result2["result"] - original) < 0.0001


def test_convert_units_temperature_kelvin_to_celsius():
    """Test converting Kelvin to Celsius (explicit value check)."""
    # 0 K = -273.15°C
    result = convert_units(0, "kelvin", "celsius")
    assert result["success"] is True
    assert abs(result["result"] - (-273.15)) < 0.01


def test_convert_units_temperature_list():
    """Test converting a list of temperature values."""
    result = convert_units([32, 212], "fahrenheit", "celsius")
    assert result["success"] is True
    assert abs(result["result"][0] - 0.0) < 0.01
    assert abs(result["result"][1] - 100.0) < 0.01


def test_convert_units_time_hour_to_minute():
    """Test converting hours to minutes (explicit value check)."""
    result = convert_units(1, "hour", "minute")
    assert result["success"] is True
    assert result["result"] == 60.0


def test_convert_units_time_round_trip():
    """Test round-trip conversion: hour -> minute -> hour."""
    original = 2.5
    result1 = convert_units(original, "hour", "minute")
    assert result1["success"] is True
    
    result2 = convert_units(result1["result"], "minute", "hour")
    assert result2["success"] is True
    assert abs(result2["result"] - original) < 0.0001


def test_convert_units_volume_liter_to_gallon():
    """Test converting liters to gallons."""
    result = convert_units(1, "liter", "gallon")
    assert result["success"] is True
    # 1 liter ≈ 0.264172 gallons
    assert abs(result["result"] - 0.264172) < 0.01


def test_convert_units_volume_round_trip():
    """Test round-trip conversion: liter -> gallon -> liter."""
    original = 10.0
    result1 = convert_units(original, "liter", "gallon")
    assert result1["success"] is True
    
    result2 = convert_units(result1["result"], "gallon", "liter")
    assert result2["success"] is True
    assert abs(result2["result"] - original) < 0.0001


def test_convert_units_speed_kmh_to_mph():
    """Test converting km/h to mph."""
    result = convert_units(100, "kilometer_per_hour", "mile_per_hour")
    assert result["success"] is True
    # 100 km/h ≈ 62.1371 mph
    assert abs(result["result"] - 62.1371) < 0.1


def test_convert_units_speed_round_trip():
    """Test round-trip conversion: km/h -> mph -> km/h."""
    original = 60.0
    result1 = convert_units(original, "kilometer_per_hour", "mile_per_hour")
    assert result1["success"] is True
    
    result2 = convert_units(result1["result"], "mile_per_hour", "kilometer_per_hour")
    assert result2["success"] is True
    assert abs(result2["result"] - original) < 0.1


def test_convert_units_numpy_array():
    """Test converting numpy array."""
    values = np.array([1, 2, 3])
    result = convert_units(values, "meter", "kilometer")
    assert result["success"] is True
    assert isinstance(result["result"], np.ndarray)
    assert np.allclose(result["result"], [0.001, 0.002, 0.003])


def test_convert_units_pandas_series():
    """Test converting pandas Series."""
    values = pd.Series([1, 2, 3])
    result = convert_units(values, "meter", "kilometer")
    assert result["success"] is True
    assert isinstance(result["result"], pd.Series)
    assert result["result"].tolist() == [0.001, 0.002, 0.003]


def test_convert_units_tuple_preserves_type():
    """Test that tuple input preserves tuple output."""
    values = (1, 2, 3)
    result = convert_units(values, "meter", "kilometer")
    assert result["success"] is True
    assert isinstance(result["result"], tuple)
    assert result["result"] == (0.001, 0.002, 0.003)


def test_convert_units_error_unknown_source_unit():
    """Test error handling for unknown source unit."""
    result = convert_units(100, "unknown_unit", "meter")
    assert result["success"] is False
    assert result["result"] is None
    assert "Unknown source unit" in result["error"]


def test_convert_units_error_unknown_target_unit():
    """Test error handling for unknown target unit."""
    result = convert_units(100, "meter", "unknown_unit")
    assert result["success"] is False
    assert result["result"] is None
    assert "Unknown target unit" in result["error"]


def test_convert_units_error_different_categories():
    """Test error handling for converting between different categories."""
    result = convert_units(100, "meter", "kilogram")
    assert result["success"] is False
    assert result["result"] is None
    assert "different unit categories" in result["error"]

