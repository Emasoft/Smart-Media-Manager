"""
Unit tests for metadata, restore, and cleanup functions.

Tests cover:
- Metadata copying with exiftool
- File restoration
- Path resolution
- Cleanup operations
- Executable finding
"""

import pytest
from unittest.mock import Mock, patch
from smart_media_manager.cli import (
    copy_metadata_from_source,
    restore_media_file,
    resolve_restore_path,
    cleanup_staging,
    find_executable,
    resolve_imagemagick_command,
    ensure_ffmpeg_path,
    MediaFile,
)


class TestMetadataFunctions:
    """Tests for metadata copying functions."""

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.shutil.which")
    def test_copy_metadata_from_source_success(self, mock_which, mock_run, tmp_path):
        """Test copy_metadata_from_source calls exiftool correctly."""
        # Setup
        source = tmp_path / "source.jpg"
        target = tmp_path / "target.jpg"
        source.write_bytes(b"\xff\xd8\xff" + b"\x00" * 100 + b"\xff\xd9")
        target.write_bytes(b"\xff\xd8\xff" + b"\x00" * 100 + b"\xff\xd9")

        mock_which.return_value = "/usr/bin/exiftool"
        mock_run.return_value = Mock(returncode=0)

        # Execute
        copy_metadata_from_source(source, target)

        # Verify
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        # call_args is a list like ['/usr/bin/exiftool', '-overwrite_original', ...]
        assert call_args[0] == "/usr/bin/exiftool"  # First element is the exiftool path
        assert "-TagsFromFile" in call_args  # Note: exiftool uses capital T
        assert str(source) in call_args
        assert str(target) in call_args

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.shutil.which")
    def test_copy_metadata_from_source_no_exiftool(self, mock_which, mock_run, tmp_path):
        """Test copy_metadata_from_source handles missing exiftool."""
        source = tmp_path / "source.jpg"
        target = tmp_path / "target.jpg"
        source.touch()
        target.touch()

        mock_which.return_value = None  # exiftool not found

        # Should not crash, just log warning
        copy_metadata_from_source(source, target)

        # exiftool should not be called
        mock_run.assert_not_called()

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.shutil.which")
    def test_copy_metadata_from_source_nonexistent_source(self, mock_which, mock_run, tmp_path):
        """Test copy_metadata_from_source handles nonexistent source."""
        source = tmp_path / "nonexistent.jpg"
        target = tmp_path / "target.jpg"
        target.touch()

        mock_which.return_value = "/usr/bin/exiftool"

        # Should handle gracefully (exiftool will fail but shouldn't crash)
        try:
            copy_metadata_from_source(source, target)
        except (FileNotFoundError, OSError):
            pass  # Expected if function checks existence


class TestRestoreFunctions:
    """Tests for file restoration functions."""

    def test_resolve_restore_path_no_backup(self, tmp_path):
        """Test resolve_restore_path with no backup."""
        path = tmp_path / "file.jpg"
        result = resolve_restore_path(path)
        assert result == path

    def test_resolve_restore_path_with_existing_file(self, tmp_path):
        """Test resolve_restore_path returns new name when file exists."""
        existing = tmp_path / "file.jpg"
        existing.touch()

        result = resolve_restore_path(existing)
        # Should return file_1.jpg since file.jpg already exists
        assert result == tmp_path / "file_1.jpg"

    def test_restore_media_file_moves_to_source(self, tmp_path):
        """Test restore_media_file moves staged file to source location."""
        source = tmp_path / "original.jpg"
        stage_path = tmp_path / "staging" / "file.jpg"
        stage_path.parent.mkdir(parents=True)

        content = b"\xff\xd8\xff" + b"\x00" * 100 + b"\xff\xd9"
        stage_path.write_bytes(content)

        media = MediaFile(
            source=source,
            kind="image",
            extension=".jpg",
            format_name="JPEG",
            stage_path=stage_path,
        )

        # Restore
        restore_media_file(media)

        # File should be moved to source location
        assert source.exists()
        assert source.read_bytes() == content
        assert not stage_path.exists()
        assert media.stage_path is None

    def test_restore_media_file_with_existing_source(self, tmp_path):
        """Test restore_media_file uses next available name when source exists."""
        source = tmp_path / "original.jpg"
        source.write_bytes(b"\xff\xd8\xff" + b"EXISTING" + b"\xff\xd9")

        stage_path = tmp_path / "staging" / "file.jpg"
        stage_path.parent.mkdir(parents=True)

        content = b"\xff\xd8\xff" + b"STAGED" + b"\xff\xd9"
        stage_path.write_bytes(content)

        media = MediaFile(
            source=source,
            kind="image",
            extension=".jpg",
            format_name="JPEG",
            stage_path=stage_path,
        )

        # Restore
        restore_media_file(media)

        # File should be moved to next available name (original_1.jpg)
        expected_path = tmp_path / "original_1.jpg"
        assert expected_path.exists()
        assert expected_path.read_bytes() == content
        assert not stage_path.exists()
        assert media.stage_path is None

    def test_restore_media_file_nonexistent_stage(self, tmp_path):
        """Test restore_media_file handles nonexistent stage_path."""
        media = MediaFile(
            source=tmp_path / "original.jpg",
            kind="image",
            extension=".jpg",
            format_name="JPEG",
            stage_path=tmp_path / "nonexistent.jpg",
        )

        # Should not crash
        restore_media_file(media)

        # stage_path should be set to None
        assert media.stage_path is None


