"""
Return mode constants for Agent classes.
"""

CHAT_RESPONSE_MODES = {"chat_response", "response", "chat"}
TOOL_OUTPUT_VALUE_MODES = {"tool_output_value", "tool_value", "output_value", "value"}
TOOL_FULL_OUTPUT_MODES = {"tool_full_output", "tool_full", "full_output", "full"}
ALL_VALID_MODES = TOOL_OUTPUT_VALUE_MODES | TOOL_FULL_OUTPUT_MODES | CHAT_RESPONSE_MODES

