"""Shared testing helpers for Smart Media Manager."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from smart_media_manager.cli import MediaFile, move_to_staging


def stage_media(
    media_files: Iterable[MediaFile],
    staging_dir: Path,
    originals_dir: Path | None = None,
    copy_files: bool = False,
) -> Path:
    """Stage media files for tests, creating a default originals directory.

    Args:
        media_files: Media objects to stage.
        staging_dir: Destination staging directory.
        originals_dir: Optional directory for archived originals. Defaults to
            ``staging_dir.parent / "originals"`` when omitted.

    Returns:
        The originals directory that was used.
    """
    originals = originals_dir or staging_dir.parent / "originals"
    originals.mkdir(parents=True, exist_ok=True)
    move_to_staging(media_files, staging_dir, originals, copy_files=copy_files)
    return originals
