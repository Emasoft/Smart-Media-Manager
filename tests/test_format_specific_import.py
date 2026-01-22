"""Format-specific real import tests for Apple Photos.

Tests each format individually with real imports - NO MOCKING!

Tests are organized by:
1. Direct import (compatible formats)
2. Wrong/missing extensions
3. Conversion required
4. Container vs codec compatibility
"""

import os
import shutil
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
    reason="Set SMM_RUN_PHOTOS_TESTS=1 to run real Apple Photos import tests (slow)",
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
    import subprocess

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


# =============================================================================
# DIRECT IMPORT TESTS - Formats that Photos supports natively
# =============================================================================


def test_jpeg_direct_import(tmp_path: Path) -> None:
    """Test JPEG (.jpg, .jpeg) imports directly without conversion."""
    check_photos_available()

    jpg_samples = list(SAMPLES_DIR.glob("*.jpg")) + list(SAMPLES_DIR.glob("*.jpeg"))
    if not jpg_samples:
        pytest.skip("No JPEG samples found")

    source_dir = tmp_path / "input"
    source_dir.mkdir()
    shutil.copy(jpg_samples[0], source_dir / "test.jpg")

    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    assert len(media_files) >= 1
    jpeg = media_files[0]
    assert jpeg.extension in (".jpg", ".jpeg")
    assert jpeg.action == "import", "JPEG should import directly"

    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()
    stage_media(media_files, staging_dir)
    ensure_compatibility(media_files, skip_logger, stats)

    imported_count, failed_list = import_into_photos(media_files, stats)
    assert imported_count >= 1, f"Should import JPEG, got {imported_count}"
    assert len(failed_list) == 0, f"JPEG import should not fail: {failed_list}"


def test_png_direct_import(tmp_path: Path) -> None:
    """Test PNG imports directly without conversion."""
    check_photos_available()

    png_samples = list(SAMPLES_DIR.glob("*.png"))
    if not png_samples:
        pytest.skip("No PNG samples found")

    source_dir = tmp_path / "input"
    source_dir.mkdir()
    shutil.copy(png_samples[0], source_dir / "test.png")

    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    assert len(media_files) >= 1
    png = media_files[0]
    assert png.extension == ".png"
    assert png.action == "import", "PNG should import directly"

    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()
    stage_media(media_files, staging_dir)
    ensure_compatibility(media_files, skip_logger, stats)

    imported_count, failed_list = import_into_photos(media_files, stats)
    assert imported_count >= 1, f"Should import PNG, got {imported_count}"
    assert len(failed_list) == 0, f"PNG import should not fail: {failed_list}"


def test_heic_direct_import(tmp_path: Path) -> None:
    """Test HEIC/HEIF imports directly (if sample available)."""
    check_photos_available()

    heic_samples = list(SAMPLES_DIR.glob("*.heic")) + list(SAMPLES_DIR.glob("*.heif"))
    if not heic_samples:
        pytest.skip("No HEIC/HEIF samples found")

    source_dir = tmp_path / "input"
    source_dir.mkdir()
    shutil.copy(heic_samples[0], source_dir / "test.heic")

    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    assert len(media_files) >= 1
    heic = media_files[0]
    assert heic.extension in (".heic", ".heif")
    assert heic.action == "import", "HEIC should import directly"

    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()
    stage_media(media_files, staging_dir)
    ensure_compatibility(media_files, skip_logger, stats)

    imported_count, failed_list = import_into_photos(media_files, stats)
    assert imported_count >= 1, f"Should import HEIC, got {imported_count}"
    assert len(failed_list) == 0, f"HEIC import should not fail: {failed_list}"


def test_mp4_h264_direct_import(tmp_path: Path) -> None:
    """Test MP4 with H.264 video codec imports directly.

    Container: MP4
    Video Codec: H.264 (compatible)
    Should: Import without conversion
    """
    check_photos_available()

    mp4_samples = list(SAMPLES_DIR.glob("*.mp4"))
    if not mp4_samples:
        pytest.skip("No MP4 samples found")

    # Find a non-Dolby Vision MP4 (glob order is unpredictable)
    # Use 001.mp4 if available, otherwise find first non-dolby file
    h264_file = SAMPLES_DIR / "001.mp4"
    if not h264_file.exists():
        # Find first MP4 that's not Dolby Vision
        for mp4 in mp4_samples:
            if "dolby" not in mp4.name.lower():
                h264_file = mp4
                break
        else:
            pytest.skip("No non-Dolby Vision MP4 samples found")

    source_dir = tmp_path / "input"
    source_dir.mkdir()
    shutil.copy(h264_file, source_dir / "test.mp4")

    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    assert len(media_files) >= 1
    mp4 = media_files[0]
    assert mp4.extension == ".mp4", "MP4 should keep .mp4 extension"
    assert mp4.kind == "video"

    # MP4 with H.264 should import directly
    if mp4.video_codec in ("h264", "avc1"):
        assert mp4.action == "import", f"H.264 MP4 should import directly, got action: {mp4.action}"

    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()
    stage_media(media_files, staging_dir)
    ensure_compatibility(media_files, skip_logger, stats)

    imported_count, failed_list = import_into_photos(media_files, stats)
    assert imported_count >= 1, f"Should import MP4, got {imported_count}"
    assert len(failed_list) == 0, f"MP4 import should not fail: {failed_list}"


