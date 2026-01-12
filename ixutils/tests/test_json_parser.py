"""
Tests for robust JSON parsing utilities.
"""

from ixutils import (
    repair_json,
    parse_json_robust,
    parse_json_or_python_literal,
)


def test_repair_unquoted_tool_obj_reference():
    """Test that unquoted tool_obj references are quoted."""
    input_json = '{"data": <tool_obj:default:call_abc>}'
    repaired = repair_json(input_json)
    assert repaired == '{"data": "<tool_obj:default:call_abc>"}'


def test_repair_unquoted_obj_reference():
    """Test that unquoted obj references are quoted."""
    input_json = '{"name": <obj:my_object>}'
    repaired = repair_json(input_json)
    assert repaired == '{"name": "<obj:my_object>"}'


def test_repair_unquoted_conv_obj_reference():
    """Test that unquoted conv_obj references are quoted."""
    input_json = '{"data": <conv_obj:conv1:my_data>}'
    repaired = repair_json(input_json)
    assert repaired == '{"data": "<conv_obj:conv1:my_data>"}'


def test_repair_unquoted_sys_reference():
    """Test that unquoted sys references are quoted."""
    input_json = '{"llm": <sys:llm>}'
    repaired = repair_json(input_json)
    assert repaired == '{"llm": "<sys:llm>"}'


def test_repair_multiple_unquoted_references():
    """Test that multiple unquoted references are all quoted."""
    input_json = '{"tool": <tool_obj:default:call_123>, "obj": <obj:my_obj>, "sys": <sys:self>}'
    repaired = repair_json(input_json)
    assert '<tool_obj:default:call_123>' in repaired
    assert '"<tool_obj:default:call_123>"' in repaired
    assert '"<obj:my_obj>"' in repaired
    assert '"<sys:self>"' in repaired


def test_repair_trailing_comma_in_object():
    """Test that trailing commas in objects are removed."""
    input_json = '{"key": "value",}'
    repaired = repair_json(input_json)
    assert repaired == '{"key": "value"}'


def test_repair_trailing_comma_in_array():
    """Test that trailing commas in arrays are removed."""
    input_json = '["item1", "item2",]'
    repaired = repair_json(input_json)
    assert repaired == '["item1", "item2"]'


def test_repair_multiple_trailing_commas():
    """Test that multiple trailing commas are removed."""
    input_json = '{"a": 1, "b": 2,}'
    repaired = repair_json(input_json)
    assert repaired == '{"a": 1, "b": 2}'


def test_repair_does_not_modify_valid_json():
    """Test that valid JSON is not modified."""
    valid_json = '{"key": "value", "number": 42}'
    repaired = repair_json(valid_json)
    assert repaired == valid_json


def test_repair_does_not_modify_already_quoted_references():
    """Test that already quoted references are not modified."""
    input_json = '{"data": "<tool_obj:default:call_abc>"}'
    repaired = repair_json(input_json)
    assert repaired == input_json


def test_repair_complex_nested_structure():
    """Test repair with complex nested JSON."""
    input_json = '{"outer": {"inner": <tool_obj:test:call_xyz>, "other": "value",}, "list": [1, 2, 3,]}'
    repaired = repair_json(input_json)
    assert '"<tool_obj:test:call_xyz>"' in repaired
    assert ',}' not in repaired  # Trailing comma removed
    assert ',]' not in repaired  # Trailing comma removed


def test_parse_valid_json():
    """Test that valid JSON is parsed correctly."""
    valid_json = '{"key": "value", "number": 42}'
    result = parse_json_robust(valid_json)
    assert result == {"key": "value", "number": 42}


def test_parse_unquoted_reference():
    """Test parsing JSON with unquoted special object reference."""
    input_json = '{"data": <tool_obj:default:call_abc>}'
    result = parse_json_robust(input_json)
    assert result == {"data": "<tool_obj:default:call_abc>"}


def test_parse_trailing_comma():
    """Test parsing JSON with trailing comma."""
    input_json = '{"key": "value",}'
    result = parse_json_robust(input_json)
    assert result == {"key": "value"}


def test_parse_array_with_trailing_comma():
    """Test parsing array with trailing comma."""
    input_json = '[1, 2, 3,]'
    result = parse_json_robust(input_json)
    assert result == [1, 2, 3]


def test_parse_multiple_issues():
    """Test parsing JSON with multiple issues."""
    input_json = '{"tool": <tool_obj:test:call_123>, "obj": <obj:my_obj>,}'
    result = parse_json_robust(input_json)
    assert result["tool"] == "<tool_obj:test:call_123>"
    assert result["obj"] == "<obj:my_obj>"


def test_parse_python_literal_fallback():
    """Test that Python literal format is parsed as fallback."""
    python_literal = "{'key': 'value', 'number': 42}"
    result = parse_json_robust(python_literal)
    assert result == {"key": "value", "number": 42}


def test_parse_returns_string_if_all_fails():
    """Test that original string is returned if all parsing fails."""
    invalid = "not json at all"
    result = parse_json_robust(invalid)
    assert result == invalid


def test_parse_nested_structures():
    """Test parsing nested JSON structures."""
    input_json = '{"outer": {"inner": <tool_obj:test:call_xyz>}, "list": [1, 2, 3]}'
    result = parse_json_robust(input_json)
    assert result["outer"]["inner"] == "<tool_obj:test:call_xyz>"
    assert result["list"] == [1, 2, 3]


def test_parse_array():
    """Test parsing JSON array."""
    input_json = '[1, 2, 3, "four"]'
    result = parse_json_robust(input_json)
    assert result == [1, 2, 3, "four"]


