"""
Unit tests for media refinement and validation functions.

Tests cover:
- refine_image_media: Image corruption detection and PSD validation
- refine_raw_media: RAW file processing with rawpy
- refine_video_media: Video/audio codec validation
- prompt_retry_failed_imports: User input prompting

These functions perform detailed validation and return (media, error) tuples.
"""

from unittest.mock import patch, Mock


class TestPromptRetryFailedImports:
    """Tests for prompt_retry_failed_imports function."""

    @patch("builtins.input")
    def test_prompt_retry_failed_imports_returns_true_for_yes(self, mock_input):
        """Test prompt_retry_failed_imports returns True for 'y' input."""
        from smart_media_manager.cli import prompt_retry_failed_imports

        mock_input.return_value = "y"

        result = prompt_retry_failed_imports()

        assert result is True

    @patch("builtins.input")
    def test_prompt_retry_failed_imports_returns_true_for_full_yes(self, mock_input):
        """Test prompt_retry_failed_imports returns True for 'yes' input."""
        from smart_media_manager.cli import prompt_retry_failed_imports

        mock_input.return_value = "yes"

        result = prompt_retry_failed_imports()

        assert result is True

    @patch("builtins.input")
    def test_prompt_retry_failed_imports_returns_false_for_no(self, mock_input):
        """Test prompt_retry_failed_imports returns False for 'n' input."""
        from smart_media_manager.cli import prompt_retry_failed_imports

        mock_input.return_value = "n"

        result = prompt_retry_failed_imports()

        assert result is False

    @patch("builtins.input")
    def test_prompt_retry_failed_imports_retries_on_invalid_input(self, mock_input):
        """Test prompt_retry_failed_imports retries on invalid input."""
        from smart_media_manager.cli import prompt_retry_failed_imports

        # First two invalid, third valid
        mock_input.side_effect = ["invalid", "maybe", "y"]

        result = prompt_retry_failed_imports()

        assert result is True
        assert mock_input.call_count == 3

    @patch("builtins.input")
    def test_prompt_retry_failed_imports_handles_keyboard_interrupt(self, mock_input):
        """Test prompt_retry_failed_imports handles Ctrl+C gracefully."""
        from smart_media_manager.cli import prompt_retry_failed_imports

        mock_input.side_effect = KeyboardInterrupt()

        result = prompt_retry_failed_imports()

        assert result is False

    @patch("builtins.input")
    def test_prompt_retry_failed_imports_handles_eof_error(self, mock_input):
        """Test prompt_retry_failed_imports handles EOF gracefully."""
        from smart_media_manager.cli import prompt_retry_failed_imports

        mock_input.side_effect = EOFError()

        result = prompt_retry_failed_imports()

        assert result is False


class TestRefineRawMedia:
    """Tests for refine_raw_media function."""

    @patch("smart_media_manager.cli.rawpy")
    def test_refine_raw_media_succeeds_with_valid_raw(self, mock_rawpy, tmp_path):
        """Test refine_raw_media succeeds with valid RAW file."""
        from smart_media_manager.cli import refine_raw_media

        raw_file = tmp_path / "IMG_001.CR3"
        raw_file.touch()

        # Mock rawpy imread
        mock_raw = Mock()
        mock_raw.metadata.camera_make = "Canon"
        mock_raw.metadata.camera_model = "EOS R5"
        mock_rawpy.imread.return_value.__enter__.return_value = mock_raw

        media, error = refine_raw_media(raw_file, [".cr3"])

        assert media is not None
        assert error is None
        assert media.kind == "raw"
        assert media.extension == ".cr3"
        assert media.format_name == "Canon EOS R5"
        assert media.compatible is True
        assert media.original_suffix == ".CR3"

    @patch("smart_media_manager.cli.rawpy")
    def test_refine_raw_media_handles_unsupported_raw(self, mock_rawpy, tmp_path):
        """Test refine_raw_media handles unsupported RAW formats."""
        from smart_media_manager.cli import refine_raw_media
        import rawpy

        raw_file = tmp_path / "IMG_001.DNG"
        raw_file.touch()

        # Mock rawpy raising LibRawFileUnsupportedError
        mock_rawpy.imread.side_effect = rawpy.LibRawFileUnsupportedError("Unsupported")
        mock_rawpy.LibRawFileUnsupportedError = rawpy.LibRawFileUnsupportedError

        media, error = refine_raw_media(raw_file, [".dng"])

        assert media is None
        assert "rawpy unsupported raw" in error

    @patch("smart_media_manager.cli.rawpy")
    def test_refine_raw_media_uses_first_valid_extension_candidate(self, mock_rawpy, tmp_path):
        """Test refine_raw_media uses first valid extension from candidates."""
        from smart_media_manager.cli import refine_raw_media

        raw_file = tmp_path / "IMG_001.nef"
        raw_file.touch()

        mock_raw = Mock()
        mock_raw.metadata.camera_make = "Nikon"
        mock_raw.metadata.camera_model = "D850"
        mock_rawpy.imread.return_value.__enter__.return_value = mock_raw

        # Multiple candidates, should use first valid one
        media, error = refine_raw_media(raw_file, [None, ".nef", ".tiff"])

        assert media.extension == ".nef"

    @patch("smart_media_manager.cli.rawpy")
    def test_refine_raw_media_falls_back_to_file_suffix_when_no_candidates(self, mock_rawpy, tmp_path):
        """Test refine_raw_media falls back to file suffix when no valid candidates."""
        from smart_media_manager.cli import refine_raw_media

        raw_file = tmp_path / "IMG_001.arw"
        raw_file.touch()

        mock_raw = Mock()
        mock_raw.metadata.camera_make = "Sony"
        mock_raw.metadata.camera_model = "A7R IV"
        mock_rawpy.imread.return_value.__enter__.return_value = mock_raw

        # No valid candidates
        media, error = refine_raw_media(raw_file, [None, ".jpg"])

        # Should fall back to file's own suffix
        assert media.extension == ".arw"


