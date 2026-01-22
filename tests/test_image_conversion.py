"""
Unit tests for image conversion functions.

Tests cover:
- convert_to_png: FFmpeg-based PNG conversion
- convert_to_tiff: ImageMagick-based TIFF conversion
- convert_image: FFmpeg-based JPEG conversion
- convert_to_heic_lossless: HEIC lossless encoding (handles JPEG XL)

All use fail-fast approach with no backups.
"""

from pathlib import Path
from unittest.mock import patch
import pytest


# Path to test samples
SAMPLES_DIR = Path(__file__).parent / "samples" / "ci"
TEST_IMAGE = SAMPLES_DIR / "images" / "test_image.jpg"


class TestConvertToPng:
    """Tests for convert_to_png function."""

    @patch("smart_media_manager.cli.copy_metadata_from_source")
    @patch("smart_media_manager.cli.run_command_with_progress")
    def test_convert_to_png_succeeds_and_updates_media(self, mock_run, mock_copy, tmp_path):
        """Test convert_to_png succeeds and updates MediaFile."""
        from smart_media_manager.cli import convert_to_png, MediaFile

        source = tmp_path / "source.webp"
        source.touch()

        media = MediaFile(
            source=source,
            kind="image",
            extension=".webp",
            format_name="webp",
            stage_path=source,
        )

        # Mock successful conversion
        mock_run.return_value = None

        convert_to_png(media)

        # Should call ffmpeg with correct args
        assert mock_run.called
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "ffmpeg"
        assert "-i" in call_args
        assert str(source) in call_args
        assert "-pix_fmt" in call_args
        assert "rgba" in call_args

        # Should copy metadata
        mock_copy.assert_called_once()

        # Should delete original
        assert not source.exists()

        # Should update MediaFile
        assert media.stage_path.suffix == ".png"
        assert media.extension == ".png"
        assert media.format_name == "png"
        assert media.requires_processing is False
        assert media.compatible is True

    @patch("smart_media_manager.cli.run_command_with_progress")
    def test_convert_to_png_raises_when_stage_path_missing(self, mock_run):
        """Test convert_to_png raises RuntimeError when stage_path is None."""
        from smart_media_manager.cli import convert_to_png, MediaFile

        media = MediaFile(
            source=Path("test.webp"),
            kind="image",
            extension=".webp",
            format_name="webp",
            stage_path=None,  # Missing!
        )

        with pytest.raises(RuntimeError, match="Stage path missing"):
            convert_to_png(media)

        # Should not call ffmpeg
        mock_run.assert_not_called()

    @patch("smart_media_manager.cli.copy_metadata_from_source")
    @patch("smart_media_manager.cli.run_command_with_progress")
    def test_convert_to_png_cleans_up_on_failure(self, mock_run, mock_copy, tmp_path):
        """Test convert_to_png cleans up partial target on failure."""
        from smart_media_manager.cli import convert_to_png, MediaFile

        source = tmp_path / "source.webp"
        source.write_bytes(b"fake webp data")

        media = MediaFile(
            source=source,
            kind="image",
            extension=".webp",
            format_name="webp",
            stage_path=source,
        )

        # Mock conversion failure that creates partial file BEFORE failing
        # This simulates ffmpeg starting conversion but failing midway
        def mock_run_with_partial_file(cmd, description):
            # Extract target path from ffmpeg command (last argument)
            target_path = Path(cmd[-1])
            # Simulate partial conversion by creating incomplete file
            target_path.write_bytes(b"incomplete png data")
            # Then fail to simulate conversion error
            raise RuntimeError("ffmpeg failed")

        mock_run.side_effect = mock_run_with_partial_file

        with pytest.raises(RuntimeError, match="ffmpeg failed"):
            convert_to_png(media)

        # Original should still exist
        assert source.exists()
        assert source.read_bytes() == b"fake webp data"

        # Partial target should be cleaned up by exception handler
        png_files = list(tmp_path.glob("*.png"))
        assert len(png_files) == 0, f"Expected cleanup to remove partial PNG, but found: {png_files}"


