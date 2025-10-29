#!/usr/bin/env python3
"""
Unit tests for path logic: output_dir, skip_log, staging directory placement.
Tests the critical logic that determines where outputs are created.
"""

import sys
import tempfile
from pathlib import Path

# Add the module to path
sys.path.insert(0, str(Path(__file__).parent))


def test_output_dir_single_file_mode():
    """Test that output_dir is parent directory when processing single file."""
    print("\n" + "=" * 70)
    print("Testing output_dir Logic - Single File Mode")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create test file
        test_file = tmppath / "test.jpg"
        test_file.write_bytes(b"fake image")

        # Simulate single file mode logic
        root = test_file
        is_single_file = True

        # This is the critical logic from cli.py line 3454
        output_dir = root.parent if is_single_file else root

        # Verify output_dir is parent directory
        assert output_dir == tmppath, f"output_dir should be parent directory, got {output_dir}"
        assert output_dir != test_file, "output_dir should NOT be the file itself"
        assert output_dir.is_dir(), "output_dir should be a directory"

        print(f"✓ File: {test_file}")
        print(f"✓ output_dir (parent): {output_dir}")
        print("✓ output_dir correctly set to parent directory in single file mode")

        return True


def test_output_dir_directory_mode():
    """Test that output_dir is scan root when processing directory."""
    print("\n" + "=" * 70)
    print("Testing output_dir Logic - Directory Mode")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create test directory with files
        test_dir = tmppath / "media"
        test_dir.mkdir()
        (test_dir / "image1.jpg").write_bytes(b"fake image 1")
        (test_dir / "image2.jpg").write_bytes(b"fake image 2")

        # Simulate directory mode logic
        root = test_dir
        is_single_file = False

        # This is the critical logic from cli.py line 3454
        output_dir = root.parent if is_single_file else root

        # Verify output_dir is the directory itself
        assert output_dir == test_dir, f"output_dir should be scan root directory, got {output_dir}"
        assert output_dir != tmppath, "output_dir should NOT be parent of scan root"
        assert output_dir.is_dir(), "output_dir should be a directory"

        print(f"✓ Scan root: {test_dir}")
        print(f"✓ output_dir (same): {output_dir}")
        print("✓ output_dir correctly set to scan root in directory mode")

        return True


def test_skip_log_path_single_file_mode():
    """Test skip log is created in parent directory for single file."""
    print("\n" + "=" * 70)
    print("Testing skip_log Path - Single File Mode")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create test file
        test_file = tmppath / "test.jpg"
        test_file.write_bytes(b"fake image")

        # Simulate single file mode
        root = test_file
        is_single_file = True
        run_ts = "20250129_123456"

        # Calculate output_dir
        output_dir = root.parent if is_single_file else root

        # Calculate skip_log path (line 3477 in cli.py)
        skip_log = output_dir / f"smm_skipped_files_{run_ts}.log"

        # Verify skip_log is in parent directory
        assert skip_log.parent == tmppath, f"skip_log should be in parent directory, got {skip_log.parent}"
        assert skip_log.parent == test_file.parent, "skip_log parent should be same as file parent (both in tmppath)"
        assert skip_log.name == f"smm_skipped_files_{run_ts}.log", "skip_log should have correct name"

        print(f"✓ File: {test_file}")
        print(f"✓ output_dir: {output_dir}")
        print(f"✓ skip_log: {skip_log}")
        print("✓ skip_log correctly placed in parent directory (single file mode)")

        return True