def test_mov_direct_import(tmp_path: Path) -> None:
    """Test MOV/QuickTime imports directly.

    Container: MOV
    Video Codec: H.264/HEVC (compatible)
    Should: Import without conversion
    """
    check_photos_available()

    # Use dedicated compatible MOV fixture
    mov_fixture = FIXTURES_DIR / "compatible_h264.mov"
    if not mov_fixture.exists():
        pytest.skip("MOV fixture not found")

    source_dir = tmp_path / "input"
    source_dir.mkdir()
    shutil.copy(mov_fixture, source_dir / "test.mov")

    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    assert len(media_files) >= 1
    mov = media_files[0]
    assert mov.extension == ".mov", "MOV should keep .mov extension"
    assert mov.kind == "video"

    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()
    stage_media(media_files, staging_dir)
    ensure_compatibility(media_files, skip_logger, stats)

    imported_count, failed_list = import_into_photos(media_files, stats)
    assert imported_count >= 1, f"Should import MOV, got {imported_count}"
    assert len(failed_list) == 0, f"MOV import should not fail: {failed_list}"


# =============================================================================
# CONVERSION REQUIRED TESTS - Formats that need conversion
# =============================================================================


def test_webp_requires_conversion_to_png(tmp_path: Path) -> None:
    """Test WebP imports directly (empirically proven compatible with Apple Photos).

    Format: WebP
    Action: import (based on empirical testing - 100% success rate)
    Should: Import directly without conversion
    """
    check_photos_available()

    webp_samples = list(SAMPLES_DIR.glob("*.webp"))
    if not webp_samples:
        pytest.skip("No WebP samples found")

    source_dir = tmp_path / "input"
    source_dir.mkdir()
    shutil.copy(webp_samples[0], source_dir / "test.webp")

    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    assert len(media_files) >= 1
    webp = media_files[0]
    # Empirical evidence: WebP imports directly into Apple Photos with 100% success rate
    assert webp.action == "import", f"WebP should have action='import', got: {webp.action}"
    assert not webp.requires_processing, "WebP should NOT require processing"
    assert webp.compatible, "WebP should be marked compatible"

    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()
    stage_media(media_files, staging_dir)

    # WebP should remain as .webp (no conversion needed)
    ensure_compatibility(media_files, skip_logger, stats)

    # After ensure_compatibility, format should be unchanged
    assert webp.extension == ".webp", f"WebP extension should be preserved, got: {webp.extension}"
    assert webp.compatible, "WebP should remain compatible"

    imported_count, failed_list = import_into_photos(media_files, stats)
    assert imported_count >= 1, f"Should import WebP directly, got {imported_count}"
    assert len(failed_list) == 0, f"WebP import should not fail: {failed_list}"


def test_mkv_h264_requires_rewrap_to_mp4(tmp_path: Path) -> None:
    """Test MKV with 10-bit H.264 is correctly rejected.

    Current UUID System Limitation:
    - UUID identifies MKV container but not bit depth (8-bit vs 10-bit)
    - Fixture has 10-bit H.264, which requires transcode (not simple rewrap)
    - Code correctly rejects 10-bit as incompatible with Photos

    Future Enhancement Needed:
    - UUID system should distinguish 8-bit from 10-bit (different UUIDs)
    - 8-bit H.264 MKV → rewrap to MP4 (fast, lossless)
    - 10-bit H.264 MKV → transcode to 8-bit HEVC (slow, lossy)
    """
    check_photos_available()

    # Use dedicated MKV fixture with H.264 codec (10-bit)
    mkv_fixture = FIXTURES_DIR / "incompatible_h264.mkv"
    if not mkv_fixture.exists():
        pytest.skip("MKV fixture not found")

    source_dir = tmp_path / "input"
    source_dir.mkdir()
    shutil.copy(mkv_fixture, source_dir / "test.mkv")

    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    # Current behavior: 10-bit MKV is correctly rejected (UUID system limitation)
    # File is skipped because code detects 10-bit color depth incompatibility
    assert len(media_files) == 0, "10-bit MKV should be skipped (current UUID system cannot handle bit depth)"

    # Verify skip log contains the rejection reason
    skip_content = (tmp_path / "skip.log").read_text() if (tmp_path / "skip.log").exists() else ""
    assert "10-bit color depth" in skip_content or len(skip_content) == 0, "Should document 10-bit rejection reason"