def test_parse_with_numbers_and_booleans():
    """Test parsing JSON with various types."""
    input_json = '{"int": 42, "float": 3.14, "bool": true, "null": null}'
    result = parse_json_robust(input_json)
    assert result["int"] == 42
    assert result["float"] == 3.14
    assert result["bool"] is True
    assert result["null"] is None


def test_parse_json_or_python_literal_valid_json():
    """Test parsing valid JSON."""
    valid_json = '{"key": "value"}'
    result = parse_json_or_python_literal(valid_json)
    assert result == {"key": "value"}


def test_parse_json_or_python_literal_python_format():
    """Test parsing Python literal format."""
    python_literal = "{'key': 'value'}"
    result = parse_json_or_python_literal(python_literal)
    assert result == {"key": "value"}


def test_parse_json_or_python_literal_unquoted_reference():
    """Test parsing with unquoted reference (should be repaired)."""
    input_json = '{"data": <tool_obj:default:call_abc>}'
    result = parse_json_or_python_literal(input_json)
    assert result == {"data": "<tool_obj:default:call_abc>"}


def test_parse_json_or_python_literal_returns_original_if_not_json_like():
    """Test that non-JSON-like strings are returned as-is."""
    plain_string = "just a regular string"
    result = parse_json_or_python_literal(plain_string)
    assert result == plain_string


def test_parse_json_or_python_literal_handles_non_string_input():
    """Test that non-string input is returned as-is."""
    result = parse_json_or_python_literal(42)
    assert result == 42


def test_parse_json_or_python_literal_complex_malformed_json():
    """Test parsing complex malformed JSON."""
    input_json = '{"tool": <tool_obj:test:call_123>, "list": [1, 2, 3,], "nested": {"inner": <obj:my_obj>,},}'
    result = parse_json_or_python_literal(input_json)
    assert result["tool"] == "<tool_obj:test:call_123>"
    assert result["list"] == [1, 2, 3]
    assert result["nested"]["inner"] == "<obj:my_obj>"


def test_repair_does_not_match_regular_json_arrays():
    """Test that regular JSON arrays are not modified."""
    # Regular array of numbers
    input_json = '{"data": [1, 2, 3]}'
    repaired = repair_json(input_json)
    assert repaired == input_json  # Should not be modified
    
    # Regular array of strings
    input_json = '{"data": ["item1", "item2"]}'
    repaired = repair_json(input_json)
    assert repaired == input_json  # Should not be modified
    
    # Regular array of objects
    input_json = '{"data": [{"key": "value"}]}'
    repaired = repair_json(input_json)
    assert repaired == input_json  # Should not be modified
    
    # Mixed: regular array and special reference
    input_json = '{"list": [1, 2, 3], "ref": <tool_obj:test:call_123>}'
    repaired = repair_json(input_json)
    assert '[1, 2, 3]' in repaired  # Regular array unchanged
    assert '"<tool_obj:test:call_123>"' in repaired  # Special reference quoted


def test_repair_handles_nested_arrays_with_special_references():
    """Test that nested structures with arrays and references work correctly."""
    input_json = '{"outer": {"inner": <tool_obj:test:call_xyz>}, "list": [1, 2, 3]}'
    repaired = repair_json(input_json)
    assert '"<tool_obj:test:call_xyz>"' in repaired
    assert '[1, 2, 3]' in repaired  # Regular array should remain unchanged


def test_parse_json_robust_strips_markdown_code_block_with_json_tag():
    """Test that markdown code blocks with json tag are stripped and parsed."""
    response = '```json\n{"entities": true}\n```'
    result = parse_json_robust(response)
    assert result == {"entities": True}
    assert isinstance(result, dict)


def test_parse_json_robust_strips_markdown_code_block_without_tag():
    """Test that markdown code blocks without tag are stripped and parsed."""
    response = '```\n{"entities": true}\n```'
    result = parse_json_robust(response)
    assert result == {"entities": True}
    assert isinstance(result, dict)


def test_parse_json_robust_strips_markdown_code_block_with_whitespace():
    """Test that markdown code blocks with extra whitespace are handled."""
    response = '  ```json\n{"entities": true}\n```  '
    result = parse_json_robust(response)
    assert result == {"entities": True}
    assert isinstance(result, dict)


def test_parse_json_robust_strips_multiline_json_in_code_block():
    """Test that multiline JSON in code blocks is parsed correctly."""
    response = '```json\n{\n    "entities": true,\n    "numbers": false\n}\n```'
    result = parse_json_robust(response)
    assert result == {"entities": True, "numbers": False}
    assert isinstance(result, dict)


def test_parse_json_robust_handles_clean_json_without_code_block():
    """Test that clean JSON without code blocks still works."""
    response = '{"entities": true}'
    result = parse_json_robust(response)
    assert result == {"entities": True}
    assert isinstance(result, dict)


def test_parse_json_robust_handles_malformed_json_in_code_block():
    """Test that malformed JSON in code blocks is repaired and parsed."""
    response = '```json\n{"entities": true,}\n```'
    result = parse_json_robust(response)
    assert result == {"entities": True}
    assert isinstance(result, dict)


def test_parse_json_robust_handles_unquoted_reference_in_code_block():
    """Test that unquoted references in code blocks are handled."""
    response = '```json\n{"data": <tool_obj:default:call_abc>}\n```'
    result = parse_json_robust(response)
    assert result == {"data": "<tool_obj:default:call_abc>"}
    assert isinstance(result, dict)


def test_parse_json_or_python_literal_strips_markdown_code_block():
    """Test that parse_json_or_python_literal also handles markdown code blocks."""
    response = '```json\n{"entities": true}\n```'
    result = parse_json_or_python_literal(response)
    assert result == {"entities": True}
    assert isinstance(result, dict)

