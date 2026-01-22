"""
Unit tests for video rewrapping and cleanup functions.

Tests cover:
- rewrap_to_mp4: Container rewrapping without transcoding
- revert_media_files: Cleanup and revert staged files

All use fail-fast approach.
"""

from pathlib import Path
from unittest.mock import patch
import pytest


class TestRewrapToMp4:
    """Tests for rewrap_to_mp4 function."""

    @patch("smart_media_manager.cli.run_command_with_progress")
    @patch("smart_media_manager.cli.ensure_ffmpeg_path")
    def test_rewrap_to_mp4_succeeds_and_updates_media(self, mock_ffmpeg, mock_run, tmp_path):
        """Test rewrap_to_mp4 succeeds and updates MediaFile."""
        from smart_media_manager.cli import rewrap_to_mp4, MediaFile

        source = tmp_path / "source.mkv"
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

        rewrap_to_mp4(media)

        # Should call ffmpeg with copy codec
        assert mock_run.called
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "ffmpeg"
        assert "-i" in call_args
        assert str(source) in call_args
        assert "-c" in call_args
        assert "copy" in call_args
        assert "-map" in call_args
        assert "0" in call_args
        assert "-map_metadata" in call_args
        assert "-movflags" in call_args
        assert "+faststart" in call_args

        # Should delete original
        assert not source.exists()

        # Should update MediaFile
        assert media.stage_path.suffix == ".mp4"
        assert media.extension == ".mp4"
        assert media.format_name == "mp4"
        assert media.requires_processing is False
        assert media.compatible is True

    @patch("smart_media_manager.cli.ensure_ffmpeg_path")
    def test_rewrap_to_mp4_raises_when_stage_path_missing(self, mock_ffmpeg):
        """Test rewrap_to_mp4 raises RuntimeError when stage_path is None."""
        from smart_media_manager.cli import rewrap_to_mp4, MediaFile

        media = MediaFile(
            source=Path("test.mkv"),
            kind="video",
            extension=".mkv",
            format_name="mkv",
            stage_path=None,  # Missing!
        )

        with pytest.raises(RuntimeError, match="Stage path missing"):
            rewrap_to_mp4(media)

    @patch("smart_media_manager.cli.run_command_with_progress")
    @patch("smart_media_manager.cli.ensure_ffmpeg_path")
    def test_rewrap_to_mp4_preserves_original_on_failure(self, mock_ffmpeg, mock_run, tmp_path):
        """Test rewrap_to_mp4 preserves original when ffmpeg fails.

        NOTE: rewrap_to_mp4 does NOT have cleanup logic for partial target files.
        If ffmpeg creates a partial file before failing, it will be left behind.
        This test verifies the function's CURRENT behavior (preserving original),
        not ideal behavior (which would include cleanup).
        """
        from smart_media_manager.cli import rewrap_to_mp4, MediaFile

        source = tmp_path / "source.mkv"
        source.write_bytes(b"fake mkv data")

        media = MediaFile(
            source=source,
            kind="video",
            extension=".mkv",
            format_name="mkv",
            stage_path=source,
        )

        mock_ffmpeg.return_value = "ffmpeg"

        # Mock ffmpeg failure that creates partial file BEFORE failing
        # This simulates realistic ffmpeg behavior (starts writing output, then fails)
        def mock_run_with_partial_file(cmd, description):
            # Extract target path from ffmpeg command (last argument)
            target_path = Path(cmd[-1])
            # Simulate partial conversion by creating incomplete file
            target_path.write_bytes(b"incomplete mp4 data")
            # Then fail to simulate conversion error
            raise RuntimeError("ffmpeg failed")

        mock_run.side_effect = mock_run_with_partial_file

        with pytest.raises(RuntimeError, match="ffmpeg failed"):
            rewrap_to_mp4(media)

        # Original should still exist (unlink() is only called AFTER success)
        assert source.exists()
        assert source.read_bytes() == b"fake mkv data"

        # KNOWN ISSUE: Partial target is NOT cleaned up (function has no cleanup logic)
        # This verifies CURRENT behavior, which may leave partial files behind
        mp4_files = list(tmp_path.glob("*.mp4"))
        # The partial file will exist because rewrap_to_mp4 has no cleanup
        assert len(mp4_files) == 1, "Partial MP4 is left behind (function has no cleanup logic)"


