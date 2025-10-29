#!/usr/bin/env python3
"""
Test move_to_staging() actual behavior with real file scenarios.
Tests OBSERVABLE BEHAVIOR, not duplicated implementation logic.
"""

import sys
import tempfile
from pathlib import Path

# Add the module to path
sys.path.insert(0, str(Path(__file__).parent))

from smart_media_manager.cli import (
    move_to_staging,
    MediaFile,
    timestamp,
)


def test_move_to_staging_preserves_filename():
    """Test that move_to_staging preserves original filename when safe."""
    print("\n" + "=" * 70)
    print("Testing move_to_staging() - Preserves Safe Filename")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create source file with safe name
        source_file = tmppath / "vacation_photo.jpg"
        source_file.write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")

        # Create staging directory
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_dir.mkdir()

        # Create MediaFile object
        media = MediaFile(
            source=source_file,
            kind="image",
            extension=".jpg",
            format_name="JPEG",
            stage_path=None,
            compatible=True,
            rule_id="R-IMG-001",
            action="import",
            requires_processing=False,
        )

        # Call ACTUAL function (takes iterable of media files)
        move_to_staging([media], staging_dir)

        # Verify ACTUAL behavior - media object is modified in-place
        assert media.stage_path is not None, "stage_path should be set"
        assert media.stage_path.exists(), f"Staged file should exist: {media.stage_path}"
        assert media.stage_path.name == "vacation_photo.jpg", f"Filename should be preserved, got {media.stage_path.name}"
        assert media.stage_path.parent == staging_dir, "File should be in staging directory"

        print(f"✓ Original: {source_file.name}")
        print(f"✓ Staged:   {media.stage_path.name}")
        print("✓ Filename preserved (safe name)")

        return True


def test_move_to_staging_creates_staging_directory():
    """Test that move_to_staging creates staging directory if it doesn't exist."""
    print("\n" + "=" * 70)
    print("Testing move_to_staging() - Creates Staging Directory")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create source file
        source_file = tmppath / "test.jpg"
        source_file.write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")

        # Don't create staging directory yet
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"

        # Verify staging directory doesn't exist
        assert not staging_dir.exists(), "Staging directory should not exist yet"

        # Create MediaFile object
        media = MediaFile(
            source=source_file,
            kind="image",
            extension=".jpg",
            format_name="JPEG",
            stage_path=None,
            compatible=True,
            rule_id="R-IMG-001",
            action="import",
            requires_processing=False,
        )

        # Call ACTUAL function
        move_to_staging([media], staging_dir)

        # Verify ACTUAL behavior
        assert staging_dir.exists(), "Staging directory should be created"
        assert staging_dir.is_dir(), "Staging directory should be a directory"
        assert media.stage_path.exists(), "Staged file should exist"
        assert media.stage_path.parent == staging_dir, "File should be in staging directory"

        print(f"✓ Staging directory created: {staging_dir.name}")
        print(f"✓ File staged: {media.stage_path.name}")

        return True


def test_move_to_staging_moves_file():
    """Test that move_to_staging actually moves the file (doesn't copy)."""
    print("\n" + "=" * 70)
    print("Testing move_to_staging() - Moves File (Not Copy)")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create source file
        source_file = tmppath / "original.jpg"
        source_file.write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")

        # Verify source exists
        assert source_file.exists(), "Source file should exist before move"

        # Create staging directory
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_dir.mkdir()

        # Create MediaFile object
        media = MediaFile(
            source=source_file,
            kind="image",
            extension=".jpg",
            format_name="JPEG",
            stage_path=None,
            compatible=True,
            rule_id="R-IMG-001",
            action="import",
            requires_processing=False,
        )

        # Call ACTUAL function
        move_to_staging([media], staging_dir)

        # Verify ACTUAL behavior
        assert media.stage_path.exists(), "Staged file should exist"
        assert not source_file.exists(), "Source file should no longer exist (moved, not copied)"

        print(f"✓ Source file moved (not copied)")
        print(f"✓ Staged at: {media.stage_path}")

        return True


def test_move_to_staging_handles_name_collision():
    """Test that move_to_staging handles filename collisions."""
    print("\n" + "=" * 70)
    print("Testing move_to_staging() - Handles Name Collision")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create staging directory
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_dir.mkdir()

        # Pre-create a file in staging with the name we'll try to use
        (staging_dir / "photo.jpg").write_text("existing file")

        # Create source file with same name
        source_file = tmppath / "photo.jpg"
        source_file.write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")

        # Create MediaFile object
        media = MediaFile(
            source=source_file,
            kind="image",
            extension=".jpg",
            format_name="JPEG",
            stage_path=None,
            compatible=True,
            rule_id="R-IMG-001",
            action="import",
            requires_processing=False,
        )

        # Call ACTUAL function
        move_to_staging([media], staging_dir)

        # Verify ACTUAL behavior
        assert media.stage_path.exists(), "Staged file should exist"
        assert media.stage_path.name != "photo.jpg", f"Should have unique name, got {media.stage_path.name}"
        assert media.stage_path.parent == staging_dir, "File should be in staging directory"

        # Original file should still exist (collision prevented move)
        assert (staging_dir / "photo.jpg").exists(), "Original file should still exist"

        print(f"✓ Collision detected")
        print(f"✓ Original:  photo.jpg")
        print(f"✓ Unique:    {media.stage_path.name}")

        return True


