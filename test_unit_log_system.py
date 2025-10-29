#!/usr/bin/env python3
"""
Comprehensive unit tests for log directory system.
Tests individual functions and edge cases in isolation.
"""

import sys
import tempfile
import logging
from pathlib import Path
import os

# Add the module to path
sys.path.insert(0, str(Path(__file__).parent))

from smart_media_manager.cli import (
    attach_file_logger,
    SMM_LOGS_SUBDIR,
    timestamp,
    _FILE_LOG_HANDLER,
    should_ignore,
    gather_media_files,
    SkipLogger,
    RunStatistics,
)


def test_should_ignore_log_directories():
    """Test that should_ignore correctly filters log directories."""
    print("\n" + "=" * 70)
    print("Testing should_ignore() - Log Directories")
    print("=" * 70)

    test_cases = [
        # (path_name, should_be_ignored, description)
        (".smm__runtime_logs_20250129_123456_abc123", True, "Timestamped log directory"),
        (".smm__runtime_logs_20250129_123456", True, "Log directory without UUID"),
        (".smm__runtime_logs_", True, "Log directory prefix only"),
        ("smm__runtime_logs_20250129", False, "Missing leading dot"),
        (".smm_runtime_logs_20250129", False, "Single underscore instead of double"),
        ("my_smm__runtime_logs_folder", False, "Log prefix in middle of name"),
        (".smm__runtime_logs_test", True, "Log directory with custom suffix"),
    ]

    passed = 0
    failed = 0

    for path_name, expected_ignored, description in test_cases:
        path = Path(path_name)
        result = should_ignore(path)
        status = "✓" if result == expected_ignored else "✗"

        if result == expected_ignored:
            passed += 1
            print(f"{status} {description}")
            print(f"  Path: {path_name}")
            print(f"  Expected ignored: {expected_ignored}, Got: {result}")
        else:
            failed += 1
            print(f"{status} {description} - FAILED")
            print(f"  Path: {path_name}")
            print(f"  Expected ignored: {expected_ignored}, Got: {result}")
        print()

    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


def test_should_ignore_staging_directories():
    """Test that should_ignore correctly filters staging directories."""
    print("\n" + "=" * 70)
    print("Testing should_ignore() - Staging Directories")
    print("=" * 70)

    test_cases = [
        ("FOUND_MEDIA_FILES_20250129_123456", True, "Staging directory with timestamp"),
        ("FOUND_MEDIA_FILES_test", True, "Staging directory with custom suffix"),
        ("FOUND_MEDIA_FILES_", True, "Staging directory prefix only"),
        ("found_media_files_20250129", False, "Lowercase staging directory"),
        ("MY_FOUND_MEDIA_FILES_20250129", False, "Staging prefix in middle"),
        ("FOUND_MEDIA_FILES", False, "Exact prefix without underscore"),
    ]

    passed = 0
    failed = 0

    for path_name, expected_ignored, description in test_cases:
        path = Path(path_name)
        result = should_ignore(path)
        status = "✓" if result == expected_ignored else "✗"

        if result == expected_ignored:
            passed += 1
            print(f"{status} {description}")
        else:
            failed += 1
            print(f"{status} {description} - FAILED")
            print(f"  Expected: {expected_ignored}, Got: {result}")
        print()

    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


def test_should_ignore_log_files():
    """Test that should_ignore correctly filters individual log files."""
    print("\n" + "=" * 70)
    print("Testing should_ignore() - Log Files")
    print("=" * 70)

    test_cases = [
        ("smm_run_20250129_123456.log", True, "SMM run log file"),
        ("smm_skipped_files_20250129_123456.log", True, "SMM skip log file"),
        ("smm_run_.log", True, "Run log with minimal naming"),
        ("smm_skipped_files_.log", True, "Skip log with minimal naming"),
        ("my_smm_run_20250129.log", False, "SMM prefix in middle"),
        ("smm_test_20250129.log", False, "Different SMM log type"),
        (".DS_Store", True, "macOS metadata file"),
        ("DS_Store", False, "DS_Store without leading dot"),
    ]

    passed = 0
    failed = 0

    for path_name, expected_ignored, description in test_cases:
        path = Path(path_name)
        result = should_ignore(path)
        status = "✓" if result == expected_ignored else "✗"

        if result == expected_ignored:
            passed += 1
            print(f"{status} {description}")
        else:
            failed += 1
            print(f"{status} {description} - FAILED")
            print(f"  Expected: {expected_ignored}, Got: {result}")
        print()

    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


