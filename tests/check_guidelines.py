"""
Guideline checker for ixmachina project.

This script checks various project guidelines and raises errors if they are violated.
It is automatically run as part of the test suite.
"""

import ast
import os
from pathlib import Path
from typing import List, Tuple, Dict, Any
import re


class GuidelineViolation:
    """Represents a guideline violation."""
    
    def __init__(
        self,
        file_path: str,
        line_number: int,
        rule_name: str,
        message: str,
    ):
        self.file_path = file_path
        self.line_number = line_number
        self.rule_name = rule_name
        self.message = message
    
    def __str__(self) -> str:
        return f"{self.file_path}:{self.line_number}: {self.rule_name}: {self.message}"


class GuidelineChecker:
    """Checks code against project guidelines."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.violations: List[GuidelineViolation] = []
        self.time_module_path = self.project_root / "ixmachina" / "utils" / "time.py"
    
    def _is_in_comment_or_docstring(
        self,
        content: str,
        line_num: int,
        lines: List[str],
    ) -> bool:
        """
        Check if a line is in a comment or docstring.
        
        Args:
            content: Full file content.
            line_num: Line number (1-indexed).
            lines: List of lines.
        
        Returns:
            True if line is in comment or docstring, False otherwise.
        """
        line = lines[line_num - 1]
        
        # Check if line starts with comment
        stripped = line.strip()
        if stripped.startswith("#"):
            return True
        
        # Check if line is part of a docstring using AST
        try:
            tree = ast.parse(content)
            
            # Find all docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                    docstring = ast.get_docstring(node)
                    if docstring:
                        # Get the line range of the docstring
                        if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                            # Docstring is typically on the line after the definition
                            doc_start = node.lineno + 1
                            # Estimate docstring end (rough approximation)
                            doc_lines = docstring.split("\n")
                            doc_end = doc_start + len(doc_lines) + 2  # +2 for triple quotes
                            
                            if doc_start <= line_num <= doc_end:
                                return True
        except (SyntaxError, ValueError):
            # If we can't parse, use simple heuristics
            pass
        
        # Simple heuristic: check if line is in triple-quoted string
        # Look backwards for opening triple quotes
        in_triple_quote = False
        quote_type = None
        for i in range(line_num - 1, -1, -1):
            line_text = lines[i]
            if '"""' in line_text:
                if quote_type is None or quote_type == '"""':
                    in_triple_quote = not in_triple_quote
                    quote_type = '"""'
            elif "'''" in line_text:
                if quote_type is None or quote_type == "'''":
                    in_triple_quote = not in_triple_quote
                    quote_type = "'''"
        
        return in_triple_quote
    
    def check_all(self) -> List[GuidelineViolation]:
        """Run all guideline checks."""
        self.violations = []
        
        # Find all Python files
        package_files = list((self.project_root / "ixmachina").rglob("*.py"))
        test_files = list((self.project_root / "tests").rglob("*.py"))
        all_files = package_files + test_files
        
        for file_path in all_files:
            # Skip __pycache__ and other hidden directories
            if "__pycache__" in str(file_path) or ".pyc" in str(file_path):
                continue
            
            # Skip the guideline checker itself
            if file_path.name == "check_guidelines.py":
                continue
            
            relative_path = file_path.relative_to(self.project_root)
            
            # Check different rules
            self._check_datetime_imports(file_path, relative_path)
            self._check_import_locations(file_path, relative_path)
            self._check_absolute_imports(file_path, relative_path)
            self._check_file_size(file_path, relative_path)
            self._check_class_size(file_path, relative_path)
            
            # Test-specific checks
            if "tests" in str(relative_path):
                self._check_test_structure(file_path, relative_path)
                self._check_no_mocks(file_path, relative_path)
                self._check_no_pytest_skip(file_path, relative_path)
                self._check_os_getenv_usage(file_path, relative_path)
        
        # Root directory checks
        self._check_root_directory_files()
        
        return self.violations
    
    def _check_datetime_imports(
        self,
        file_path: Path,
        relative_path: Path,
    ) -> None:
        """Check that datetime/time imports are only in utils/time.py."""
        # Skip the time module itself
        if file_path == self.time_module_path:
            return
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
        except Exception:
            return
        
        # Patterns to check for
        datetime_patterns = [
            (r"from datetime import", "datetime import"),
            (r"import datetime", "datetime import"),
            (r"from time import", "time import"),
            (r"import time", "time import"),
        ]
        
        for line_num, line in enumerate(lines, 1):
            # Skip if in comment or docstring
            if self._is_in_comment_or_docstring(content, line_num, lines):
                continue
            
            for pattern, violation_type in datetime_patterns:
                if re.search(pattern, line):
                    # Allow datetime.strptime for specialized date parsing
                    # Check if this is for strptime usage (specialized case)
                    context_lines = lines[max(0, line_num - 5):min(len(lines), line_num + 5)]
                    context = " ".join(context_lines).lower()
                    if "strptime" in context and "datetime" in violation_type:
                        # This is likely for strptime which is acceptable
                        continue
                    
                    self.violations.append(
                        GuidelineViolation(
                            file_path=str(relative_path),
                            line_number=line_num,
                            rule_name="datetime/time_import",
                            message=(
                                f"Direct {violation_type} detected. "
                                "Use ixmachina.utils.time utilities instead."
                            ),
                        )
                    )
    
    def _check_import_locations(
        self,
        file_path: Path,
        relative_path: Path,
    ) -> None:
        """Check that imports are at the top of the file, not inside functions/classes."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return
        
        # Track top-level imports
        top_level_imports = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if hasattr(node, "lineno"):
                    top_level_imports.add(node.lineno)
        
        # Build parent map for AST nodes
        parent_map = {}
        def build_parent_map(node, parent=None):
            if parent is not None:
                parent_map[node] = parent
            for child in ast.iter_child_nodes(node):
                build_parent_map(child, node)
        build_parent_map(tree)
        
        # Find imports inside functions/classes
        class ImportVisitor(ast.NodeVisitor):
            def __init__(self, checker, content, relative_path, parent_map):
                self.checker = checker
                self.content = content
                self.relative_path = relative_path
                self.parent_map = parent_map
                self.violations = []
                self.current_function = None
                self.current_class = None
            
            def visit_FunctionDef(self, node):
                old_function = self.current_function
                self.current_function = node.name
                self.generic_visit(node)
                self.current_function = old_function
            
            def visit_ClassDef(self, node):
                old_class = self.current_class
                self.current_class = node.name
                self.generic_visit(node)
                self.current_class = old_class
            
            def _is_in_try_block(self, node):
                """Check if import is inside a try block (indicates optional dependency)."""
                parent = self.parent_map.get(node)
                while parent:
                    if isinstance(parent, ast.Try):
                        # Check if it's a try/except ImportError pattern
                        for handler in parent.handlers:
                            if handler.type:
                                if isinstance(handler.type, ast.Name):
                                    if handler.type.id == "ImportError":
                                        return True
                                elif isinstance(handler.type, ast.Attribute):
                                    if handler.type.attr == "ImportError":
                                        return True
                    parent = self.parent_map.get(parent)
                return False
            
            def visit_Import(self, node):
                # Check if import is inside try block (optional dependency - not allowed)
                if self._is_in_try_block(node):
                    self.violations.append(
                        GuidelineViolation(
                            file_path=str(relative_path),
                            line_number=node.lineno,
                                rule_name="optional_dependency",
                                message=(
                                    "Import inside try/except ImportError block detected (optional dependency). "
                                    "Optional dependencies are not allowed. All dependencies must be required and declared in pyproject.toml."
                                ),
                        )
                    )
                    return
                
                if self.current_function or self.current_class:
                    # Check if there's a comment about circular dependencies or performance
                    # Lazy imports are allowed for:
                    # 1. Circular dependencies
                    # 2. Performance optimization (heavy libraries, conditional features)
                    lines = content.split("\n")
                    context = " ".join(lines[max(0, node.lineno - 3):node.lineno]).lower()
                    if (
                        "circular import" not in context
                        and "circular dependenc" not in context
                        and "performance" not in context
                        and "lazy import" not in context
                    ):
                        self.violations.append(
                            GuidelineViolation(
                                file_path=str(relative_path),
                                line_number=node.lineno,
                                rule_name="import_location",
                                message=(
                                    f"Import inside {self.current_class or self.current_function}. "
                                    "Imports must be at the top of the file. "
                                    "Lazy imports are allowed for: "
                                    "(1) circular dependencies - add comment: '# Lazy import to avoid circular dependencies', "
                                    "(2) performance - add comment: '# Lazy import for performance (heavy library/conditional feature)'."
                                ),
                            )
                        )
            
            def visit_ImportFrom(self, node):
                # Check if import is inside try block (optional dependency - not allowed)
                if self._is_in_try_block(node):
                    self.violations.append(
                        GuidelineViolation(
                            file_path=str(relative_path),
                            line_number=node.lineno,
                                rule_name="optional_dependency",
                                message=(
                                    "Import inside try/except ImportError block detected (optional dependency). "
                                    "Optional dependencies are not allowed. All dependencies must be required and declared in pyproject.toml."
                                ),
                        )
                    )
                    return
                
                if self.current_function or self.current_class:
                    # Check if there's a comment about circular dependencies or performance
                    # Lazy imports are allowed for:
                    # 1. Circular dependencies
                    # 2. Performance optimization (heavy libraries, conditional features)
                    lines = content.split("\n")
                    context = " ".join(lines[max(0, node.lineno - 3):node.lineno]).lower()
                    if (
                        "circular import" not in context
                        and "circular dependenc" not in context
                        and "performance" not in context
                        and "lazy import" not in context
                    ):
                        self.violations.append(
                            GuidelineViolation(
                                file_path=str(relative_path),
                                line_number=node.lineno,
                                rule_name="import_location",
                                message=(
                                    f"Import inside {self.current_class or self.current_function}. "
                                    "Imports must be at the top of the file. "
                                    "Lazy imports are allowed for: "
                                    "(1) circular dependencies - add comment: '# Lazy import to avoid circular dependencies', "
                                    "(2) performance - add comment: '# Lazy import for performance (heavy library/conditional feature)'."
                                ),
                            )
                        )
        
        visitor = ImportVisitor(self, content, relative_path, parent_map)
        visitor.visit(tree)
        self.violations.extend(visitor.violations)
    
    def _check_absolute_imports(
        self,
        file_path: Path,
        relative_path: Path,
    ) -> None:
        """Check that absolute imports from package name are not used within the package."""
        # Only check package files, not tests
        if "tests" in str(relative_path):
            return
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
        except Exception:
            return
        
        for line_num, line in enumerate(lines, 1):
            # Check for absolute imports from ixmachina
            if re.search(r"from\s+ixmachina\.", line):
                # Skip if it's in a comment or docstring
                if self._is_in_comment_or_docstring(content, line_num, lines):
                    continue
                
                self.violations.append(
                    GuidelineViolation(
                        file_path=str(relative_path),
                        line_number=line_num,
                        rule_name="absolute_import",
                        message=(
                            "Absolute import from 'ixmachina' detected. "
                            "Use relative imports within the package (e.g., 'from .module import Class')."
                        ),
                    )
                )
    
    def _check_file_size(
        self,
        file_path: Path,
        relative_path: Path,
    ) -> None:
        """Check that files don't exceed ~512 lines."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            return
        
        line_count = len(lines)
        if line_count > 512:
            self.violations.append(
                GuidelineViolation(
                    file_path=str(relative_path),
                    line_number=1,
                    rule_name="file_size",
                    message=(
                        f"File has {line_count} lines. "
                        "Files should not exceed ~512 lines. "
                        "Consider breaking into smaller modules."
                    ),
                )
            )
    
    def _check_class_size(
        self,
        file_path: Path,
        relative_path: Path,
    ) -> None:
        """Check that classes don't exceed ~512 lines."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Calculate class size (end_lineno - lineno)
                if hasattr(node, "end_lineno") and node.end_lineno:
                    class_size = node.end_lineno - node.lineno + 1
                    if class_size > 512:
                        self.violations.append(
                            GuidelineViolation(
                                file_path=str(relative_path),
                                line_number=node.lineno,
                                rule_name="class_size",
                                message=(
                                    f"Class '{node.name}' has {class_size} lines. "
                                    "Classes should not exceed ~512 lines. "
                                    "Consider breaking into smaller classes or using composition."
                                ),
                            )
                        )
    
    def _check_test_structure(
        self,
        file_path: Path,
        relative_path: Path,
    ) -> None:
        """Check that tests don't use unittest or test classes."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
        except Exception:
            return
        
        # Check for unittest imports
        for line_num, line in enumerate(lines, 1):
            if "import unittest" in line or "from unittest" in line:
                self.violations.append(
                    GuidelineViolation(
                        file_path=str(relative_path),
                        line_number=line_num,
                        rule_name="test_structure",
                        message=(
                            "unittest module detected. "
                            "Use pytest with simple test functions, not unittest."
                        ),
                    )
                )
        
        # Check for test classes
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if class name starts with Test (common unittest pattern)
                if node.name.startswith("Test") and any(
                    isinstance(base, ast.Name) and base.id == "TestCase"
                    for base in node.bases
                ):
                    self.violations.append(
                        GuidelineViolation(
                            file_path=str(relative_path),
                            line_number=node.lineno,
                            rule_name="test_structure",
                            message=(
                                f"Test class '{node.name}' detected. "
                                "Use standalone test functions with pytest, not test classes."
                            ),
                        )
                    )
    
    def _check_no_mocks(
        self,
        file_path: Path,
        relative_path: Path,
    ) -> None:
        """Check that tests don't use mocks."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
        except Exception:
            return
        
        mock_patterns = [
            (r"from unittest.mock import", "unittest.mock"),
            (r"import unittest.mock", "unittest.mock"),
            (r"from mock import", "mock"),
            (r"import mock", "mock"),
            (r"@patch", "patch decorator"),
            (r"Mock\(\)", "Mock()"),
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern, violation_type in mock_patterns:
                if re.search(pattern, line):
                    self.violations.append(
                        GuidelineViolation(
                            file_path=str(relative_path),
                            line_number=line_num,
                            rule_name="no_mocks",
                            message=(
                                f"{violation_type} detected. "
                                "Tests must use real implementations, not mocks."
                            ),
                        )
                    )
    
    def _check_no_pytest_skip(
        self,
        file_path: Path,
        relative_path: Path,
    ) -> None:
        """Check that tests don't use pytest.skip()."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
        except Exception:
            return
        
        for line_num, line in enumerate(lines, 1):
            if "pytest.skip" in line:
                # Check if there's a comment about optional dependencies
                context_lines = lines[max(0, line_num - 3):min(len(lines), line_num + 1)]
                context = " ".join(context_lines).lower()
                if "optional" in context or "missing" in context or "not installed" in context:
                    # Allow skip for optional dependencies with explanation
                    continue
                
                self.violations.append(
                    GuidelineViolation(
                        file_path=str(relative_path),
                        line_number=line_num,
                        rule_name="no_pytest_skip",
                        message=(
                            "pytest.skip() detected. "
                            "Tests should fail if requirements aren't met, not silently skip. "
                            "If skipping for optional dependencies, add a comment explaining why."
                        ),
                    )
                )
    
    def _check_os_getenv_usage(
        self,
        file_path: Path,
        relative_path: Path,
    ) -> None:
        """Check that tests don't use os.getenv() directly - should use API key helper functions."""
        # Allow os.getenv() in api_keys.py itself (that's where the helper functions are)
        if relative_path.name == "api_keys.py":
            return
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
        except Exception:
            return
        
        for line_num, line in enumerate(lines, 1):
            # Check for os.getenv() usage
            if re.search(r"os\.getenv\s*\(", line):
                # Check if it's in a comment or docstring
                if self._is_in_comment_or_docstring(content, line_num, lines):
                    continue
                
                self.violations.append(
                    GuidelineViolation(
                        file_path=str(relative_path),
                        line_number=line_num,
                        rule_name="no_os_getenv",
                        message=(
                            "os.getenv() detected. "
                            "Tests should use API key helper functions from tests.api_keys "
                            "(e.g., get_openai_api_key(), get_brave_api_key()) instead of os.getenv() directly. "
                            "The only place os.getenv() should be used is inside the helper functions themselves."
                        ),
                    )
                )
    
    def _check_root_directory_files(self) -> None:
        """Check that no ad-hoc Python files exist in root directory."""
        root = self.project_root
        
        # Allowed files in root
        allowed_files = {
            "setup.py",
            "setup.cfg",
            "pyproject.toml",
            "pytest.ini",
            "conftest.py",  # Actually should be in tests/, but check anyway
        }
        
        for file_path in root.glob("*.py"):
            if file_path.name not in allowed_files:
                # Check if it's actually a script (has if __name__ == "__main__")
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if "__main__" in content or "if __name__" in content:
                            self.violations.append(
                                GuidelineViolation(
                                    file_path=str(file_path.relative_to(self.project_root)),
                                    line_number=1,
                                    rule_name="root_directory_scripts",
                                    message=(
                                        "Python script found in root directory. "
                                        "Ad-hoc scripts should not be in root. "
                                        "Use proper test files in tests/ directory or Python REPL."
                                    ),
                                )
                            )
                except Exception:
                    pass