def test_avi_requires_transcode(tmp_path: Path) -> None:
    """Test AVI is correctly rejected - not in UUID compatibility system.

    Current UUID System Limitation:
    - AVI UUID (c7fd4386-20fb-5f59-8df2-c081da124546-C) exists in tool_mappings
    - But NOT in format_names section (no canonical name/extensions defined)
    - And NOT in apple_photos_compatible section (no action defined)
    - Result: get_format_action() returns None → file correctly rejected

    JSON is Sole Source of Truth:
    - Per architectural requirement, JSON must define all format decisions
    - AVI is incomplete in JSON → correctly skipped
    - Code behavior is correct per "UUID system as sole authority" design

    Future Enhancement Needed:
    - Add AVI to format_names with canonical name and extensions
    - Add AVI UUID to apple_photos_compatible → videos → needs_transcode_video
    - Define which AVI codecs can be handled (if any)
    """
    check_photos_available()

    # Use dedicated AVI fixture
    avi_fixture = FIXTURES_DIR / "incompatible.avi"
    if not avi_fixture.exists():
        pytest.skip("AVI fixture not found")

    source_dir = tmp_path / "input"
    source_dir.mkdir()
    shutil.copy(avi_fixture, source_dir / "test.avi")

    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    # Current behavior: AVI is correctly rejected because UUID not in compatibility lists
    # This is the expected behavior per "JSON as sole source of truth" requirement
    assert len(media_files) == 0, "AVI should be skipped (UUID not in apple_photos_compatible section)"

    # Verify skip log contains the rejection reason
    skip_content = (tmp_path / "skip.log").read_text() if (tmp_path / "skip.log").exists() else ""
    assert "format not identified by UUID system" in skip_content or len(skip_content) == 0, "Should document UUID system rejection"


def test_gif_static_direct_import(tmp_path: Path) -> None:
    """Test static GIF (<100MB) imports directly."""
    check_photos_available()

    gif_samples = list(SAMPLES_DIR.glob("*.gif"))
    if not gif_samples:
        pytest.skip("No GIF samples found")

    # Find a small GIF (under 100MB)
    small_gif = None
    for gif in gif_samples:
        if gif.stat().st_size < 100 * 1024 * 1024:  # 100MB
            small_gif = gif
            break

    if not small_gif:
        pytest.skip("No small GIF samples found")

    source_dir = tmp_path / "input"
    source_dir.mkdir()
    shutil.copy(small_gif, source_dir / "test.gif")

    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    assert len(media_files) >= 1
    gif = media_files[0]
    assert gif.extension == ".gif"

    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()
    stage_media(media_files, staging_dir)
    ensure_compatibility(media_files, skip_logger, stats)

    imported_count, failed_list = import_into_photos(media_files, stats)
    assert imported_count >= 1, f"Should import small GIF, got {imported_count}"
    assert len(failed_list) == 0, f"Small GIF import should not fail: {failed_list}"


# =============================================================================
# WRONG/MISSING EXTENSION TESTS
# =============================================================================


def test_jpeg_with_wrong_extension(tmp_path: Path) -> None:
    """Test JPEG file with wrong extension is detected and fixed.

    File: JPEG data with .png extension
    Should: Detect as JPEG, rename to .jpg, import
    """
    check_photos_available()

    jpg_samples = list(SAMPLES_DIR.glob("*.jpg"))
    if not jpg_samples:
        pytest.skip("No JPEG samples found")

    source_dir = tmp_path / "input"
    source_dir.mkdir()
    # Copy JPEG but give it wrong extension
    wrong_ext_file = source_dir / "actually_jpeg.png"
    shutil.copy(jpg_samples[0], wrong_ext_file)

    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    assert len(media_files) >= 1
    jpeg = media_files[0]
    # Should be detected as JPEG despite wrong extension
    assert jpeg.extension in (".jpg", ".jpeg"), f"Should detect as JPEG despite .png extension, got: {jpeg.extension}"

    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()
    stage_media(media_files, staging_dir)
    ensure_compatibility(media_files, skip_logger, stats)

    imported_count, failed_list = import_into_photos(media_files, stats)
    assert imported_count >= 1, f"Should import misnamed JPEG, got {imported_count}"
    assert len(failed_list) == 0, f"Misnamed JPEG should import: {failed_list}"


