#!/usr/bin/env python3
"""
Test log directory creation in CWD with timestamp and exclusion from scanning.
"""

import sys
import tempfile
from pathlib import Path

# Add the module to path
sys.path.insert(0, str(Path(__file__).parent))

from smart_media_manager.cli import attach_file_logger, SMM_LOGS_SUBDIR, timestamp


def test_log_directory_creation():
    """Test that log directory is created in CWD with unique timestamp."""
    print("\n" + "=" * 70)
    print("Testing Log Directory Creation")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create a fake scan directory
        scan_dir = tmppath / "media_to_scan"
        scan_dir.mkdir()

        # Change to temp directory (simulating CWD)
        import os

        original_cwd = Path.cwd()
        try:
            os.chdir(tmppath)

            # Create log directory
            run_ts = timestamp()
            log_path = attach_file_logger(scan_dir, run_ts)

            print(f"\nLog file created at: {log_path}")
            print(f"  Expected in CWD: {tmppath}")
            print(f"  Actual parent: {log_path.parent.parent}")

            # Verify log directory is in CWD (not scan_dir)
            # Use resolve() to handle /var vs /private/var on macOS
            assert log_path.parent.parent.resolve() == tmppath.resolve(), f"Log directory should be in CWD ({tmppath.resolve()}), not in scan directory"

            # Verify log directory name matches pattern
            log_dir_name = log_path.parent.name
            assert log_dir_name.startswith(SMM_LOGS_SUBDIR), f"Log directory should start with {SMM_LOGS_SUBDIR}"
            assert run_ts in log_dir_name, f"Log directory should contain timestamp {run_ts}"

            # Verify log file exists
            assert log_path.exists(), "Log file should exist"

            # Verify log directory contains UUID for uniqueness
            parts = log_dir_name.split("_")
            assert len(parts) >= 4, "Log directory should have format: .smm__runtime_logs_YYYYMMDD_HHMMSS_<uuid>"

            print(f"\n✓ Log directory created successfully: {log_dir_name}")
            print("✓ Log directory is in CWD (not scan directory)")
            print(f"✓ Log directory contains timestamp: {run_ts}")
            print("✓ Log directory contains UUID for uniqueness")

            return True

        finally:
            os.chdir(original_cwd)


def test_log_directory_exclusion():
    """Test that log directories are excluded from scanning."""
    print("\n" + "=" * 70)
    print("Testing Log Directory Exclusion from Scanning")
    print("=" * 70)

    from smart_media_manager.cli import gather_media_files, SkipLogger, RunStatistics

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create test media file
        test_media = tmppath / "test_image.jpg"
        test_media.write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")  # Minimal JPEG header

        # Create log directory matching our pattern
        log_dir = tmppath / f"{SMM_LOGS_SUBDIR}20250129_123456_abc123"
        log_dir.mkdir()

        # Create fake log file inside log directory
        fake_log = log_dir / "smm_run_20250129_123456.log"
        fake_log.write_text("fake log content")

        # Also create a standalone log file (should also be ignored)
        standalone_log = tmppath / "smm_run_20250129_999999.log"
        standalone_log.write_text("standalone log")

        # Scan directory
        skip_logger = SkipLogger(tmppath / "skip_test.log")
        stats = RunStatistics()

        media_files = gather_media_files(root=tmppath, recursive=True, follow_symlinks=False, skip_logger=skip_logger, stats=stats, skip_compatibility_check=True)

        # Verify results
        print("\nFiles found in directory:")
        for entry in tmppath.rglob("*"):
            if entry.is_file():
                print(f"  {entry.relative_to(tmppath)}")

        print(f"\nMedia files detected: {len(media_files)}")
        for media in media_files:
            print(f"  {media.source.relative_to(tmppath)}")

        # Should find only test_image.jpg, not logs
        assert len(media_files) == 1, f"Expected 1 media file, found {len(media_files)}"
        assert media_files[0].source.name == "test_image.jpg", "Should find test_image.jpg"

        print(f"\n✓ Log directory {SMM_LOGS_SUBDIR}* correctly excluded from scanning")
        print("✓ Log files smm_run_* correctly excluded from scanning")
        print("✓ Only test_image.jpg was scanned")

        # SkipLogger doesn't have a close() method, just cleanup the file
        if skip_logger.path.exists():
            skip_logger.path.unlink()

        return True


