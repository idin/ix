"""
Test that all project guidelines are followed.

This test runs the guideline checker and fails if any violations are found.
"""

import os
from pathlib import Path

from tests.check_guidelines import check_guidelines


def test_guidelines():
    """
    Test that all project guidelines are followed.
    
    This test will fail if any guideline violations are detected.
    """
    project_root = Path(__file__).parent.parent
    violations = check_guidelines(str(project_root))
    
    if violations:
        error_message = f"Found {len(violations)} guideline violation(s):\n\n"
        for violation in violations:
            error_message += f"{violation}\n"
        raise AssertionError(error_message)

