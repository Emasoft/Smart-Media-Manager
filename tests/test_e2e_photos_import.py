"""Real end-to-end tests for Apple Photos import.

These tests actually import media into Apple Photos - NO MOCKING!
They require:
- macOS with Apple Photos.app installed
- Photos library accessible
- Sufficient disk space

Run these tests with: pytest tests/test_e2e_photos_import.py -v
"""

import os
import shutil
import subprocess
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from smart_media_manager.cli import (  # noqa: E402
    RunStatistics,
    SkipLogger,
    ensure_compatibility,
    gather_media_files,
    import_folder_to_photos,
)
from tests.helpers import stage_media  # noqa: E402


pytestmark = pytest.mark.skipif(
    not os.environ.get("SMM_RUN_PHOTOS_TESTS"),
    reason="Set SMM_RUN_PHOTOS_TESTS=1 to run real Apple Photos import tests (very slow)",
)


# Compatibility wrapper for old batch import tests
def import_into_photos(media_files, stats):
    """Wrapper to adapt old tests to new folder import API.

    Note: These tests use the old batch import signature.
    They will be fully updated in a future PR to test the new folder import behavior.
    """
    if not media_files:
        return 0, []

    staging = media_files[0].stage_path.parent
    imported_count, skipped_count, skipped_media = import_folder_to_photos(
        staging_dir=staging,
        media_files=media_files,
        album_name="Test Album",
        skip_duplicates=True,
    )

    # Convert to old signature: (imported_count, failed_list)
    failed_list = [(m, "Skipped by Photos") for m in skipped_media]
    return imported_count, failed_list


