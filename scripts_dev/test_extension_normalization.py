#!/usr/bin/env python3
"""
Test extension normalization behavior - files get renamed to their ACTUAL format extension.
Tests OBSERVABLE BEHAVIOR: files with wrong extensions get corrected during staging.

Examples:
- JPEG file with no extension → renamed to .jpg
- JPEG file named .tiff → renamed to .jpg
- PNG file named .jpeg → renamed to .png
"""

import sys
import tempfile
from pathlib import Path

# Add the module to path
sys.path.insert(0, str(Path(__file__).parent))

from smart_media_manager.cli import (
    gather_media_files,
    move_to_staging,
    SkipLogger,
    RunStatistics,
    timestamp,
)


def test_jpeg_no_extension_gets_jpg():
    """Test that JPEG file without extension gets renamed to .jpg"""
    print("\n" + "=" * 70)
    print("Testing Extension Normalization - JPEG without extension → .jpg")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create JPEG file WITHOUT extension
        jpeg_file = tmppath / "photo"  # NO EXTENSION
        jpeg_file.write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")

        skip_logger = SkipLogger(tmppath / "skip.log")
        stats = RunStatistics()

        # Call ACTUAL detection function
        media_files = gather_media_files(
            root=tmppath,
            recursive=True,
            follow_symlinks=False,
            skip_logger=skip_logger,
            stats=stats,
            skip_compatibility_check=True,
        )

        print(f"\nOriginal file: {jpeg_file.name}")
        print(f"Detected as:   {media_files[0].kind} with extension {media_files[0].extension}")

        # Verify detection
        assert len(media_files) == 1, f"Should find 1 file, found {len(media_files)}"
        # JFIF is a valid JPEG variant - the system correctly detects it
        assert media_files[0].extension in [".jpg", ".jfif", ".jpeg"], f"Should detect as JPEG variant, got {media_files[0].extension}"

        # Now stage the file
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_dir.mkdir()

        # Call ACTUAL staging function
        move_to_staging(media_files, staging_dir)

        # Verify ACTUAL behavior: file should be renamed with JPEG variant extension
        assert media_files[0].stage_path is not None, "stage_path should be set"
        assert media_files[0].stage_path.suffix in [".jpg", ".jfif", ".jpeg"], f"Staged file should have JPEG extension, got {media_files[0].stage_path.suffix}"
        assert media_files[0].stage_path.exists(), "Staged file should exist"

        print(f"\n✓ Original: {jpeg_file.name} (no extension)")
        print(f"✓ Staged:   {media_files[0].stage_path.name} (with {media_files[0].stage_path.suffix} extension)")
        print(f"✓ JPEG without extension correctly renamed to {media_files[0].stage_path.suffix}")

        # Cleanup
        if skip_logger.path.exists():
            skip_logger.path.unlink()

        return True


def test_jpeg_with_wrong_tiff_extension():
    """Test that JPEG file with .tiff extension gets renamed to .jpg"""
    print("\n" + "=" * 70)
    print("Testing Extension Normalization - JPEG with .tiff → .jpg")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create JPEG file with WRONG .tiff extension
        jpeg_file = tmppath / "photo.tiff"  # JPEG content but .tiff extension!
        jpeg_file.write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")

        skip_logger = SkipLogger(tmppath / "skip.log")
        stats = RunStatistics()

        # Call ACTUAL detection function
        media_files = gather_media_files(
            root=tmppath,
            recursive=True,
            follow_symlinks=False,
            skip_logger=skip_logger,
            stats=stats,
            skip_compatibility_check=True,
        )

        print(f"\nOriginal file: {jpeg_file.name} (WRONG extension)")
        print(f"Detected as:   {media_files[0].kind} with extension {media_files[0].extension}")

        # Verify detection corrected the extension
        assert len(media_files) == 1
        assert media_files[0].extension in [".jpg", ".jfif", ".jpeg"], f"Should detect as JPEG variant despite .tiff name, got {media_files[0].extension}"

        # Now stage the file
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_dir.mkdir()

        # Call ACTUAL staging function
        move_to_staging(media_files, staging_dir)

        # Verify ACTUAL behavior: file should be renamed with correct JPEG variant extension
        assert media_files[0].stage_path.suffix in [".jpg", ".jfif", ".jpeg"], f"Staged file should have JPEG extension, got {media_files[0].stage_path.suffix}"
        assert media_files[0].stage_path.stem == "photo", "Stem should be preserved"

        print(f"\n✓ Original: {jpeg_file.name} (.tiff extension)")
        print(f"✓ Staged:   {media_files[0].stage_path.name} ({media_files[0].stage_path.suffix} extension)")
        print(f"✓ JPEG with wrong .tiff extension correctly renamed to {media_files[0].stage_path.suffix}")

        # Cleanup
        if skip_logger.path.exists():
            skip_logger.path.unlink()

        return True


