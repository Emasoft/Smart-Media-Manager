"""
Unit tests for video processing and validation functions.

Tests cover:
- Video corruption detection
- Video validation

Uses sample files from tests/samples/ci/ directory.
"""

from pathlib import Path
from unittest.mock import Mock, patch
import subprocess
import pytest


# Path to test samples
SAMPLES_DIR = Path(__file__).parent / "samples" / "ci"
TEST_VIDEO = SAMPLES_DIR / "videos" / "test_video.mp4"


class TestIsVideoCorruptOrTruncated:
    """Tests for is_video_corrupt_or_truncated function."""

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.ffprobe")
    def test_is_video_corrupt_or_truncated_detects_unreadable_file(self, mock_ffprobe, mock_run):
        """Test is_video_corrupt_or_truncated detects file ffprobe cannot read."""
        from smart_media_manager.cli import is_video_corrupt_or_truncated

        mock_ffprobe.return_value = None

        is_corrupt, reason = is_video_corrupt_or_truncated(TEST_VIDEO)

        assert is_corrupt is True
        assert "ffprobe cannot read file" in reason

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.ffprobe")
    def test_is_video_corrupt_or_truncated_detects_no_streams(self, mock_ffprobe, mock_run):
        """Test is_video_corrupt_or_truncated detects missing streams."""
        from smart_media_manager.cli import is_video_corrupt_or_truncated

        mock_ffprobe.return_value = {"format": {}, "streams": []}

        is_corrupt, reason = is_video_corrupt_or_truncated(TEST_VIDEO)

        assert is_corrupt is True
        assert "no streams found" in reason

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.ffprobe")
    def test_is_video_corrupt_or_truncated_detects_no_video_stream(self, mock_ffprobe, mock_run):
        """Test is_video_corrupt_or_truncated detects missing video stream."""
        from smart_media_manager.cli import is_video_corrupt_or_truncated

        # Audio-only file
        mock_ffprobe.return_value = {
            "format": {"duration": "10.0"},
            "streams": [{"codec_type": "audio"}],
        }

        is_corrupt, reason = is_video_corrupt_or_truncated(TEST_VIDEO)

        assert is_corrupt is True
        assert "no video stream found" in reason

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.ffprobe")
    def test_is_video_corrupt_or_truncated_detects_invalid_duration(self, mock_ffprobe, mock_run):
        """Test is_video_corrupt_or_truncated detects invalid duration."""
        from smart_media_manager.cli import is_video_corrupt_or_truncated

        mock_ffprobe.return_value = {
            "format": {"duration": "0"},
            "streams": [{"codec_type": "video"}],
        }

        is_corrupt, reason = is_video_corrupt_or_truncated(TEST_VIDEO)

        assert is_corrupt is True
        assert "invalid or missing duration" in reason

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.ffprobe")
    def test_is_video_corrupt_or_truncated_passes_valid_video(self, mock_ffprobe, mock_run):
        """Test is_video_corrupt_or_truncated passes valid video."""
        from smart_media_manager.cli import is_video_corrupt_or_truncated

        mock_ffprobe.return_value = {
            "format": {"duration": "5.0"},
            "streams": [{"codec_type": "video", "codec_name": "h264"}],
        }

        # Mock successful ffmpeg decode
        mock_run.return_value = Mock(returncode=0, stderr="")

        is_corrupt, reason = is_video_corrupt_or_truncated(TEST_VIDEO)

        assert is_corrupt is False
        assert reason is None

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.ffprobe")
    def test_is_video_corrupt_or_truncated_detects_corruption_in_stderr(self, mock_ffprobe, mock_run):
        """Test is_video_corrupt_or_truncated detects corruption indicators in stderr."""
        from smart_media_manager.cli import is_video_corrupt_or_truncated

        mock_ffprobe.return_value = {
            "format": {"duration": "5.0"},
            "streams": [{"codec_type": "video"}],
        }

        # Mock ffmpeg with corruption in stderr
        mock_run.return_value = Mock(returncode=0, stderr="Error: partial file detected at byte 1024")

        is_corrupt, reason = is_video_corrupt_or_truncated(TEST_VIDEO)

        assert is_corrupt is True
        assert "corruption detected" in reason
        assert "partial file" in reason.lower()

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.ffprobe")
    def test_is_video_corrupt_or_truncated_detects_decode_failure(self, mock_ffprobe, mock_run):
        """Test is_video_corrupt_or_truncated detects ffmpeg decode failure."""
        from smart_media_manager.cli import is_video_corrupt_or_truncated

        mock_ffprobe.return_value = {
            "format": {"duration": "5.0"},
            "streams": [{"codec_type": "video"}],
        }

        # Mock ffmpeg failure with error that doesn't match corruption indicators
        mock_run.return_value = Mock(returncode=1, stderr="Generic ffmpeg error")

        is_corrupt, reason = is_video_corrupt_or_truncated(TEST_VIDEO)

        assert is_corrupt is True
        assert "decode failed" in reason

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.ffprobe")
    def test_is_video_corrupt_or_truncated_handles_timeout(self, mock_ffprobe, mock_run):
        """Test is_video_corrupt_or_truncated handles subprocess timeout."""
        from smart_media_manager.cli import is_video_corrupt_or_truncated

        mock_ffprobe.return_value = {
            "format": {"duration": "5.0"},
            "streams": [{"codec_type": "video"}],
        }

        # Mock subprocess timeout
        mock_run.side_effect = subprocess.TimeoutExpired(cmd=["ffmpeg"], timeout=5)

        is_corrupt, reason = is_video_corrupt_or_truncated(TEST_VIDEO)

        assert is_corrupt is True
        assert "timeout" in reason.lower()

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.ffprobe")
    def test_is_video_corrupt_or_truncated_checks_end_for_long_videos(self, mock_ffprobe, mock_run):
        """Test is_video_corrupt_or_truncated checks end of video for long files."""
        from smart_media_manager.cli import is_video_corrupt_or_truncated

        # Long video (>10 seconds)
        mock_ffprobe.return_value = {
            "format": {"duration": "30.0"},
            "streams": [{"codec_type": "video"}],
        }

        # First call (start check) succeeds, second call (end check) fails
        mock_run.side_effect = [
            Mock(returncode=0, stderr=""),  # Start check OK
            Mock(returncode=0, stderr="Error: truncated at end"),  # End check fails
        ]

        is_corrupt, reason = is_video_corrupt_or_truncated(TEST_VIDEO)

        assert is_corrupt is True
        assert "truncated at end" in reason

        # Should have called subprocess.run twice (start + end)
        assert mock_run.call_count == 2

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.ffprobe")
    def test_is_video_corrupt_or_truncated_uses_correct_ffmpeg_args(self, mock_ffprobe, mock_run):
        """Test is_video_corrupt_or_truncated uses correct ffmpeg arguments."""
        from smart_media_manager.cli import is_video_corrupt_or_truncated

        mock_ffprobe.return_value = {
            "format": {"duration": "5.0"},
            "streams": [{"codec_type": "video"}],
        }

        mock_run.return_value = Mock(returncode=0, stderr="")

        is_video_corrupt_or_truncated(TEST_VIDEO)

        # Check first call arguments
        first_call_args = mock_run.call_args_list[0][0][0]
        assert first_call_args[0] == "ffmpeg"
        assert "-err_detect" in first_call_args
        assert "explode" in first_call_args
        assert "-t" in first_call_args
        assert "5" in first_call_args  # 5 second decode
        assert str(TEST_VIDEO) in first_call_args


@pytest.mark.skipif(not TEST_VIDEO.exists(), reason="Test video not available")
class TestIsVideoCorruptWithRealFile:
    """Integration tests using real sample video file."""

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.ffprobe")
    def test_is_video_corrupt_or_truncated_with_real_video_file(self, mock_ffprobe, mock_run):
        """Test is_video_corrupt_or_truncated with actual test video file."""
        from smart_media_manager.cli import is_video_corrupt_or_truncated

        # Mock ffprobe to return valid video info
        mock_ffprobe.return_value = {
            "format": {"duration": "1.0", "filename": str(TEST_VIDEO)},
            "streams": [
                {"codec_type": "video", "codec_name": "h264"},
                {"codec_type": "audio", "codec_name": "aac"},
            ],
        }

        # Mock ffmpeg success
        mock_run.return_value = Mock(returncode=0, stderr="")

        is_corrupt, reason = is_video_corrupt_or_truncated(TEST_VIDEO)

        # Should pass since mocked as valid
        assert is_corrupt is False
        assert reason is None