class TestRefineImageMedia:
    """Tests for refine_image_media function."""

    def test_refine_image_media_skips_validation_when_flag_set(self, tmp_path):
        """Test refine_image_media skips all validation when flag is True."""
        from smart_media_manager.cli import refine_image_media, MediaFile

        img_file = tmp_path / "test.jpg"
        img_file.touch()

        media = MediaFile(
            source=img_file,
            kind="image",
            extension=".jpg",
            format_name="jpeg",
        )

        media_out, error = refine_image_media(media, skip_compatibility_check=True)

        assert media_out == media
        assert error is None

    def test_refine_image_media_detects_invalid_jpeg_soi(self, tmp_path):
        """Test refine_image_media detects invalid JPEG SOI marker."""
        from smart_media_manager.cli import refine_image_media, MediaFile

        img_file = tmp_path / "test.jpg"
        img_file.write_bytes(b"\x00\x00" + b"\xff\xd9")  # Wrong SOI

        media = MediaFile(
            source=img_file,
            kind="image",
            extension=".jpg",
            format_name="jpeg",
        )

        media_out, error = refine_image_media(media)

        assert media_out is None
        assert "missing SOI marker" in error

    def test_refine_image_media_detects_truncated_jpeg_eoi(self, tmp_path):
        """Test refine_image_media detects missing JPEG EOI marker."""
        from smart_media_manager.cli import refine_image_media, MediaFile

        img_file = tmp_path / "test.jpg"
        img_file.write_bytes(b"\xff\xd8" + b"A" * 100)  # Valid SOI, garbage content

        media = MediaFile(
            source=img_file,
            kind="image",
            extension=".jpg",
            format_name="jpeg",
        )

        media_out, error = refine_image_media(media)

        assert media_out is None
        # Pillow catches truncated/invalid JPEGs with "cannot identify" error
        # (we removed the naive EOI marker check since valid files can have trailing data)
        assert "cannot identify" in error or "invalid image" in error

    def test_refine_image_media_detects_invalid_png_signature(self, tmp_path):
        """Test refine_image_media detects invalid PNG signature."""
        from smart_media_manager.cli import refine_image_media, MediaFile

        img_file = tmp_path / "test.png"
        img_file.write_bytes(b"NOTPNG\r\n\x1a\n" + b"A" * 100)

        media = MediaFile(
            source=img_file,
            kind="image",
            extension=".png",
            format_name="png",
        )

        media_out, error = refine_image_media(media)

        assert media_out is None
        assert "missing signature" in error

    def test_refine_image_media_flags_cmyk_psd_for_conversion(self, tmp_path):
        """Test refine_image_media flags CMYK PSD files for TIFF conversion instead of rejecting."""
        from smart_media_manager.cli import refine_image_media, MediaFile

        psd_file = tmp_path / "test.psd"
        psd_file.touch()

        media = MediaFile(
            source=psd_file,
            kind="image",
            extension=".psd",
            format_name="psd",
            metadata={"psd_color_mode": "cmyk"},
        )

        media_out, error = refine_image_media(media)

        # Should flag for conversion, not reject
        assert media_out is not None
        assert error is None
        assert media_out.action == "convert_to_tiff"
        assert media_out.requires_processing is True
        assert media_out.compatible is False
        assert "CMYK PSD not supported" in media_out.notes


