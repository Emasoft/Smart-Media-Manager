"""
Unit tests for video transcoding functions.

Tests cover:
- convert_video: H.264 MP4 transcoding
- transcode_to_hevc_mp4: HEVC (H.265) transcoding with audio options
- convert_animation_to_hevc_mp4: Animated GIF/APNG/WebP to HEVC MP4
- transcode_audio_to_supported: Audio normalization to AAC/EAC3
- rewrap_or_transcode_to_mp4: Two-stage rewrap then transcode fallback

All use fail-fast approach.
"""

from pathlib import Path
from unittest.mock import patch
import pytest


class TestConvertVideo:
    """Tests for convert_video function."""

    @patch("smart_media_manager.cli.run_checked")
    def test_convert_video_transcodes_with_audio(self, mock_run, tmp_path):
        """Test convert_video transcodes video with audio to H.264 MP4."""
        from smart_media_manager.cli import convert_video, MediaFile

        source = tmp_path / "source.avi"
        source.touch()

        media = MediaFile(
            source=source,
            kind="video",
            extension=".avi",
            format_name="avi",
            stage_path=source,
            audio_codec="mp3",  # Has audio
        )

        mock_run.return_value = None

        convert_video(media)

        # Should call ffmpeg with video and audio mapping
        assert mock_run.called
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "ffmpeg"
        assert "-i" in call_args
        assert str(source) in call_args
        assert "-c:v" in call_args
        assert "libx264" in call_args
        assert "-preset" in call_args
        assert "medium" in call_args
        assert "-crf" in call_args
        assert "18" in call_args
        assert "-movflags" in call_args
        assert "+faststart" in call_args
        # Audio mapping
        assert "-map" in call_args
        assert "0:a:0" in call_args
        assert "-c:a" in call_args
        assert "aac" in call_args

        # Should delete original
        assert not source.exists()

        # Should update MediaFile
        assert media.stage_path.suffix == ".mp4"
        assert media.extension == ".mp4"
        assert media.format_name == "mp4"
        assert media.video_codec == "h264"
        assert media.audio_codec == "aac"
        assert media.compatible is True

    @patch("smart_media_manager.cli.run_checked")
    def test_convert_video_transcodes_without_audio(self, mock_run, tmp_path):
        """Test convert_video transcodes video without audio."""
        from smart_media_manager.cli import convert_video, MediaFile

        source = tmp_path / "source.avi"
        source.touch()

        media = MediaFile(
            source=source,
            kind="video",
            extension=".avi",
            format_name="avi",
            stage_path=source,
            audio_codec=None,  # No audio
        )

        mock_run.return_value = None

        convert_video(media)

        # Should call ffmpeg with -an flag (no audio)
        call_args = mock_run.call_args[0][0]
        assert "-an" in call_args
        # Should NOT have audio mapping
        assert "0:a:0" not in call_args

        # Should update audio_codec to None
        assert media.audio_codec is None

    @patch("smart_media_manager.cli.run_checked")
    def test_convert_video_fails_when_stage_path_missing(self, mock_run):
        """Test convert_video fails when stage_path is None."""
        from smart_media_manager.cli import convert_video, MediaFile

        media = MediaFile(
            source=Path("test.avi"),
            kind="video",
            extension=".avi",
            format_name="avi",
            stage_path=None,  # Missing!
        )

        # Should fail assertion
        with pytest.raises(AssertionError):
            convert_video(media)

        mock_run.assert_not_called()

    @patch("smart_media_manager.cli.run_checked")
    def test_convert_video_cleans_up_on_failure(self, mock_run, tmp_path):
        """Test convert_video cleans up partial target on failure."""
        from smart_media_manager.cli import convert_video, MediaFile
        from pathlib import Path

        source = tmp_path / "source.avi"
        source.write_bytes(b"fake avi data")

        media = MediaFile(
            source=source,
            kind="video",
            extension=".avi",
            format_name="avi",
            stage_path=source,
        )

        # Mock conversion failure that creates partial file BEFORE failing
        # This simulates ffmpeg starting conversion but failing midway
        def mock_run_with_partial_file(cmd):
            # Extract target path from ffmpeg command (last argument)
            target_path = Path(cmd[-1])
            # Simulate partial conversion by creating incomplete file
            target_path.write_bytes(b"incomplete mp4 data")
            # Then fail to simulate conversion error
            raise RuntimeError("ffmpeg failed")

        mock_run.side_effect = mock_run_with_partial_file

        with pytest.raises(RuntimeError, match="ffmpeg failed"):
            convert_video(media)

        # Original should still exist
        assert source.exists()
        assert source.read_bytes() == b"fake avi data"

        # Partial target should be cleaned up by exception handler
        mp4_files = list(tmp_path.glob("*.mp4"))
        assert len(mp4_files) == 0, f"Expected cleanup to remove partial MP4, but found: {mp4_files}"


