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
        ('path/with<>:|"?*.txt', "path/with:.txt", "Invalid Windows characters (colon valid on Unix)"),
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
            print("✓ Non-existent path - Correctly rejected")
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
            print("✓ Empty path - Correctly rejected")
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


def test_error_scenarios():
    """Test comprehensive error scenarios."""
    print("\n" + "=" * 70)
    print("Testing Error Scenarios")
    print("=" * 70)

    passed = 0
    failed = 0

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Test 1: Empty file (should warn but not fail)
        print("\nTest 1: Empty file...")
        empty_file = tmppath / "empty.txt"
        empty_file.touch()
        try:
            result = validate_path_argument(str(empty_file))
            print(f"✓ Empty file validated (warning expected): {result}")
            passed += 1
        except argparse.ArgumentTypeError as e:
            print(f"✗ Empty file - Should have warned but not failed: {e}")
            failed += 1
        print()

        # Test 2: Permission denied (directory)
        print("Test 2: Permission denied on directory...")
        restricted_dir = tmppath / "restricted_dir"
        restricted_dir.mkdir()
        (restricted_dir / "test.txt").write_text("test")

        # Make directory unreadable
        import os
        import stat

        try:
            os.chmod(restricted_dir, 0o000)
            try:
                validate_path_argument(str(restricted_dir))
                print("✗ Should have raised permission error")
                failed += 1
            except argparse.ArgumentTypeError as e:
                if "Permission denied" in str(e):
                    print(f"✓ Permission error correctly detected: {e}")
                    passed += 1
                else:
                    print(f"✗ Wrong error type: {e}")
                    failed += 1
        finally:
            # Restore permissions for cleanup
            os.chmod(restricted_dir, stat.S_IRWXU)
        print()

        # Test 3: Permission denied (file)
        print("Test 3: Permission denied on file...")
        restricted_file = tmppath / "restricted.txt"
        restricted_file.write_text("test content")

        try:
            os.chmod(restricted_file, 0o000)
            try:
                validate_path_argument(str(restricted_file))
                print("✗ Should have raised permission error")
                failed += 1
            except argparse.ArgumentTypeError as e:
                if "Permission denied" in str(e):
                    print(f"✓ Permission error correctly detected: {e}")
                    passed += 1
                else:
                    print(f"✗ Wrong error type: {e}")
                    failed += 1
        finally:
            # Restore permissions for cleanup
            os.chmod(restricted_file, stat.S_IRUSR | stat.S_IWUSR)
        print()

        # Test 4: File that exists but can't be read
        print("Test 4: Readable file (should pass)...")
        readable_file = tmppath / "readable.txt"
        readable_file.write_text("test content")
        try:
            result = validate_path_argument(str(readable_file))
            print(f"✓ Readable file validated: {result}")
            passed += 1
        except argparse.ArgumentTypeError as e:
            print(f"✗ Readable file should have passed: {e}")
            failed += 1
        print()

        # Test 5: Unmounted volume simulation (parent doesn't exist)
        print("Test 5: Unmounted volume simulation...")
        unmounted_path = "/Volumes/NonExistentDrive/some/path/file.txt"
        try:
            validate_path_argument(unmounted_path)
            print("✗ Should have raised unmounted volume error")
            failed += 1
        except argparse.ArgumentTypeError as e:
            if "unmounted volume" in str(e).lower() or "does not exist" in str(e):
                print(f"✓ Unmounted volume error correctly detected: {e}")
                passed += 1
            else:
                print(f"✗ Wrong error type: {e}")
                failed += 1
        print()

        # Test 6: Valid directory with files
        print("Test 6: Valid directory with files...")
        valid_dir = tmppath / "valid_dir"
        valid_dir.mkdir()
        (valid_dir / "file1.txt").write_text("content 1")
        (valid_dir / "file2.txt").write_text("content 2")
        try:
            result = validate_path_argument(str(valid_dir))
            print(f"✓ Valid directory validated: {result}")
            passed += 1
        except argparse.ArgumentTypeError as e:
            print(f"✗ Valid directory should have passed: {e}")
            failed += 1
        print()

    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


def main():
    print("=" * 70)
    print("Path Validation Test Suite")
    print("=" * 70)

    results = []

    # Run all tests
    results.append(("sanitize_path_string", test_sanitize_path_string()))
    results.append(("validate_path_argument", test_validate_path_argument()))
    results.append(("CLI unicode paths", test_cli_with_unicode_paths()))
    results.append(("Error scenarios", test_error_scenarios()))

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
