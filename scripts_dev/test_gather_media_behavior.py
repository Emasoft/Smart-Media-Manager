#!/usr/bin/env python3
"""
Test gather_media_files() actual behavior with real file scenarios.
Tests OBSERVABLE BEHAVIOR, not duplicated implementation logic.
"""

import sys
import tempfile
from pathlib import Path

# Add the module to path
sys.path.insert(0, str(Path(__file__).parent))

from smart_media_manager.cli import (
    gather_media_files,
    SkipLogger,
    RunStatistics,
)


def test_gather_empty_directory():
    """Test that gather_media_files returns empty list for empty directory."""
    print("\n" + "=" * 70)
    print("Testing gather_media_files() - Empty Directory")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        skip_logger = SkipLogger(tmppath / "skip.log")
        stats = RunStatistics()

        # Call ACTUAL function
        result = gather_media_files(
            root=tmppath,
            recursive=True,
            follow_symlinks=False,
            skip_logger=skip_logger,
            stats=stats,
            skip_compatibility_check=True,
        )

        # Verify ACTUAL behavior
        assert len(result) == 0, f"Empty directory should return empty list, got {len(result)} files"
        print("✓ Empty directory returns empty list")

        # Cleanup
        if skip_logger.path.exists():
            skip_logger.path.unlink()

        return True


def test_gather_single_jpeg():
    """Test that gather_media_files finds a single JPEG file."""
    print("\n" + "=" * 70)
    print("Testing gather_media_files() - Single JPEG File")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create a minimal JPEG file
        jpeg_file = tmppath / "test.jpg"
        jpeg_file.write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")

        skip_logger = SkipLogger(tmppath / "skip.log")
        stats = RunStatistics()

        # Call ACTUAL function
        result = gather_media_files(
            root=tmppath,
            recursive=True,
            follow_symlinks=False,
            skip_logger=skip_logger,
            stats=stats,
            skip_compatibility_check=True,
        )

        # Verify ACTUAL behavior
        assert len(result) == 1, f"Should find 1 JPEG file, found {len(result)}"
        assert result[0].source.name == "test.jpg", f"Should find test.jpg, found {result[0].source.name}"
        print(f"✓ Found JPEG file: {result[0].source.name}")
        print(f"  Kind: {result[0].kind}")
        print(f"  Extension: {result[0].extension}")

        # Cleanup
        if skip_logger.path.exists():
            skip_logger.path.unlink()

        return True


def test_gather_recursive_vs_non_recursive():
    """Test that recursive flag controls subdirectory scanning."""
    print("\n" + "=" * 70)
    print("Testing gather_media_files() - Recursive vs Non-Recursive")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create files in root
        (tmppath / "root.jpg").write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")

        # Create subdirectory with file
        subdir = tmppath / "subdir"
        subdir.mkdir()
        (subdir / "sub.jpg").write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")

        skip_logger = SkipLogger(tmppath / "skip.log")
        stats_recursive = RunStatistics()
        stats_non_recursive = RunStatistics()

        # Test with recursive=True
        result_recursive = gather_media_files(
            root=tmppath,
            recursive=True,
            follow_symlinks=False,
            skip_logger=skip_logger,
            stats=stats_recursive,
            skip_compatibility_check=True,
        )

        # Test with recursive=False
        result_non_recursive = gather_media_files(
            root=tmppath,
            recursive=False,
            follow_symlinks=False,
            skip_logger=skip_logger,
            stats=stats_non_recursive,
            skip_compatibility_check=True,
        )

        # Verify ACTUAL behavior
        print(f"\nRecursive=True found: {len(result_recursive)} files")
        for media in result_recursive:
            print(f"  {media.source.relative_to(tmppath)}")

        print(f"\nRecursive=False found: {len(result_non_recursive)} files")
        for media in result_non_recursive:
            print(f"  {media.source.relative_to(tmppath)}")

        assert len(result_recursive) == 2, f"Recursive should find 2 files, found {len(result_recursive)}"
        assert len(result_non_recursive) == 1, f"Non-recursive should find 1 file, found {len(result_non_recursive)}"
        assert result_non_recursive[0].source.name == "root.jpg", "Non-recursive should only find root.jpg"

        print("\n✓ Recursive flag correctly controls subdirectory scanning")

        # Cleanup
        if skip_logger.path.exists():
            skip_logger.path.unlink()

        return True