class TestConvertToTiff:
    """Tests for convert_to_tiff function."""

    @patch("smart_media_manager.cli.copy_metadata_from_source")
    @patch("smart_media_manager.cli.run_command_with_progress")
    @patch("smart_media_manager.cli.resolve_imagemagick_command")
    def test_convert_to_tiff_succeeds_and_updates_media(self, mock_resolve, mock_run, mock_copy, tmp_path):
        """Test convert_to_tiff succeeds and updates MediaFile."""
        from smart_media_manager.cli import convert_to_tiff, MediaFile

        source = tmp_path / "source.psd"
        source.touch()

        media = MediaFile(
            source=source,
            kind="image",
            extension=".psd",
            format_name="psd",
            stage_path=source,
        )

        # Mock ImageMagick command resolution
        mock_resolve.return_value = "magick"

        # Mock successful conversion
        mock_run.return_value = None

        convert_to_tiff(media)

        # Should call ImageMagick with correct args
        assert mock_run.called
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "magick"
        assert str(source) in call_args
        assert "-alpha" in call_args
        assert "on" in call_args
        assert "-depth" in call_args
        assert "16" in call_args
        assert "-flatten" in call_args

        # Should copy metadata
        mock_copy.assert_called_once()

        # Should delete original
        assert not source.exists()

        # Should update MediaFile
        assert media.stage_path.suffix == ".tiff"
        assert media.extension == ".tiff"
        assert media.format_name == "tiff"
        assert media.requires_processing is False
        assert media.compatible is True

    @patch("smart_media_manager.cli.resolve_imagemagick_command")
    @patch("smart_media_manager.cli.run_command_with_progress")
    def test_convert_to_tiff_raises_when_stage_path_missing(self, mock_run, mock_resolve):
        """Test convert_to_tiff raises RuntimeError when stage_path is None."""
        from smart_media_manager.cli import convert_to_tiff, MediaFile

        media = MediaFile(
            source=Path("test.psd"),
            kind="image",
            extension=".psd",
            format_name="psd",
            stage_path=None,  # Missing!
        )

        with pytest.raises(RuntimeError, match="Stage path missing"):
            convert_to_tiff(media)

        # Should not call ImageMagick
        mock_run.assert_not_called()

    @patch("smart_media_manager.cli.copy_metadata_from_source")
    @patch("smart_media_manager.cli.run_command_with_progress")
    @patch("smart_media_manager.cli.resolve_imagemagick_command")
    def test_convert_to_tiff_cleans_up_on_failure(self, mock_resolve, mock_run, mock_copy, tmp_path):
        """Test convert_to_tiff cleans up partial target on failure."""
        from smart_media_manager.cli import convert_to_tiff, MediaFile

        source = tmp_path / "source.psd"
        source.write_bytes(b"fake psd data")

        media = MediaFile(
            source=source,
            kind="image",
            extension=".psd",
            format_name="psd",
            stage_path=source,
        )

        mock_resolve.return_value = "magick"

        # Mock conversion failure that creates partial file BEFORE failing
        # This simulates ImageMagick starting conversion but failing midway
        def mock_run_with_partial_file(cmd, description):
            # Extract target path from ImageMagick command (last argument)
            target_path = Path(cmd[-1])
            # Simulate partial conversion by creating incomplete file
            target_path.write_bytes(b"incomplete tiff data")
            # Then fail to simulate conversion error
            raise RuntimeError("ImageMagick failed")

        mock_run.side_effect = mock_run_with_partial_file

        with pytest.raises(RuntimeError, match="ImageMagick failed"):
            convert_to_tiff(media)

        # Original should still exist
        assert source.exists()
        assert source.read_bytes() == b"fake psd data"

        # Partial target should be cleaned up by exception handler
        tiff_files = list(tmp_path.glob("*.tiff"))
        assert len(tiff_files) == 0, f"Expected cleanup to remove partial TIFF, but found: {tiff_files}"


