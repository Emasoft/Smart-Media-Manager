#!/usr/bin/env python3
"""
Test path validation with unicode, diacritics, and control characters.
"""

import sys
import tempfile
from pathlib import Path

# Add the module to path
sys.path.insert(0, str(Path(__file__).parent))

from smart_media_manager.cli import sanitize_path_string, validate_path_argument
import argparse


def test_sanitize_path_string():
    """Test path string sanitization."""
    print("\n" + "=" * 70)
    print("Testing sanitize_path_string()")
    print("=" * 70)

    test_cases = [
        # (input, expected_cleaned, description)
        ("normal/path/file.jpg", "normal/path/file.jpg", "Normal ASCII path"),
        ("  /path/with/spaces.txt  ", "/path/with/spaces.txt", "Leading/trailing spaces"),
        ("/path/with\x00null\x01chars.jpg", "/path/withnullchars.jpg", "Null and control characters"),
        ("café/résumé/naïve.txt", "café/résumé/naïve.txt", "French diacritics"),
        ("日本語/ファイル.jpg", "日本語/ファイル.jpg", "Japanese characters"),
        ("Москва/файл.txt", "Москва/файл.txt", "Cyrillic characters"),
        ("Tëst/Fîlé/Ñame.png", "Tëst/Fîlé/Ñame.png", "Mixed diacritics"),
        ("path\twith\ttabs.txt", "pathwithtabs.txt", "Tab characters"),
        ("path\nwith\nnewlines.txt", "pathwithnewlines.txt", "Newline characters"),
        ("path/with<>:|\"?*.txt", "path/with:.txt", "Invalid Windows characters (colon valid on Unix)"),
        ("   ", "", "Only whitespace"),
        ("/ümlaut/Übung.doc", "/ümlaut/Übung.doc", "German umlauts"),
        ("مجلد/ملف.txt", "مجلد/ملف.txt", "Arabic characters"),
        ("תיקייה/קובץ.txt", "תיקייה/קובץ.txt", "Hebrew characters"),
        ("Δοκιμή/αρχείο.txt", "Δοκιμή/αρχείο.txt", "Greek characters"),
    ]

    passed = 0
    failed = 0

    for input_str, expected, description in test_cases:
        result = sanitize_path_string(input_str)
        status = "✓" if result == expected else "✗"

        if result == expected:
            passed += 1
            print(f"{status} {description}")
            print(f"  Input:    {repr(input_str)}")
            print(f"  Expected: {repr(expected)}")
            print(f"  Got:      {repr(result)}")
        else:
            failed += 1
            print(f"{status} {description} - FAILED")
            print(f"  Input:    {repr(input_str)}")
            print(f"  Expected: {repr(expected)}")
            print(f"  Got:      {repr(result)}")
        print()

    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


def test_validate_path_argument():
    """Test path argument validation with real files."""
    print("\n" + "=" * 70)
    print("Testing validate_path_argument()")
    print("=" * 70)

    # Create temporary test files with various names
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Test cases: (filename, should_succeed, description)
        test_cases = [
            ("normal_file.txt", True, "Normal ASCII filename"),
            ("café.txt", True, "French diacritics"),
            ("файл.txt", True, "Cyrillic characters"),
            ("ファイル.txt", True, "Japanese characters"),
            ("Tëst_Fîlé.txt", True, "Mixed diacritics"),
        ]

        passed = 0
        failed = 0

        for filename, should_succeed, description in test_cases:
            # Create the test file
            test_file = tmppath / filename
            test_file.write_text("test content")

            try:
                result = validate_path_argument(str(test_file))
                if should_succeed:
                    if result.exists():
                        print(f"✓ {description}")
                        print(f"  Path: {result}")
                        passed += 1
                    else:
                        print(f"✗ {description} - Path doesn't exist after validation")
                        print(f"  Path: {result}")
                        failed += 1
                else:
                    print(f"✗ {description} - Should have failed but succeeded")
                    print(f"  Path: {result}")
                    failed += 1
            except argparse.ArgumentTypeError as e:
                if not should_succeed:
                    print(f"✓ {description} - Correctly rejected")
                    print(f"  Error: {e}")
                    passed += 1
                else:
                    print(f"✗ {description} - Should have succeeded but failed")
                    print(f"  Error: {e}")
                    failed += 1
            print()

        # Test non-existent path
        print("Testing non-existent path...")
        try:
            validate_path_argument("/this/path/does/not/exist.txt")
            print("✗ Non-existent path - Should have raised error")
            failed += 1
        except argparse.ArgumentTypeError as e:
            print(f"✓ Non-existent path - Correctly rejected")
            print(f"  Error: {e}")
            passed += 1
        print()

        # Test empty path
        print("Testing empty path...")
        try:
            validate_path_argument("   ")
            print("✗ Empty path - Should have raised error")
            failed += 1
        except argparse.ArgumentTypeError as e:
            print(f"✓ Empty path - Correctly rejected")
            print(f"  Error: {e}")
            passed += 1
        print()

        print(f"Results: {passed} passed, {failed} failed")
        return failed == 0


def test_cli_with_unicode_paths():
    """Test CLI argument parsing with unicode paths."""
    print("\n" + "=" * 70)
    print("Testing CLI with unicode paths")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create directories with unicode names
        unicode_dirs = [
            "café_photos",
            "日本の写真",
            "Москва_фото",
            "test_ñ_ü_é",
        ]

        for dirname in unicode_dirs:
            dirpath = tmppath / dirname
            dirpath.mkdir()
            # Create a test file in each directory
            (dirpath / "test.txt").write_text("test")

        print("Created test directories:")
        for dirname in unicode_dirs:
            dirpath = tmppath / dirname
            print(f"  {dirpath}")

            # Try to validate each path
            try:
                validated = validate_path_argument(str(dirpath))
                print(f"    ✓ Validated: {validated}")
            except Exception as e:
                print(f"    ✗ Failed: {e}")

        print("\nAll unicode path tests completed!")
        return True


def main():
    print("=" * 70)
    print("Path Validation Test Suite")
    print("=" * 70)

    results = []

    # Run all tests
    results.append(("sanitize_path_string", test_sanitize_path_string()))
    results.append(("validate_path_argument", test_validate_path_argument()))
    results.append(("CLI unicode paths", test_cli_with_unicode_paths()))

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False

    print("=" * 70)

    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