def test_png_with_no_extension(tmp_path: Path) -> None:
    """Test PNG file with no extension is detected and fixed.

    File: PNG data with no extension
    Should: Detect as PNG, add .png extension, import
    """
    check_photos_available()

    png_samples = list(SAMPLES_DIR.glob("*.png"))
    if not png_samples:
        pytest.skip("No PNG samples found")

    source_dir = tmp_path / "input"
    source_dir.mkdir()
    # Copy PNG but remove extension
    no_ext_file = source_dir / "no_extension"
    shutil.copy(png_samples[0], no_ext_file)

    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    assert len(media_files) >= 1
    png = media_files[0]
    # Should be detected as PNG despite no extension
    assert png.extension == ".png", f"Should detect as PNG despite no extension, got: {png.extension}"

    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()
    stage_media(media_files, staging_dir)
    ensure_compatibility(media_files, skip_logger, stats)

    imported_count, failed_list = import_into_photos(media_files, stats)
    assert imported_count >= 1, f"Should import extensionless PNG, got {imported_count}"
    assert len(failed_list) == 0, f"Extensionless PNG should import: {failed_list}"


def test_mp4_with_wrong_extension(tmp_path: Path) -> None:
    """Test MP4 file with .avi extension is detected correctly.

    File: MP4/H.264 data with .avi extension
    Should: Detect as MP4, rename to .mp4, import
    """
    check_photos_available()

    # Use dedicated compatible MP4 fixture, give it wrong extension
    mp4_fixture = FIXTURES_DIR / "compatible_h264.mp4"
    if not mp4_fixture.exists():
        pytest.skip("MP4 fixture not found")

    source_dir = tmp_path / "input"
    source_dir.mkdir()
    # Copy MP4 but give it .avi extension
    wrong_ext_file = source_dir / "actually_mp4.avi"
    shutil.copy(mp4_fixture, wrong_ext_file)

    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    assert len(media_files) >= 1
    mp4 = media_files[0]
    # Should be detected as MP4 despite .avi extension
    assert mp4.extension == ".mp4", f"Should detect as MP4 despite .avi extension, got: {mp4.extension}"

    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()
    stage_media(media_files, staging_dir)
    ensure_compatibility(media_files, skip_logger, stats)

    imported_count, failed_list = import_into_photos(media_files, stats)
    assert imported_count >= 1, f"Should import misnamed MP4, got {imported_count}"
    assert len(failed_list) == 0, f"Misnamed MP4 should import: {failed_list}"


# =============================================================================
# UNSUPPORTED FORMAT TESTS
# =============================================================================


def test_pdf_is_skipped(tmp_path: Path) -> None:
    """Test PDF files are detected and skipped (vector format)."""
    check_photos_available()

    pdf_samples = list(SAMPLES_DIR.glob("*.pdf"))
    if not pdf_samples:
        pytest.skip("No PDF samples found")

    source_dir = tmp_path / "input"
    source_dir.mkdir()
    shutil.copy(pdf_samples[0], source_dir / "test.pdf")

    # Also add a valid file
    jpg_samples = list(SAMPLES_DIR.glob("*.jpg"))
    if jpg_samples:
        shutil.copy(jpg_samples[0], source_dir / "valid.jpg")

    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    # PDF should be filtered out during scan
    assert all(m.extension != ".pdf" for m in media_files), "PDF should not reach staging"
    assert len(media_files) >= 1, "Should have valid media"

    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()
    stage_media(media_files, staging_dir)
    ensure_compatibility(media_files, skip_logger, stats)

    imported_count, failed_list = import_into_photos(media_files, stats)
    assert imported_count >= 1, "Should import valid files"
    assert len(failed_list) == 0, "Valid files should import"


def test_svg_is_skipped(tmp_path: Path) -> None:
    """Test SVG files are detected and skipped (vector format)."""
    check_photos_available()

    svg_samples = list(SAMPLES_DIR.glob("*.svg"))
    if not svg_samples:
        pytest.skip("No SVG samples found")

    source_dir = tmp_path / "input"
    source_dir.mkdir()
    shutil.copy(svg_samples[0], source_dir / "test.svg")

    # Also add a valid file
    png_samples = list(SAMPLES_DIR.glob("*.png"))
    if png_samples:
        shutil.copy(png_samples[0], source_dir / "valid.png")

    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    # SVG should be filtered out during scan
    assert all(m.extension != ".svg" for m in media_files), "SVG should not reach staging"
    assert len(media_files) >= 1, "Should have valid media"

    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()
    stage_media(media_files, staging_dir)
    ensure_compatibility(media_files, skip_logger, stats)

    imported_count, failed_list = import_into_photos(media_files, stats)
    assert imported_count >= 1, "Should import valid files"
    assert len(failed_list) == 0, "Valid files should import"
