"""Integration test that runs staging/compatibility on the sample media set."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from smart_media_manager.cli import (
    RunStatistics,
    SkipLogger,
    ensure_compatibility,
    gather_media_files,
    move_to_staging,
    update_stats_after_compatibility,
)


SAMPLE_MEDIA_ROOT = Path(__file__).parent / "samples" / "media"
SAMPLE_FILES = [
    "file_example_PNG_3MB.png",
    "file_example_WEBP_1500kB.webp",
    "file_example_GIF_3500kB.gif",
    "file_example_AVI_1920_2_3MG.avi",
    "file_example_MP4_1920_18MG.mp4",
    "23KBN1J0041526.pdf",
    "chart.svg",
    "_2585d616-9d1c-4ae8-8110-78fe5ba1acb3.RAW",
]


@pytest.mark.e2e
def test_staging_counts_before_photos_import(tmp_path: Path) -> None:
    """Only compatible + successfully converted files must remain staged."""

    input_root = tmp_path / "input"
    input_root.mkdir()
    for filename in SAMPLE_FILES:
        shutil.copy2(SAMPLE_MEDIA_ROOT / filename, input_root / filename)

    staging = tmp_path / "staging"
    staging.mkdir()
    originals = tmp_path / "originals"
    skip_log = tmp_path / "skip.log"
    skip_logger = SkipLogger(skip_log)
    stats = RunStatistics()

    media_files = gather_media_files(
        input_root,
        recursive=True,
        follow_symlinks=False,
        skip_logger=skip_logger,
        stats=stats,
        skip_compatibility_check=False,
    )

    move_to_staging(media_files, staging, originals)
    ensure_compatibility(media_files, skip_logger, stats, skip_convert=False)

    staged_media = [m for m in media_files if m.stage_path and m.stage_path.exists()]
    staged_files = [path.name for path in staging.iterdir()]

    update_stats_after_compatibility(stats, media_files)
    assert stats.total_media_detected == len(media_files)

    initial_compatible = sum(1 for m in media_files if m.detected_compatible)
    initial_incompatible = stats.total_media_detected - initial_compatible

    assert stats.media_compatible == initial_compatible
    assert stats.media_incompatible == initial_incompatible

    converted_success = sum(1 for m in media_files if m.was_converted)
    assert stats.incompatible_with_conversion_rule == converted_success
    assert converted_success <= initial_incompatible

    assert len(staged_media) == initial_compatible + converted_success
    assert stats.staging_total == len(staged_media)
    assert stats.staging_expected == initial_compatible + converted_success
    assert len(staged_files) == len(staged_media)
    assert set(staged_files) == {m.stage_path.name for m in staged_media}

    assert len(staged_media) > 0
    for media in staged_media:
        assert media.stage_path is not None and media.stage_path.exists()
