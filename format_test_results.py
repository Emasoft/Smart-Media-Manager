#!/usr/bin/env python3
"""Format test results into a nice table."""

import subprocess
import re
from pathlib import Path

def get_test_info():
    """Extract test information with docstrings."""
    result = subprocess.run(
        ["uv", "run", "pytest", "tests/", "--collect-only", "-q"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent
    )

    tests = []
    for line in result.stdout.split('\n'):
        if '::test_' in line or '::Test' in line:
            tests.append(line.strip())

    return tests

def run_tests():
    """Run tests and capture results."""
    result = subprocess.run(
        ["uv", "run", "pytest", "tests/", "-v", "--tb=no"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent,
        timeout=300
    )

    return result.stdout

def parse_results(output):
    """Parse pytest output into structured data."""
    tests = []

    for line in output.split('\n'):
        if '::test_' in line or ('::Test' in line and 'test_' in line):
            # Extract file, test name, and result
            match = re.search(r'tests/([^:]+)::([^\s]+)\s+(PASSED|FAILED|SKIPPED)', line)
            if match:
                file_name, test_name, status = match.groups()
                tests.append({
                    'file': file_name,
                    'test': test_name,
                    'status': status
                })

    return tests

def get_test_docstrings():
    """Extract test docstrings from test files."""
    docstrings = {}
    test_dir = Path(__file__).parent / 'tests'

    for test_file in test_dir.glob('test_*.py'):
        content = test_file.read_text()

        # Find all test functions and their docstrings
        pattern = r'def (test_\w+)\([^)]*\):\s*"""([^"]+)"""'
        matches = re.findall(pattern, content, re.MULTILINE)

        for test_name, docstring in matches:
            # Clean up docstring
            first_line = docstring.strip().split('\n')[0]
            docstrings[test_name] = first_line

    return docstrings

def format_table(tests, docstrings):
    """Format tests into a nice unicode table."""
    # Calculate column widths
    max_file = max(len(t['file']) for t in tests) if tests else 20
    max_test = max(len(t['test']) for t in tests) if tests else 40
    max_desc = 80  # Cap description length

    # Table borders
    thick_line = '═'
    thin_line = '─'
    thick_corner_tl = '╔'
    thick_corner_tr = '╗'
    thick_corner_bl = '╚'
    thick_corner_br = '╝'
    thin_corner_tl = '┌'
    thin_corner_tr = '┐'
    thin_corner_bl = '└'
    thin_corner_br = '┘'
    thick_cross = '╬'
    thin_cross = '┼'
    thick_t_down = '╦'
    thick_t_up = '╩'
    thin_t_down = '┬'
    thin_t_up = '┴'
    thick_t_right = '╠'
    thick_t_left = '╣'
    thin_t_right = '├'
    thin_t_left = '┤'
    vert = '│'
    vert_thick = '║'

    # Header
    header_line = (thick_corner_tl + thick_line * (max_file + 2) +
                   thick_t_down + thick_line * (max_test + 2) +
                   thick_t_down + thick_line * (max_desc + 2) +
                   thick_t_down + thick_line * 8 + thick_corner_tr)

    print(header_line)
    print(f"{vert_thick} {'File':<{max_file}} {vert_thick} {'Test Function':<{max_test}} {vert_thick} {'Description':<{max_desc}} {vert_thick} Status {vert_thick}")

    separator = (thick_t_right + thick_line * (max_file + 2) +
                 thick_cross + thick_line * (max_test + 2) +
                 thick_cross + thick_line * (max_desc + 2) +
                 thick_cross + thick_line * 8 + thick_t_left)
    print(separator)

    # Body
    for test in tests:
        test_name = test['test'].split('::')[-1]  # Get function name if class::method
        desc = docstrings.get(test_name, "")

        # Truncate description if too long
        if len(desc) > max_desc:
            desc = desc[:max_desc-3] + "..."

        # Color code status
        status = test['status']
        if status == 'PASSED':
            status_display = f"✅ PASS "
        elif status == 'FAILED':
            status_display = f"❌ FAIL "
        else:  # SKIPPED
            status_display = f"⏭️  SKIP "

        print(f"{vert} {test['file']:<{max_file}} {vert} {test_name:<{max_test}} {vert} {desc:<{max_desc}} {vert} {status_display}{vert}")

    # Footer
    footer = (thick_corner_bl + thick_line * (max_file + 2) +
              thick_t_up + thick_line * (max_test + 2) +
              thick_t_up + thick_line * (max_desc + 2) +
              thick_t_up + thick_line * 8 + thick_corner_br)
    print(footer)

    # Summary
    total = len(tests)
    passed = sum(1 for t in tests if t['status'] == 'PASSED')
    failed = sum(1 for t in tests if t['status'] == 'FAILED')
    skipped = sum(1 for t in tests if t['status'] == 'SKIPPED')

    print(f"\n📊 Summary: {total} tests | ✅ {passed} passed | ❌ {failed} failed | ⏭️  {skipped} skipped")
    print(f"📈 Success rate: {passed/total*100:.1f}%")

if __name__ == '__main__':
    print("Running tests and collecting results...\n")
    output = run_tests()
    tests = parse_results(output)
    docstrings = get_test_docstrings()
    format_table(tests, docstrings)