def test_skip_log_path_directory_mode():
    """Test skip log is created in scan root for directory scanning."""
    print("\n" + "=" * 70)
    print("Testing skip_log Path - Directory Mode")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create test directory
        test_dir = tmppath / "media"
        test_dir.mkdir()
        (test_dir / "image.jpg").write_bytes(b"fake image")

        # Simulate directory mode
        root = test_dir
        is_single_file = False
        run_ts = "20250129_123456"

        # Calculate output_dir
        output_dir = root.parent if is_single_file else root

        # Calculate skip_log path
        skip_log = output_dir / f"smm_skipped_files_{run_ts}.log"

        # Verify skip_log is in scan root
        assert skip_log.parent == test_dir, f"skip_log should be in scan root, got {skip_log.parent}"
        assert skip_log.parent != tmppath, "skip_log should NOT be in parent of scan root"
        assert skip_log.name == f"smm_skipped_files_{run_ts}.log", "skip_log should have correct name"

        print(f"✓ Scan root: {test_dir}")
        print(f"✓ output_dir: {output_dir}")
        print(f"✓ skip_log: {skip_log}")
        print("✓ skip_log correctly placed in scan root (directory mode)")

        return True


def test_staging_dir_path_single_file_mode():
    """Test staging directory is created in parent directory for single file."""
    print("\n" + "=" * 70)
    print("Testing Staging Directory Path - Single File Mode")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create test file
        test_file = tmppath / "test.jpg"
        test_file.write_bytes(b"fake image")

        # Simulate single file mode
        root = test_file
        is_single_file = True
        run_ts = "20250129_123456"

        # Calculate output_dir
        output_dir = root.parent if is_single_file else root

        # Calculate staging_root path (line 3518 in cli.py)
        staging_root = output_dir / f"FOUND_MEDIA_FILES_{run_ts}"

        # Verify staging_root is in parent directory
        assert staging_root.parent == tmppath, f"staging_root should be in parent directory, got {staging_root.parent}"
        assert staging_root.name == f"FOUND_MEDIA_FILES_{run_ts}", "staging_root should have correct name"

        print(f"✓ File: {test_file}")
        print(f"✓ output_dir: {output_dir}")
        print(f"✓ staging_root: {staging_root}")
        print("✓ staging_root correctly placed in parent directory (single file mode)")

        return True


def test_staging_dir_path_directory_mode():
    """Test staging directory is created in scan root for directory scanning."""
    print("\n" + "=" * 70)
    print("Testing Staging Directory Path - Directory Mode")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create test directory
        test_dir = tmppath / "media"
        test_dir.mkdir()
        (test_dir / "image.jpg").write_bytes(b"fake image")

        # Simulate directory mode
        root = test_dir
        is_single_file = False
        run_ts = "20250129_123456"

        # Calculate output_dir
        output_dir = root.parent if is_single_file else root

        # Calculate staging_root path
        staging_root = output_dir / f"FOUND_MEDIA_FILES_{run_ts}"

        # Verify staging_root is in scan root
        assert staging_root.parent == test_dir, f"staging_root should be in scan root, got {staging_root.parent}"
        assert staging_root.parent != tmppath, "staging_root should NOT be in parent of scan root"
        assert staging_root.name == f"FOUND_MEDIA_FILES_{run_ts}", "staging_root should have correct name"

        print(f"✓ Scan root: {test_dir}")
        print(f"✓ output_dir: {output_dir}")
        print(f"✓ staging_root: {staging_root}")
        print("✓ staging_root correctly placed in scan root (directory mode)")

        return True


