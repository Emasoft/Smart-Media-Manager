"""
Unit tests for utility helper functions.

Tests cover:
- Safe wrapper functions for filetype and puremagic
- Command execution helpers
"""

from unittest.mock import Mock, patch


class TestSafeFiletypeGuess:
    """Tests for safe_filetype_guess function."""

    @patch("smart_media_manager.cli.filetype")
    def test_safe_filetype_guess_returns_signature_on_success(self, mock_filetype, tmp_path):
        """Test safe_filetype_guess returns Signature on successful guess."""
        from smart_media_manager.cli import safe_filetype_guess

        test_file = tmp_path / "test.jpg"
        test_file.touch()

        mock_guess = Mock()
        mock_guess.extension = "jpg"
        mock_guess.mime = "image/jpeg"
        mock_filetype.guess.return_value = mock_guess

        result = safe_filetype_guess(test_file)

        assert result.extension == "jpg"  # normalize_extension removes dot
        assert result.mime == "image/jpeg"

    @patch("smart_media_manager.cli.filetype")
    def test_safe_filetype_guess_returns_empty_signature_on_no_match(self, mock_filetype, tmp_path):
        """Test safe_filetype_guess returns empty Signature when no match."""
        from smart_media_manager.cli import safe_filetype_guess

        test_file = tmp_path / "test.bin"
        test_file.touch()

        mock_filetype.guess.return_value = None

        result = safe_filetype_guess(test_file)

        assert result.is_empty()

    @patch("smart_media_manager.cli.filetype")
    def test_safe_filetype_guess_returns_empty_signature_on_exception(self, mock_filetype, tmp_path):
        """Test safe_filetype_guess returns empty Signature on exception."""
        from smart_media_manager.cli import safe_filetype_guess

        test_file = tmp_path / "test.bin"
        test_file.touch()

        mock_filetype.guess.side_effect = Exception("File error")

        result = safe_filetype_guess(test_file)

        assert result.is_empty()

    @patch("smart_media_manager.cli.filetype")
    def test_safe_filetype_guess_normalizes_extension(self, mock_filetype, tmp_path):
        """Test safe_filetype_guess normalizes extension."""
        from smart_media_manager.cli import safe_filetype_guess

        test_file = tmp_path / "test.jpeg"
        test_file.touch()

        mock_guess = Mock()
        mock_guess.extension = ".JPEG"  # With dot and uppercase
        mock_guess.mime = "image/jpeg"
        mock_filetype.guess.return_value = mock_guess

        result = safe_filetype_guess(test_file)

        # Should normalize to lowercase without dot
        assert result.extension == "jpeg"


class TestSafePuremagicGuess:
    """Tests for safe_puremagic_guess function."""

    @patch("smart_media_manager.cli.puremagic")
    def test_safe_puremagic_guess_returns_signature_on_success(self, mock_puremagic, tmp_path):
        """Test safe_puremagic_guess returns Signature on successful guess."""
        from smart_media_manager.cli import safe_puremagic_guess

        test_file = tmp_path / "test.jpg"
        test_file.touch()

        # Mock extension and MIME calls separately
        mock_puremagic.from_file.side_effect = [
            "jpg",  # First call for extension
            "image/jpeg",  # Second call for MIME
        ]

        result = safe_puremagic_guess(test_file)

        assert result.extension == "jpg"  # normalize_extension removes dot
        assert result.mime == "image/jpeg"

    @patch("smart_media_manager.cli.puremagic")
    def test_safe_puremagic_guess_handles_extension_error(self, mock_puremagic, tmp_path):
        """Test safe_puremagic_guess handles exception when guessing extension."""
        from smart_media_manager.cli import safe_puremagic_guess
        import puremagic

        test_file = tmp_path / "test.bin"
        test_file.touch()

        # First call raises PureError, second succeeds
        mock_puremagic.from_file.side_effect = [
            puremagic.PureError("No match"),
            "application/octet-stream",
        ]
        mock_puremagic.PureError = puremagic.PureError

        result = safe_puremagic_guess(test_file)

        assert result.extension is None
        assert result.mime == "application/octet-stream"

    @patch("smart_media_manager.cli.puremagic")
    def test_safe_puremagic_guess_handles_mime_error(self, mock_puremagic, tmp_path):
        """Test safe_puremagic_guess handles exception when guessing MIME."""
        from smart_media_manager.cli import safe_puremagic_guess
        import puremagic

        test_file = tmp_path / "test.bin"
        test_file.touch()

        # First call succeeds, second raises PureError
        mock_puremagic.from_file.side_effect = [
            "bin",
            puremagic.PureError("No match"),
        ]
        mock_puremagic.PureError = puremagic.PureError

        result = safe_puremagic_guess(test_file)

        assert result.extension == "bin"  # normalize_extension removes dot
        assert result.mime is None

    @patch("smart_media_manager.cli.puremagic")
    def test_safe_puremagic_guess_handles_both_errors(self, mock_puremagic, tmp_path):
        """Test safe_puremagic_guess handles exceptions for both calls."""
        from smart_media_manager.cli import safe_puremagic_guess
        import puremagic

        test_file = tmp_path / "test.bin"
        test_file.touch()

        mock_puremagic.from_file.side_effect = [
            Exception("Generic error"),
            Exception("Generic error"),
        ]
        mock_puremagic.PureError = puremagic.PureError

        result = safe_puremagic_guess(test_file)

        assert result.extension is None
        assert result.mime is None

    @patch("smart_media_manager.cli.puremagic")
    def test_safe_puremagic_guess_normalizes_extension(self, mock_puremagic, tmp_path):
        """Test safe_puremagic_guess normalizes extension."""
        from smart_media_manager.cli import safe_puremagic_guess

        test_file = tmp_path / "test.jpeg"
        test_file.touch()

        mock_puremagic.from_file.side_effect = [
            "jpeg",
            "image/jpeg",
        ]

        result = safe_puremagic_guess(test_file)

        # Should normalize to lowercase without dot
        assert result.extension == "jpeg"


