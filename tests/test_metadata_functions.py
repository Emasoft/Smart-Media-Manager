"""
Unit tests for metadata extraction and dependency checking functions.

Tests cover:
- Dependency checking
- FFprobe execution
- Metadata extraction and normalization
"""

from unittest.mock import Mock, patch
import json


class TestEnsureDependency:
    """Tests for ensure_dependency function."""

    @patch("smart_media_manager.cli.shutil.which")
    def test_ensure_dependency_succeeds_when_available(self, mock_which):
        """Test ensure_dependency succeeds when dependency is on PATH."""
        from smart_media_manager.cli import ensure_dependency

        mock_which.return_value = "/usr/bin/ffmpeg"

        # Should not raise
        ensure_dependency("ffmpeg")

        mock_which.assert_called_once_with("ffmpeg")

    @patch("smart_media_manager.cli.shutil.which")
    def test_ensure_dependency_raises_when_not_available(self, mock_which):
        """Test ensure_dependency raises RuntimeError when dependency missing."""
        from smart_media_manager.cli import ensure_dependency
        import pytest

        mock_which.return_value = None

        with pytest.raises(RuntimeError, match="Required dependency 'nonexistent' is not available"):
            ensure_dependency("nonexistent")

    @patch("smart_media_manager.cli.shutil.which")
    def test_ensure_dependency_checks_correct_command(self, mock_which):
        """Test ensure_dependency checks the correct command name."""
        from smart_media_manager.cli import ensure_dependency

        mock_which.return_value = "/usr/local/bin/exiftool"

        ensure_dependency("exiftool")

        mock_which.assert_called_once_with("exiftool")


class TestFfprobe:
    """Tests for ffprobe function."""

    @patch("smart_media_manager.cli.subprocess.run")
    def test_ffprobe_returns_parsed_json_on_success(self, mock_run, tmp_path):
        """Test ffprobe returns parsed JSON on successful execution."""
        from smart_media_manager.cli import ffprobe

        test_file = tmp_path / "test.mp4"
        test_file.touch()

        probe_data = {
            "format": {"filename": "test.mp4", "duration": "10.0"},
            "streams": [{"codec_name": "h264", "codec_type": "video"}],
        }

        mock_run.return_value = Mock(returncode=0, stdout=json.dumps(probe_data))

        result = ffprobe(test_file)

        assert result == probe_data
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "ffprobe"
        assert str(test_file) in call_args

    @patch("smart_media_manager.cli.subprocess.run")
    def test_ffprobe_returns_none_on_command_failure(self, mock_run, tmp_path):
        """Test ffprobe returns None when command fails."""
        from smart_media_manager.cli import ffprobe

        test_file = tmp_path / "test.bin"
        test_file.touch()

        mock_run.return_value = Mock(returncode=1, stdout="")

        result = ffprobe(test_file)

        assert result is None

    @patch("smart_media_manager.cli.subprocess.run")
    def test_ffprobe_returns_none_on_invalid_json(self, mock_run, tmp_path):
        """Test ffprobe returns None when output is not valid JSON."""
        from smart_media_manager.cli import ffprobe

        test_file = tmp_path / "test.mp4"
        test_file.touch()

        mock_run.return_value = Mock(returncode=0, stdout="not valid json")

        result = ffprobe(test_file)

        assert result is None

    @patch("smart_media_manager.cli.subprocess.run")
    def test_ffprobe_uses_correct_command_arguments(self, mock_run, tmp_path):
        """Test ffprobe uses correct ffprobe command arguments."""
        from smart_media_manager.cli import ffprobe

        test_file = tmp_path / "test.mp4"
        test_file.touch()

        mock_run.return_value = Mock(returncode=0, stdout="{}")

        ffprobe(test_file)

        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "ffprobe"
        assert "-v" in call_args
        assert "error" in call_args
        assert "-print_format" in call_args
        assert "json" in call_args
        assert "-show_streams" in call_args
        assert "-show_format" in call_args