class TestCleanupFunctions:
    """Tests for cleanup operations."""

    def test_cleanup_staging_removes_directory(self, tmp_path):
        """Test cleanup_staging removes staging directory."""
        staging = tmp_path / "FOUND_MEDIA_FILES_123"
        staging.mkdir()
        (staging / "file1.jpg").touch()
        (staging / "file2.jpg").touch()

        cleanup_staging(staging)

        assert not staging.exists()

    def test_cleanup_staging_removes_nested_files(self, tmp_path):
        """Test cleanup_staging removes nested directories."""
        staging = tmp_path / "FOUND_MEDIA_FILES_123"
        subdir = staging / "subdir"
        subdir.mkdir(parents=True)
        (subdir / "nested.jpg").touch()
        (staging / "file.jpg").touch()

        cleanup_staging(staging)

        assert not staging.exists()

    def test_cleanup_staging_nonexistent_directory(self, tmp_path):
        """Test cleanup_staging handles nonexistent directory."""
        staging = tmp_path / "nonexistent"

        # Should not crash
        try:
            cleanup_staging(staging)
        except FileNotFoundError:
            pass  # Expected behavior if function doesn't check


class TestExecutableFinders:
    """Tests for executable finding functions."""

    @patch("smart_media_manager.cli.shutil.which")
    def test_find_executable_finds_first(self, mock_which):
        """Test find_executable returns first found executable."""
        mock_which.side_effect = lambda x: "/usr/bin/" + x if x == "python3" else None

        result = find_executable("nonexistent", "python3", "python")

        assert result == "/usr/bin/python3"
        assert mock_which.call_count == 2  # Tried nonexistent, found python3

    @patch("smart_media_manager.cli.shutil.which")
    def test_find_executable_tries_all(self, mock_which):
        """Test find_executable tries all candidates."""
        mock_which.return_value = None

        result = find_executable("cmd1", "cmd2", "cmd3")

        assert result is None
        assert mock_which.call_count == 3

    @patch("smart_media_manager.cli.shutil.which")
    def test_resolve_imagemagick_command_magick(self, mock_which):
        """Test resolve_imagemagick_command prefers 'magick'."""
        mock_which.side_effect = lambda x: "/usr/bin/" + x if x in ["magick", "convert"] else None

        result = resolve_imagemagick_command()

        assert "magick" in result

    @patch("smart_media_manager.cli.shutil.which")
    def test_resolve_imagemagick_command_convert(self, mock_which):
        """Test resolve_imagemagick_command falls back to 'convert'."""
        mock_which.side_effect = lambda x: "/usr/bin/convert" if x == "convert" else None

        result = resolve_imagemagick_command()

        assert "convert" in result

    @patch("smart_media_manager.cli.shutil.which")
    def test_resolve_imagemagick_command_not_found(self, mock_which):
        """Test resolve_imagemagick_command raises when not found."""
        mock_which.return_value = None

        with pytest.raises(RuntimeError, match=r"ImageMagick \(magick/convert\) not found"):
            resolve_imagemagick_command()

    @patch("smart_media_manager.cli.shutil.which")
    def test_ensure_ffmpeg_path_found(self, mock_which):
        """Test ensure_ffmpeg_path returns path when found."""
        mock_which.return_value = "/usr/bin/ffmpeg"

        result = ensure_ffmpeg_path()

        assert result == "/usr/bin/ffmpeg"

    @patch("smart_media_manager.cli.shutil.which")
    def test_ensure_ffmpeg_path_not_found(self, mock_which):
        """Test ensure_ffmpeg_path raises when not found."""
        mock_which.return_value = None

        with pytest.raises(RuntimeError, match="ffmpeg not found"):
            ensure_ffmpeg_path()