def test_gather_ignores_log_directories():
    """Test that gather_media_files ignores log directories."""
    print("\n" + "=" * 70)
    print("Testing gather_media_files() - Ignores Log Directories")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create regular file
        (tmppath / "regular.jpg").write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")

        # Create log directory with media file
        log_dir = tmppath / ".smm__runtime_logs_20250129_123456"
        log_dir.mkdir()
        (log_dir / "inside_log.jpg").write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")

        # Create staging directory with media file
        staging_dir = tmppath / "FOUND_MEDIA_FILES_20250129_123456"
        staging_dir.mkdir()
        (staging_dir / "inside_staging.jpg").write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")

        skip_logger = SkipLogger(tmppath / "skip.log")
        stats = RunStatistics()

        # Call ACTUAL function
        result = gather_media_files(
            root=tmppath,
            recursive=True,
            follow_symlinks=False,
            skip_logger=skip_logger,
            stats=stats,
            skip_compatibility_check=True,
        )

        # Verify ACTUAL behavior
        print(f"\nFound {len(result)} files:")
        for media in result:
            print(f"  {media.source.relative_to(tmppath)}")

        assert len(result) == 1, f"Should only find regular.jpg, found {len(result)} files"
        assert result[0].source.name == "regular.jpg", f"Should find regular.jpg, found {result[0].source.name}"

        print("\n✓ Log directories correctly ignored")
        print("✓ Staging directories correctly ignored")

        # Cleanup
        if skip_logger.path.exists():
            skip_logger.path.unlink()

        return True


def test_gather_ignores_text_files():
    """Test that gather_media_files ignores text files."""
    print("\n" + "=" * 70)
    print("Testing gather_media_files() - Ignores Text Files")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create media file
        (tmppath / "image.jpg").write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")

        # Create text file with .txt extension
        (tmppath / "readme.txt").write_text("This is a text file")

        # Create text file with no extension
        (tmppath / "LICENSE").write_text("MIT License\nCopyright...")

        # Create JSON file
        (tmppath / "config.json").write_text('{"key": "value"}')

        skip_logger = SkipLogger(tmppath / "skip.log")
        stats = RunStatistics()

        # Call ACTUAL function
        result = gather_media_files(
            root=tmppath,
            recursive=True,
            follow_symlinks=False,
            skip_logger=skip_logger,
            stats=stats,
            skip_compatibility_check=True,
        )

        # Verify ACTUAL behavior
        print(f"\nFound {len(result)} files:")
        for media in result:
            print(f"  {media.source.name}")

        assert len(result) == 1, f"Should only find image.jpg, found {len(result)} files"
        assert result[0].source.name == "image.jpg", f"Should find image.jpg, found {result[0].source.name}"

        print("\n✓ Text files correctly ignored")
        print("✓ JSON files correctly ignored")

        # Cleanup
        if skip_logger.path.exists():
            skip_logger.path.unlink()

        return True