class TestRunChecked:
    """Tests for run_checked function."""

    @patch("smart_media_manager.cli.subprocess.run")
    def test_run_checked_succeeds_for_successful_command(self, mock_run):
        """Test run_checked succeeds when command returns 0."""
        from smart_media_manager.cli import run_checked

        mock_run.return_value = Mock(returncode=0, stderr="")

        # Should not raise
        run_checked(["echo", "hello"])

        mock_run.assert_called_once_with(["echo", "hello"], capture_output=True, text=True, check=False, timeout=300)

    @patch("smart_media_manager.cli.subprocess.run")
    def test_run_checked_raises_for_failed_command(self, mock_run):
        """Test run_checked raises RuntimeError when command fails."""
        from smart_media_manager.cli import run_checked
        import pytest

        mock_run.return_value = Mock(returncode=1, stderr="Command not found")

        with pytest.raises(RuntimeError, match="failed with exit code 1"):
            run_checked(["nonexistent-command"])

    @patch("smart_media_manager.cli.subprocess.run")
    def test_run_checked_captures_stderr_in_error(self, mock_run):
        """Test run_checked captures stderr in error message."""
        from smart_media_manager.cli import run_checked
        import pytest

        mock_run.return_value = Mock(returncode=127, stderr="command not found\n")

        with pytest.raises(RuntimeError):
            run_checked(["bad-command"])


class TestRunCommandWithProgress:
    """Tests for run_command_with_progress function."""

    @patch("smart_media_manager.cli.sys.stdout")
    @patch("smart_media_manager.cli.time.sleep")
    @patch("smart_media_manager.cli.time.time")
    @patch("smart_media_manager.cli.subprocess.Popen")
    def test_run_command_with_progress_succeeds_for_successful_command(self, mock_popen, mock_time, mock_sleep, mock_stdout):
        """Test run_command_with_progress succeeds when command returns 0."""
        from smart_media_manager.cli import run_command_with_progress

        mock_proc = Mock()
        mock_proc.poll.side_effect = [None, None, 0]  # Running, running, done
        mock_proc.returncode = 0
        mock_popen.return_value.__enter__.return_value = mock_proc

        mock_time.side_effect = [0.0, 0.2, 0.4, 0.6]  # Elapsed times

        # Should not raise
        run_command_with_progress(["echo", "hello"], "Testing")

        mock_popen.assert_called_once()

    @patch("smart_media_manager.cli.sys.stdout")
    @patch("smart_media_manager.cli.time.sleep")
    @patch("smart_media_manager.cli.time.time")
    @patch("smart_media_manager.cli.subprocess.Popen")
    def test_run_command_with_progress_raises_for_failed_command(self, mock_popen, mock_time, mock_sleep, mock_stdout):
        """Test run_command_with_progress raises RuntimeError when command fails."""
        from smart_media_manager.cli import run_command_with_progress
        import pytest

        mock_proc = Mock()
        mock_proc.poll.return_value = 1  # Failed
        mock_proc.returncode = 1
        mock_popen.return_value.__enter__.return_value = mock_proc

        mock_time.side_effect = [0.0, 0.2]

        with pytest.raises(RuntimeError, match=r"Command .* failed"):
            run_command_with_progress(["false"], "Testing")

    @patch("smart_media_manager.cli.sys.stdout")
    @patch("smart_media_manager.cli.time.sleep")
    @patch("smart_media_manager.cli.time.time")
    @patch("smart_media_manager.cli.subprocess.Popen")
    def test_run_command_with_progress_uses_custom_environment(self, mock_popen, mock_time, mock_sleep, mock_stdout):
        """Test run_command_with_progress uses custom environment."""
        from smart_media_manager.cli import run_command_with_progress

        mock_proc = Mock()
        mock_proc.poll.return_value = 0
        mock_proc.returncode = 0
        mock_popen.return_value.__enter__.return_value = mock_proc

        mock_time.side_effect = [0.0, 0.2]

        custom_env = {"PATH": "/custom/path"}
        run_command_with_progress(["test"], "Testing", env=custom_env)

        # Verify env was passed
        call_args = mock_popen.call_args
        assert call_args[1]["env"] == custom_env

    @patch("smart_media_manager.cli.sys.stdout")
    @patch("smart_media_manager.cli.time.sleep")
    @patch("smart_media_manager.cli.time.time")
    @patch("smart_media_manager.cli.subprocess.Popen")
    def test_run_command_with_progress_clears_progress_bar_on_completion(self, mock_popen, mock_time, mock_sleep, mock_stdout):
        """Test run_command_with_progress clears progress bar after completion."""
        from smart_media_manager.cli import run_command_with_progress

        mock_proc = Mock()
        mock_proc.poll.return_value = 0
        mock_proc.returncode = 0
        mock_popen.return_value.__enter__.return_value = mock_proc

        mock_time.side_effect = [0.0, 0.2]

        run_command_with_progress(["echo", "hello"], "Processing")

        # Should call write to clear the line
        assert mock_stdout.write.called
        assert mock_stdout.flush.called