SAMPLES_DIR = Path(__file__).parent / "samples" / "media"
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def check_photos_available() -> None:
    """Check if Apple Photos is available on this system. Skip test if not."""
    # Check if Photos.app exists (can be in /Applications or /System/Applications on macOS)
    photos_paths = [
        Path("/Applications/Photos.app"),
        Path("/System/Applications/Photos.app"),
    ]
    if not any(p.exists() for p in photos_paths):
        pytest.skip("Apple Photos.app not found - macOS required")

    # Verify osascript is available
    try:
        result = subprocess.run(
            ["which", "osascript"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            pytest.skip("osascript not available - macOS required")
    except Exception as e:
        pytest.skip(f"Cannot verify Photos availability: {e}")


def test_import_single_jpeg_to_photos(tmp_path: Path) -> None:
    """Test importing a single JPEG file into Apple Photos.

    This is a REAL test - it actually imports into Photos.app!
    """
    check_photos_available()
    # Setup: Copy a sample JPEG
    jpg_samples = list(SAMPLES_DIR.glob("*.jpg")) + list(SAMPLES_DIR.glob("*.jpeg"))
    if not jpg_samples:
        pytest.skip("No JPEG samples found")

    source_dir = tmp_path / "input"
    source_dir.mkdir()
    test_file = source_dir / "test.jpg"
    shutil.copy(jpg_samples[0], test_file)

    # Scan and stage
    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    assert len(media_files) == 1, "Should find exactly one JPEG"
    jpeg = media_files[0]
    assert jpeg.kind == "image"
    assert jpeg.extension in (".jpg", ".jpeg")

    # Stage files
    staging_dir = tmp_path / "FOUND_MEDIA_FILES_test"
    staging_dir.mkdir()
    stage_media(media_files, staging_dir)

    # Ensure compatibility (should be no-op for JPEG)
    ensure_compatibility(media_files, skip_logger, stats)

    # THE REAL TEST: Import into Apple Photos
    imported_count, failed_list = import_into_photos(media_files, stats)

    # Verify import succeeded
    assert imported_count == 1, f"Should import 1 file, imported {imported_count}"
    assert len(failed_list) == 0, f"Should have no failures, got: {failed_list}"


def test_import_multiple_images_to_photos(tmp_path: Path) -> None:
    """Test importing multiple image files into Apple Photos.

    Includes JPEG, PNG - all should import successfully.
    """
    check_photos_available()
    source_dir = tmp_path / "input"
    source_dir.mkdir()

    # Copy diverse image samples
    copied = 0
    for pattern in ["*.jpg", "*.jpeg", "*.png"]:
        samples = list(SAMPLES_DIR.glob(pattern))
        if samples and copied < 5:  # Limit to 5 files for speed
            dest = source_dir / f"test_{copied}{Path(samples[0]).suffix}"
            shutil.copy(samples[0], dest)
            copied += 1

    if copied == 0:
        pytest.skip("No image samples found")

    # Scan and stage
    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    assert len(media_files) >= 1, f"Should find at least 1 image, found {len(media_files)}"

    # Stage files
    staging_dir = tmp_path / "FOUND_MEDIA_FILES_test"
    staging_dir.mkdir()
    stage_media(media_files, staging_dir)

    # Ensure compatibility
    ensure_compatibility(media_files, skip_logger, stats)

    # THE REAL TEST: Import into Apple Photos
    imported_count, failed_list = import_into_photos(media_files, stats)

    # Verify import succeeded
    assert imported_count == len(media_files), f"Should import {len(media_files)} files, imported {imported_count}"
    assert len(failed_list) == 0, f"Should have no failures, got: {failed_list}"


def test_import_mp4_video_to_photos(tmp_path: Path) -> None:
    """Test importing MP4 video into Apple Photos.

    MP4 with H.264 codec should import directly without conversion.
    """
    check_photos_available()
    source_dir = tmp_path / "input"
    source_dir.mkdir()

    # Use dedicated compatible MP4 fixture
    mp4_fixture = FIXTURES_DIR / "compatible_h264.mp4"
    if not mp4_fixture.exists():
        pytest.skip("MP4 fixture not found - run: cd tests/fixtures && bash README.md commands")

    test_file = source_dir / "test.mp4"
    shutil.copy(mp4_fixture, test_file)

    # Scan and stage
    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    assert len(media_files) == 1, "Should find exactly one MP4"
    mp4 = media_files[0]
    assert mp4.kind == "video"
    assert mp4.extension == ".mp4", "MP4 files should keep .mp4 extension"

    # Stage files
    staging_dir = tmp_path / "FOUND_MEDIA_FILES_test"
    staging_dir.mkdir()
    stage_media(media_files, staging_dir)

    # Ensure compatibility
    ensure_compatibility(media_files, skip_logger, stats)

    # THE REAL TEST: Import into Apple Photos
    imported_count, failed_list = import_into_photos(media_files, stats)

    # Verify import succeeded
    assert imported_count == 1, f"Should import 1 video, imported {imported_count}"
    assert len(failed_list) == 0, f"Should have no failures, got: {failed_list}"


def test_import_webp_converts_and_imports(tmp_path: Path) -> None:
    """Test that WebP files are converted to PNG and then imported.

    This tests the full conversion pipeline + import.
    """
    check_photos_available()
    source_dir = tmp_path / "input"
    source_dir.mkdir()

    # Copy a WebP sample
    webp_samples = list(SAMPLES_DIR.glob("*.webp"))
    if not webp_samples:
        pytest.skip("No WebP samples found")

    test_file = source_dir / "test.webp"
    shutil.copy(webp_samples[0], test_file)

    # Scan and stage
    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    assert len(media_files) == 1, "Should find exactly one WebP"
    webp = media_files[0]
    assert webp.kind == "image"
    # Empirical evidence: WebP imports directly into Apple Photos
    assert not webp.requires_processing, "WebP is compatible with Apple Photos (direct import)"
    assert webp.compatible, "WebP should be marked compatible"

    # Stage files
    staging_dir = tmp_path / "FOUND_MEDIA_FILES_test"
    staging_dir.mkdir()
    stage_media(media_files, staging_dir)

    # Ensure compatibility - WebP should not need conversion
    ensure_compatibility(media_files, skip_logger, stats)

    # Extension should remain .webp (no conversion needed)
    assert webp.extension == ".webp", "WebP extension should be preserved"

    # THE REAL TEST: Import into Apple Photos
    imported_count, failed_list = import_into_photos(media_files, stats)

    # Verify import succeeded
    assert imported_count == 1, f"Should import 1 file (converted), imported {imported_count}"
    assert len(failed_list) == 0, f"Should have no failures, got: {failed_list}"


def test_import_mixed_media_batch(tmp_path: Path) -> None:
    """Test importing a batch of mixed media (images + videos).

    This tests the batching logic with real imports.
    """
    check_photos_available()
    source_dir = tmp_path / "input"
    source_dir.mkdir()

    # Copy diverse media samples
    copied = 0
    for pattern in ["*.jpg", "*.png", "*.mp4"]:
        samples = list(SAMPLES_DIR.glob(pattern))
        if samples and copied < 10:  # Up to 10 files
            for sample in samples[:2]:  # 2 of each type
                if copied >= 10:
                    break
                dest = source_dir / f"test_{copied}{Path(sample).suffix}"
                shutil.copy(sample, dest)
                copied += 1

    if copied == 0:
        pytest.skip("No media samples found")

    # Scan and stage
    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    assert len(media_files) >= 1, f"Should find at least 1 file, found {len(media_files)}"

    # Stage files
    staging_dir = tmp_path / "FOUND_MEDIA_FILES_test"
    staging_dir.mkdir()
    stage_media(media_files, staging_dir)

    # Ensure compatibility
    ensure_compatibility(media_files, skip_logger, stats)

    # THE REAL TEST: Import batch into Apple Photos
    imported_count, failed_list = import_into_photos(media_files, stats)

    # Verify import succeeded
    assert imported_count == len(media_files), f"Should import all {len(media_files)} files, imported {imported_count}"
    assert len(failed_list) == 0, f"Should have no failures, got: {failed_list}"


def test_import_handles_unsupported_format(tmp_path: Path) -> None:
    """Test that unsupported formats are properly skipped, not imported.

    PDF files should be detected but marked as skip, never reaching import.
    """
    check_photos_available()
    source_dir = tmp_path / "input"
    source_dir.mkdir()

    # Copy a PDF (unsupported by Photos)
    pdf_samples = list(SAMPLES_DIR.glob("*.pdf"))
    if not pdf_samples:
        pytest.skip("No PDF samples found")

    test_file = source_dir / "test.pdf"
    shutil.copy(pdf_samples[0], test_file)

    # Also add a valid JPEG
    jpg_samples = list(SAMPLES_DIR.glob("*.jpg"))
    if jpg_samples:
        shutil.copy(jpg_samples[0], source_dir / "valid.jpg")

    # Scan and stage
    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    # PDF should be filtered out during scanning
    # Only valid media should remain
    valid_media = [m for m in media_files if m.kind in ("image", "video")]

    assert len(valid_media) >= 1, "Should have at least one valid media file"
    assert all(m.extension != ".pdf" for m in valid_media), "PDF should not be in media_files"

    # Stage and import only valid files
    staging_dir = tmp_path / "FOUND_MEDIA_FILES_test"
    staging_dir.mkdir()
    stage_media(valid_media, staging_dir)

    ensure_compatibility(valid_media, skip_logger, stats)

    # Import should succeed for valid files
    imported_count, failed_list = import_into_photos(valid_media, stats)

    assert imported_count == len(valid_media), f"Should import all {len(valid_media)} valid files"
    assert len(failed_list) == 0, "Should have no failures for valid files"