def test_no_code_duplication():
    """Test that output_dir logic is not duplicated in cli.py."""
    print("\n" + "=" * 70)
    print("Testing for Code Duplication")
    print("=" * 70)

    with open(Path(__file__).parent / "smart_media_manager" / "cli.py") as f:
        cli_content = f.read()

    # Check that "root.parent if is_single_file else root" appears only once
    duplication_pattern = "root.parent if is_single_file else root"
    count = cli_content.count(duplication_pattern)

    print("\nChecking for duplicated directory calculation pattern:")
    print(f"  Pattern: '{duplication_pattern}'")
    print(f"  Occurrences: {count}")

    if count > 1:
        print(f"✗ FAILED: Pattern appears {count} times (should be 1)")
        print("  This indicates code duplication that should be refactored")
        return False
    elif count == 1:
        print("✓ Pattern appears exactly once (stored in output_dir variable)")
        return True
    else:
        print("✗ FAILED: Pattern not found (might have been renamed)")
        return False


def test_output_dir_usage_consistency():
    """Test that output_dir is used consistently throughout main()."""
    print("\n" + "=" * 70)
    print("Testing output_dir Usage Consistency")
    print("=" * 70)

    with open(Path(__file__).parent / "smart_media_manager" / "cli.py") as f:
        cli_content = f.read()

    # Extract main() function
    import re

    main_match = re.search(r"def main\(\).*?(?=\ndef |\Z)", cli_content, re.DOTALL)
    if not main_match:
        print("✗ Could not find main() function")
        return False

    main_content = main_match.group(0)

    # Check that output_dir is defined
    if "output_dir = root.parent if is_single_file else root" not in main_content:
        print("✗ output_dir variable not found in main()")
        return False

    # Check that skip_log uses output_dir
    if "skip_log = output_dir /" in main_content:
        print("✓ skip_log uses output_dir")
    else:
        print("✗ skip_log does not use output_dir")
        return False

    # Check that staging_root uses output_dir
    if "staging_root = output_dir /" in main_content:
        print("✓ staging_root uses output_dir")
    else:
        print("✗ staging_root does not use output_dir")
        return False

    print("\n✓ output_dir is used consistently for all outputs")
    return True


def test_write_permission_checks_present():
    """Test that write permission checks are present for all necessary directories."""
    print("\n" + "=" * 70)
    print("Testing Write Permission Checks")
    print("=" * 70)

    with open(Path(__file__).parent / "smart_media_manager" / "cli.py") as f:
        cli_content = f.read()

    # Check for CWD write permission check
    if 'check_write_permission(Path.cwd(), "create logs")' in cli_content:
        print("✓ Write permission check for CWD (logs) found")
    else:
        print("✗ Missing write permission check for CWD")
        return False

    # Check for output_dir write permission check
    if 'check_write_permission(output_dir, "create skip logs and staging directory")' in cli_content:
        print("✓ Write permission check for output_dir (skip logs/staging) found")
    else:
        print("✗ Missing write permission check for output_dir")
        return False

    print("\n✓ All necessary write permission checks are present")
    return True


def main():
    print("=" * 70)
    print("Log Directory Test Suite")
    print("=" * 70)

    results = []

    # Run all tests
    try:
        results.append(("Log directory creation", test_log_directory_creation()))
    except Exception as e:
        print(f"\n✗ Log directory creation FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("Log directory creation", False))

    try:
        results.append(("Log directory exclusion", test_log_directory_exclusion()))
    except Exception as e:
        print(f"\n✗ Log directory exclusion FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("Log directory exclusion", False))

    try:
        results.append(("No code duplication", test_no_code_duplication()))
    except Exception as e:
        print(f"\n✗ Code duplication test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("No code duplication", False))

    try:
        results.append(("output_dir usage consistency", test_output_dir_usage_consistency()))
    except Exception as e:
        print(f"\n✗ output_dir consistency test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("output_dir usage consistency", False))

    try:
        results.append(("Write permission checks", test_write_permission_checks_present()))
    except Exception as e:
        print(f"\n✗ Write permission check test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("Write permission checks", False))

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