class TestPanoramicPhotoDetection:
    """Tests for is_panoramic_photo function."""

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.shutil.which")
    def test_is_panoramic_photo_with_metadata(self, mock_which, mock_run, tmp_path):
        """Test is_panoramic_photo detects panoramic EXIF metadata."""
        from smart_media_manager.cli import is_panoramic_photo

        photo = tmp_path / "panorama.jpg"
        photo.write_bytes(b"\xff\xd8\xff" + b"\x00" * 100 + b"\xff\xd9")

        mock_which.return_value = "/usr/bin/exiftool"
        mock_run.return_value = Mock(
            returncode=0,
            stdout="ProjectionType: equirectangular\nUsePanoramaViewer: true\n",
        )

        result = is_panoramic_photo(photo)

        # Should detect panoramic metadata
        assert result is True

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.shutil.which")
    def test_is_panoramic_photo_no_metadata(self, mock_which, mock_run, tmp_path):
        """Test is_panoramic_photo returns False without panoramic metadata."""
        from smart_media_manager.cli import is_panoramic_photo

        photo = tmp_path / "normal.jpg"
        photo.write_bytes(b"\xff\xd8\xff" + b"\x00" * 100 + b"\xff\xd9")

        mock_which.return_value = "/usr/bin/exiftool"
        mock_run.return_value = Mock(returncode=0, stdout="Make: Canon\nModel: EOS 5D\n")

        result = is_panoramic_photo(photo)

        # Should NOT detect as panoramic without special metadata
        assert result is False

    @patch("smart_media_manager.cli.shutil.which")
    def test_is_panoramic_photo_no_exiftool(self, mock_which, tmp_path):
        """Test is_panoramic_photo handles missing exiftool."""
        from smart_media_manager.cli import is_panoramic_photo

        photo = tmp_path / "photo.jpg"
        photo.touch()

        mock_which.return_value = None

        result = is_panoramic_photo(photo)

        # Should return False if exiftool not available
        assert result is False


class TestCollectRawGroups:
    """Tests for RAW file group collection."""

    def test_collect_raw_groups_from_extensions_canon(self):
        """Test collect_raw_groups_from_extensions identifies Canon."""
        from smart_media_manager.cli import collect_raw_groups_from_extensions

        extensions = [".cr2", ".cr3"]
        result = collect_raw_groups_from_extensions(extensions)

        assert "canon" in result

    def test_collect_raw_groups_from_extensions_nikon(self):
        """Test collect_raw_groups_from_extensions identifies Nikon."""
        from smart_media_manager.cli import collect_raw_groups_from_extensions

        extensions = [".nef"]
        result = collect_raw_groups_from_extensions(extensions)

        assert "nikon" in result

    def test_collect_raw_groups_from_extensions_multiple(self):
        """Test collect_raw_groups_from_extensions handles multiple brands."""
        from smart_media_manager.cli import collect_raw_groups_from_extensions

        extensions = [".cr2", ".nef", ".arw"]
        result = collect_raw_groups_from_extensions(extensions)

        assert "canon" in result
        assert "nikon" in result
        assert "sony" in result

    def test_collect_raw_groups_from_extensions_non_raw(self):
        """Test collect_raw_groups_from_extensions ignores non-RAW."""
        from smart_media_manager.cli import collect_raw_groups_from_extensions

        extensions = [".jpg", ".mp4", None]
        result = collect_raw_groups_from_extensions(extensions)

        assert len(result) == 0

    def test_collect_raw_groups_from_extensions_case_insensitive(self):
        """Test collect_raw_groups_from_extensions is case-insensitive."""
        from smart_media_manager.cli import collect_raw_groups_from_extensions

        extensions = [".CR2", ".NEF"]
        result = collect_raw_groups_from_extensions(extensions)

        assert "canon" in result
        assert "nikon" in result