def test_gather_mixed_media_types():
    """Test that gather_media_files finds multiple media types."""
    print("\n" + "=" * 70)
    print("Testing gather_media_files() - Mixed Media Types")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create JPEG
        (tmppath / "photo.jpg").write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")

        # Create PNG (minimal header)
        png_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
        (tmppath / "graphic.png").write_bytes(png_data)

        # Create GIF (minimal header)
        gif_data = b"GIF89a\x01\x00\x01\x00\x00\x00\x00,"
        (tmppath / "animation.gif").write_bytes(gif_data)

        skip_logger = SkipLogger(tmppath / "skip.log")
        stats = RunStatistics()

        # Call ACTUAL function
        result = gather_media_files(
            root=tmppath,
            recursive=True,
            follow_symlinks=False,
            skip_logger=skip_logger,
            stats=stats,
            skip_compatibility_check=True,
        )

        # Verify ACTUAL behavior
        print(f"\nFound {len(result)} files:")
        for media in result:
            print(f"  {media.source.name} - Kind: {media.kind}, Extension: {media.extension}")

        assert len(result) == 3, f"Should find 3 media files, found {len(result)}"

        filenames = {m.source.name for m in result}
        assert "photo.jpg" in filenames, "Should find photo.jpg"
        assert "graphic.png" in filenames, "Should find graphic.png"
        assert "animation.gif" in filenames, "Should find animation.gif"

        print("\n✓ Multiple media types correctly detected")

        # Cleanup
        if skip_logger.path.exists():
            skip_logger.path.unlink()

        return True


def test_gather_nested_directories():
    """Test that gather_media_files handles deeply nested directories."""
    print("\n" + "=" * 70)
    print("Testing gather_media_files() - Nested Directories")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create nested directory structure
        level1 = tmppath / "Photos"
        level2 = level1 / "2025"
        level3 = level2 / "January"
        level3.mkdir(parents=True)

        # Place files at different levels
        (tmppath / "root.jpg").write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")
        (level1 / "level1.jpg").write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")
        (level2 / "level2.jpg").write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")
        (level3 / "level3.jpg").write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")

        skip_logger = SkipLogger(tmppath / "skip.log")
        stats = RunStatistics()

        # Call ACTUAL function
        result = gather_media_files(
            root=tmppath,
            recursive=True,
            follow_symlinks=False,
            skip_logger=skip_logger,
            stats=stats,
            skip_compatibility_check=True,
        )

        # Verify ACTUAL behavior
        print(f"\nFound {len(result)} files:")
        for media in result:
            print(f"  {media.source.relative_to(tmppath)}")

        assert len(result) == 4, f"Should find 4 files at different nesting levels, found {len(result)}"

        filenames = {m.source.name for m in result}
        assert "root.jpg" in filenames, "Should find root.jpg"
        assert "level1.jpg" in filenames, "Should find level1.jpg"
        assert "level2.jpg" in filenames, "Should find level2.jpg"
        assert "level3.jpg" in filenames, "Should find level3.jpg"

        print("\n✓ Nested directories correctly scanned")

        # Cleanup
        if skip_logger.path.exists():
            skip_logger.path.unlink()

        return True


def main():
    print("=" * 70)
    print("gather_media_files() Behavior Tests")
    print("=" * 70)

    results = []

    # Run all tests
    try:
        results.append(("Empty directory", test_gather_empty_directory()))
    except Exception as e:
        print(f"\n✗ Empty directory test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("Empty directory", False))

    try:
        results.append(("Single JPEG file", test_gather_single_jpeg()))
    except Exception as e:
        print(f"\n✗ Single JPEG test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("Single JPEG file", False))

    try:
        results.append(("Recursive vs non-recursive", test_gather_recursive_vs_non_recursive()))
    except Exception as e:
        print(f"\n✗ Recursive test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("Recursive vs non-recursive", False))

    try:
        results.append(("Ignores log directories", test_gather_ignores_log_directories()))
    except Exception as e:
        print(f"\n✗ Log directory test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("Ignores log directories", False))

    try:
        results.append(("Ignores text files", test_gather_ignores_text_files()))
    except Exception as e:
        print(f"\n✗ Text file test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("Ignores text files", False))

    try:
        results.append(("Mixed media types", test_gather_mixed_media_types()))
    except Exception as e:
        print(f"\n✗ Mixed media test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("Mixed media types", False))

    try:
        results.append(("Nested directories", test_gather_nested_directories()))
    except Exception as e:
        print(f"\n✗ Nested directories test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("Nested directories", False))

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
