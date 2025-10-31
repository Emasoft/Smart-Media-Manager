"""Tests for v0.5.0 folder import architecture.

This module tests the major architectural changes in v0.5.0:
- Sequential filename suffixes in move_to_staging()
- Folder import via import_folder_to_photos()
- Filename reconciliation logic
- New CLI arguments (--album, --check-duplicates)
"""

import shutil
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from smart_media_manager.cli import (  # noqa: E402
    MediaFile,
    RunStatistics,
    SkipLogger,
    import_folder_to_photos,
    move_to_staging,
    parse_args,
)


class TestSequentialSuffixStaging:
    """Test sequential suffix logic in move_to_staging()."""

    def test_sequential_suffix_single_file(self, tmp_path: Path) -> None:
        """Test that a single file gets (1) suffix."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        photo = source_dir / "photo.jpg"
        Image.new("RGB", (10, 10)).save(photo)

        media = MediaFile(
            source=photo,
            kind="image",
            extension=".jpg",
            format_name="jpeg",
            compatible=True,
            original_suffix=".jpg",
            rule_id="R-IMG-001",
            action="import",
            requires_processing=False,
            notes="JPEG",
        )

        staging = tmp_path / "staging"
        staging.mkdir()
        move_to_staging([media], staging)

        assert media.stage_path is not None
        assert media.stage_path.name == "photo (1).jpg"
        assert media.stage_path.exists()

    def test_sequential_suffix_multiple_files(self, tmp_path: Path) -> None:
        """Test that multiple files get sequential (N) suffixes."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        media_files = []
        for i in range(5):
            photo = source_dir / f"photo{i}.jpg"
            Image.new("RGB", (10, 10)).save(photo)
            media = MediaFile(
                source=photo,
                kind="image",
                extension=".jpg",
                format_name="jpeg",
                compatible=True,
                original_suffix=".jpg",
                rule_id="R-IMG-001",
                action="import",
                requires_processing=False,
                notes="JPEG",
            )
            media_files.append(media)

        staging = tmp_path / "staging"
        staging.mkdir()
        move_to_staging(media_files, staging)

        # Check sequential suffixes: (1), (2), (3), (4), (5)
        for i, media in enumerate(media_files, start=1):
            assert media.stage_path is not None
            expected_suffix = f" ({i}).jpg"
            assert media.stage_path.name.endswith(expected_suffix)
            assert media.stage_path.exists()

    def test_sequential_suffix_same_stem_different_folders(self, tmp_path: Path) -> None:
        """Test that files with same name from different folders get unique suffixes."""
        source_dir1 = tmp_path / "source1"
        source_dir1.mkdir()
        source_dir2 = tmp_path / "source2"
        source_dir2.mkdir()

        photo1 = source_dir1 / "photo.jpg"
        photo2 = source_dir2 / "photo.jpg"
        Image.new("RGB", (10, 10)).save(photo1)
        Image.new("RGB", (10, 10)).save(photo2)

        media1 = MediaFile(
            source=photo1,
            kind="image",
            extension=".jpg",
            format_name="jpeg",
            compatible=True,
            original_suffix=".jpg",
            rule_id="R-IMG-001",
            action="import",
            requires_processing=False,
            notes="JPEG",
        )

        media2 = MediaFile(
            source=photo2,
            kind="image",
            extension=".jpg",
            format_name="jpeg",
            compatible=True,
            original_suffix=".jpg",
            rule_id="R-IMG-001",
            action="import",
            requires_processing=False,
            notes="JPEG",
        )

        staging = tmp_path / "staging"
        staging.mkdir()
        move_to_staging([media1, media2], staging)

        # Both should have different suffixes despite same original name
        assert media1.stage_path is not None
        assert media2.stage_path is not None
        assert media1.stage_path.name == "photo (1).jpg"
        assert media2.stage_path.name == "photo (2).jpg"
        assert media1.stage_path.exists()
        assert media2.stage_path.exists()

    def test_sequential_suffix_collision_handling(self, tmp_path: Path) -> None:
        """Test collision handling with sub-suffix when a file already exists."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        staging = tmp_path / "staging"
        staging.mkdir()

        # Pre-create a file with (1) suffix to force collision
        existing = staging / "photo (1).jpg"
        existing.write_text("existing file")

        photo = source_dir / "photo.jpg"
        Image.new("RGB", (10, 10)).save(photo)

        media = MediaFile(
            source=photo,
            kind="image",
            extension=".jpg",
            format_name="jpeg",
            compatible=True,
            original_suffix=".jpg",
            rule_id="R-IMG-001",
            action="import",
            requires_processing=False,
            notes="JPEG",
        )

        move_to_staging([media], staging)

        # Should get collision sub-suffix: (1-2)
        assert media.stage_path is not None
        assert media.stage_path.name == "photo (1-2).jpg"
        assert media.stage_path.exists()

    def test_sequential_suffix_preserves_extensions(self, tmp_path: Path) -> None:
        """Test that suffix is inserted before extension correctly."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        # Test various extensions (only those PIL can save)
        extensions = [".jpg", ".png", ".gif", ".bmp", ".tiff"]
        media_files = []

        for i, ext in enumerate(extensions):
            photo = source_dir / f"media{i}{ext}"
            # Save using appropriate PIL format
            if ext == ".tiff":
                Image.new("RGB", (10, 10)).save(photo, format="TIFF")
            else:
                Image.new("RGB", (10, 10)).save(photo)

            media = MediaFile(
                source=photo,
                kind="image",
                extension=ext,
                format_name="test",
                compatible=True,
                original_suffix=ext,
                rule_id="R-TEST-001",
                action="import",
                requires_processing=False,
                notes="Test",
            )
            media_files.append(media)

        staging = tmp_path / "staging"
        staging.mkdir()
        move_to_staging(media_files, staging)

        # Verify each file has suffix before extension
        for i, (media, ext) in enumerate(zip(media_files, extensions), start=1):
            assert media.stage_path is not None
            assert media.stage_path.name == f"media{i - 1} ({i}){ext}"
            assert media.stage_path.exists()


