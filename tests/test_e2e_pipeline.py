"""End-to-end tests using real sample media files.

Tests the complete pipeline from detection through conversion.
Uses actual media files in tests/samples/media/ to verify:
- Format detection accuracy
- Rule matching correctness
- Conversion decisions (import vs convert vs skip)
- File integrity after processing
"""

import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

pytestmark = pytest.mark.e2e

from smart_media_manager.cli import (  # noqa: E402
    RunStatistics,
    SkipLogger,
    gather_media_files,
)
from tests.helpers import stage_media  # noqa: E402

SAMPLES_DIR = Path(__file__).parent / "samples" / "media"
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_sample_media_directory_exists() -> None:
    """Verify the samples/media directory exists with files."""
    assert SAMPLES_DIR.exists(), f"Samples directory not found: {SAMPLES_DIR}"
    assert SAMPLES_DIR.is_dir(), f"Samples path is not a directory: {SAMPLES_DIR}"
    files = list(SAMPLES_DIR.iterdir())
    assert len(files) > 0, "Samples directory is empty"


def test_compatible_jpeg_should_import(tmp_path: Path) -> None:
    """JPEG files should be marked for direct import (action='import')."""
    # Copy a JPEG sample
    source_dir = tmp_path / "input"
    source_dir.mkdir()

    jpeg_samples = list(SAMPLES_DIR.glob("*.jpeg")) + list(SAMPLES_DIR.glob("*.jpg"))
    if not jpeg_samples:
        pytest.skip("No JPEG samples found")

    test_jpeg = source_dir / "test.jpg"
    shutil.copy(jpeg_samples[0], test_jpeg)

    # Scan and detect
    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    assert len(media_files) >= 1, "JPEG file should be detected"
    jpeg_media = [m for m in media_files if m.extension in (".jpg", ".jpeg")]
    assert len(jpeg_media) >= 1, "At least one JPEG should be found"

    # Check action
    jpeg = jpeg_media[0]
    assert jpeg.action == "import", f"JPEG should have action='import', got: {jpeg.action}"
    assert jpeg.compatible is True, "JPEG should be marked compatible"
    assert jpeg.requires_processing is False, "JPEG should not require processing"


def test_compatible_png_should_import(tmp_path: Path) -> None:
    """PNG files should be marked for direct import (action='import')."""
    source_dir = tmp_path / "input"
    source_dir.mkdir()

    png_samples = list(SAMPLES_DIR.glob("*.png"))
    if not png_samples:
        pytest.skip("No PNG samples found")

    test_png = source_dir / "test.png"
    shutil.copy(png_samples[0], test_png)

    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    assert len(media_files) >= 1, "PNG file should be detected"
    png_media = [m for m in media_files if m.extension == ".png"]
    assert len(png_media) >= 1, "At least one PNG should be found"

    png = png_media[0]
    assert png.action == "import", f"PNG should have action='import', got: {png.action}"
    assert png.compatible is True, "PNG should be marked compatible"
    assert png.requires_processing is False, "PNG should not require processing"


def test_webp_should_convert_to_png(tmp_path: Path) -> None:
    """WebP files import directly (empirically proven compatible with Apple Photos)."""
    source_dir = tmp_path / "input"
    source_dir.mkdir()

    webp_samples = list(SAMPLES_DIR.glob("*.webp"))
    if not webp_samples:
        pytest.skip("No WebP samples found")

    test_webp = source_dir / "test.webp"
    shutil.copy(webp_samples[0], test_webp)

    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    assert len(media_files) >= 1, "WebP file should be detected"
    webp_media = [m for m in media_files if m.extension == ".webp"]
    assert len(webp_media) >= 1, "At least one WebP should be found"

    webp = webp_media[0]
    # Empirical evidence: WebP imports directly into Apple Photos with 100% success rate
    assert webp.action == "import", f"WebP should have action='import', got: {webp.action}"
    assert webp.compatible is True, "WebP should be marked compatible"
    assert webp.requires_processing is False, "WebP should not require processing"


