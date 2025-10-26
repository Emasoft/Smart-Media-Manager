import shutil
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from smart_media_manager.cli import (  # noqa: E402
    MediaFile,
    RunStatistics,
    SkipLogger,
    enforce_safe_fallback,
    ensure_compatibility,
    gather_media_files,
    move_to_staging,
)


def test_png_import_pipeline(monkeypatch, tmp_path: Path) -> None:
    source_dir = tmp_path / "input"
    source_dir.mkdir()
    png_path = source_dir / "photo.png"
    shutil.copy(Path(__file__).parent / "sample.png", png_path)

    def fake_detect(path: Path):
        media = MediaFile(
            source=path,
            kind="image",
            extension=".png",
            format_name="png",
            compatible=True,
            original_suffix=path.suffix,
            rule_id="R-IMG-002",
            action="import",
            requires_processing=False,
            notes="PNG",
        )
        return media, None

    monkeypatch.setattr("smart_media_manager.cli.detect_media", fake_detect)

    skip_log = tmp_path / "skip.log"
    stats = RunStatistics()
    media_files = gather_media_files(source_dir, recursive=False, follow_symlinks=False, skip_logger=SkipLogger(skip_log), stats=stats)

    assert len(media_files) == 1
    media = media_files[0]
    assert media.action == "import"

    staging_root = tmp_path / "staging"
    staging_root.mkdir()
    move_to_staging(media_files, staging_root)
    ensure_compatibility(media_files, SkipLogger(skip_log), stats)

    assert media_files[0].stage_path is not None
    assert media_files[0].stage_path.exists()
    assert media_files[0].requires_processing is False
    assert media_files[0].rule_id == "R-IMG-002"


def test_pdf_vector_skipped(monkeypatch, tmp_path: Path) -> None:
    source_dir = tmp_path / "input"
    source_dir.mkdir()
    pdf_path = source_dir / "vector.pdf"
    shutil.copy(Path(__file__).parent / "sample.pdf", pdf_path)

    def fake_detect(_path: Path):
        return None, "vector formats are not supported"

    monkeypatch.setattr("smart_media_manager.cli.detect_media", fake_detect)

    skip_log = tmp_path / "skip.log"
    stats = RunStatistics()
    media_files = gather_media_files(source_dir, recursive=False, follow_symlinks=False, skip_logger=SkipLogger(skip_log), stats=stats)

    assert media_files == []
    assert skip_log.exists()
    log_content = skip_log.read_text()
    assert "vector" in log_content.lower()


def test_corrupt_png_skipped(tmp_path: Path) -> None:
    source_dir = tmp_path / "input"
    source_dir.mkdir()
    corrupt_path = source_dir / "bad.png"
    corrupt_path.write_bytes(b"\x89PNG\r\n\x1a\n\x00")

    skip_log = tmp_path / "skip.log"
    stats = RunStatistics()
    media_files = gather_media_files(source_dir, recursive=False, follow_symlinks=False, skip_logger=SkipLogger(skip_log), stats=stats)

    assert media_files == []
    assert skip_log.exists()
    assert "corrupt" in skip_log.read_text().lower()


def test_enforce_safe_fallback_assigns_actions(monkeypatch, tmp_path: Path) -> None:
    staging_dir = tmp_path / "stage"
    staging_dir.mkdir()

    image_stage = staging_dir / "img.heic"
    video_stage = staging_dir / "vid.mkv"
    image_stage.write_bytes(b"dummy")
    video_stage.write_bytes(b"dummy")

    media_image = MediaFile(
        source=tmp_path / "img.heic",
        kind="image",
        extension=".heic",
        format_name="heic",
        compatible=False,
        original_suffix=".heic",
        stage_path=image_stage,
        rule_id="R-IMG-013",
        action="convert_to_heic_lossless",
        requires_processing=True,
    )

    media_video = MediaFile(
        source=tmp_path / "vid.mkv",
        kind="video",
        extension=".mkv",
        format_name="mkv",
        compatible=False,
        original_suffix=".mkv",
        stage_path=video_stage,
        rule_id="R-VID-007",
        action="transcode_to_hevc_mp4",
        requires_processing=True,
    )

    called = {}

    def fake_ensure(media_files, _logger, _stats):
        called["count"] = called.get("count", 0) + 1

    monkeypatch.setattr("smart_media_manager.cli.ensure_compatibility", fake_ensure)

    skip_log = tmp_path / "skip.log"
    stats = RunStatistics()
    enforce_safe_fallback([media_image, media_video], SkipLogger(skip_log), stats)

    assert media_image.action == "convert_to_png"
    assert media_video.action == "transcode_to_hevc_mp4"
    assert media_image.metadata.get("safe_fallback") is True
    assert media_video.metadata.get("safe_fallback") is True
    assert called.get("count") == 1


def test_typescript_file_is_skipped(tmp_path: Path) -> None:
    source_dir = tmp_path / "input"
    source_dir.mkdir()
    target = source_dir / "use-database.ts"
    sample = Path(__file__).parent / "samples" / "use-database.ts"
    shutil.copy(sample, target)

    skip_log = tmp_path / "skip.log"
    logger = SkipLogger(skip_log)
    stats = RunStatistics()
    media_files = gather_media_files(source_dir, recursive=False, follow_symlinks=False, skip_logger=logger, stats=stats)

    assert media_files == []
    assert skip_log.exists()
    assert "text file" in skip_log.read_text().lower()


def test_media_with_wrong_extension_is_normalised(tmp_path: Path) -> None:
    source_dir = tmp_path / "input"
    source_dir.mkdir()
    wrong_ext_path = source_dir / "photo.ts"
    image_path = tmp_path / "generated.png"
    Image.new("RGB", (2, 2), color=(123, 222, 111)).save(image_path)
    shutil.copy(image_path, wrong_ext_path)

    skip_log = tmp_path / "skip.log"
    logger = SkipLogger(skip_log)
    stats = RunStatistics()
    media_files = gather_media_files(source_dir, recursive=False, follow_symlinks=False, skip_logger=logger, stats=stats)

    assert len(media_files) == 1
    media = media_files[0]
    assert media.extension == ".png"
    assert media.rule_id.startswith("R-IMG")

    staging_dir = tmp_path / "stage"
    staging_dir.mkdir()
    move_to_staging(media_files, staging_dir)

    assert media.stage_path is not None
    assert media.stage_path.suffix == ".png"