class TestFolderImport:
    """Test folder import functionality."""

    def test_import_folder_to_photos_success(self, tmp_path: Path) -> None:
        """Test successful folder import with all files imported."""
        staging = tmp_path / "staging"
        staging.mkdir()

        # Create test files
        media_files = []
        for i in range(3):
            photo = staging / f"photo ({i + 1}).jpg"
            Image.new("RGB", (10, 10)).save(photo)
            media = MediaFile(
                source=tmp_path / f"source{i}.jpg",  # Original location
                kind="image",
                extension=".jpg",
                format_name="jpeg",
                compatible=True,
                original_suffix=".jpg",
                rule_id="R-IMG-001",
                action="import",
                requires_processing=False,
                notes="JPEG",
            )
            media.stage_path = photo
            media_files.append(media)

        # Mock AppleScript output - all files imported
        mock_output = "FN\tphoto (1).jpg\nFN\tphoto (2).jpg\nFN\tphoto (3).jpg"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=mock_output,
                stderr="",
            )

            imported, skipped, skipped_media = import_folder_to_photos(
                staging_dir=staging,
                media_files=media_files,
                album_name="Test Album",
                skip_duplicates=True,
            )

            assert imported == 3
            assert skipped == 0
            assert len(skipped_media) == 0

            # Verify AppleScript was called correctly
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args[0][0][0] == "osascript"
            assert "Test Album" in call_args[0][0]
            assert "true" in call_args[0][0]  # skip_duplicates
            assert str(staging) in call_args[0][0]

    def test_import_folder_to_photos_with_skipped(self, tmp_path: Path) -> None:
        """Test folder import with some files skipped (duplicates)."""
        staging = tmp_path / "staging"
        staging.mkdir()

        media_files = []
        for i in range(4):
            photo = staging / f"photo ({i + 1}).jpg"
            Image.new("RGB", (10, 10)).save(photo)
            media = MediaFile(
                source=tmp_path / f"source{i}.jpg",
                kind="image",
                extension=".jpg",
                format_name="jpeg",
                compatible=True,
                original_suffix=".jpg",
                rule_id="R-IMG-001",
                action="import",
                requires_processing=False,
                notes="JPEG",
            )
            media.stage_path = photo
            media_files.append(media)

        # Mock AppleScript output - only 2 files imported (2 and 4 skipped)
        mock_output = "FN\tphoto (1).jpg\nFN\tphoto (3).jpg"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=mock_output,
                stderr="",
            )

            imported, skipped, skipped_media = import_folder_to_photos(
                staging_dir=staging,
                media_files=media_files,
                album_name="Test Album",
                skip_duplicates=True,
            )

            assert imported == 2
            assert skipped == 2
            assert len(skipped_media) == 2

            # Verify skipped files are photo (2) and photo (4)
            skipped_names = {m.stage_path.name for m in skipped_media}
            assert skipped_names == {"photo (2).jpg", "photo (4).jpg"}

    def test_import_folder_to_photos_applescript_error(self, tmp_path: Path) -> None:
        """Test that AppleScript errors are raised properly."""
        staging = tmp_path / "staging"
        staging.mkdir()

        photo = staging / "photo (1).jpg"
        Image.new("RGB", (10, 10)).save(photo)
        media = MediaFile(
            source=tmp_path / "source.jpg",
            kind="image",
            extension=".jpg",
            format_name="jpeg",
            compatible=True,
            original_suffix=".jpg",
            rule_id="R-IMG-001",
            action="import",
            requires_processing=False,
            notes="JPEG",
        )
        media.stage_path = photo

        # Mock AppleScript error
        mock_output = "ERR\t-1728\tPhotos.app not running"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=mock_output,
                stderr="",
            )

            with pytest.raises(RuntimeError, match="Photos import failed.*-1728.*Photos.app not running"):
                import_folder_to_photos(
                    staging_dir=staging,
                    media_files=[media],
                    album_name="Test Album",
                    skip_duplicates=True,
                )

    def test_import_folder_to_photos_timeout(self, tmp_path: Path) -> None:
        """Test that timeout errors are handled properly."""
        staging = tmp_path / "staging"
        staging.mkdir()

        photo = staging / "photo (1).jpg"
        Image.new("RGB", (10, 10)).save(photo)
        media = MediaFile(
            source=tmp_path / "source.jpg",
            kind="image",
            extension=".jpg",
            format_name="jpeg",
            compatible=True,
            original_suffix=".jpg",
            rule_id="R-IMG-001",
            action="import",
            requires_processing=False,
            notes="JPEG",
        )
        media.stage_path = photo

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(cmd="osascript", timeout=1800)

            with pytest.raises(RuntimeError, match="Photos folder import timed out after 1800 seconds"):
                import_folder_to_photos(
                    staging_dir=staging,
                    media_files=[media],
                    album_name="Test Album",
                    skip_duplicates=True,
                )


