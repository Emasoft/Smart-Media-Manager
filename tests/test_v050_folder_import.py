"""Tests for v0.5.0 folder import architecture.

This module tests the major architectural changes in v0.5.0:
- Sequential filename suffixes in move_to_staging()
- Folder import via import_folder_to_photos()
- Filename reconciliation logic
- New CLI arguments (--album, --skip-duplicate-check)
"""

import re
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
    import_folder_to_photos,
    parse_args,
)
from tests.helpers import stage_media  # noqa: E402


STAGING_NAME_RE = re.compile(r"^(?P<stem>.+)__SMM(?P<token>[A-Za-z0-9]+)__(?P<suffix>_\([0-9-]+\))(?P<ext>\.[^.]+)$")


def assert_staged_name(name: str, expected_suffix: str, expected_ext: str) -> None:
    match = STAGING_NAME_RE.match(name)
    assert match, f"Unexpected staging name format: {name}"
    assert len(match.group("token")) >= 6
    assert match.group("suffix") == expected_suffix
    assert match.group("ext") == expected_ext


class TestSequentialSuffixStaging:
    """Test sequential suffix logic in stage_media()."""

    def test_sequential_suffix_single_file(self, tmp_path: Path) -> None:
        """Test that a single file gets _(1) suffix."""
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
        stage_media([media], staging)

        assert media.stage_path is not None
        assert_staged_name(media.stage_path.name, "_(1)", ".jpg")
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
        stage_media(media_files, staging)

        # Check sequential suffixes: (1), (2), (3), (4), (5)
        for i, media in enumerate(media_files, start=1):
            assert media.stage_path is not None
        expected_suffix = f"_({i})"
        assert_staged_name(media.stage_path.name, expected_suffix, ".jpg")
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
        stage_media([media1, media2], staging)

        # Both should have different suffixes despite same original name
        assert media1.stage_path is not None
        assert media2.stage_path is not None
        assert_staged_name(media1.stage_path.name, "_(1)", ".jpg")
        assert_staged_name(media2.stage_path.name, "_(2)", ".jpg")
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

        stage_media([media], staging)

        # Existing file should not be overwritten; staged file keeps unique name
        assert media.stage_path is not None
        assert_staged_name(media.stage_path.name, "_(1)", ".jpg")
        assert media.stage_path.name != "photo_(1).jpg"
        assert media.stage_path.exists()

    def test_staging_name_truncated_for_photos_limit(self, tmp_path: Path) -> None:
        """Ensure staged filenames obey Apple Photos 60-char limit (including extension)."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        long_name = "a" * 120
        photo = source_dir / f"{long_name}.jpg"
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
        stage_media([media], staging)

        assert media.stage_path is not None
        assert len(media.stage_path.name) <= 60

    def test_copy_mode_keeps_originals(self, tmp_path: Path) -> None:
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
        stage_media([media], staging, copy_files=True)

        assert media.stage_path is not None
        assert media.stage_path.exists()
        assert photo.exists(), "Original file should remain when using --copy"

    def test_spaces_are_replaced_with_underscores(self, tmp_path: Path) -> None:
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        photo = source_dir / "my photo name.jpg"
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
        stage_media([media], staging)

        assert media.stage_path is not None
        assert " " not in media.stage_path.name
        assert "my_photo_name" in media.stage_path.stem

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
        stage_media(media_files, staging)

        # Verify each file has suffix before extension
        for i, (media, ext) in enumerate(zip(media_files, extensions), start=1):
            assert media.stage_path is not None
            assert_staged_name(media.stage_path.name, f"_({i})", ext)
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

            skipped_suffixes = set()
            for media in skipped_media:
                assert media.stage_path is not None
                name = media.stage_path.name
                match = STAGING_NAME_RE.match(name)
                if match:
                    skipped_suffixes.add(match.group("suffix"))
                else:
                    legacy = re.match(r"^.* \(([0-9-]+)\)\.[^.]+$", name)
                    assert legacy, name
                    skipped_suffixes.add(f"({legacy.group(1)})")
            assert skipped_suffixes == {"(2)", "(4)"}

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

            with pytest.raises(
                RuntimeError,
                match="Photos import failed.*-1728.*Photos.app not running",
            ):
                import_folder_to_photos(
                    staging_dir=staging,
                    media_files=[media],
                    album_name="Test Album",
                    skip_duplicates=True,
                )

    def test_import_folder_to_photos_appleevent_timeout_abort(self, tmp_path: Path) -> None:
        """Test that AppleEvent timeout (-1712) is handled with user abort."""
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

        # Mock AppleScript returning error -1712 (AppleEvent timed out)
        mock_output = "ERR\t-1712\tAppleEvent timed out"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=mock_output,
                stderr="",
            )
            # Mock user typing 'abort' to cancel
            with patch("builtins.input", return_value="abort"):
                with pytest.raises(
                    RuntimeError,
                    match="Photos import aborted by user after AppleEvent timeout",
                ):
                    import_folder_to_photos(
                        staging_dir=staging,
                        media_files=[media],
                        album_name="Test Album",
                        skip_duplicates=True,
                    )

    def test_import_folder_to_photos_trimmed_suffix(self, tmp_path: Path) -> None:
        """Photos may drop the SMM staging suffix; reconciliation should still succeed."""
        src_dir = tmp_path / "src"
        staging = tmp_path / "staging"
        src_dir.mkdir()
        staging.mkdir()

        file_with_suffix = src_dir / "foo (100).png"
        file_with_suffix.write_bytes(b"test")
        plain_file = src_dir / "bar.png"
        plain_file.write_bytes(b"test")

        media1 = MediaFile(
            source=file_with_suffix,
            kind="image",
            extension=".png",
            format_name="png",
            compatible=True,
            original_suffix=".png",
            rule_id="R-IMG-001",
            action="import",
            requires_processing=False,
            notes="Test",
        )
        media2 = MediaFile(
            source=plain_file,
            kind="image",
            extension=".png",
            format_name="png",
            compatible=True,
            original_suffix=".png",
            rule_id="R-IMG-001",
            action="import",
            requires_processing=False,
            notes="Test",
        )

        staging_originals = stage_media([media1, media2], staging)
        assert staging_originals.exists()

        staged_name1 = media1.stage_path.name
        staged_name2 = media2.stage_path.name

        # Photos returns one name without the appended staging suffix
        # Staging format: <stem>__SMM<token>___(<number>)<ext>
        match = re.match(r"(.*)__SMM[A-Za-z0-9]+___\(\d+\)(\.[^.]+)$", staged_name1)
        assert match is not None, f"Unexpected staging name format: {staged_name1}"
        trimmed_name1 = f"{match.group(1)}{match.group(2)}"

        single_token_name = re.sub(r"(__SMM[0-9A-Za-z]+)__", r"\1_", staged_name1)
        extra_token_name = single_token_name.replace("_ ", "_") + "_62abc123_SMMdeadbeef__"

        returned_names = "\n".join(
            [
                f"FN\t{trimmed_name1}",
                f"FN\t{extra_token_name}",
                f"FN\t{staged_name2}",
            ]
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=returned_names, stderr="")

            imported, skipped, skipped_media = import_folder_to_photos(
                staging_dir=staging,
                media_files=[media1, media2],
                album_name="Album",
                skip_duplicates=True,
            )

        assert imported == 2
        assert skipped == 0
        assert not skipped_media

    def test_import_folder_to_photos_rejection_log(self, tmp_path: Path) -> None:
        """Skipped media should be recorded in a dedicated rejection log."""
        src_dir = tmp_path / "src"
        staging = tmp_path / "staging"
        src_dir.mkdir()
        staging.mkdir()

        media_files = []
        for idx in range(2):
            file_path = src_dir / f"clip{idx}.mp4"
            file_path.write_bytes(b"fake")
            media = MediaFile(
                source=file_path,
                kind="video",
                extension=".mp4",
                format_name="mp4",
                compatible=True,
                original_suffix=".mp4",
                rule_id="R-VID-001",
                action="import",
                requires_processing=False,
                notes="Test",
            )
            media_files.append(media)

        stage_media(media_files, staging)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            imported, skipped, skipped_media = import_folder_to_photos(
                staging_dir=staging,
                media_files=media_files,
                album_name="Album",
                skip_duplicates=True,
            )

        assert imported == 0
        assert skipped == 2
        assert len(skipped_media) == 2

        rejection_logs = sorted((staging.parent).glob("Photos_rejections_*.txt"))
        assert rejection_logs, "Expected Photos rejection log to be created"
        log_content = rejection_logs[-1].read_text(encoding="utf-8")
        for media in media_files:
            staged_name = media.stage_path.name if media.stage_path else ""
            assert staged_name in log_content


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
        monkeypatch.setattr(
            "sys.argv",
            ["smart-media-manager", "--album", "My Custom Album", str(tmp_path)],
        )
        args = parse_args()
        assert args.album == "My Custom Album"

    def test_skip_duplicate_check_argument_default(self, tmp_path: Path, monkeypatch) -> None:
        """Test --skip-duplicate-check is False by default (duplicate checking enabled)."""
        monkeypatch.setattr("sys.argv", ["smart-media-manager", str(tmp_path)])
        args = parse_args()
        assert hasattr(args, "skip_duplicate_check")
        assert args.skip_duplicate_check is False

    def test_skip_duplicate_check_argument_enabled(self, tmp_path: Path, monkeypatch) -> None:
        """Test --skip-duplicate-check flag when enabled."""
        monkeypatch.setattr("sys.argv", ["smart-media-manager", "--skip-duplicate-check", str(tmp_path)])
        args = parse_args()
        assert args.skip_duplicate_check is True

    def test_both_arguments_together(self, tmp_path: Path, monkeypatch) -> None:
        """Test using both --album and --skip-duplicate-check together."""
        monkeypatch.setattr(
            "sys.argv",
            [
                "smart-media-manager",
                "--album",
                "Test Album",
                "--skip-duplicate-check",
                str(tmp_path),
            ],
        )
        args = parse_args()
        assert args.album == "Test Album"
        assert args.skip_duplicate_check is True
        assert args.path == tmp_path

    def test_max_image_pixels_default(self, tmp_path: Path, monkeypatch) -> None:
        """Test --max-image-pixels defaults to disabled."""
        monkeypatch.delenv("SMART_MEDIA_MANAGER_MAX_IMAGE_PIXELS", raising=False)
        monkeypatch.setattr("sys.argv", ["smart-media-manager", str(tmp_path)])
        args = parse_args()
        assert args.max_image_pixels is None

    def test_max_image_pixels_custom(self, tmp_path: Path, monkeypatch) -> None:
        """Test --max-image-pixels with an explicit value."""
        monkeypatch.setattr(
            "sys.argv",
            ["smart-media-manager", "--max-image-pixels", "12345", str(tmp_path)],
        )
        args = parse_args()
        assert args.max_image_pixels == 12345

    def test_max_image_pixels_env_override(self, tmp_path: Path, monkeypatch) -> None:
        """Test SMART_MEDIA_MANAGER_MAX_IMAGE_PIXELS applies when CLI flag is omitted."""
        monkeypatch.setenv("SMART_MEDIA_MANAGER_MAX_IMAGE_PIXELS", "98765")
        monkeypatch.setattr("sys.argv", ["smart-media-manager", str(tmp_path)])
        args = parse_args()
        assert args.max_image_pixels == 98765

    def test_short_flag_recursive(self, tmp_path: Path, monkeypatch) -> None:
        """Test -r short flag for --recursive."""
        monkeypatch.setattr("sys.argv", ["smart-media-manager", "-r", str(tmp_path)])
        args = parse_args()
        assert args.recursive is True

    def test_short_flag_delete(self, tmp_path: Path, monkeypatch) -> None:
        """Test -d short flag for --delete."""
        monkeypatch.setattr("sys.argv", ["smart-media-manager", "-d", str(tmp_path)])
        args = parse_args()
        assert args.delete is True

    def test_short_flag_copy(self, tmp_path: Path, monkeypatch) -> None:
        """Test -c short flag for --copy."""
        monkeypatch.setattr("sys.argv", ["smart-media-manager", "-c", str(tmp_path)])
        args = parse_args()
        assert args.copy_mode is True

    def test_combined_short_flags(self, tmp_path: Path, monkeypatch) -> None:
        """Test combining multiple short flags."""
        monkeypatch.setattr("sys.argv", ["smart-media-manager", "-r", "-c", "-n", str(tmp_path)])
        args = parse_args()
        assert args.recursive is True
        assert args.copy_mode is True
        assert args.dry_run is True
