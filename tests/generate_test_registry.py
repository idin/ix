"""
Generate a test registry markdown file from a tests directory.

This script recursively scans a tests folder and creates a markdown file
with all test functions organized by directory structure.
"""

import ast
import argparse
from pathlib import Path
from typing import Dict, List


def find_test_functions(file_path: Path) -> List[str]:
    """
    Find all test functions in a Python file.
    
    Args:
        file_path: Path to the Python file.
    
    Returns:
        List of test function names (functions starting with 'test_').
    """
    test_functions = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return test_functions
    
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return test_functions
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name.startswith("test_"):
                test_functions.append(node.name)
    
    return sorted(test_functions)


def build_directory_structure(tests_path: Path) -> Dict:
    """
    Build a nested dictionary structure representing the tests directory.
    
    Recursively scans all subdirectories at any depth to find all test files.
    
    Args:
        tests_path: Path to the tests directory.
    
    Returns:
        Nested dictionary with directory structure and test files.
    """
    structure = {}
    files_processed = 0
    files_with_tests = 0
    
    # Walk through all Python files recursively (rglob goes to any depth)
    # This ensures we don't miss any tests, no matter how deeply nested
    for file_path in sorted(tests_path.rglob("*.py")):
        # Skip __pycache__ and __init__.py
        if "__pycache__" in str(file_path) or file_path.name == "__init__.py":
            continue
        
        files_processed += 1
        
        # Find test functions in this file
        test_functions = find_test_functions(file_path)
        
        # Only include files that have test functions
        if not test_functions:
            continue
        
        files_with_tests += 1
        
        # Get relative path from tests directory
        relative_path = file_path.relative_to(tests_path)
        parts = relative_path.parts
        
        # Build nested structure - handles any depth
        # This creates all intermediate directories in the structure
        current = structure
        for part in parts[:-1]:  # All parts except the filename
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Add file with its test functions
        filename = parts[-1]
        current[filename] = {
            "_path": file_path,
            "_tests": test_functions,
        }
    
    print(f"  Processed {files_processed} Python files, found {files_with_tests} files with test functions")
    
    return structure


def generate_markdown_content(
    structure: Dict,
    level: int = 1,
) -> List[str]:
    """
    Generate markdown content from directory structure.
    
    Args:
        structure: Nested dictionary structure.
        level: Current nesting level (for markdown headers, starting at 1).
    
    Returns:
        List of markdown lines.
    """
    lines = []
    
    for key, value in sorted(structure.items()):
        if isinstance(value, dict):
            if "_path" in value and "_tests" in value:
                # This is a file
                filename = key
                test_functions = value["_tests"]
                
                # Write file header (same level as parent directory)
                lines.append(f"{'#' * level} {filename}\n")
                lines.append("\n")
                
                # Write test functions as checkboxes
                for test_func in test_functions:
                    lines.append(f"- [ ] {test_func}\n")
                
                if test_functions:
                    lines.append("\n")
            else:
                # This is a directory
                dir_name = key
                lines.append(f"{'#' * level} {dir_name}\n")
                lines.append("\n")
                
                # Recursively process subdirectories
                sub_lines = generate_markdown_content(value, level + 1)
                lines.extend(sub_lines)
    
    return lines


def main():
    """Main function to generate test registry."""
    parser = argparse.ArgumentParser(
        description="Generate a test registry markdown file from a tests directory."
    )
    parser.add_argument(
        "tests_path",
        type=str,
        help="Path to the tests directory to scan",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Output markdown file path (default: tests_path/TEST_REGISTRY.md)",
    )
    
    args = parser.parse_args()
    
    tests_path = Path(args.tests_path).resolve()
    
    if not tests_path.exists():
        print(f"Error: Tests directory does not exist: {tests_path}")
        return 1
    
    if not tests_path.is_dir():
        print(f"Error: Path is not a directory: {tests_path}")
        return 1
    
    # Determine output path
    if args.output:
        output_path = Path(args.output).resolve()
    else:
        output_path = tests_path / "TEST_REGISTRY.md"
    
    # Build directory structure
    print(f"Scanning tests directory (recursive, any depth): {tests_path}")
    structure = build_directory_structure(tests_path)
    
    # Generate markdown
    print(f"Generating markdown: {output_path}")
    
    # Generate markdown content
    markdown_lines = generate_markdown_content(structure, level=1)
    
    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# Test Registry\n\n")
        f.write(f"Generated from: `{tests_path}`\n\n")
        f.write("=" * 80 + "\n\n")
        f.writelines(markdown_lines)
    
    print(f"✅ Test registry generated: {output_path}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
