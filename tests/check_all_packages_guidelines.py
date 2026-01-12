"""
Check guidelines for all ix packages.

This script runs the guideline checker on each package (ixcore, ixagent, ixmemory, ixtools, ixutils)
and generates a comprehensive report.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict

# Import the guideline checker (no path manipulation needed - we're in tests/)
from check_guidelines import GuidelineChecker, GuidelineViolation


def check_package_guidelines(package_name: str, project_root: Path) -> List[GuidelineViolation]:
    """
    Check guidelines for a specific package.
    
    Args:
        package_name: Name of the package (e.g., "ixcore")
        project_root: Root directory of the project.
    
    Returns:
        List of violations found in the package.
    """
    package_dir = project_root / package_name
    
    if not package_dir.exists():
        return []
    
    # Create checker with package directory as root
    checker = GuidelineChecker(str(package_dir))
    
    # Modify time_module_path - check if package has utils/time.py, otherwise check ixutils
    package_time_path = package_dir / package_name / "utils" / "time.py"
    ixutils_time_path = project_root / "ixutils" / "ixutils" / "time.py"
    
    if package_time_path.exists():
        checker.time_module_path = package_time_path
    elif ixutils_time_path.exists():
        checker.time_module_path = ixutils_time_path
    else:
        # If neither exists, set to a non-existent path so checks still work
        checker.time_module_path = package_dir / "nonexistent" / "time.py"
    
    # Find all Python files in the package
    package_module_dir = package_dir / package_name
    test_dir = package_dir / "tests"
    
    all_files = []
    if package_module_dir.exists():
        all_files.extend(package_module_dir.rglob("*.py"))
    if test_dir.exists():
        all_files.extend(test_dir.rglob("*.py"))
    
    # Reset violations list
    checker.violations = []
    
    for file_path in all_files:
        # Skip __pycache__ and other hidden directories
        if "__pycache__" in str(file_path) or ".pyc" in str(file_path):
            continue
        
        # Skip the guideline checker itself
        if file_path.name == "check_guidelines.py":
            continue
        
        relative_path = file_path.relative_to(package_dir)
        
        # Run all checks
        try:
            checker._check_datetime_imports(file_path, relative_path)
            checker._check_import_locations(file_path, relative_path)
            checker._check_absolute_imports(file_path, relative_path)
            checker._check_file_size(file_path, relative_path)
            checker._check_class_size(file_path, relative_path)
            
            # Test-specific checks
            if "tests" in str(relative_path):
                checker._check_test_structure(file_path, relative_path)
                checker._check_no_mocks(file_path, relative_path)
                checker._check_no_pytest_skip(file_path, relative_path)
                checker._check_os_getenv_usage(file_path, relative_path)
        except Exception as e:
            # If a check fails, continue with other files
            print(f"Warning: Error checking {file_path}: {e}", file=sys.stderr)
    
    # Update file paths to be relative to project root for reporting
    for violation in checker.violations:
        violation.file_path = f"{package_name}/{violation.file_path}"
    
    return checker.violations


def write_package_report(
    package_name: str,
    violations: List[GuidelineViolation],
    package_dir: Path,
) -> None:
    """
    Write a report for a single package to its .documents folder.
    
    Args:
        package_name: Name of the package.
        violations: List of violations for this package.
        package_dir: Directory of the package.
    """
    documents_dir = package_dir / ".documents"
    documents_dir.mkdir(parents=True, exist_ok=True)
    report_file = documents_dir / "GUIDELINE_CHECK_RESULTS.md"
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# Guideline Check Results - {package_name}\n\n")
        f.write("This document shows guideline violations found in this package.\n\n")
        f.write("=" * 80 + "\n\n")
        
        if not violations:
            f.write("**✅ All guidelines passed! No violations found.**\n")
            return
        
        f.write(f"**Total Violations: {len(violations)}**\n\n")
        
        # Group by rule type
        by_rule: Dict[str, List[GuidelineViolation]] = {}
        for violation in violations:
            if violation.rule_name not in by_rule:
                by_rule[violation.rule_name] = []
            by_rule[violation.rule_name].append(violation)
        
        # Summary by rule
        f.write("## Summary by Rule Type\n\n")
        for rule_name in sorted(by_rule.keys()):
            count = len(by_rule[rule_name])
            f.write(f"- **{rule_name}**: {count} violations\n")
        f.write("\n")
        
        # Detailed results grouped by rule
        for rule_name in sorted(by_rule.keys()):
            rule_violations = by_rule[rule_name]
            f.write(f"\n## {rule_name} ({len(rule_violations)} violations)\n\n")
            f.write("-" * 80 + "\n\n")
            
            for violation in sorted(rule_violations, key=lambda v: (v.file_path, v.line_number)):
                f.write(f"**File:** `{violation.file_path}`  \n")
                f.write(f"**Line:** {violation.line_number}  \n")
                f.write(f"**Issue:** {violation.message}  \n\n")


def main():
    """Check all packages and generate reports for each package."""
    # Get project root (parent of tests directory)
    project_root = Path(__file__).parent.parent
    
    packages = ["ixcore", "ixagent", "ixmemory", "ixtools", "ixutils"]
    
    all_results: Dict[str, List[GuidelineViolation]] = {}
    
    print("Checking guidelines for all packages...")
    print("=" * 80)
    
    for package in packages:
        print(f"\nChecking {package}...")
        violations = check_package_guidelines(package, project_root)
        all_results[package] = violations
        count = len(violations)
        status = "✅ PASS" if count == 0 else f"❌ {count} violations"
        print(f"  {status}")
        
        # Write individual package report
        package_dir = project_root / package
        write_package_report(package, violations, package_dir)
        print(f"  Report saved to: {package_dir / '.documents' / 'GUIDELINE_CHECK_RESULTS.md'}")
    
    # Also generate a summary report in root
    total_violations = sum(len(v) for v in all_results.values())
    summary_file = project_root / ".documents" / "GUIDELINE_CHECK_SUMMARY.md"
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("# Guideline Check Summary\n\n")
        f.write("Summary of guideline violations across all packages.\n\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"**Total Violations: {total_violations}**\n\n")
        
        # Summary by package
        f.write("## Summary by Package\n\n")
        for package in packages:
            count = len(all_results[package])
            status = "✅ PASS" if count == 0 else f"❌ {count} violations"
            f.write(f"- **{package}**: {status}\n")
            if count > 0:
                f.write(f"  - See `{package}/.documents/GUIDELINE_CHECK_RESULTS.md` for details\n")
        f.write("\n")
    
    print(f"\n{'=' * 80}")
    print(f"Summary report written to: {summary_file}")
    print(f"Total violations: {total_violations}")
    
    if total_violations > 0:
        print(f"\n❌ Found {total_violations} guideline violation(s)")
        print("See individual package reports for details.")
        sys.exit(1)
    else:
        print("\n✅ All guidelines passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()