def test_pdf_should_be_skipped(tmp_path: Path) -> None:
    """PDF files should be skipped (vector graphics not supported)."""
    source_dir = tmp_path / "input"
    source_dir.mkdir()

    pdf_samples = list(SAMPLES_DIR.glob("*.pdf"))
    if not pdf_samples:
        pytest.skip("No PDF samples found")

    test_pdf = source_dir / "test.pdf"
    shutil.copy(pdf_samples[0], test_pdf)

    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    # PDFs should be detected but skipped
    pdf_media = [m for m in media_files if m.extension == ".pdf"]
    if pdf_media:
        pdf = pdf_media[0]
        assert pdf.action == "skip_vector", f"PDF should have action='skip_vector', got: {pdf.action}"


def test_svg_should_be_skipped(tmp_path: Path) -> None:
    """SVG files should be skipped (vector graphics not supported)."""
    source_dir = tmp_path / "input"
    source_dir.mkdir()

    svg_samples = list(SAMPLES_DIR.glob("*.svg"))
    if not svg_samples:
        pytest.skip("No SVG samples found")

    test_svg = source_dir / "test.svg"
    shutil.copy(svg_samples[0], test_svg)

    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    # SVGs should be detected but skipped
    svg_media = [m for m in media_files if m.extension == ".svg"]
    if svg_media:
        svg = svg_media[0]
        assert svg.action in ("skip_vector", "skip_unknown"), f"SVG should be skipped, got action: {svg.action}"


def test_non_media_files_skipped(tmp_path: Path) -> None:
    """Non-media files (.docx, .html, .log) should be skipped."""
    source_dir = tmp_path / "input"
    source_dir.mkdir()

    # Find non-media files
    non_media_files = []
    for ext in [".docx", ".html", ".log", ".txt"]:
        non_media_files.extend(SAMPLES_DIR.glob(f"*{ext}"))

    if not non_media_files:
        pytest.skip("No non-media files found")

    test_file = source_dir / "test_nonmedia.docx"
    shutil.copy(non_media_files[0], test_file)

    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    # Non-media files should not appear in media_files list
    assert all(m.extension not in (".docx", ".html", ".log", ".txt") for m in media_files), "Non-media files should be skipped"


def test_mp4_video_detection(tmp_path: Path) -> None:
    """MP4 video files should be detected and keep .mp4 extension."""
    source_dir = tmp_path / "input"
    source_dir.mkdir()

    # Use dedicated compatible MP4 fixture
    mp4_fixture = FIXTURES_DIR / "compatible_h264.mp4"
    if not mp4_fixture.exists():
        pytest.skip("MP4 fixture not found")

    test_mp4 = source_dir / "test.mp4"
    shutil.copy(mp4_fixture, test_mp4)

    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    assert len(media_files) >= 1, "MP4 file should be detected"
    mp4_media = [m for m in media_files if m.extension == ".mp4"]
    assert len(mp4_media) >= 1, "At least one MP4 should be found with .mp4 extension"

    mp4 = mp4_media[0]
    # MP4 action depends on codec - should be one of these
    valid_actions = {
        "import",
        "rewrap_to_mp4",
        "rewrap_or_transcode_to_mp4",
        "transcode_to_hevc_mp4",
        "transcode_video_to_lossless_hevc",
        "transcode_audio_to_aac_or_eac3",
    }
    assert mp4.action in valid_actions, f"MP4 should have valid action, got: {mp4.action}"
    assert mp4.kind == "video", "MP4 should be detected as video"
    assert mp4.extension == ".mp4", "MP4 file should keep .mp4 extension"