class TestConvertImage:
    """Tests for convert_image function."""

    @patch("smart_media_manager.cli.run_checked")
    def test_convert_image_succeeds_and_updates_media(self, mock_run, tmp_path):
        """Test convert_image succeeds and updates MediaFile."""
        from smart_media_manager.cli import convert_image, MediaFile

        source = tmp_path / "source.bmp"
        source.touch()

        media = MediaFile(
            source=source,
            kind="image",
            extension=".bmp",
            format_name="bmp",
            stage_path=source,
        )

        # Mock successful conversion
        mock_run.return_value = None

        convert_image(media)

        # Should call ffmpeg with correct args
        assert mock_run.called
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "ffmpeg"
        assert "-i" in call_args
        assert str(source) in call_args
        assert "-map_metadata" in call_args
        assert "0" in call_args
        assert "-c:v" in call_args
        assert "mjpeg" in call_args
        assert "-qscale:v" in call_args
        assert "2" in call_args

        # Should delete original
        assert not source.exists()

        # Should update MediaFile
        assert media.stage_path.suffix == ".jpg"
        assert media.extension == ".jpg"
        assert media.format_name == "jpeg"
        assert media.compatible is True

    @patch("smart_media_manager.cli.run_checked")
    def test_convert_image_fails_when_stage_path_missing(self, mock_run):
        """Test convert_image fails when stage_path is None."""
        from smart_media_manager.cli import convert_image, MediaFile

        media = MediaFile(
            source=Path("test.bmp"),
            kind="image",
            extension=".bmp",
            format_name="bmp",
            stage_path=None,  # Missing!
        )

        # Should fail assertion
        with pytest.raises(AssertionError):
            convert_image(media)

        # Should not call ffmpeg
        mock_run.assert_not_called()

    @patch("smart_media_manager.cli.run_checked")
    def test_convert_image_cleans_up_on_failure(self, mock_run, tmp_path):
        """Test convert_image cleans up partial target on failure."""
        from smart_media_manager.cli import convert_image, MediaFile

        source = tmp_path / "source.bmp"
        source.write_bytes(b"fake bmp data")

        media = MediaFile(
            source=source,
            kind="image",
            extension=".bmp",
            format_name="bmp",
            stage_path=source,
        )

        # Mock conversion failure that creates partial file BEFORE failing
        # This simulates ffmpeg starting conversion but failing midway
        def mock_run_with_partial_file(cmd):
            # Extract target path from ffmpeg command (last argument)
            target_path = Path(cmd[-1])
            # Simulate partial conversion by creating incomplete file
            target_path.write_bytes(b"incomplete jpeg data")
            # Then fail to simulate conversion error
            raise RuntimeError("ffmpeg failed")

        mock_run.side_effect = mock_run_with_partial_file

        with pytest.raises(RuntimeError, match="ffmpeg failed"):
            convert_image(media)

        # Original should still exist
        assert source.exists()
        assert source.read_bytes() == b"fake bmp data"

        # Partial target should be cleaned up by exception handler
        jpg_files = list(tmp_path.glob("*.jpg"))
        assert len(jpg_files) == 0, f"Expected cleanup to remove partial JPEG, but found: {jpg_files}"


