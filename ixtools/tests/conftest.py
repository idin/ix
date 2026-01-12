"""
Pytest configuration and shared fixtures for ixtools tests.
"""

import os

# Test data directory - all test files should use this for temporary test data
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), ".test_data")

# Ensure test data directory exists
os.makedirs(TEST_DATA_DIR, exist_ok=True)

# Default LLM model for testing (cheaper model for cost-effective testing)
DEFAULT_TEST_MODEL = "gpt-4o-mini"

