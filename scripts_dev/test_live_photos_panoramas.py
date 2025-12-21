#!/usr/bin/env python3
"""
Test Live Photo pairing and Panoramic photo detection.
Tests OBSERVABLE BEHAVIOR, not duplicated implementation logic.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the module to path
sys.path.insert(0, str(Path(__file__).parent))

from smart_media_manager.cli import (
    extract_live_photo_content_id,
    is_panoramic_photo,
    detect_live_photo_pairs,
    gather_media_files,
    move_to_staging,
    MediaFile,
    SkipLogger,
    RunStatistics,
    timestamp,
)


def test_extract_live_photo_content_id_success():
    """Test that extract_live_photo_content_id extracts content identifier."""
    print("\n" + "=" * 70)
    print("Testing extract_live_photo_content_id() - Success")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create a mock HEIC file
        heic_file = tmppath / "IMG_1234.HEIC"
        heic_file.write_bytes(b"\x00\x00\x00\x18ftypheic")

        # Mock exiftool response
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "ABC123-DEF456-GHI789\n"

        with patch("subprocess.run", return_value=mock_result):
            content_id = extract_live_photo_content_id(heic_file)

        assert content_id == "ABC123-DEF456-GHI789", f"Expected content ID, got {content_id}"
        print(f"✓ Extracted content ID: {content_id}")

        return True


def test_extract_live_photo_content_id_no_metadata():
    """Test that extract_live_photo_content_id returns None when no metadata found."""
    print("\n" + "=" * 70)
    print("Testing extract_live_photo_content_id() - No Metadata")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create a mock HEIC file
        heic_file = tmppath / "IMG_1234.HEIC"
        heic_file.write_bytes(b"\x00\x00\x00\x18ftypheic")

        # Mock exiftool response (no content ID)
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "\n"

        with patch("subprocess.run", return_value=mock_result):
            content_id = extract_live_photo_content_id(heic_file)

        assert content_id is None, f"Expected None, got {content_id}"
        print("✓ No content ID extracted (as expected)")

        return True


def test_is_panoramic_photo_success():
    """Test that is_panoramic_photo detects panoramic metadata."""
    print("\n" + "=" * 70)
    print("Testing is_panoramic_photo() - Success")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create a mock HEIC file
        heic_file = tmppath / "PANO_1234.HEIC"
        heic_file.write_bytes(b"\x00\x00\x00\x18ftypheic")

        # Mock exiftool response with panoramic metadata
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "equirectangular\n"

        with patch("subprocess.run", return_value=mock_result):
            is_pano = is_panoramic_photo(heic_file)

        assert is_pano is True, f"Expected True, got {is_pano}"
        print("✓ Detected panoramic photo")

        return True


def test_is_panoramic_photo_not_panoramic():
    """Test that is_panoramic_photo returns False for non-panoramic photos."""
    print("\n" + "=" * 70)
    print("Testing is_panoramic_photo() - Not Panoramic")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create a mock HEIC file
        heic_file = tmppath / "IMG_1234.HEIC"
        heic_file.write_bytes(b"\x00\x00\x00\x18ftypheic")

        # Mock exiftool response (no panoramic metadata)
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "\n"

        with patch("subprocess.run", return_value=mock_result):
            is_pano = is_panoramic_photo(heic_file)

        assert is_pano is False, f"Expected False, got {is_pano}"
        print("✓ Not a panoramic photo (as expected)")

        return True


def test_detect_live_photo_pairs_success():
    """Test that detect_live_photo_pairs correctly identifies and pairs Live Photos."""
    print("\n" + "=" * 70)
    print("Testing detect_live_photo_pairs() - Success")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create Live Photo files
        heic_file = tmppath / "IMG_1234.HEIC"
        heic_file.write_bytes(b"\x00\x00\x00\x18ftypheic")

        mov_file = tmppath / "IMG_1234.MOV"
        mov_file.write_bytes(b"\x00\x00\x00\x14ftypqt  ")

        # Create MediaFile objects
        heic_media = MediaFile(
            source=heic_file,
            kind="image",
            extension=".heic",
            format_name="HEIC",
            stage_path=None,
            compatible=True,
            rule_id="R-IMG-003",
            action="import",
            requires_processing=False,
        )

        mov_media = MediaFile(
            source=mov_file,
            kind="video",
            extension=".mov",
            format_name="QuickTime",
            stage_path=None,
            compatible=True,
            rule_id="R-VID-001",
            action="import",
            requires_processing=False,
        )

        media_files = [heic_media, mov_media]

        # Mock exiftool to return matching content IDs
        def mock_extract_content_id(path):
            return "ABC123-DEF456-GHI789"

        with patch("smart_media_manager.cli.extract_live_photo_content_id", side_effect=mock_extract_content_id):
            pairs = detect_live_photo_pairs(media_files)

        assert len(pairs) == 1, f"Expected 1 Live Photo pair, got {len(pairs)}"
        assert "ABC123-DEF456-GHI789" in pairs, "Expected content ID in pairs"

        # Verify metadata was added
        assert heic_media.metadata.get("is_live_photo") is True, "HEIC should be marked as Live Photo"
        assert mov_media.metadata.get("is_live_photo") is True, "MOV should be marked as Live Photo"
        assert heic_media.metadata.get("live_photo_content_id") == "ABC123-DEF456-GHI789"
        assert mov_media.metadata.get("live_photo_content_id") == "ABC123-DEF456-GHI789"

        print("✓ Detected 1 Live Photo pair")
        print("✓ Content ID: ABC123-DEF456-GHI789")
        print(f"✓ Pair: {heic_file.name} + {mov_file.name}")

        return True


def test_detect_live_photo_pairs_no_pairs():
    """Test that detect_live_photo_pairs returns empty dict when no pairs found."""
    print("\n" + "=" * 70)
    print("Testing detect_live_photo_pairs() - No Pairs")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create files with different stems (not a pair)
        heic_file = tmppath / "IMG_1234.HEIC"
        heic_file.write_bytes(b"\x00\x00\x00\x18ftypheic")

        mov_file = tmppath / "IMG_5678.MOV"
        mov_file.write_bytes(b"\x00\x00\x00\x14ftypqt  ")

        # Create MediaFile objects
        heic_media = MediaFile(
            source=heic_file,
            kind="image",
            extension=".heic",
            format_name="HEIC",
            stage_path=None,
            compatible=True,
            rule_id="R-IMG-003",
            action="import",
            requires_processing=False,
        )

        mov_media = MediaFile(
            source=mov_file,
            kind="video",
            extension=".mov",
            format_name="QuickTime",
            stage_path=None,
            compatible=True,
            rule_id="R-VID-001",
            action="import",
            requires_processing=False,
        )

        media_files = [heic_media, mov_media]

        pairs = detect_live_photo_pairs(media_files)

        assert len(pairs) == 0, f"Expected 0 pairs, got {len(pairs)}"
        print("✓ No Live Photo pairs detected (different stems)")

        return True


def test_move_to_staging_preserves_live_photo_pair_names():
    """Test that move_to_staging keeps Live Photo pairs with consistent naming."""
    print("\n" + "=" * 70)
    print("Testing move_to_staging() - Live Photo Pair Naming")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create Live Photo files
        heic_file = tmppath / "IMG_1234.HEIC"
        heic_file.write_bytes(b"\x00\x00\x00\x18ftypheic")

        mov_file = tmppath / "IMG_1234.MOV"
        mov_file.write_bytes(b"\x00\x00\x00\x14ftypqt  ")

        # Create staging directory
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_dir.mkdir()

        # Create MediaFile objects with Live Photo metadata
        heic_media = MediaFile(
            source=heic_file,
            kind="image",
            extension=".heic",
            format_name="HEIC",
            stage_path=None,
            compatible=True,
            rule_id="R-IMG-003",
            action="import",
            requires_processing=False,
        )
        heic_media.metadata["is_live_photo"] = True
        heic_media.metadata["live_photo_content_id"] = "ABC123"

        mov_media = MediaFile(
            source=mov_file,
            kind="video",
            extension=".mov",
            format_name="QuickTime",
            stage_path=None,
            compatible=True,
            rule_id="R-VID-001",
            action="import",
            requires_processing=False,
        )
        mov_media.metadata["is_live_photo"] = True
        mov_media.metadata["live_photo_content_id"] = "ABC123"

        # Move to staging
        move_to_staging([heic_media, mov_media], staging_dir)

        # Verify both files have consistent stem
        assert heic_media.stage_path is not None, "HEIC stage_path should be set"
        assert mov_media.stage_path is not None, "MOV stage_path should be set"

        heic_stem = heic_media.stage_path.stem
        mov_stem = mov_media.stage_path.stem

        assert heic_stem == mov_stem, f"Live Photo pair should have same stem: {heic_stem} != {mov_stem}"

        print(f"✓ HEIC staged: {heic_media.stage_path.name}")
        print(f"✓ MOV staged:  {mov_media.stage_path.name}")
        print(f"✓ Consistent stem: {heic_stem}")

        return True


def test_gather_media_files_detects_panoramic():
    """Test that gather_media_files detects and marks panoramic photos."""
    print("\n" + "=" * 70)
    print("Testing gather_media_files() - Panoramic Detection")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create a HEIC file
        heic_file = tmppath / "PANO_1234.HEIC"
        heic_file.write_bytes(b"\x00\x00\x00\x18ftypheic" + b"\x00" * 100)

        skip_logger = SkipLogger(tmppath / "skip.log")
        stats = RunStatistics()

        # Mock is_panoramic_photo to return True
        with patch("smart_media_manager.cli.is_panoramic_photo", return_value=True):
            # Mock detect_media to return a valid MediaFile
            mock_media = MediaFile(
                source=heic_file,
                kind="image",
                extension=".heic",
                format_name="HEIC",
                stage_path=None,
                compatible=True,
                rule_id="R-IMG-003",
                action="import",
                requires_processing=False,
            )

            with patch("smart_media_manager.cli.detect_media", return_value=(mock_media, None)):
                media_files = gather_media_files(
                    root=tmppath,
                    recursive=False,
                    follow_symlinks=False,
                    skip_logger=skip_logger,
                    stats=stats,
                    skip_compatibility_check=True,
                )

        assert len(media_files) == 1, f"Expected 1 media file, got {len(media_files)}"
        assert media_files[0].metadata.get("is_panoramic") is True, "Photo should be marked as panoramic"

        print(f"✓ Detected panoramic photo: {heic_file.name}")
        print("✓ Metadata: is_panoramic = True")

        return True


def test_gather_media_files_detects_live_photo_pairs():
    """Test that gather_media_files detects Live Photo pairs."""
    print("\n" + "=" * 70)
    print("Testing gather_media_files() - Live Photo Pair Detection")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create Live Photo files
        heic_file = tmppath / "IMG_1234.HEIC"
        heic_file.write_bytes(b"\x00\x00\x00\x18ftypheic" + b"\x00" * 100)

        mov_file = tmppath / "IMG_1234.MOV"
        mov_file.write_bytes(b"\x00\x00\x00\x14ftypqt  " + b"\x00" * 100)

        skip_logger = SkipLogger(tmppath / "skip.log")
        stats = RunStatistics()

        # Mock detect_media to return MediaFile objects
        def mock_detect_media(path, skip_check):
            if path.suffix.lower() == ".heic":
                return (
                    MediaFile(
                        source=path,
                        kind="image",
                        extension=".heic",
                        format_name="HEIC",
                        stage_path=None,
                        compatible=True,
                        rule_id="R-IMG-003",
                        action="import",
                        requires_processing=False,
                    ),
                    None,
                )
            elif path.suffix.lower() == ".mov":
                return (
                    MediaFile(
                        source=path,
                        kind="video",
                        extension=".mov",
                        format_name="QuickTime",
                        stage_path=None,
                        compatible=True,
                        rule_id="R-VID-001",
                        action="import",
                        requires_processing=False,
                    ),
                    None,
                )
            return None, "unknown format"

        # Mock extract_live_photo_content_id to return matching IDs
        def mock_extract_content_id(path):
            return "ABC123-DEF456-GHI789"

        with patch("smart_media_manager.cli.detect_media", side_effect=mock_detect_media):
            with patch("smart_media_manager.cli.extract_live_photo_content_id", side_effect=mock_extract_content_id):
                with patch("smart_media_manager.cli.is_panoramic_photo", return_value=False):
                    media_files = gather_media_files(
                        root=tmppath,
                        recursive=False,
                        follow_symlinks=False,
                        skip_logger=skip_logger,
                        stats=stats,
                        skip_compatibility_check=True,
                    )

        assert len(media_files) == 2, f"Expected 2 media files, got {len(media_files)}"

        # Find the HEIC and MOV files
        heic_media = next((m for m in media_files if m.extension == ".heic"), None)
        mov_media = next((m for m in media_files if m.extension == ".mov"), None)

        assert heic_media is not None, "HEIC file should be detected"
        assert mov_media is not None, "MOV file should be detected"

        # Verify Live Photo metadata
        assert heic_media.metadata.get("is_live_photo") is True, "HEIC should be marked as Live Photo"
        assert mov_media.metadata.get("is_live_photo") is True, "MOV should be marked as Live Photo"
        assert heic_media.metadata.get("live_photo_content_id") == mov_media.metadata.get("live_photo_content_id")

        print(f"✓ Detected Live Photo pair: {heic_file.name} + {mov_file.name}")
        print(f"✓ Content ID: {heic_media.metadata.get('live_photo_content_id')}")

        return True


def main():
    print("=" * 70)
    print("Live Photos and Panoramic Photos Tests")
    print("=" * 70)

    results = []

    # Run all tests
    try:
        results.append(("extract_live_photo_content_id - Success", test_extract_live_photo_content_id_success()))
    except Exception as e:
        print(f"\n✗ Content ID extraction test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("extract_live_photo_content_id - Success", False))

    try:
        results.append(("extract_live_photo_content_id - No Metadata", test_extract_live_photo_content_id_no_metadata()))
    except Exception as e:
        print(f"\n✗ No metadata test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("extract_live_photo_content_id - No Metadata", False))

    try:
        results.append(("is_panoramic_photo - Success", test_is_panoramic_photo_success()))
    except Exception as e:
        print(f"\n✗ Panoramic detection test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("is_panoramic_photo - Success", False))

    try:
        results.append(("is_panoramic_photo - Not Panoramic", test_is_panoramic_photo_not_panoramic()))
    except Exception as e:
        print(f"\n✗ Not panoramic test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("is_panoramic_photo - Not Panoramic", False))

    try:
        results.append(("detect_live_photo_pairs - Success", test_detect_live_photo_pairs_success()))
    except Exception as e:
        print(f"\n✗ Live Photo pairing test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("detect_live_photo_pairs - Success", False))

    try:
        results.append(("detect_live_photo_pairs - No Pairs", test_detect_live_photo_pairs_no_pairs()))
    except Exception as e:
        print(f"\n✗ No pairs test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("detect_live_photo_pairs - No Pairs", False))

    try:
        results.append(("move_to_staging - Live Photo Pair Naming", test_move_to_staging_preserves_live_photo_pair_names()))
    except Exception as e:
        print(f"\n✗ Live Photo staging test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("move_to_staging - Live Photo Pair Naming", False))

    try:
        results.append(("gather_media_files - Panoramic Detection", test_gather_media_files_detects_panoramic()))
    except Exception as e:
        print(f"\n✗ Panoramic gathering test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("gather_media_files - Panoramic Detection", False))

    try:
        results.append(("gather_media_files - Live Photo Pairs", test_gather_media_files_detects_live_photo_pairs()))
    except Exception as e:
        print(f"\n✗ Live Photo gathering test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("gather_media_files - Live Photo Pairs", False))

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
        print("✓ All Live Photo and Panoramic tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