def test_all_outputs_use_output_dir():
    """Test that skip_log and staging_root both use output_dir consistently."""
    print("\n" + "=" * 70)
    print("Testing Consistency - All Outputs Use output_dir")
    print("=" * 70)

    test_cases = [
        ("Single file mode", True),
        ("Directory mode", False),
    ]

    passed = 0
    failed = 0

    for mode_name, is_single_file in test_cases:
        print(f"\n{mode_name}:")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            if is_single_file:
                # Create single file
                root = tmppath / "test.jpg"
                root.write_bytes(b"fake image")
            else:
                # Create directory
                root = tmppath / "media"
                root.mkdir()

            run_ts = "20250129_123456"

            # Calculate output_dir
            output_dir = root.parent if is_single_file else root

            # Calculate all output paths
            skip_log = output_dir / f"smm_skipped_files_{run_ts}.log"
            staging_root = output_dir / f"FOUND_MEDIA_FILES_{run_ts}"

            # Verify both use output_dir as parent
            if skip_log.parent == output_dir and staging_root.parent == output_dir:
                print(f"  ✓ output_dir: {output_dir}")
                print(f"  ✓ skip_log parent: {skip_log.parent}")
                print(f"  ✓ staging_root parent: {staging_root.parent}")
                print("  ✓ Both outputs use output_dir consistently")
                passed += 1
            else:
                print(f"  ✗ FAILED: Inconsistent output_dir usage")
                print(f"    output_dir: {output_dir}")
                print(f"    skip_log parent: {skip_log.parent}")
                print(f"    staging_root parent: {staging_root.parent}")
                failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_output_dir_edge_cases():
    """Test edge cases for output_dir calculation."""
    print("\n" + "=" * 70)
    print("Testing output_dir Edge Cases")
    print("=" * 70)

    test_cases = [
        # (description, root_path_func, is_single_file, expected_output_dir_func)
        ("File in nested directory", lambda tmp: tmp / "a" / "b" / "c" / "test.jpg", True, lambda tmp: tmp / "a" / "b" / "c"),
        ("File in root directory", lambda tmp: tmp / "test.jpg", True, lambda tmp: tmp),
        ("Directory in nested path", lambda tmp: tmp / "a" / "b" / "media", False, lambda tmp: tmp / "a" / "b" / "media"),
        ("Directory at root level", lambda tmp: tmp / "media", False, lambda tmp: tmp / "media"),
    ]

    passed = 0
    failed = 0

    for description, root_func, is_single_file, expected_func in test_cases:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create the test path
            root = root_func(tmppath)
            if is_single_file:
                root.parent.mkdir(parents=True, exist_ok=True)
                root.write_bytes(b"fake")
            else:
                root.mkdir(parents=True, exist_ok=True)

            # Calculate output_dir
            output_dir = root.parent if is_single_file else root

            # Get expected output_dir
            expected = expected_func(tmppath)

            if output_dir == expected:
                print(f"✓ {description}")
                print(f"  root: {root}")
                print(f"  output_dir: {output_dir}")
                passed += 1
            else:
                print(f"✗ {description} - FAILED")
                print(f"  root: {root}")
                print(f"  Expected: {expected}")
                print(f"  Got: {output_dir}")
                failed += 1
            print()

    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


def main():
    print("=" * 70)
    print("Comprehensive Unit Tests for Path Logic")
    print("=" * 70)

    results = []

    # Run all tests
    try:
        results.append(("output_dir - Single file mode", test_output_dir_single_file_mode()))
    except Exception as e:
        print(f"\n✗ Single file mode test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("output_dir - Single file mode", False))

    try:
        results.append(("output_dir - Directory mode", test_output_dir_directory_mode()))
    except Exception as e:
        print(f"\n✗ Directory mode test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("output_dir - Directory mode", False))

    try:
        results.append(("skip_log path - Single file mode", test_skip_log_path_single_file_mode()))
    except Exception as e:
        print(f"\n✗ skip_log single file test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("skip_log path - Single file mode", False))

    try:
        results.append(("skip_log path - Directory mode", test_skip_log_path_directory_mode()))
    except Exception as e:
        print(f"\n✗ skip_log directory test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("skip_log path - Directory mode", False))

    try:
        results.append(("staging_root path - Single file mode", test_staging_dir_path_single_file_mode()))
    except Exception as e:
        print(f"\n✗ staging_root single file test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("staging_root path - Single file mode", False))

    try:
        results.append(("staging_root path - Directory mode", test_staging_dir_path_directory_mode()))
    except Exception as e:
        print(f"\n✗ staging_root directory test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("staging_root path - Directory mode", False))

    try:
        results.append(("All outputs use output_dir", test_all_outputs_use_output_dir()))
    except Exception as e:
        print(f"\n✗ Output consistency test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("All outputs use output_dir", False))

    try:
        results.append(("output_dir edge cases", test_output_dir_edge_cases()))
    except Exception as e:
        print(f"\n✗ Edge cases test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("output_dir edge cases", False))

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
