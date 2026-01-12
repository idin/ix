"""
Tests for infer_string_type function.
"""

from ixtools.string import infer_string_type
from ixcore import LLM
from ixutils import EnvVar
from tests.api_keys import get_openai_api_key


def test_infer_string_type_dict_json():
    """Test infer_string_type with valid JSON dictionary."""
    result = infer_string_type('{"key": "value", "number": 42}')
    
    assert result["success"] is True
    assert result["type"] == "dict"
    assert result["method"] == "json"
    assert isinstance(result["value"], dict)
    assert result["value"]["key"] == "value"
    assert result["value"]["number"] == 42
    assert result["error"] is None


def test_infer_string_type_list_json():
    """Test infer_string_type with valid JSON list."""
    result = infer_string_type('[1, 2, 3, "four"]')
    
    assert result["success"] is True
    assert result["type"] == "list"
    assert result["method"] == "json"
    assert isinstance(result["value"], list)
    assert result["value"] == [1, 2, 3, "four"]
    assert result["error"] is None


def test_infer_string_type_int_json():
    """Test infer_string_type with valid JSON integer."""
    result = infer_string_type("42")
    
    assert result["success"] is True
    assert result["type"] == "int"
    assert result["method"] == "json"
    assert isinstance(result["value"], int)
    assert result["value"] == 42
    assert result["error"] is None


def test_infer_string_type_float_json():
    """Test infer_string_type with valid JSON float."""
    result = infer_string_type("3.14")
    
    assert result["success"] is True
    assert result["type"] == "float"
    assert result["method"] == "json"
    assert isinstance(result["value"], float)
    assert result["value"] == 3.14
    assert result["error"] is None


def test_infer_string_type_bool_json():
    """Test infer_string_type with valid JSON boolean."""
    result = infer_string_type("true")
    
    assert result["success"] is True
    assert result["type"] == "bool"
    assert result["method"] == "json"
    assert isinstance(result["value"], bool)
    assert result["value"] is True
    assert result["error"] is None


def test_infer_string_type_bool_false_json():
    """Test infer_string_type with valid JSON boolean false."""
    result = infer_string_type("false")
    
    assert result["success"] is True
    assert result["type"] == "bool"
    assert result["method"] == "json"
    assert isinstance(result["value"], bool)
    assert result["value"] is False
    assert result["error"] is None


def test_infer_string_type_str_json():
    """Test infer_string_type with valid JSON string."""
    result = infer_string_type('"hello world"')
    
    assert result["success"] is True
    assert result["type"] == "str"
    assert result["method"] == "json"
    assert isinstance(result["value"], str)
    assert result["value"] == "hello world"
    assert result["error"] is None


def test_infer_string_type_int_fallback():
    """Test infer_string_type with integer using fallback method."""
    result = infer_string_type("42", llm=None)
    
    assert result["success"] is True
    assert result["type"] == "int"
    assert result["method"] in ["json", "fallback"]
    assert isinstance(result["value"], int)
    assert result["value"] == 42
    assert result["error"] is None


def test_infer_string_type_int_negative_fallback():
    """Test infer_string_type with negative integer using fallback method."""
    result = infer_string_type("-42", llm=None)
    
    assert result["success"] is True
    assert result["type"] == "int"
    assert result["method"] in ["json", "fallback"]
    assert isinstance(result["value"], int)
    assert result["value"] == -42
    assert result["error"] is None


def test_infer_string_type_float_fallback():
    """Test infer_string_type with float using fallback method."""
    result = infer_string_type("3.14", llm=None)
    
    assert result["success"] is True
    assert result["type"] == "float"
    assert result["method"] in ["json", "fallback"]
    assert isinstance(result["value"], float)
    assert result["value"] == 3.14
    assert result["error"] is None


def test_infer_string_type_float_scientific_fallback():
    """Test infer_string_type with scientific notation float using fallback method."""
    result = infer_string_type("1.5e2", llm=None)
    
    assert result["success"] is True
    assert result["type"] == "float"
    assert result["method"] in ["json", "fallback"]
    assert isinstance(result["value"], float)
    assert result["value"] == 150.0
    assert result["error"] is None