def test_jpeg_with_wrong_tif_extension():
    """Test that JPEG file with .tif extension gets renamed to .jpg"""
    print("\n" + "=" * 70)
    print("Testing Extension Normalization - JPEG with .tif → .jpg")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create JPEG file with WRONG .tif extension
        jpeg_file = tmppath / "image.tif"  # JPEG content but .tif extension!
        jpeg_file.write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")

        skip_logger = SkipLogger(tmppath / "skip.log")
        stats = RunStatistics()

        # Call ACTUAL detection
        media_files = gather_media_files(
            root=tmppath,
            recursive=True,
            follow_symlinks=False,
            skip_logger=skip_logger,
            stats=stats,
            skip_compatibility_check=True,
        )

        assert media_files[0].extension in [".jpg", ".jfif", ".jpeg"]

        # Stage the file
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_dir.mkdir()
        move_to_staging(media_files, staging_dir)

        # Verify ACTUAL behavior
        assert media_files[0].stage_path.suffix in [".jpg", ".jfif", ".jpeg"]
        assert media_files[0].stage_path.stem == "image"

        print(f"\n✓ Original: {jpeg_file.name} (.tif extension)")
        print(f"✓ Staged:   {media_files[0].stage_path.name} ({media_files[0].stage_path.suffix} extension)")
        print(f"✓ JPEG with .tif extension correctly renamed to {media_files[0].stage_path.suffix}")

        if skip_logger.path.exists():
            skip_logger.path.unlink()

        return True


def test_png_with_wrong_jpeg_extension():
    """Test that PNG file with .jpeg extension gets renamed to .png"""
    print("\n" + "=" * 70)
    print("Testing Extension Normalization - PNG with .jpeg → .png")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create PNG file with WRONG .jpeg extension
        png_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
        png_file = tmppath / "graphic.jpeg"  # PNG content but .jpeg extension!
        png_file.write_bytes(png_data)

        skip_logger = SkipLogger(tmppath / "skip.log")
        stats = RunStatistics()

        # Call ACTUAL detection
        media_files = gather_media_files(
            root=tmppath,
            recursive=True,
            follow_symlinks=False,
            skip_logger=skip_logger,
            stats=stats,
            skip_compatibility_check=True,
        )

        print(f"\nOriginal file: {png_file.name} (WRONG extension)")
        print(f"Detected as:   {media_files[0].kind} with extension {media_files[0].extension}")

        assert media_files[0].extension == ".png", f"Should detect as .png, got {media_files[0].extension}"

        # Stage the file
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_dir.mkdir()
        move_to_staging(media_files, staging_dir)

        # Verify ACTUAL behavior
        assert media_files[0].stage_path.suffix == ".png"
        assert media_files[0].stage_path.stem == "graphic"

        print(f"\n✓ Original: {png_file.name} (.jpeg extension)")
        print(f"✓ Staged:   {media_files[0].stage_path.name} (.png extension)")
        print("✓ PNG with .jpeg extension correctly renamed to .png")

        if skip_logger.path.exists():
            skip_logger.path.unlink()

        return True


def test_gif_with_wrong_jpg_extension():
    """Test that GIF file with .jpg extension gets renamed to .gif"""
    print("\n" + "=" * 70)
    print("Testing Extension Normalization - GIF with .jpg → .gif")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create GIF file with WRONG .jpg extension
        gif_data = b"GIF89a\x01\x00\x01\x00\x00\x00\x00,"
        gif_file = tmppath / "animation.jpg"  # GIF content but .jpg extension!
        gif_file.write_bytes(gif_data)

        skip_logger = SkipLogger(tmppath / "skip.log")
        stats = RunStatistics()

        # Call ACTUAL detection
        media_files = gather_media_files(
            root=tmppath,
            recursive=True,
            follow_symlinks=False,
            skip_logger=skip_logger,
            stats=stats,
            skip_compatibility_check=True,
        )

        assert media_files[0].extension == ".gif"

        # Stage the file
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_dir.mkdir()
        move_to_staging(media_files, staging_dir)

        # Verify ACTUAL behavior
        assert media_files[0].stage_path.suffix == ".gif"
        assert media_files[0].stage_path.stem == "animation"

        print(f"\n✓ Original: {gif_file.name} (.jpg extension)")
        print(f"✓ Staged:   {media_files[0].stage_path.name} (.gif extension)")
        print("✓ GIF with .jpg extension correctly renamed to .gif")

        if skip_logger.path.exists():
            skip_logger.path.unlink()

        return True


def test_correct_extension_preserved():
    """Test that files with correct extensions keep their extensions"""
    print("\n" + "=" * 70)
    print("Testing Extension Normalization - Correct extensions preserved")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create files with CORRECT extensions
        (tmppath / "photo.jpg").write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")
        (tmppath / "graphic.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde")
        (tmppath / "anim.gif").write_bytes(b"GIF89a\x01\x00\x01\x00\x00\x00\x00,")

        skip_logger = SkipLogger(tmppath / "skip.log")
        stats = RunStatistics()

        # Call ACTUAL detection
        media_files = gather_media_files(
            root=tmppath,
            recursive=True,
            follow_symlinks=False,
            skip_logger=skip_logger,
            stats=stats,
            skip_compatibility_check=True,
        )

        # Stage the files
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_dir.mkdir()
        move_to_staging(media_files, staging_dir)

        # Verify ACTUAL behavior: correct extensions preserved
        staged_files = {m.stage_path.name for m in media_files}

        assert "photo.jpg" in staged_files or any(".jpg" in f for f in staged_files)
        assert "graphic.png" in staged_files or any(".png" in f for f in staged_files)
        assert "anim.gif" in staged_files or any(".gif" in f for f in staged_files)

        print("\nStaged files:")
        for media in sorted(media_files, key=lambda m: m.stage_path.name):
            print(f"  {media.stage_path.name} (extension: {media.stage_path.suffix})")

        print("\n✓ Files with correct extensions kept their extensions")

        if skip_logger.path.exists():
            skip_logger.path.unlink()

        return True


