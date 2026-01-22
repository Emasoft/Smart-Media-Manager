"""
Unit tests for Live Photo detection and pairing functions.

Tests cover:
- Content ID extraction from Live Photos
- Live Photo pair detection
- Video skipping logic
"""

from pathlib import Path
from unittest.mock import Mock, patch
import subprocess


# Path to test samples
SAMPLES_DIR = Path(__file__).parent / "samples" / "ci"
TEST_IMAGE = SAMPLES_DIR / "images" / "test_image.jpg"
TEST_VIDEO = SAMPLES_DIR / "videos" / "test_video.mp4"


class TestExtractLivePhotoContentId:
    """Tests for extract_live_photo_content_id function."""

    @patch("smart_media_manager.cli.find_executable")
    def test_extract_live_photo_content_id_returns_none_without_exiftool(self, mock_find):
        """Test extract_live_photo_content_id returns None when exiftool unavailable."""
        from smart_media_manager.cli import extract_live_photo_content_id

        mock_find.return_value = None

        result = extract_live_photo_content_id(TEST_IMAGE)

        assert result is None
        mock_find.assert_called_once_with("exiftool")

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.find_executable")
    def test_extract_live_photo_content_id_returns_content_id_on_success(self, mock_find, mock_run, tmp_path):
        """Test extract_live_photo_content_id returns content ID when found."""
        from smart_media_manager.cli import extract_live_photo_content_id

        test_file = tmp_path / "IMG_1234.HEIC"
        test_file.touch()

        mock_find.return_value = "/usr/bin/exiftool"
        mock_run.return_value = Mock(returncode=0, stdout="ABC123-DEF456-GHI789\n", stderr="")

        result = extract_live_photo_content_id(test_file)

        assert result == "ABC123-DEF456-GHI789"
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "/usr/bin/exiftool"
        assert "-ContentIdentifier" in call_args
        assert "-b" in call_args
        assert str(test_file) in call_args

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.find_executable")
    def test_extract_live_photo_content_id_returns_none_on_failure(self, mock_find, mock_run, tmp_path):
        """Test extract_live_photo_content_id returns None when exiftool fails."""
        from smart_media_manager.cli import extract_live_photo_content_id

        test_file = tmp_path / "IMG_1234.HEIC"
        test_file.touch()

        mock_find.return_value = "/usr/bin/exiftool"
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="Error")

        result = extract_live_photo_content_id(test_file)

        assert result is None

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.find_executable")
    def test_extract_live_photo_content_id_returns_none_on_empty_output(self, mock_find, mock_run, tmp_path):
        """Test extract_live_photo_content_id returns None when output empty."""
        from smart_media_manager.cli import extract_live_photo_content_id

        test_file = tmp_path / "IMG_1234.HEIC"
        test_file.touch()

        mock_find.return_value = "/usr/bin/exiftool"
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        result = extract_live_photo_content_id(test_file)

        assert result is None

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.find_executable")
    def test_extract_live_photo_content_id_handles_timeout(self, mock_find, mock_run, tmp_path):
        """Test extract_live_photo_content_id handles subprocess timeout."""
        from smart_media_manager.cli import extract_live_photo_content_id

        test_file = tmp_path / "IMG_1234.HEIC"
        test_file.touch()

        mock_find.return_value = "/usr/bin/exiftool"
        mock_run.side_effect = subprocess.TimeoutExpired(cmd=["exiftool"], timeout=10)

        result = extract_live_photo_content_id(test_file)

        assert result is None

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli.find_executable")
    def test_extract_live_photo_content_id_handles_exception(self, mock_find, mock_run, tmp_path):
        """Test extract_live_photo_content_id handles subprocess exceptions."""
        from smart_media_manager.cli import extract_live_photo_content_id
        import subprocess

        test_file = tmp_path / "IMG_1234.HEIC"
        test_file.touch()

        mock_find.return_value = "/usr/bin/exiftool"
        mock_run.side_effect = subprocess.SubprocessError("Unexpected error")

        result = extract_live_photo_content_id(test_file)

        assert result is None