class TestTranscodeToHevcMp4:
    """Tests for transcode_to_hevc_mp4 function."""

    @patch("smart_media_manager.cli.run_command_with_progress")
    @patch("smart_media_manager.cli.ensure_ffmpeg_path")
    def test_transcode_to_hevc_mp4_with_aac_audio(self, mock_ffmpeg, mock_run, tmp_path):
        """Test transcode_to_hevc_mp4 transcodes to HEVC with AAC audio."""
        from smart_media_manager.cli import transcode_to_hevc_mp4, MediaFile

        source = tmp_path / "source.mp4"
        source.touch()

        media = MediaFile(
            source=source,
            kind="video",
            extension=".mp4",
            format_name="mp4",
            stage_path=source,
            audio_codec="opus",
        )

        mock_ffmpeg.return_value = "ffmpeg"
        mock_run.return_value = None

        transcode_to_hevc_mp4(media, copy_audio=False)

        # Should call ffmpeg with HEVC codec and AAC audio
        assert mock_run.called
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "ffmpeg"
        assert "-c:v" in call_args
        assert "libx265" in call_args
        assert "-preset" in call_args
        assert "slow" in call_args
        assert "lossless=1" in call_args
        assert "-c:a" in call_args
        assert "aac" in call_args
        assert "-b:a" in call_args
        assert "256k" in call_args

        # Should delete original
        assert not source.exists()

        # Should update MediaFile
        assert media.stage_path.suffix == ".mp4"
        assert media.video_codec == "hevc"
        assert media.audio_codec == "aac"
        assert media.requires_processing is False
        assert media.compatible is True

    @patch("smart_media_manager.cli.run_command_with_progress")
    @patch("smart_media_manager.cli.ensure_ffmpeg_path")
    def test_transcode_to_hevc_mp4_with_copy_audio(self, mock_ffmpeg, mock_run, tmp_path):
        """Test transcode_to_hevc_mp4 copies audio when copy_audio=True."""
        from smart_media_manager.cli import transcode_to_hevc_mp4, MediaFile

        source = tmp_path / "source.mp4"
        source.touch()

        media = MediaFile(
            source=source,
            kind="video",
            extension=".mp4",
            format_name="mp4",
            stage_path=source,
            audio_codec="aac",
        )

        mock_ffmpeg.return_value = "ffmpeg"
        mock_run.return_value = None

        transcode_to_hevc_mp4(media, copy_audio=True)

        # Should call ffmpeg with copy audio
        call_args = mock_run.call_args[0][0]
        assert "-c:a" in call_args
        assert "copy" in call_args
        # Should NOT have AAC encoding
        assert "256k" not in call_args

        # Audio codec should be preserved
        assert media.audio_codec == "aac"

    @patch("smart_media_manager.cli.ensure_ffmpeg_path")
    def test_transcode_to_hevc_mp4_raises_when_stage_path_missing(self, mock_ffmpeg):
        """Test transcode_to_hevc_mp4 raises RuntimeError when stage_path is None."""
        from smart_media_manager.cli import transcode_to_hevc_mp4, MediaFile

        media = MediaFile(
            source=Path("test.mp4"),
            kind="video",
            extension=".mp4",
            format_name="mp4",
            stage_path=None,  # Missing!
        )

        with pytest.raises(RuntimeError, match="Stage path missing"):
            transcode_to_hevc_mp4(media)

    @patch("smart_media_manager.cli.run_command_with_progress")
    @patch("smart_media_manager.cli.ensure_ffmpeg_path")
    def test_transcode_to_hevc_mp4_cleans_up_on_failure(self, mock_ffmpeg, mock_run, tmp_path):
        """Test transcode_to_hevc_mp4 cleans up partial target on failure."""
        from smart_media_manager.cli import transcode_to_hevc_mp4, MediaFile
        from pathlib import Path

        source = tmp_path / "source.mp4"
        source.write_bytes(b"fake mp4 data")

        media = MediaFile(
            source=source,
            kind="video",
            extension=".mp4",
            format_name="mp4",
            stage_path=source,
        )

        mock_ffmpeg.return_value = "ffmpeg"

        # Mock transcoding failure that creates partial file BEFORE failing
        # This simulates ffmpeg starting conversion but failing midway
        def mock_run_with_partial_file(cmd, description):
            # Extract target path from ffmpeg command (last argument)
            target_path = Path(cmd[-1])
            # Simulate partial conversion by creating incomplete file
            target_path.write_bytes(b"incomplete hevc mp4 data")
            # Then fail to simulate conversion error
            raise RuntimeError("ffmpeg failed")

        mock_run.side_effect = mock_run_with_partial_file

        with pytest.raises(RuntimeError, match="ffmpeg failed"):
            transcode_to_hevc_mp4(media)

        # Original should still exist
        assert source.exists()
        assert source.read_bytes() == b"fake mp4 data"

        # Partial target should be cleaned up by exception handler
        # Note: target has _1.mp4 suffix (next_available_name), so we can distinguish it
        mp4_files = [f for f in tmp_path.glob("*.mp4") if f != source]
        assert len(mp4_files) == 0, f"Expected cleanup to remove partial MP4, but found: {mp4_files}"