class TestRefineVideoMedia:
    """Tests for refine_video_media function."""

    def test_refine_video_media_skips_validation_when_flag_set(self, tmp_path):
        """Test refine_video_media skips all validation when flag is True."""
        from smart_media_manager.cli import refine_video_media, MediaFile

        vid_file = tmp_path / "test.mp4"
        vid_file.touch()

        media = MediaFile(
            source=vid_file,
            kind="video",
            extension=".mp4",
            format_name="mp4",
        )

        media_out, error = refine_video_media(media, skip_compatibility_check=True)

        assert media_out == media
        assert error is None

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.shutil.which")
    def test_refine_video_media_flags_avc3_for_remux(self, mock_which, mock_run, tmp_path):
        """Test refine_video_media flags avc3 codec tag for remuxing instead of rejecting."""
        from smart_media_manager.cli import refine_video_media, MediaFile

        vid_file = tmp_path / "test.mp4"
        vid_file.touch()

        media = MediaFile(
            source=vid_file,
            kind="video",
            extension=".mp4",
            format_name="mp4",
        )

        mock_which.return_value = "/usr/bin/ffprobe"
        mock_run.return_value = Mock(
            returncode=0,
            stdout="codec_tag_string=avc3\ncodec_name=h264",
        )

        media_out, error = refine_video_media(media)

        # Should flag for remux, not reject
        assert media_out is not None
        assert error is None
        assert media_out.action == "rewrap_to_mp4"
        assert media_out.requires_processing is True
        assert media_out.compatible is False
        assert "avc3" in media_out.notes

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.shutil.which")
    def test_refine_video_media_flags_dolby_vision_for_transcode(self, mock_which, mock_run, tmp_path):
        """Test refine_video_media flags Dolby Vision for transcoding instead of rejecting."""
        from smart_media_manager.cli import refine_video_media, MediaFile

        vid_file = tmp_path / "test.mp4"
        vid_file.touch()

        media = MediaFile(
            source=vid_file,
            kind="video",
            extension=".mp4",
            format_name="mp4",
        )

        mock_which.return_value = "/usr/bin/ffprobe"
        mock_run.return_value = Mock(
            returncode=0,
            stdout="codec_tag_string=dvh1\ncodec_name=hevc",
        )

        media_out, error = refine_video_media(media)

        # Should flag for transcode, not reject
        assert media_out is not None
        assert error is None
        assert media_out.action == "transcode_to_hevc_mp4"
        assert media_out.requires_processing is True
        assert media_out.compatible is False
        assert "Dolby Vision" in media_out.notes

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.shutil.which")
    def test_refine_video_media_accepts_10bit_color(self, mock_which, mock_run, tmp_path):
        """Test refine_video_media accepts 10-bit color depth.

        Note: 10-bit videos are accepted for detection; the format detection
        system handles marking them for transcoding via the action field.
        Apple Photos on modern macOS supports HEVC Main 10 profile.
        """
        from smart_media_manager.cli import refine_video_media, MediaFile

        vid_file = tmp_path / "test.mp4"
        vid_file.touch()

        media = MediaFile(
            source=vid_file,
            kind="video",
            extension=".mp4",
            format_name="mp4",
        )

        mock_which.return_value = "/usr/bin/ffprobe"
        mock_run.return_value = Mock(
            returncode=0,
            stdout="codec_tag_string=hvc1\npix_fmt=yuv420p10le",
        )

        media_out, error = refine_video_media(media)

        # 10-bit videos are now accepted (not rejected) - format system handles transcoding
        assert media_out is not None
        assert error is None

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.shutil.which")
    def test_refine_video_media_flags_opus_audio_for_transcode(self, mock_which, mock_run, tmp_path):
        """Test refine_video_media flags Opus audio for transcoding instead of rejecting."""
        from smart_media_manager.cli import refine_video_media, MediaFile

        vid_file = tmp_path / "test.mp4"
        vid_file.touch()

        # audio_codec must be set for refine_video_media to check it
        # (it's populated during detect_media, not parsed from ffprobe in refinement)
        media = MediaFile(
            source=vid_file,
            kind="video",
            extension=".mp4",
            format_name="mp4",
            audio_codec="opus",
        )

        mock_which.return_value = "/usr/bin/ffprobe"
        mock_run.return_value = Mock(
            returncode=0,
            stdout="codec_tag_string=hvc1\ncodec_name=opus\nsample_rate=48000",
        )

        media_out, error = refine_video_media(media)

        # Should flag for audio transcode, not reject
        assert media_out is not None
        assert error is None
        assert media_out.action == "transcode_audio_to_aac_or_eac3"
        assert media_out.requires_processing is True
        assert media_out.compatible is False
        assert "Opus audio" in media_out.notes