class TestConvertToHeicLossless:
    """Tests for convert_to_heic_lossless function."""

    @patch("smart_media_manager.cli.copy_metadata_from_source")
    @patch("smart_media_manager.cli.run_command_with_progress")
    @patch("smart_media_manager.cli.find_executable")
    def test_convert_to_heic_lossless_with_heif_enc(self, mock_find, mock_run, mock_copy, tmp_path):
        """Test convert_to_heic_lossless uses heif-enc when available."""
        from smart_media_manager.cli import convert_to_heic_lossless, MediaFile

        source = tmp_path / "source.png"
        source.touch()

        media = MediaFile(
            source=source,
            kind="image",
            extension=".png",
            format_name="png",
            stage_path=source,
        )

        # Mock heif-enc available
        mock_find.return_value = "/usr/local/bin/heif-enc"
        mock_run.return_value = None

        convert_to_heic_lossless(media)

        # Should use heif-enc
        assert mock_run.called
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "/usr/local/bin/heif-enc"
        assert "--lossless" in call_args
        assert str(source) in call_args

        # Should copy metadata and update MediaFile
        mock_copy.assert_called_once()
        assert media.extension == ".heic"
        assert media.format_name == "heic"
        assert media.compatible is True

    @patch("smart_media_manager.cli.copy_metadata_from_source")
    @patch("smart_media_manager.cli.run_command_with_progress")
    @patch("smart_media_manager.cli.ensure_ffmpeg_path")
    @patch("smart_media_manager.cli.find_executable")
    def test_convert_to_heic_lossless_with_ffmpeg_fallback(self, mock_find, mock_ffmpeg, mock_run, mock_copy, tmp_path):
        """Test convert_to_heic_lossless falls back to ffmpeg when heif-enc unavailable."""
        from smart_media_manager.cli import convert_to_heic_lossless, MediaFile

        source = tmp_path / "source.png"
        source.touch()

        media = MediaFile(
            source=source,
            kind="image",
            extension=".png",
            format_name="png",
            stage_path=source,
        )

        # Mock heif-enc NOT available
        mock_find.return_value = None
        mock_ffmpeg.return_value = "ffmpeg"
        mock_run.return_value = None

        convert_to_heic_lossless(media)

        # Should use ffmpeg with libx265
        assert mock_run.called
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "ffmpeg"
        assert "-c:v" in call_args
        assert "libx265" in call_args
        assert "lossless=1" in call_args

        # Should copy metadata and update MediaFile
        mock_copy.assert_called_once()
        assert media.extension == ".heic"

    @patch("smart_media_manager.cli.copy_metadata_from_source")
    @patch("smart_media_manager.cli.run_command_with_progress")
    @patch("smart_media_manager.cli.find_executable")
    def test_convert_to_heic_lossless_handles_jxl_with_djxl(self, mock_find, mock_run, mock_copy, tmp_path):
        """Test convert_to_heic_lossless decodes JXL with djxl before encoding."""
        from smart_media_manager.cli import convert_to_heic_lossless, MediaFile

        source = tmp_path / "source.jxl"
        source.touch()

        media = MediaFile(
            source=source,
            kind="image",
            extension=".jxl",
            format_name="jxl",
            stage_path=source,
        )

        # Mock djxl available, heif-enc available
        mock_find.side_effect = [
            "/usr/local/bin/djxl",  # First call for djxl
            "/usr/local/bin/heif-enc",  # Second call for heif-enc
        ]
        mock_run.return_value = None

        convert_to_heic_lossless(media)

        # Should call run_command_with_progress twice (djxl + heif-enc)
        assert mock_run.call_count == 2

        # First call should be djxl
        first_call = mock_run.call_args_list[0][0][0]
        assert first_call[0] == "/usr/local/bin/djxl"
        assert "--lossless" in first_call

        # Second call should be heif-enc
        second_call = mock_run.call_args_list[1][0][0]
        assert second_call[0] == "/usr/local/bin/heif-enc"
        assert "--lossless" in second_call

        # Should update MediaFile
        assert media.extension == ".heic"

    @patch("smart_media_manager.cli.convert_to_tiff")
    @patch("smart_media_manager.cli.find_executable")
    def test_convert_to_heic_lossless_falls_back_to_tiff_for_jxl_without_djxl(self, mock_find, mock_convert, tmp_path):
        """Test convert_to_heic_lossless falls back to TIFF when djxl unavailable for JXL."""
        from smart_media_manager.cli import convert_to_heic_lossless, MediaFile

        source = tmp_path / "source.jxl"
        source.touch()

        media = MediaFile(
            source=source,
            kind="image",
            extension=".jxl",
            format_name="jxl",
            stage_path=source,
        )

        # Mock djxl NOT available
        mock_find.return_value = None

        convert_to_heic_lossless(media)

        # Should call convert_to_tiff instead
        mock_convert.assert_called_once_with(media)

    @patch("smart_media_manager.cli.run_command_with_progress")
    def test_convert_to_heic_lossless_raises_when_stage_path_missing(self, mock_run):
        """Test convert_to_heic_lossless raises RuntimeError when stage_path is None."""
        from smart_media_manager.cli import convert_to_heic_lossless, MediaFile

        media = MediaFile(
            source=Path("test.png"),
            kind="image",
            extension=".png",
            format_name="png",
            stage_path=None,  # Missing!
        )

        with pytest.raises(RuntimeError, match="Stage path missing"):
            convert_to_heic_lossless(media)

        mock_run.assert_not_called()

    @patch("smart_media_manager.cli.copy_metadata_from_source")
    @patch("smart_media_manager.cli.run_command_with_progress")
    @patch("smart_media_manager.cli.find_executable")
    def test_convert_to_heic_lossless_cleans_up_on_failure(self, mock_find, mock_run, mock_copy, tmp_path):
        """Test convert_to_heic_lossless cleans up target and intermediate on failure."""
        from smart_media_manager.cli import convert_to_heic_lossless, MediaFile

        source = tmp_path / "source.png"
        source.write_bytes(b"fake png data")

        media = MediaFile(
            source=source,
            kind="image",
            extension=".png",
            format_name="png",
            stage_path=source,
        )

        # Mock heif-enc available but fails
        mock_find.return_value = "/usr/local/bin/heif-enc"
        mock_run.side_effect = RuntimeError("heif-enc failed")

        with pytest.raises(RuntimeError, match="heif-enc failed"):
            convert_to_heic_lossless(media)

        # Original should still exist
        assert source.exists()
        assert source.read_bytes() == b"fake png data"

        # Partial target should be cleaned up
        heic_files = list(tmp_path.glob("*.heic"))
        assert len(heic_files) == 0
