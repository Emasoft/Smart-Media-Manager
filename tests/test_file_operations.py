"""
Unit tests for file operation functions.

Tests cover:
- Write permission checking
- File validation
- Path validation
"""

import pytest
from unittest.mock import patch


class TestCheckWritePermission:
    """Tests for check_write_permission function."""

    def test_check_write_permission_succeeds_for_writable_directory(self, tmp_path):
        """Test check_write_permission succeeds for writable directory."""
        from smart_media_manager.cli import check_write_permission

        # Should not raise any exception
        check_write_permission(tmp_path)

    def test_check_write_permission_raises_for_nonexistent_directory(self, tmp_path):
        """Test check_write_permission raises for nonexistent directory."""
        from smart_media_manager.cli import check_write_permission

        nonexistent = tmp_path / "nonexistent"

        with pytest.raises(OSError, match="Directory does not exist"):
            check_write_permission(nonexistent)

    def test_check_write_permission_raises_for_file_path(self, tmp_path):
        """Test check_write_permission raises when path is a file."""
        from smart_media_manager.cli import check_write_permission

        file_path = tmp_path / "file.txt"
        file_path.touch()

        with pytest.raises(OSError, match="Path is not a directory"):
            check_write_permission(file_path)

    @patch("smart_media_manager.cli.tempfile.NamedTemporaryFile")
    def test_check_write_permission_raises_on_permission_denied(self, mock_temp, tmp_path):
        """Test check_write_permission raises PermissionError when cannot write."""
        from smart_media_manager.cli import check_write_permission

        mock_temp.side_effect = PermissionError("Permission denied")

        with pytest.raises(PermissionError, match="Permission denied: Cannot write"):
            check_write_permission(tmp_path, "write")

    def test_check_write_permission_uses_custom_operation_name(self, tmp_path):
        """Test check_write_permission uses custom operation name in messages."""
        from smart_media_manager.cli import check_write_permission

        # Should succeed with custom operation name
        check_write_permission(tmp_path, "create staging directory")


class TestValidatePathArgument:
    """Tests for validate_path_argument function."""

    def test_validate_path_argument_succeeds_for_valid_directory(self, tmp_path):
        """Test validate_path_argument succeeds for valid directory."""
        from smart_media_manager.cli import validate_path_argument

        result = validate_path_argument(str(tmp_path))

        assert result == tmp_path.resolve()

    def test_validate_path_argument_succeeds_for_valid_file(self, tmp_path):
        """Test validate_path_argument succeeds for valid file."""
        from smart_media_manager.cli import validate_path_argument

        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        result = validate_path_argument(str(test_file))

        assert result == test_file.resolve()

    def test_validate_path_argument_raises_for_nonexistent_path(self, tmp_path):
        """Test validate_path_argument raises for nonexistent path."""
        import argparse
        from smart_media_manager.cli import validate_path_argument

        nonexistent = tmp_path / "nonexistent"

        with pytest.raises(argparse.ArgumentTypeError, match="Path does not exist"):
            validate_path_argument(str(nonexistent))

    def test_validate_path_argument_raises_for_unmounted_volume(self, tmp_path):
        """Test validate_path_argument raises for unmounted volume."""
        import argparse
        from smart_media_manager.cli import validate_path_argument

        # Simulate unmounted volume by using deeply nested nonexistent path
        unmounted = tmp_path / "nonexistent_parent" / "nonexistent_child"

        with pytest.raises(argparse.ArgumentTypeError, match="unmounted volume or network path"):
            validate_path_argument(str(unmounted))

    def test_validate_path_argument_warns_for_empty_file(self, tmp_path):
        """Test validate_path_argument warns but succeeds for empty file."""
        from smart_media_manager.cli import validate_path_argument

        empty_file = tmp_path / "empty.txt"
        empty_file.touch()

        result = validate_path_argument(str(empty_file))

        assert result == empty_file.resolve()

    @patch("smart_media_manager.cli.Path.iterdir")
    def test_validate_path_argument_raises_for_unreadable_directory(self, mock_iterdir, tmp_path):
        """Test validate_path_argument raises for unreadable directory."""
        import argparse
        from smart_media_manager.cli import validate_path_argument

        mock_iterdir.side_effect = PermissionError("Permission denied")

        with pytest.raises(argparse.ArgumentTypeError, match="Permission denied"):
            validate_path_argument(str(tmp_path))

    @patch("smart_media_manager.cli.Path.open")
    def test_validate_path_argument_raises_for_unreadable_file(self, mock_open, tmp_path):
        """Test validate_path_argument raises for unreadable file."""
        import argparse
        from smart_media_manager.cli import validate_path_argument

        test_file = tmp_path / "test.txt"
        test_file.touch()

        mock_open.side_effect = PermissionError("Permission denied")

        with pytest.raises(argparse.ArgumentTypeError, match="Permission denied"):
            validate_path_argument(str(test_file))

    def test_validate_path_argument_expands_user_home(self, tmp_path, monkeypatch):
        """Test validate_path_argument expands ~ to home directory."""
        from smart_media_manager.cli import validate_path_argument

        # Mock home to be tmp_path
        monkeypatch.setenv("HOME", str(tmp_path))

        result = validate_path_argument("~")

        assert result == tmp_path.resolve()


class TestValidateRoot:
    """Tests for validate_root function."""

    def test_validate_root_succeeds_for_valid_directory(self, tmp_path):
        """Test validate_root succeeds for valid directory."""
        from smart_media_manager.cli import validate_root

        result = validate_root(tmp_path)

        assert result == tmp_path.resolve()

    def test_validate_root_raises_for_nonexistent_path(self, tmp_path):
        """Test validate_root raises RuntimeError for nonexistent path."""
        from smart_media_manager.cli import validate_root

        nonexistent = tmp_path / "nonexistent"

        with pytest.raises(RuntimeError, match="Path does not exist"):
            validate_root(nonexistent)

    def test_validate_root_raises_for_file_when_directory_required(self, tmp_path):
        """Test validate_root raises RuntimeError when path is file."""
        from smart_media_manager.cli import validate_root

        test_file = tmp_path / "test.txt"
        test_file.touch()

        with pytest.raises(RuntimeError, match="Path must be a directory"):
            validate_root(test_file)

    def test_validate_root_succeeds_for_file_when_allowed(self, tmp_path):
        """Test validate_root succeeds for file when allow_file=True."""
        from smart_media_manager.cli import validate_root

        test_file = tmp_path / "test.txt"
        test_file.touch()

        result = validate_root(test_file, allow_file=True)

        assert result == test_file.resolve()

    def test_validate_root_expands_user_home(self, tmp_path, monkeypatch):
        """Test validate_root expands ~ to home directory."""
        from smart_media_manager.cli import validate_root
        from pathlib import Path

        # Mock home to be tmp_path
        monkeypatch.setenv("HOME", str(tmp_path))

        result = validate_root(Path("~"))

        assert result == tmp_path.resolve()