def test_should_ignore_regular_files():
    """Test that should_ignore does NOT filter regular media files."""
    print("\n" + "=" * 70)
    print("Testing should_ignore() - Regular Files (Should NOT Ignore)")
    print("=" * 70)

    test_cases = [
        ("image.jpg", False, "Regular JPEG image"),
        ("video.mp4", False, "Regular MP4 video"),
        ("photo_20250129_123456.jpg", False, "Timestamped photo"),
        ("my_vacation.mov", False, "Regular MOV video"),
        ("document.pdf", False, "PDF document"),
        (".hidden_file.txt", False, "Hidden file (but not .DS_Store)"),
        ("normal_directory", False, "Regular directory"),
    ]

    passed = 0
    failed = 0

    for path_name, expected_ignored, description in test_cases:
        path = Path(path_name)
        result = should_ignore(path)
        status = "✓" if result == expected_ignored else "✗"

        if result == expected_ignored:
            passed += 1
            print(f"{status} {description}")
        else:
            failed += 1
            print(f"{status} {description} - FAILED")
            print(f"  Expected: {expected_ignored}, Got: {result}")
        print()

    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


def test_attach_file_logger_creates_unique_dirs():
    """Test that attach_file_logger creates unique directories with UUIDs."""
    print("\n" + "=" * 70)
    print("Testing attach_file_logger() - Unique Directory Creation")
    print("=" * 70)

    # Reset global handler
    global _FILE_LOG_HANDLER
    from smart_media_manager import cli
    cli._FILE_LOG_HANDLER = None

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        original_cwd = Path.cwd()

        try:
            os.chdir(tmppath)

            # Create first log
            run_ts1 = "20250129_120000"
            log_path1 = attach_file_logger(tmppath, run_ts1)

            # Reset handler to create second log
            cli._FILE_LOG_HANDLER = None

            # Create second log with same timestamp
            run_ts2 = "20250129_120000"
            log_path2 = attach_file_logger(tmppath, run_ts2)

            # Verify both exist
            assert log_path1.exists(), f"First log should exist: {log_path1}"
            assert log_path2.exists(), f"Second log should exist: {log_path2}"

            # Verify they're in different directories (UUID makes them unique)
            assert log_path1.parent != log_path2.parent, "Log directories should be unique (different UUIDs)"

            # Verify both are in CWD
            assert log_path1.parent.parent.resolve() == tmppath.resolve(), "First log should be in CWD"
            assert log_path2.parent.parent.resolve() == tmppath.resolve(), "Second log should be in CWD"

            # Verify directory names contain timestamp
            assert run_ts1 in log_path1.parent.name, "First log directory should contain timestamp"
            assert run_ts2 in log_path2.parent.name, "Second log directory should contain timestamp"

            print(f"✓ First log: {log_path1.parent.name}")
            print(f"✓ Second log: {log_path2.parent.name}")
            print("✓ Both logs exist in separate unique directories")
            print("✓ Both directories are in CWD")

            return True

        finally:
            os.chdir(original_cwd)
            cli._FILE_LOG_HANDLER = None