class TestExtractAndNormalizeMetadata:
    """Tests for extract_and_normalize_metadata function."""

    @patch("smart_media_manager.cli.metadata_registry")
    def test_extract_and_normalize_metadata_extracts_format_tags(self, mock_registry):
        """Test extract_and_normalize_metadata extracts format-level tags."""
        from smart_media_manager.cli import extract_and_normalize_metadata

        probe_data = {
            "format": {
                "tags": {
                    "creation_time": "2024-01-15T12:00:00Z",
                    "artist": "Test Artist",
                }
            }
        }

        mock_registry.normalize_metadata_dict.return_value = {
            "uuid-creation-time": "2024-01-15T12:00:00Z",
            "uuid-artist": "Test Artist",
        }

        result = extract_and_normalize_metadata(probe_data)

        # Should have called normalize with lowercase keys
        mock_registry.normalize_metadata_dict.assert_called_once()
        call_args = mock_registry.normalize_metadata_dict.call_args[0]
        assert call_args[0] == "ffprobe"
        assert "creation_time" in call_args[1]
        assert "artist" in call_args[1]

        assert result == {
            "uuid-creation-time": "2024-01-15T12:00:00Z",
            "uuid-artist": "Test Artist",
        }

    @patch("smart_media_manager.cli.metadata_registry")
    def test_extract_and_normalize_metadata_extracts_stream_tags(self, mock_registry):
        """Test extract_and_normalize_metadata extracts stream-level tags."""
        from smart_media_manager.cli import extract_and_normalize_metadata

        probe_data = {
            "format": {},
            "streams": [
                {"tags": {"language": "eng", "title": "English Audio"}},
                {"tags": {"language": "spa", "title": "Spanish Audio"}},
            ],
        }

        mock_registry.normalize_metadata_dict.return_value = {
            "uuid-language": "eng",
            "uuid-title": "English Audio",
        }

        extract_and_normalize_metadata(probe_data)

        # Should extract tags from first stream (and not duplicate from second)
        mock_registry.normalize_metadata_dict.assert_called_once()
        call_args = mock_registry.normalize_metadata_dict.call_args[0]
        assert "language" in call_args[1]
        assert "title" in call_args[1]

    @patch("smart_media_manager.cli.metadata_registry")
    def test_extract_and_normalize_metadata_prioritizes_format_over_stream(self, mock_registry):
        """Test extract_and_normalize_metadata prioritizes format tags over stream tags."""
        from smart_media_manager.cli import extract_and_normalize_metadata

        probe_data = {
            "format": {"tags": {"title": "Format Title"}},
            "streams": [{"tags": {"title": "Stream Title"}}],
        }

        mock_registry.normalize_metadata_dict.return_value = {"uuid-title": "Format Title"}

        extract_and_normalize_metadata(probe_data)

        # Should use format-level title, not stream-level
        call_args = mock_registry.normalize_metadata_dict.call_args[0]
        assert call_args[1]["title"] == "Format Title"

    @patch("smart_media_manager.cli.metadata_registry")
    def test_extract_and_normalize_metadata_normalizes_keys_to_lowercase(self, mock_registry):
        """Test extract_and_normalize_metadata normalizes tag keys to lowercase."""
        from smart_media_manager.cli import extract_and_normalize_metadata

        probe_data = {
            "format": {
                "tags": {
                    "Creation_Time": "2024-01-15",
                    "ARTIST": "Test",
                }
            }
        }

        mock_registry.normalize_metadata_dict.return_value = {}

        extract_and_normalize_metadata(probe_data)

        # Should have passed lowercase keys
        call_args = mock_registry.normalize_metadata_dict.call_args[0]
        assert "creation_time" in call_args[1]
        assert "artist" in call_args[1]

    @patch("smart_media_manager.cli.metadata_registry")
    def test_extract_and_normalize_metadata_returns_empty_dict_when_no_tags(self, mock_registry):
        """Test extract_and_normalize_metadata returns empty dict when no tags."""
        from smart_media_manager.cli import extract_and_normalize_metadata

        probe_data = {"format": {}, "streams": []}

        result = extract_and_normalize_metadata(probe_data)

        # Should return empty dict and not call normalize
        assert result == {}
        mock_registry.normalize_metadata_dict.assert_not_called()

    @patch("smart_media_manager.cli.metadata_registry")
    def test_extract_and_normalize_metadata_handles_missing_keys(self, mock_registry):
        """Test extract_and_normalize_metadata handles missing format/streams keys."""
        from smart_media_manager.cli import extract_and_normalize_metadata

        probe_data = {}

        result = extract_and_normalize_metadata(probe_data)

        assert result == {}
        mock_registry.normalize_metadata_dict.assert_not_called()
