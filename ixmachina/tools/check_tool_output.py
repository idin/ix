def check_tool_output(output: dict) -> bool:
    """
    Validate that tool output follows the standard structure.
    
    Rules:
    - Must have SUCCESS_KEY, RESULT_KEY, and ERROR_KEY at top level
    - METADATA_KEY is optional at top level
    - RESULT_KEY contains just the data (what the user needs), not metadata
    - Metadata (like file paths) goes in METADATA_KEY at top level, not in RESULT_KEY
    """
    from .constants import SUCCESS_KEY, RESULT_KEY, ERROR_KEY, METADATA_KEY
    
    # Must have all three required keys
    if SUCCESS_KEY not in output:
        return False
    if RESULT_KEY not in output:
        return False
    if ERROR_KEY not in output:
        return False
    
    # Top level can have: SUCCESS_KEY, RESULT_KEY, ERROR_KEY, METADATA_KEY (optional)
    allowed_keys = {SUCCESS_KEY, RESULT_KEY, ERROR_KEY, METADATA_KEY}
    if not set(output.keys()).issubset(allowed_keys):
        return False
    
    # RESULT_KEY should contain just the data, not metadata nested inside
    # METADATA_KEY (if present) should be at top level
    return True