class TestConvertAnimationToHevcMp4:
    """Tests for convert_animation_to_hevc_mp4 function."""

    @patch("smart_media_manager.cli.run_command_with_progress")
    @patch("smart_media_manager.cli.ensure_ffmpeg_path")
    def test_convert_animation_to_hevc_mp4_succeeds(self, mock_ffmpeg, mock_run, tmp_path):
        """Test convert_animation_to_hevc_mp4 converts animation to HEVC MP4."""
        from smart_media_manager.cli import convert_animation_to_hevc_mp4, MediaFile

        source = tmp_path / "animation.gif"
        source.touch()

        media = MediaFile(
            source=source,
            kind="image",
            extension=".gif",
            format_name="gif",
            stage_path=source,
        )

        mock_ffmpeg.return_value = "ffmpeg"
        mock_run.return_value = None

        convert_animation_to_hevc_mp4(media)

        # Should call ffmpeg with HEVC and lossless params
        assert mock_run.called
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "ffmpeg"
        assert "-c:v" in call_args
        assert "libx265" in call_args
        assert "lossless=1" in call_args
        assert "yuv444p10le" in call_args
        assert "-an" in call_args  # Remove audio

        # Should delete original
        assert not source.exists()

        # Should update MediaFile
        assert media.stage_path.suffix == ".mp4"
        assert media.extension == ".mp4"
        assert media.video_codec == "hevc"
        assert media.audio_codec is None
        assert media.kind == "video"
        assert media.compatible is True

    @patch("smart_media_manager.cli.ensure_ffmpeg_path")
    def test_convert_animation_to_hevc_mp4_raises_when_stage_path_missing(self, mock_ffmpeg):
        """Test convert_animation_to_hevc_mp4 raises when stage_path is None."""
        from smart_media_manager.cli import convert_animation_to_hevc_mp4, MediaFile

        media = MediaFile(
            source=Path("animation.gif"),
            kind="image",
            extension=".gif",
            format_name="gif",
            stage_path=None,
        )

        with pytest.raises(RuntimeError, match="Stage path missing"):
            convert_animation_to_hevc_mp4(media)