def check_guidelines(project_root: str = None) -> List[GuidelineViolation]:
    """
    Check all guidelines for the project.
    
    Args:
        project_root: Root directory of the project. If None, uses current directory.
    
    Returns:
        List of guideline violations.
    """
    if project_root is None:
        project_root = os.getcwd()
    
    checker = GuidelineChecker(project_root)
    violations = checker.check_all()
    
    # Write violations to file
    violations_file = Path(project_root) / "tests" / "guideline_violations.txt"
    with open(violations_file, "w", encoding="utf-8") as f:
        if violations:
            f.write(f"Found {len(violations)} guideline violation(s):\n\n")
            # Group by rule type
            by_rule: Dict[str, List[GuidelineViolation]] = {}
            for violation in violations:
                if violation.rule_name not in by_rule:
                    by_rule[violation.rule_name] = []
                by_rule[violation.rule_name].append(violation)
            
            # Write summary
            f.write("Summary by rule type:\n")
            for rule_name, rule_violations in sorted(by_rule.items()):
                f.write(f"  {rule_name}: {len(rule_violations)} violations\n")
            f.write("\n" + "=" * 80 + "\n\n")
            
            # Write all violations grouped by rule
            for rule_name, rule_violations in sorted(by_rule.items()):
                f.write(f"\n{rule_name.upper()} ({len(rule_violations)} violations):\n")
                f.write("-" * 80 + "\n")
                for violation in sorted(rule_violations, key=lambda v: (v.file_path, v.line_number)):
                    f.write(f"{violation}\n")
        else:
            f.write("All guidelines passed! No violations found.\n")
    
    return violations


if __name__ == "__main__":
    import sys
    
    violations = check_guidelines()
    
    if violations:
        print(f"Found {len(violations)} guideline violation(s)")
        print(f"Violations written to: tests/guideline_violations.txt")
        sys.exit(1)
    else:
        print("All guidelines passed!")
        sys.exit(0)