def test_attach_file_logger_singleton_behavior():
    """Test that attach_file_logger returns same path on repeated calls."""
    print("\n" + "=" * 70)
    print("Testing attach_file_logger() - Singleton Behavior")
    print("=" * 70)

    # Reset global handler
    from smart_media_manager import cli
    cli._FILE_LOG_HANDLER = None

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        original_cwd = Path.cwd()

        try:
            os.chdir(tmppath)

            run_ts = "20250129_123456"

            # First call creates the logger
            log_path1 = attach_file_logger(tmppath, run_ts)

            # Second call should return same path without creating new directory
            log_path2 = attach_file_logger(tmppath, run_ts)

            # Third call should also return same path
            log_path3 = attach_file_logger(tmppath, run_ts)

            assert log_path1 == log_path2 == log_path3, "All calls should return same path"

            # Verify only one log directory was created
            log_dirs = list(tmppath.glob(f"{SMM_LOGS_SUBDIR}*"))
            assert len(log_dirs) == 1, f"Should create only one log directory, found {len(log_dirs)}"

            print(f"✓ Log path: {log_path1}")
            print("✓ Multiple calls return same path (singleton behavior)")
            print(f"✓ Only one log directory created: {log_dirs[0].name}")

            return True

        finally:
            os.chdir(original_cwd)
            cli._FILE_LOG_HANDLER = None


def test_attach_file_logger_directory_structure():
    """Test that attach_file_logger creates correct directory structure."""
    print("\n" + "=" * 70)
    print("Testing attach_file_logger() - Directory Structure")
    print("=" * 70)

    # Reset global handler
    from smart_media_manager import cli
    cli._FILE_LOG_HANDLER = None

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        original_cwd = Path.cwd()

        try:
            os.chdir(tmppath)

            run_ts = "20250129_123456"
            log_path = attach_file_logger(tmppath, run_ts)

            # Verify log file is nested inside log directory (use resolve() to handle /var vs /private/var on macOS)
            assert log_path.parent.parent.resolve() == tmppath.resolve(), "Log file should be inside log directory inside CWD"

            # Verify log directory name format
            log_dir_name = log_path.parent.name
            parts = log_dir_name.split("_")

            assert log_dir_name.startswith(SMM_LOGS_SUBDIR), f"Log directory should start with {SMM_LOGS_SUBDIR}"
            assert run_ts in log_dir_name, f"Log directory should contain timestamp {run_ts}"
            assert len(parts) >= 4, f"Log directory should have format: {SMM_LOGS_SUBDIR}YYYYMMDD_HHMMSS_<uuid>"

            # Verify log file name format
            log_file_name = log_path.name
            assert log_file_name == f"smm_run_{run_ts}.log", f"Log file should be named smm_run_{run_ts}.log"

            # Verify log file is writable
            assert log_path.exists(), "Log file should be created"
            assert log_path.is_file(), "Log path should be a file"

            print(f"✓ Log directory: {log_dir_name}")
            print(f"✓ Log file: {log_file_name}")
            print(f"✓ Full path: {log_path}")
            print("✓ Directory structure is correct")

            return True

        finally:
            os.chdir(original_cwd)
            cli._FILE_LOG_HANDLER = None


def main():
    print("=" * 70)
    print("Comprehensive Unit Tests for Log System")
    print("=" * 70)

    results = []

    # Run all tests
    try:
        results.append(("should_ignore - Log directories", test_should_ignore_log_directories()))
    except Exception as e:
        print(f"\n✗ Log directories test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("should_ignore - Log directories", False))

    try:
        results.append(("should_ignore - Staging directories", test_should_ignore_staging_directories()))
    except Exception as e:
        print(f"\n✗ Staging directories test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("should_ignore - Staging directories", False))

    try:
        results.append(("should_ignore - Log files", test_should_ignore_log_files()))
    except Exception as e:
        print(f"\n✗ Log files test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("should_ignore - Log files", False))

    try:
        results.append(("should_ignore - Regular files", test_should_ignore_regular_files()))
    except Exception as e:
        print(f"\n✗ Regular files test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("should_ignore - Regular files", False))

    try:
        results.append(("attach_file_logger - Unique directories", test_attach_file_logger_creates_unique_dirs()))
    except Exception as e:
        print(f"\n✗ Unique directories test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("attach_file_logger - Unique directories", False))

    try:
        results.append(("attach_file_logger - Singleton behavior", test_attach_file_logger_singleton_behavior()))
    except Exception as e:
        print(f"\n✗ Singleton behavior test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("attach_file_logger - Singleton behavior", False))

    try:
        results.append(("attach_file_logger - Directory structure", test_attach_file_logger_directory_structure()))
    except Exception as e:
        print(f"\n✗ Directory structure test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("attach_file_logger - Directory structure", False))

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
