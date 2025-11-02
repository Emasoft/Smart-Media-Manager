"""
Unit tests for format classification functions.

Tests cover:
- libmagic classification
- puremagic classification
- binwalk classification
- pyfsig classification
"""

from unittest.mock import Mock, patch


class TestClassifyWithLibmagic:
    """Tests for classify_with_libmagic function."""

    @patch("smart_media_manager.cli._MAGIC_MIME", None)
    @patch("smart_media_manager.cli._MAGIC_DESC", None)
    @patch("smart_media_manager.cli.magic")
    def test_classify_with_libmagic_success(self, mock_magic, tmp_path):
        """Test classify_with_libmagic returns FormatVote on success."""
        from smart_media_manager.cli import classify_with_libmagic

        test_file = tmp_path / "test.jpg"
        test_file.touch()

        mock_magic_mime = Mock()
        mock_magic_mime.from_file.return_value = "image/jpeg"
        mock_magic_desc = Mock()
        mock_magic_desc.from_file.return_value = "JPEG image data"
        mock_magic.Magic.side_effect = [mock_magic_mime, mock_magic_desc]

        result = classify_with_libmagic(test_file)

        assert result.tool == "libmagic"
        assert result.mime == "image/jpeg"
        assert result.description == "JPEG image data"
        assert result.extension == ".jpg"
        assert result.kind == "image"

    @patch("smart_media_manager.cli.magic", None)
    def test_classify_with_libmagic_not_installed(self, tmp_path):
        """Test classify_with_libmagic handles missing libmagic."""
        from smart_media_manager.cli import classify_with_libmagic

        test_file = tmp_path / "test.jpg"
        test_file.touch()

        result = classify_with_libmagic(test_file)

        assert result.tool == "libmagic"
        assert result.error == "libmagic not yet installed"


class TestClassifyWithPuremagic:
    """Tests for classify_with_puremagic function."""

    def test_classify_with_puremagic_success(self, tmp_path):
        """Test classify_with_puremagic returns FormatVote on success."""
        from smart_media_manager.cli import classify_with_puremagic

        test_file = tmp_path / "test.jpg"
        test_file.touch()

        mock_sig = Mock()
        mock_sig.is_empty.return_value = False
        mock_sig.extension = ".jpg"
        mock_sig.mime = "image/jpeg"

        result = classify_with_puremagic(test_file, signature=mock_sig)

        assert result.tool == "puremagic"
        assert result.mime == "image/jpeg"
        assert result.extension == ".jpg"
        assert result.kind == "image"

    def test_classify_with_puremagic_empty_signature(self, tmp_path):
        """Test classify_with_puremagic handles empty signature."""
        from smart_media_manager.cli import classify_with_puremagic

        test_file = tmp_path / "test.bin"
        test_file.touch()

        mock_sig = Mock()
        mock_sig.is_empty.return_value = True

        result = classify_with_puremagic(test_file, signature=mock_sig)

        assert result.tool == "puremagic"
        assert result.error == "no match"


class TestClassifyWithBinwalk:
    """Tests for classify_with_binwalk function."""

    @patch("smart_media_manager.cli.BINWALK_EXECUTABLE", "/usr/bin/binwalk")
    @patch("smart_media_manager.cli.subprocess.run")
    def test_classify_with_binwalk_success(self, mock_run, tmp_path):
        """Test classify_with_binwalk returns FormatVote on success."""
        from smart_media_manager.cli import classify_with_binwalk

        test_file = tmp_path / "test.jpg"
        test_file.touch()

        mock_run.return_value = Mock(
            returncode=0,
            stdout="DECIMAL       HEXADECIMAL     DESCRIPTION\n--------------------------------------------------------------------------------\n0             0x0             JPEG image data\n",
            stderr="",
        )

        result = classify_with_binwalk(test_file)

        assert result.tool == "binwalk"
        assert result.description == "JPEG image data"
        assert result.extension == ".jpg"
        assert result.kind == "image"

    @patch("smart_media_manager.cli.BINWALK_EXECUTABLE", None)
    def test_classify_with_binwalk_not_found(self, tmp_path):
        """Test classify_with_binwalk handles missing binwalk."""
        from smart_media_manager.cli import classify_with_binwalk

        test_file = tmp_path / "test.jpg"
        test_file.touch()

        result = classify_with_binwalk(test_file)

        assert result.tool == "binwalk"
        assert result.error == "binwalk executable not found"


class TestClassifyWithPyfsig:
    """Tests for classify_with_pyfsig function."""

    @patch("smart_media_manager.cli.pyfsig_interface")
    def test_classify_with_pyfsig_success(self, mock_pyfsig, tmp_path):
        """Test classify_with_pyfsig returns FormatVote on success."""
        from smart_media_manager.cli import classify_with_pyfsig

        test_file = tmp_path / "test.jpg"
        test_file.touch()

        mock_match = Mock()
        mock_match.file_extension = "jpg"
        mock_match.description = "JPEG image"
        mock_pyfsig.find_matches_for_file_path.return_value = [mock_match]

        result = classify_with_pyfsig(test_file)

        assert result.tool == "pyfsig"
        assert result.extension == ".jpg"
        assert result.description == "JPEG image"
        assert result.kind == "image"

    @patch("smart_media_manager.cli.pyfsig_interface")
    def test_classify_with_pyfsig_no_match(self, mock_pyfsig, tmp_path):
        """Test classify_with_pyfsig handles no matches."""
        from smart_media_manager.cli import classify_with_pyfsig

        test_file = tmp_path / "test.bin"
        test_file.touch()

        mock_pyfsig.find_matches_for_file_path.return_value = []

        result = classify_with_pyfsig(test_file)

        assert result.tool == "pyfsig"
        assert result.error == "no signature match"