class TestFilenameReconciliation:
    """Test filename reconciliation logic."""

    def test_multiset_reconciliation_with_duplicates(self, tmp_path: Path) -> None:
        """Test reconciliation when Photos returns duplicate filenames."""
        staging = tmp_path / "staging"
        staging.mkdir()

        # Create files with same names (from different folders)
        media_files = []
        for i in range(4):
            photo = staging / f"photo ({i + 1}).jpg"
            Image.new("RGB", (10, 10)).save(photo)
            media = MediaFile(
                source=tmp_path / f"source{i}.jpg",
                kind="image",
                extension=".jpg",
                format_name="jpeg",
                compatible=True,
                original_suffix=".jpg",
                rule_id="R-IMG-001",
                action="import",
                requires_processing=False,
                notes="JPEG",
            )
            media.stage_path = photo
            media_files.append(media)

        # Photos returns same filename twice (edge case)
        mock_output = "FN\tphoto (1).jpg\nFN\tphoto (1).jpg\nFN\tphoto (3).jpg"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=mock_output,
                stderr="",
            )

            imported, skipped, skipped_media = import_folder_to_photos(
                staging_dir=staging,
                media_files=media_files,
                album_name="Test Album",
                skip_duplicates=True,
            )

            # Multiset should handle duplicate correctly
            # We have 3 returned names but only unique entries
            # This would import based on multiset matching
            assert imported >= 1  # At least one imported
            assert imported + skipped == 4  # Total should be 4

    def test_reconciliation_empty_output(self, tmp_path: Path) -> None:
        """Test reconciliation when Photos imports nothing."""
        staging = tmp_path / "staging"
        staging.mkdir()

        photo = staging / "photo (1).jpg"
        Image.new("RGB", (10, 10)).save(photo)
        media = MediaFile(
            source=tmp_path / "source.jpg",
            kind="image",
            extension=".jpg",
            format_name="jpeg",
            compatible=True,
            original_suffix=".jpg",
            rule_id="R-IMG-001",
            action="import",
            requires_processing=False,
            notes="JPEG",
        )
        media.stage_path = photo

        # Photos returns empty (all files skipped)
        mock_output = ""

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=mock_output,
                stderr="",
            )

            imported, skipped, skipped_media = import_folder_to_photos(
                staging_dir=staging,
                media_files=[media],
                album_name="Test Album",
                skip_duplicates=True,
            )

            assert imported == 0
            assert skipped == 1
            assert len(skipped_media) == 1
            assert skipped_media[0] == media


class TestCLIArguments:
    """Test new CLI arguments added in v0.5.0."""

    def test_album_argument_default(self, tmp_path: Path, monkeypatch) -> None:
        """Test --album argument has correct default."""
        monkeypatch.setattr("sys.argv", ["smart-media-manager", str(tmp_path)])
        args = parse_args()
        assert hasattr(args, "album")
        assert args.album == "Smart Media Manager"

    def test_album_argument_custom(self, tmp_path: Path, monkeypatch) -> None:
        """Test --album argument with custom value."""
        monkeypatch.setattr("sys.argv", ["smart-media-manager", "--album", "My Custom Album", str(tmp_path)])
        args = parse_args()
        assert args.album == "My Custom Album"

    def test_check_duplicates_argument_default(self, tmp_path: Path, monkeypatch) -> None:
        """Test --check-duplicates is False by default."""
        monkeypatch.setattr("sys.argv", ["smart-media-manager", str(tmp_path)])
        args = parse_args()
        assert hasattr(args, "check_duplicates")
        assert args.check_duplicates is False

    def test_check_duplicates_argument_enabled(self, tmp_path: Path, monkeypatch) -> None:
        """Test --check-duplicates flag when enabled."""
        monkeypatch.setattr("sys.argv", ["smart-media-manager", "--check-duplicates", str(tmp_path)])
        args = parse_args()
        assert args.check_duplicates is True

    def test_both_arguments_together(self, tmp_path: Path, monkeypatch) -> None:
        """Test using both --album and --check-duplicates together."""
        monkeypatch.setattr(
            "sys.argv",
            ["smart-media-manager", "--album", "Test Album", "--check-duplicates", str(tmp_path)],
        )
        args = parse_args()
        assert args.album == "Test Album"
        assert args.check_duplicates is True
        assert args.path == tmp_path