class TestTranscodeAudioToSupported:
    """Tests for transcode_audio_to_supported function."""

    @patch("smart_media_manager.cli.run_command_with_progress")
    @patch("smart_media_manager.cli.ensure_ffmpeg_path")
    def test_transcode_audio_to_supported_uses_aac_for_stereo(self, mock_ffmpeg, mock_run, tmp_path):
        """Test transcode_audio_to_supported uses AAC for stereo audio."""
        from smart_media_manager.cli import transcode_audio_to_supported, MediaFile

        source = tmp_path / "video.mp4"
        source.touch()

        media = MediaFile(
            source=source,
            kind="video",
            extension=".mp4",
            format_name="mp4",
            stage_path=source,
            audio_codec="opus",
            metadata={"audio_channels": 2, "audio_layout": "stereo"},
        )

        mock_ffmpeg.return_value = "ffmpeg"
        mock_run.return_value = None

        transcode_audio_to_supported(media)

        # Should use AAC for stereo
        call_args = mock_run.call_args[0][0]
        assert "-c:a" in call_args
        assert "aac" in call_args
        assert "256k" in call_args
        assert "-c:v" in call_args
        assert "copy" in call_args

        # Should update media
        assert media.audio_codec == "aac"

    @patch("smart_media_manager.cli.run_command_with_progress")
    @patch("smart_media_manager.cli.ensure_ffmpeg_path")
    def test_transcode_audio_to_supported_uses_eac3_for_surround(self, mock_ffmpeg, mock_run, tmp_path):
        """Test transcode_audio_to_supported uses EAC3 for 5.1 surround."""
        from smart_media_manager.cli import transcode_audio_to_supported, MediaFile

        source = tmp_path / "video.mp4"
        source.touch()

        media = MediaFile(
            source=source,
            kind="video",
            extension=".mp4",
            format_name="mp4",
            stage_path=source,
            audio_codec="dts",
            metadata={"audio_channels": 6, "audio_layout": "5.1"},
        )

        mock_ffmpeg.return_value = "ffmpeg"
        mock_run.return_value = None

        transcode_audio_to_supported(media)

        # Should use EAC3 for 5.1
        call_args = mock_run.call_args[0][0]
        assert "-c:a" in call_args
        assert "eac3" in call_args
        assert "768k" in call_args

        # Should update media
        assert media.audio_codec == "eac3"

    @patch("smart_media_manager.cli.run_command_with_progress")
    @patch("smart_media_manager.cli.ensure_ffmpeg_path")
    def test_transcode_audio_to_supported_cleans_up_on_failure(self, mock_ffmpeg, mock_run, tmp_path):
        """Test transcode_audio_to_supported cleans up on failure."""
        from smart_media_manager.cli import transcode_audio_to_supported, MediaFile
        from pathlib import Path

        source = tmp_path / "video.mp4"
        source.write_bytes(b"fake data")

        media = MediaFile(
            source=source,
            kind="video",
            extension=".mp4",
            format_name="mp4",
            stage_path=source,
            metadata={},
        )

        mock_ffmpeg.return_value = "ffmpeg"

        # Mock conversion failure that creates partial file BEFORE failing
        # This simulates ffmpeg starting conversion but failing midway
        def mock_run_with_partial_file(cmd, description):
            # Extract target path from ffmpeg command (last argument)
            target_path = Path(cmd[-1])
            # Simulate partial conversion by creating incomplete file
            target_path.write_bytes(b"incomplete mp4 with aac audio")
            # Then fail to simulate conversion error
            raise RuntimeError("ffmpeg failed")

        mock_run.side_effect = mock_run_with_partial_file

        with pytest.raises(RuntimeError, match="ffmpeg failed"):
            transcode_audio_to_supported(media)

        # Original should still exist
        assert source.exists()
        assert source.read_bytes() == b"fake data"

        # Partial target should be cleaned up by exception handler
        # Note: target has _1.mp4 suffix (next_available_name), so we can distinguish it
        mp4_files = [f for f in tmp_path.glob("*.mp4") if f != source]
        assert len(mp4_files) == 0, f"Expected cleanup to remove partial MP4, but found: {mp4_files}"