class TestRevertMediaFiles:
    """Tests for revert_media_files function."""

    @patch("smart_media_manager.cli.shutil.rmtree")
    @patch("smart_media_manager.cli.resolve_restore_path")
    def test_revert_media_files_restores_staged_files(self, mock_resolve, mock_rmtree, tmp_path):
        """Test revert_media_files restores files to original locations."""
        from smart_media_manager.cli import revert_media_files, MediaFile

        # Create staging directory and staged files
        staging = tmp_path / "FOUND_MEDIA_FILES_123"
        staging.mkdir()

        source1 = tmp_path / "original1.jpg"
        staged1 = staging / "staged1.jpg"
        staged1.touch()

        source2 = tmp_path / "original2.mp4"
        staged2 = staging / "staged2.mp4"
        staged2.touch()

        media1 = MediaFile(
            source=source1,
            kind="image",
            extension=".jpg",
            format_name="jpeg",
            stage_path=staged1,
        )
        media2 = MediaFile(
            source=source2,
            kind="video",
            extension=".mp4",
            format_name="mp4",
            stage_path=staged2,
        )

        # Mock restore paths
        restore1 = tmp_path / "restored1.jpg"
        restore2 = tmp_path / "restored2.mp4"
        mock_resolve.side_effect = [restore1, restore2]

        revert_media_files([media1, media2], staging)

        # Should call resolve_restore_path for each media
        assert mock_resolve.call_count == 2

        # Should rename staged files to restore paths
        assert restore1.exists()
        assert restore2.exists()
        assert not staged1.exists()
        assert not staged2.exists()

        # Should clear stage_path
        assert media1.stage_path is None
        assert media2.stage_path is None

        # Should remove staging directory
        mock_rmtree.assert_called_once_with(staging, ignore_errors=True)

    @patch("smart_media_manager.cli.shutil.rmtree")
    @patch("smart_media_manager.cli.resolve_restore_path")
    def test_revert_media_files_handles_missing_staged_files(self, mock_resolve, mock_rmtree, tmp_path):
        """Test revert_media_files handles files that no longer exist in staging."""
        from smart_media_manager.cli import revert_media_files, MediaFile

        staging = tmp_path / "FOUND_MEDIA_FILES_123"
        staging.mkdir()

        source = tmp_path / "original.jpg"
        staged = staging / "staged.jpg"
        # Don't create the staged file - it's missing

        media = MediaFile(
            source=source,
            kind="image",
            extension=".jpg",
            format_name="jpeg",
            stage_path=staged,
        )

        revert_media_files([media], staging)

        # Should not call resolve_restore_path since staged file doesn't exist
        mock_resolve.assert_not_called()

        # Should still remove staging directory
        mock_rmtree.assert_called_once_with(staging, ignore_errors=True)

    @patch("smart_media_manager.cli.shutil.rmtree")
    def test_revert_media_files_handles_none_stage_path(self, mock_rmtree, tmp_path):
        """Test revert_media_files handles MediaFiles with no stage_path."""
        from smart_media_manager.cli import revert_media_files, MediaFile

        staging = tmp_path / "FOUND_MEDIA_FILES_123"
        staging.mkdir()

        source = tmp_path / "original.jpg"

        media = MediaFile(
            source=source,
            kind="image",
            extension=".jpg",
            format_name="jpeg",
            stage_path=None,  # No staging
        )

        revert_media_files([media], staging)

        # Should still remove staging directory
        mock_rmtree.assert_called_once_with(staging, ignore_errors=True)

    @patch("smart_media_manager.cli.shutil.rmtree")
    @patch("smart_media_manager.cli.resolve_restore_path")
    def test_revert_media_files_continues_on_individual_failure(self, mock_resolve, mock_rmtree, tmp_path):
        """Test revert_media_files continues processing after individual restore failure."""
        from smart_media_manager.cli import revert_media_files, MediaFile

        staging = tmp_path / "FOUND_MEDIA_FILES_123"
        staging.mkdir()

        # Create two staged files
        staged1 = staging / "staged1.jpg"
        staged1.touch()
        staged2 = staging / "staged2.mp4"
        staged2.touch()

        media1 = MediaFile(
            source=tmp_path / "original1.jpg",
            kind="image",
            extension=".jpg",
            format_name="jpeg",
            stage_path=staged1,
        )
        media2 = MediaFile(
            source=tmp_path / "original2.mp4",
            kind="video",
            extension=".mp4",
            format_name="mp4",
            stage_path=staged2,
        )

        # First restore fails, second succeeds
        restore2 = tmp_path / "restored2.mp4"
        mock_resolve.side_effect = [
            RuntimeError("Permission denied"),  # First restore fails
            restore2,  # Second restore succeeds
        ]

        # Should not raise despite first failure
        revert_media_files([media1, media2], staging)

        # Should have attempted both restores
        assert mock_resolve.call_count == 2

        # Second file should be restored
        assert restore2.exists()

        # Should still remove staging
        mock_rmtree.assert_called_once()

    @patch("smart_media_manager.cli.shutil.rmtree")
    def test_revert_media_files_handles_none_staging(self, mock_rmtree, tmp_path):
        """Test revert_media_files handles None staging directory."""
        from smart_media_manager.cli import revert_media_files, MediaFile

        media = MediaFile(
            source=tmp_path / "original.jpg",
            kind="image",
            extension=".jpg",
            format_name="jpeg",
            stage_path=None,
        )

        # Should not crash with None staging
        revert_media_files([media], None)

        # Should not try to remove anything
        mock_rmtree.assert_not_called()