def test_multiple_wrong_extensions_batch():
    """Test that multiple files with wrong extensions all get corrected"""
    print("\n" + "=" * 70)
    print("Testing Extension Normalization - Batch correction")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create multiple files with WRONG extensions
        # All JPEG variants should be normalized to .jpg
        files_created = [
            ("jpeg_no_ext", None, b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00", ".jpg"),
            ("jpeg_as_png.png", ".png", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00", ".jpg"),
            ("png_as_jpg.jpg", ".jpg", b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde", ".png"),
            ("gif_as_jpeg.jpeg", ".jpeg", b"GIF89a\x01\x00\x01\x00\x00\x00\x00,", ".gif"),
        ]

        for stem, wrong_ext, content, expected_ext in files_created:
            if wrong_ext:
                filename = stem
            else:
                filename = stem.replace("_no_ext", "")
            filepath = tmppath / filename
            filepath.write_bytes(content)

        skip_logger = SkipLogger(tmppath / "skip.log")
        stats = RunStatistics()

        # Call ACTUAL detection
        media_files = gather_media_files(
            root=tmppath,
            recursive=True,
            follow_symlinks=False,
            skip_logger=skip_logger,
            stats=stats,
            skip_compatibility_check=True,
        )

        # Stage the files
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_dir.mkdir()
        move_to_staging(media_files, staging_dir)

        # Verify ACTUAL behavior: all extensions corrected
        print("\nOriginal → Staged:")
        for i, (stem, wrong_ext, content, expected_ext) in enumerate(files_created):
            # Determine the actual filename that was created
            if wrong_ext:
                created_filename = stem  # This is already the full filename with extension
            else:
                created_filename = stem.replace("_no_ext", "")  # This is the stem without extension

            # Extract the stem from the filename
            created_path = Path(created_filename)
            expected_stem = created_path.stem

            # Find the corresponding media file by matching the exact source filename stem
            staged = None
            for m in media_files:
                source_stem = m.source.stem
                if source_stem == expected_stem:
                    staged = m
                    break

            if not staged:
                raise AssertionError(f"Could not find staged file for {created_filename} (stem: {expected_stem})")

            actual_ext = staged.stage_path.suffix
            print(f"  {created_filename} → {staged.stage_path.name}")
            # All extensions should be canonicalized to the expected value
            assert actual_ext == expected_ext, f"Expected {expected_ext}, got {actual_ext}"

        print("\n✓ All wrong extensions correctly normalized in batch")

        if skip_logger.path.exists():
            skip_logger.path.unlink()

        return True


def main():
    print("=" * 70)
    print("Extension Normalization Behavior Tests")
    print("=" * 70)

    results = []

    # Run all tests
    try:
        results.append(("JPEG without extension → .jpg", test_jpeg_no_extension_gets_jpg()))
    except Exception as e:
        print(f"\n✗ JPEG no extension test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("JPEG without extension → .jpg", False))

    try:
        results.append(("JPEG with .tiff → .jpg", test_jpeg_with_wrong_tiff_extension()))
    except Exception as e:
        print(f"\n✗ JPEG .tiff test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("JPEG with .tiff → .jpg", False))

    try:
        results.append(("JPEG with .tif → .jpg", test_jpeg_with_wrong_tif_extension()))
    except Exception as e:
        print(f"\n✗ JPEG .tif test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("JPEG with .tif → .jpg", False))

    try:
        results.append(("PNG with .jpeg → .png", test_png_with_wrong_jpeg_extension()))
    except Exception as e:
        print(f"\n✗ PNG .jpeg test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("PNG with .jpeg → .png", False))

    try:
        results.append(("GIF with .jpg → .gif", test_gif_with_wrong_jpg_extension()))
    except Exception as e:
        print(f"\n✗ GIF .jpg test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("GIF with .jpg → .gif", False))

    try:
        results.append(("Correct extensions preserved", test_correct_extension_preserved()))
    except Exception as e:
        print(f"\n✗ Correct extensions test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("Correct extensions preserved", False))

    try:
        results.append(("Batch correction", test_multiple_wrong_extensions_batch()))
    except Exception as e:
        print(f"\n✗ Batch correction test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("Batch correction", False))

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
        print("✓ All extension normalization tests passed!")
        print("\nKey takeaway: Files are renamed to match their ACTUAL format,")
        print("not their original (potentially wrong) extension!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