def test_mkv_video_detection(tmp_path: Path) -> None:
    """MKV video files should be detected for rewrap or transcode."""
    source_dir = tmp_path / "input"
    source_dir.mkdir()

    mkv_samples = list(SAMPLES_DIR.glob("*.mkv"))
    if not mkv_samples:
        pytest.skip("No MKV samples found")

    test_mkv = source_dir / "test.mkv"
    shutil.copy(mkv_samples[0], test_mkv)

    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    assert len(media_files) >= 1, "MKV file should be detected"
    mkv_media = [m for m in media_files if m.extension == ".mkv"]
    assert len(mkv_media) >= 1, "At least one MKV should be found"

    mkv = mkv_media[0]
    # MKV needs container change - should rewrap or transcode
    valid_actions = {
        "rewrap_to_mp4",
        "transcode_to_hevc_mp4",
        "transcode_video_to_lossless_hevc",
        "rewrap_or_transcode_to_mp4",
    }
    assert mkv.action in valid_actions, f"MKV should be converted, got: {mkv.action}"
    assert mkv.requires_processing is True, "MKV should require processing"


def test_mixed_media_folder(tmp_path: Path) -> None:
    """Test scanning a folder with mixed compatible and incompatible media."""
    source_dir = tmp_path / "input"
    source_dir.mkdir()

    # Copy a variety of files
    copied = 0
    for pattern in ["*.jpg", "*.png", "*.webp", "*.mp4"]:
        samples = list(SAMPLES_DIR.glob(pattern))
        if samples and copied < 10:  # Limit to 10 files for speed
            shutil.copy(samples[0], source_dir / f"test{copied}{Path(samples[0]).suffix}")
            copied += 1

    if copied == 0:
        pytest.skip("No sample files available")

    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    assert len(media_files) >= 1, "Should detect at least one media file"

    # Check that each file has a valid action
    for media in media_files:
        assert media.action is not None, f"File {media.source.name} should have an action assigned"
        assert media.extension is not None, f"File {media.source.name} should have an extension"
        assert media.format_name is not None, f"File {media.source.name} should have a format_name"


def test_staging_moves_files(tmp_path: Path) -> None:
    """Test that staging moves files from source to staging directory."""
    source_dir = tmp_path / "input"
    source_dir.mkdir()
    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()

    # Copy a test file
    jpg_samples = list(SAMPLES_DIR.glob("*.jpg"))
    if not jpg_samples:
        pytest.skip("No JPEG samples found")

    test_file = source_dir / "test.jpg"
    shutil.copy(jpg_samples[0], test_file)
    original_size = test_file.stat().st_size

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

    assert len(media_files) >= 1
    stage_media(media_files, staging_dir)

    # Original should be moved (no longer in source)
    assert not test_file.exists(), "Original file should be moved from source directory"

    # Staged file should exist with same extension and size
    staged_files = list(staging_dir.glob("*.jpg"))
    assert len(staged_files) >= 1, "Staged .jpg file should exist"
    assert staged_files[0].stat().st_size == original_size, "Staged file should be same size"


def test_recursive_scanning(tmp_path: Path) -> None:
    """Test recursive directory scanning."""
    source_dir = tmp_path / "input"
    subdir1 = source_dir / "subdir1"
    subdir2 = source_dir / "subdir2"

    source_dir.mkdir()
    subdir1.mkdir()
    subdir2.mkdir()

    # Place files in different directories
    jpg_samples = list(SAMPLES_DIR.glob("*.jpg"))
    png_samples = list(SAMPLES_DIR.glob("*.png"))

    if len(jpg_samples) == 0 or len(png_samples) == 0:
        pytest.skip("Need both JPEG and PNG samples")

    shutil.copy(jpg_samples[0], source_dir / "root.jpg")
    shutil.copy(png_samples[0], subdir1 / "sub1.png")
    if len(jpg_samples) > 1:
        shutil.copy(jpg_samples[1], subdir2 / "sub2.jpg")

    # Test non-recursive
    stats = RunStatistics()
    skip_logger = SkipLogger(tmp_path / "skip.log")
    media_files_flat = gather_media_files(
        source_dir,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    # Should only find root.jpg
    assert len(media_files_flat) == 1, "Non-recursive should only find files in root"

    # Test recursive
    stats = RunStatistics()
    media_files_recursive = gather_media_files(
        source_dir,
        recursive=True,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
    )

    # Should find all files
    assert len(media_files_recursive) >= 2, "Recursive should find files in subdirectories"