def test_move_to_staging_with_subdirectory():
    """Test that move_to_staging handles files from subdirectories."""
    print("\n" + "=" * 70)
    print("Testing move_to_staging() - Files from Subdirectories")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create nested directory structure
        subdir = tmppath / "Photos" / "2025" / "January"
        subdir.mkdir(parents=True)

        # Create source file deep in hierarchy
        source_file = subdir / "vacation.jpg"
        source_file.write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")

        # Create staging directory
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_dir.mkdir()

        # Create MediaFile object
        media = MediaFile(
            source=source_file,
            kind="image",
            extension=".jpg",
            format_name="JPEG",
            stage_path=None,
            compatible=True,
            rule_id="R-IMG-001",
            action="import",
            requires_processing=False,
        )

        # Call ACTUAL function
        move_to_staging([media], staging_dir)

        # Verify ACTUAL behavior
        assert media.stage_path.exists(), "Staged file should exist"
        assert media.stage_path.parent == staging_dir, "File should be directly in staging directory (flattened)"
        assert not source_file.exists(), "Source file should be moved"

        print(f"✓ Source:  {source_file.relative_to(tmppath)}")
        print(f"✓ Staged:  {media.stage_path.relative_to(tmppath)}")
        print("✓ Directory structure flattened")

        return True


def test_move_to_staging_preserves_content():
    """Test that move_to_staging preserves file content."""
    print("\n" + "=" * 70)
    print("Testing move_to_staging() - Preserves File Content")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create source file with specific content
        source_file = tmppath / "test.jpg"
        test_content = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00UNIQUE_CONTENT_12345"
        source_file.write_bytes(test_content)

        # Create staging directory
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_dir.mkdir()

        # Create MediaFile object
        media = MediaFile(
            source=source_file,
            kind="image",
            extension=".jpg",
            format_name="JPEG",
            stage_path=None,
            compatible=True,
            rule_id="R-IMG-001",
            action="import",
            requires_processing=False,
        )

        # Call ACTUAL function
        move_to_staging([media], staging_dir)

        # Verify ACTUAL behavior
        staged_content = media.stage_path.read_bytes()
        assert staged_content == test_content, "File content should be preserved"

        print(f"✓ Content preserved ({len(test_content)} bytes)")
        print(f"✓ Staged at: {media.stage_path.name}")

        return True


def test_move_to_staging_updates_media_object():
    """Test that move_to_staging updates MediaFile.stage_path."""
    print("\n" + "=" * 70)
    print("Testing move_to_staging() - Updates MediaFile Object")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create source file
        source_file = tmppath / "photo.jpg"
        source_file.write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")

        # Create staging directory
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_dir.mkdir()

        # Create MediaFile object
        media = MediaFile(
            source=source_file,
            kind="image",
            extension=".jpg",
            format_name="JPEG",
            stage_path=None,  # Initially None
            compatible=True,
            rule_id="R-IMG-001",
            action="import",
            requires_processing=False,
        )

        # Verify initial state
        assert media.stage_path is None, "stage_path should initially be None"

        # Call ACTUAL function (modifies media object in-place)
        move_to_staging([media], staging_dir)

        # Verify ACTUAL behavior - media object modified in-place
        assert media.stage_path is not None, "MediaFile should have stage_path set"
        assert isinstance(media.stage_path, Path), "stage_path should be a Path object"
        assert media.stage_path.exists(), "stage_path should point to existing file"
        assert media.source == source_file, "source should remain unchanged"

        print(f"✓ MediaFile.stage_path updated: {media.stage_path.name}")
        print(f"✓ MediaFile.source unchanged: {media.source.name}")

        return True


def main():
    print("=" * 70)
    print("move_to_staging() Behavior Tests")
    print("=" * 70)

    results = []

    # Run all tests
    try:
        results.append(("Preserves safe filename", test_move_to_staging_preserves_filename()))
    except Exception as e:
        print(f"\n✗ Preserve filename test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Preserves safe filename", False))

    try:
        results.append(("Creates staging directory", test_move_to_staging_creates_staging_directory()))
    except Exception as e:
        print(f"\n✗ Create directory test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Creates staging directory", False))

    try:
        results.append(("Moves file (not copy)", test_move_to_staging_moves_file()))
    except Exception as e:
        print(f"\n✗ Move file test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Moves file (not copy)", False))

    try:
        results.append(("Handles name collision", test_move_to_staging_handles_name_collision()))
    except Exception as e:
        print(f"\n✗ Name collision test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Handles name collision", False))

    try:
        results.append(("Files from subdirectories", test_move_to_staging_with_subdirectory()))
    except Exception as e:
        print(f"\n✗ Subdirectory test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Files from subdirectories", False))

    try:
        results.append(("Preserves file content", test_move_to_staging_preserves_content()))
    except Exception as e:
        print(f"\n✗ Content preservation test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Preserves file content", False))

    try:
        results.append(("Updates MediaFile object", test_move_to_staging_updates_media_object()))
    except Exception as e:
        print(f"\n✗ MediaFile update test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Updates MediaFile object", False))

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