class TestDetectLivePhotoPairs:
    """Tests for detect_live_photo_pairs function."""

    @patch("smart_media_manager.cli.extract_live_photo_content_id")
    def test_detect_live_photo_pairs_finds_matching_pairs(self, mock_extract, tmp_path):
        """Test detect_live_photo_pairs finds matching image/video pairs."""
        from smart_media_manager.cli import detect_live_photo_pairs, MediaFile

        # Create mock files with same stem
        img_path = tmp_path / "IMG_1234.HEIC"
        vid_path = tmp_path / "IMG_1234.MOV"
        img_path.touch()
        vid_path.touch()

        # Create MediaFile objects
        img_media = MediaFile(
            source=img_path,
            kind="image",
            extension=".heic",
            format_name="heic",
            compatible=True,
        )
        vid_media = MediaFile(
            source=vid_path,
            kind="video",
            extension=".mov",
            format_name="mov",
            compatible=True,
        )

        # Mock content ID extraction - both return same ID
        mock_extract.side_effect = [
            "ABC123-CONTENT-ID",  # Image
            "ABC123-CONTENT-ID",  # Video
        ]

        result = detect_live_photo_pairs([img_media, vid_media])

        # Should find one pair
        assert len(result) == 1
        assert "ABC123-CONTENT-ID" in result
        pair_img, pair_vid = result["ABC123-CONTENT-ID"]
        assert pair_img.source == img_path
        assert pair_vid.source == vid_path

        # Check metadata was added
        assert img_media.metadata["is_live_photo"] is True
        assert vid_media.metadata["is_live_photo"] is True
        assert img_media.metadata["live_photo_content_id"] == "ABC123-CONTENT-ID"

    @patch("smart_media_manager.cli.extract_live_photo_content_id")
    def test_detect_live_photo_pairs_ignores_mismatched_content_ids(self, mock_extract, tmp_path):
        """Test detect_live_photo_pairs ignores pairs with different content IDs."""
        from smart_media_manager.cli import detect_live_photo_pairs, MediaFile

        img_path = tmp_path / "IMG_1234.HEIC"
        vid_path = tmp_path / "IMG_1234.MOV"
        img_path.touch()
        vid_path.touch()

        img_media = MediaFile(source=img_path, kind="image", extension=".heic", format_name="heic")
        vid_media = MediaFile(source=vid_path, kind="video", extension=".mov", format_name="mov")

        # Different content IDs
        mock_extract.side_effect = [
            "ID-AAA",  # Image
            "ID-BBB",  # Video
        ]

        result = detect_live_photo_pairs([img_media, vid_media])

        # Should find no pairs
        assert len(result) == 0

    @patch("smart_media_manager.cli.extract_live_photo_content_id")
    def test_detect_live_photo_pairs_requires_same_stem(self, mock_extract, tmp_path):
        """Test detect_live_photo_pairs requires files to have same stem."""
        from smart_media_manager.cli import detect_live_photo_pairs, MediaFile

        # Different stems
        img_path = tmp_path / "IMG_1234.HEIC"
        vid_path = tmp_path / "IMG_5678.MOV"
        img_path.touch()
        vid_path.touch()

        img_media = MediaFile(source=img_path, kind="image", extension=".heic", format_name="heic")
        vid_media = MediaFile(source=vid_path, kind="video", extension=".mov", format_name="mov")

        mock_extract.return_value = "SAME-ID"

        result = detect_live_photo_pairs([img_media, vid_media])

        # Should find no pairs (different stems)
        assert len(result) == 0
        # extract should not be called since stems don't match
        mock_extract.assert_not_called()

    @patch("smart_media_manager.cli.extract_live_photo_content_id")
    def test_detect_live_photo_pairs_handles_missing_content_id(self, mock_extract, tmp_path):
        """Test detect_live_photo_pairs handles files without content IDs."""
        from smart_media_manager.cli import detect_live_photo_pairs, MediaFile

        img_path = tmp_path / "IMG_1234.HEIC"
        vid_path = tmp_path / "IMG_1234.MOV"
        img_path.touch()
        vid_path.touch()

        img_media = MediaFile(source=img_path, kind="image", extension=".heic", format_name="heic")
        vid_media = MediaFile(source=vid_path, kind="video", extension=".mov", format_name="mov")

        # Image has no content ID
        mock_extract.side_effect = [
            None,  # Image
            "VID-ID",  # Video (not checked since image has no ID)
        ]

        result = detect_live_photo_pairs([img_media, vid_media])

        # Should find no pairs
        assert len(result) == 0

    @patch("smart_media_manager.cli.extract_live_photo_content_id")
    def test_detect_live_photo_pairs_only_checks_heic_jpg_mov(self, mock_extract, tmp_path):
        """Test detect_live_photo_pairs only considers HEIC/JPG + MOV pairs."""
        from smart_media_manager.cli import detect_live_photo_pairs, MediaFile

        # PNG + MP4 (not a Live Photo combination)
        img_path = tmp_path / "IMG_1234.png"
        vid_path = tmp_path / "IMG_1234.mp4"
        img_path.touch()
        vid_path.touch()

        img_media = MediaFile(source=img_path, kind="image", extension=".png", format_name="png")
        vid_media = MediaFile(source=vid_path, kind="video", extension=".mp4", format_name="mp4")

        result = detect_live_photo_pairs([img_media, vid_media])

        # Should find no pairs (wrong extensions)
        assert len(result) == 0
        mock_extract.assert_not_called()


class TestSkipUnknownVideo:
    """Tests for skip_unknown_video function."""

    @patch("smart_media_manager.cli.restore_media_file")
    def test_skip_unknown_video_logs_and_restores(self, mock_restore, tmp_path):
        """Test skip_unknown_video logs skip reason and restores file."""
        from smart_media_manager.cli import skip_unknown_video, MediaFile, SkipLogger

        vid_path = tmp_path / "video.mkv"
        vid_path.touch()

        media = MediaFile(source=vid_path, kind="video", extension=".mkv", format_name="mkv")

        skip_log_path = tmp_path / "skip.log"
        skip_logger = SkipLogger(path=skip_log_path)

        result = skip_unknown_video(media, skip_logger)

        # Should return False
        assert result is False

        # Should call restore
        mock_restore.assert_called_once_with(media)

        # Should have logged to file
        assert skip_logger.entries == 1
        assert skip_log_path.exists()
        log_contents = skip_log_path.read_text()
        assert "video.mkv" in log_contents
        assert "unsupported video format" in log_contents