def test_infer_string_type_bool_true_fallback():
    """Test infer_string_type with boolean true using fallback method."""
    result = infer_string_type("true", llm=None)
    
    assert result["success"] is True
    assert result["type"] == "bool"
    assert result["method"] in ["json", "fallback"]
    assert isinstance(result["value"], bool)
    assert result["value"] is True
    assert result["error"] is None


def test_infer_string_type_bool_false_fallback():
    """Test infer_string_type with boolean false using fallback method."""
    result = infer_string_type("false", llm=None)
    
    assert result["success"] is True
    assert result["type"] == "bool"
    assert result["method"] in ["json", "fallback"]
    assert isinstance(result["value"], bool)
    assert result["value"] is False
    assert result["error"] is None


def test_infer_string_type_str_fallback():
    """Test infer_string_type with plain string using fallback method."""
    result = infer_string_type("hello world", llm=None)
    
    assert result["success"] is True
    assert result["type"] == "str"
    assert result["method"] == "fallback"
    assert isinstance(result["value"], str)
    assert result["value"] == "hello world"
    assert result["error"] is None


def test_infer_string_type_with_whitespace():
    """Test infer_string_type handles whitespace correctly."""
    result = infer_string_type('  {"key": "value"}  ')
    
    assert result["success"] is True
    assert result["type"] == "dict"
    assert result["method"] == "json"
    assert isinstance(result["value"], dict)
    assert result["value"]["key"] == "value"
    assert result["error"] is None


def test_infer_string_type_nested_dict():
    """Test infer_string_type with nested dictionary."""
    result = infer_string_type('{"outer": {"inner": "value"}}')
    
    assert result["success"] is True
    assert result["type"] == "dict"
    assert result["method"] == "json"
    assert isinstance(result["value"], dict)
    assert result["value"]["outer"]["inner"] == "value"
    assert result["error"] is None


def test_infer_string_type_list_of_dicts():
    """Test infer_string_type with list containing dictionaries."""
    result = infer_string_type('[{"a": 1}, {"b": 2}]')
    
    assert result["success"] is True
    assert result["type"] == "list"
    assert result["method"] == "json"
    assert isinstance(result["value"], list)
    assert len(result["value"]) == 2
    assert result["value"][0]["a"] == 1
    assert result["value"][1]["b"] == 2
    assert result["error"] is None


def test_infer_string_type_max_length_parameter():
    """Test infer_string_type respects max_length parameter."""
    long_text = "a" * 3000
    result = infer_string_type(long_text, llm=None, max_length=1000)
    
    assert result["success"] is True
    assert result["type"] == "str"
    assert result["method"] == "fallback"
    assert isinstance(result["value"], str)
    assert result["error"] is None


def test_infer_string_type_with_llm():
    """Test infer_string_type with LLM for non-JSON string."""
    api_key = get_openai_api_key()
    
    llm = LLM(api_key=EnvVar("OPENAI_API_KEY"), model_name="gpt-4o-mini")
    
    # Test with a string that looks like a dict but isn't valid JSON
    result = infer_string_type("key: value, number: 42", llm=llm)
    
    assert result["success"] is True
    assert result["type"] in ["dict", "str"]
    assert result["method"] in ["llm", "fallback"]
    assert result["error"] is None


def test_infer_string_type_with_llm_truncation():
    """Test infer_string_type with LLM and text truncation."""
    api_key = get_openai_api_key()
    
    llm = LLM(api_key=EnvVar("OPENAI_API_KEY"), model_name="gpt-4o-mini")
    
    # Create a long string that will be truncated
    long_text = "This is a very long string. " * 100  # ~2800 characters
    result = infer_string_type(long_text, llm=llm, max_length=2000)
    
    assert result["success"] is True
    assert result["type"] == "str"
    assert result["method"] in ["llm", "fallback"]
    assert result["error"] is None