class TestRewrapOrTranscodeToMp4:
    """Tests for rewrap_or_transcode_to_mp4 function."""

    @patch("smart_media_manager.cli.run_command_with_progress")
    @patch("smart_media_manager.cli.ensure_ffmpeg_path")
    def test_rewrap_or_transcode_to_mp4_succeeds_with_rewrap(self, mock_ffmpeg, mock_run, tmp_path):
        """Test rewrap_or_transcode_to_mp4 succeeds with fast rewrap."""
        from smart_media_manager.cli import rewrap_or_transcode_to_mp4, MediaFile

        source = tmp_path / "video.mkv"
        source.touch()

        media = MediaFile(
            source=source,
            kind="video",
            extension=".mkv",
            format_name="mkv",
            stage_path=source,
        )

        mock_ffmpeg.return_value = "ffmpeg"
        mock_run.return_value = None

        rewrap_or_transcode_to_mp4(media)

        # Should only call once (rewrap succeeded)
        assert mock_run.call_count == 1
        call_args = mock_run.call_args[0][0]
        assert "-c" in call_args
        assert "copy" in call_args

        # Should update media
        assert media.stage_path.suffix == ".mp4"
        assert media.compatible is True

    @patch("smart_media_manager.cli.run_command_with_progress")
    @patch("smart_media_manager.cli.ensure_ffmpeg_path")
    def test_rewrap_or_transcode_to_mp4_falls_back_to_transcode(self, mock_ffmpeg, mock_run, tmp_path):
        """Test rewrap_or_transcode_to_mp4 falls back to transcode on rewrap failure."""
        from smart_media_manager.cli import rewrap_or_transcode_to_mp4, MediaFile

        source = tmp_path / "video.mkv"
        source.touch()

        media = MediaFile(
            source=source,
            kind="video",
            extension=".mkv",
            format_name="mkv",
            stage_path=source,
        )

        mock_ffmpeg.return_value = "ffmpeg"
        # First call (rewrap) fails, second call (transcode) succeeds
        mock_run.side_effect = [
            RuntimeError("Rewrap failed"),
            None,  # Transcode succeeds
        ]

        rewrap_or_transcode_to_mp4(media)

        # Should call twice (rewrap + transcode)
        assert mock_run.call_count == 2

        # Second call should be transcode
        second_call = mock_run.call_args_list[1][0][0]
        assert "-c:v" in second_call
        assert "libx265" in second_call

        # Should update media
        assert media.stage_path.suffix == ".mp4"
        assert media.compatible is True

    @patch("smart_media_manager.cli.ensure_ffmpeg_path")
    def test_rewrap_or_transcode_to_mp4_raises_when_stage_path_missing(self, mock_ffmpeg):
        """Test rewrap_or_transcode_to_mp4 raises when stage_path is None."""
        from smart_media_manager.cli import rewrap_or_transcode_to_mp4, MediaFile

        media = MediaFile(
            source=Path("video.mkv"),
            kind="video",
            extension=".mkv",
            format_name="mkv",
            stage_path=None,
        )

        with pytest.raises(RuntimeError, match="Stage path missing"):
            rewrap_or_transcode_to_mp4(media)

    @patch("smart_media_manager.cli.run_command_with_progress")
    @patch("smart_media_manager.cli.ensure_ffmpeg_path")
    def test_rewrap_or_transcode_to_mp4_raises_when_both_fail(self, mock_ffmpeg, mock_run, tmp_path):
        """Test rewrap_or_transcode_to_mp4 raises when both rewrap and transcode fail."""
        from smart_media_manager.cli import rewrap_or_transcode_to_mp4, MediaFile

        source = tmp_path / "video.mkv"
        source.write_bytes(b"fake data")

        media = MediaFile(
            source=source,
            kind="video",
            extension=".mkv",
            format_name="mkv",
            stage_path=source,
        )

        mock_ffmpeg.return_value = "ffmpeg"
        # Both calls fail
        mock_run.side_effect = [
            RuntimeError("Rewrap failed"),
            RuntimeError("Transcode failed"),
        ]

        with pytest.raises(RuntimeError, match="Transcode failed"):
            rewrap_or_transcode_to_mp4(media)

        # Original should still exist
        assert source.exists()
        assert source.read_bytes() == b"fake data"
