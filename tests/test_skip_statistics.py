"""Regression tests for skip logging and non-media handling."""

from pathlib import Path

import pytest

import smart_media_manager.cli as cli


def test_non_media_files_counted_separately(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sample = tmp_path / "sample.dmg"
    sample.write_bytes(b"\x00\xff\x00\xff")

    stats = cli.RunStatistics()
    skip_log_path = tmp_path / "skip.log"
    skip_logger = cli.SkipLogger(skip_log_path)

    monkeypatch.setattr(
        cli,
        "detect_media",
        lambda path, skip: (None, "non-media: archive file"),
    )

    media_files = cli.gather_media_files(
        root=tmp_path,
        recursive=False,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
        skip_compatibility_check=False,
    )

    assert not media_files
    assert stats.skipped_non_media == 1
    assert stats.skipped_errors == 0
    # Non-media files are filtered out of the skip log
    assert not skip_logger.has_entries()
    assert not skip_log_path.exists() or skip_log_path.read_text(encoding="utf-8").strip() == ""


def test_should_ignore_photos_debug_artifacts(tmp_path: Path) -> None:
    debug_raw = tmp_path / "DEBUG_raw_applescript_output_20250101010101.txt"
    debug_photos = tmp_path / "DEBUG_photos_output_20250101010101.txt"
    debug_raw.touch()
    debug_photos.touch()

    assert cli.should_ignore(debug_raw)
    assert cli.should_ignore(debug_photos)

    # Non-debug file should still be considered
    normal_file = tmp_path / "normal.log"
    normal_file.touch()
    assert not cli.should_ignore(normal_file)
