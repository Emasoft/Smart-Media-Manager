"""
Unit tests for dependency management and bootstrap functions.

Tests cover:
- Homebrew package/cask detection
- Pip package detection
- Dependency installation
"""

from unittest.mock import Mock, patch
import subprocess


class TestBrewCaskInstalled:
    """Tests for brew_cask_installed function."""

    @patch("smart_media_manager.cli.subprocess.run")
    def test_brew_cask_installed_returns_true_when_installed(self, mock_run):
        """Test brew_cask_installed returns True when cask is installed."""
        from smart_media_manager.cli import brew_cask_installed

        mock_run.return_value = Mock(returncode=0)

        result = brew_cask_installed("/usr/local/bin/brew", "adobe-dng-converter")

        assert result is True
        mock_run.assert_called_once_with(
            ["/usr/local/bin/brew", "list", "--cask", "adobe-dng-converter"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
        )

    @patch("smart_media_manager.cli.subprocess.run")
    def test_brew_cask_installed_returns_false_when_not_installed(self, mock_run):
        """Test brew_cask_installed returns False when cask is not installed."""
        from smart_media_manager.cli import brew_cask_installed

        mock_run.return_value = Mock(returncode=1)

        result = brew_cask_installed("/usr/local/bin/brew", "adobe-dng-converter")

        assert result is False

    @patch("smart_media_manager.cli.subprocess.run")
    def test_brew_cask_installed_handles_different_brew_path(self, mock_run):
        """Test brew_cask_installed works with different Homebrew paths."""
        from smart_media_manager.cli import brew_cask_installed

        mock_run.return_value = Mock(returncode=0)

        result = brew_cask_installed("/opt/homebrew/bin/brew", "test-cask")

        assert result is True
        assert mock_run.call_args[0][0][0] == "/opt/homebrew/bin/brew"


class TestPipPackageInstalled:
    """Tests for pip_package_installed function."""

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli._PIP_PACKAGE_CACHE", set())
    def test_pip_package_installed_returns_true_when_installed(self, mock_run):
        """Test pip_package_installed returns True when package is installed."""
        from smart_media_manager.cli import pip_package_installed
        import sys

        mock_run.return_value = Mock(returncode=0)

        result = pip_package_installed("rawpy")

        assert result is True
        mock_run.assert_called_once_with(
            [sys.executable, "-m", "pip", "show", "rawpy"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
        )

    @patch("smart_media_manager.cli.subprocess.run")
    @patch("smart_media_manager.cli._PIP_PACKAGE_CACHE", set())
    def test_pip_package_installed_returns_false_when_not_installed(self, mock_run):
        """Test pip_package_installed returns False when package is not installed."""
        from smart_media_manager.cli import pip_package_installed

        mock_run.return_value = Mock(returncode=1)

        result = pip_package_installed("nonexistent-package")

        assert result is False

    @patch("smart_media_manager.cli._PIP_PACKAGE_CACHE", {"cached-package"})
    def test_pip_package_installed_uses_cache(self):
        """Test pip_package_installed returns True from cache without checking."""
        from smart_media_manager.cli import pip_package_installed

        result = pip_package_installed("cached-package")

        assert result is True


class TestEnsureBrewCask:
    """Tests for ensure_brew_cask function."""

    @patch("smart_media_manager.cli.run_command_with_progress")
    @patch("smart_media_manager.cli.brew_cask_installed")
    def test_ensure_brew_cask_installs_when_not_present(self, mock_installed, mock_run_cmd):
        """Test ensure_brew_cask installs cask when not installed."""
        from smart_media_manager.cli import ensure_brew_cask

        mock_installed.return_value = False

        ensure_brew_cask("/usr/local/bin/brew", "test-cask")

        mock_run_cmd.assert_called_once_with(
            ["/usr/local/bin/brew", "install", "--cask", "--quiet", "test-cask"],
            "Installing test-cask",
        )

    @patch("smart_media_manager.cli.run_command_with_progress")
    @patch("smart_media_manager.cli.brew_cask_installed")
    def test_ensure_brew_cask_skips_when_present(self, mock_installed, mock_run_cmd):
        """Test ensure_brew_cask skips already installed casks (no upgrade)."""
        from smart_media_manager.cli import ensure_brew_cask

        mock_installed.return_value = True

        ensure_brew_cask("/usr/local/bin/brew", "test-cask")

        # Should NOT run anything - cask is already installed and we skip upgrades
        mock_run_cmd.assert_not_called()


class TestEnsurePipPackage:
    """Tests for ensure_pip_package function."""

    @patch("smart_media_manager.cli.run_command_with_progress")
    @patch("smart_media_manager.cli.pip_package_installed")
    @patch("smart_media_manager.cli._PIP_PACKAGE_CACHE", set())
    def test_ensure_pip_package_installs_when_not_present(self, mock_installed, mock_run_cmd):
        """Test ensure_pip_package installs package when not installed."""
        from smart_media_manager.cli import ensure_pip_package
        import sys

        mock_installed.return_value = False

        ensure_pip_package("rawpy")

        mock_run_cmd.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "--upgrade", "rawpy"],
            "Installing rawpy",
        )

    @patch("smart_media_manager.cli.run_command_with_progress")
    @patch("smart_media_manager.cli.pip_package_installed")
    def test_ensure_pip_package_upgrades_when_present(self, mock_installed, mock_run_cmd):
        """Test ensure_pip_package upgrades package when already installed."""
        from smart_media_manager.cli import ensure_pip_package
        import sys

        mock_installed.return_value = True

        ensure_pip_package("rawpy")

        mock_run_cmd.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "--upgrade", "rawpy"],
            "Updating rawpy",
        )


class TestEnsureRawDependenciesForFiles:
    """Tests for ensure_raw_dependencies_for_files function."""

    @patch("smart_media_manager.cli.install_raw_dependency_groups")
    @patch("smart_media_manager.cli.collect_raw_groups_from_extensions")
    def test_ensure_raw_dependencies_for_files_installs_required_groups(self, mock_collect, mock_install):
        """Test ensure_raw_dependencies_for_files installs groups from media files."""
        from smart_media_manager.cli import ensure_raw_dependencies_for_files, MediaFile
        from pathlib import Path

        # Create media files with various RAW extensions
        media1 = MediaFile(
            source=Path("IMG_001.CR3"),
            kind="raw",
            extension=".cr3",
            format_name="cr3",
            original_suffix=".CR3",
        )
        media2 = MediaFile(
            source=Path("DSC_002.NEF"),
            kind="raw",
            extension=".nef",
            format_name="nef",
            original_suffix=".NEF",
        )
        media3 = MediaFile(
            source=Path("IMG_003.ARW"),
            kind="raw",
            extension=".arw",
            format_name="arw",
            original_suffix=".ARW",
        )

        # Mock collect_raw_groups_from_extensions to return groups
        mock_collect.side_effect = [
            {"canon"},  # For media1
            {"nikon"},  # For media2
            {"sony"},  # For media3
        ]

        ensure_raw_dependencies_for_files([media1, media2, media3])

        # Should call collect_raw_groups_from_extensions for each media file
        assert mock_collect.call_count == 3

        # Should install the collected groups
        mock_install.assert_called_once()
        installed_groups = mock_install.call_args[0][0]
        assert isinstance(installed_groups, set)
        assert installed_groups == {"canon", "nikon", "sony"}

    @patch("smart_media_manager.cli.install_raw_dependency_groups")
    @patch("smart_media_manager.cli.collect_raw_groups_from_extensions")
    def test_ensure_raw_dependencies_for_files_does_nothing_for_non_raw_files(self, mock_collect, mock_install):
        """Test ensure_raw_dependencies_for_files does nothing when no RAW files."""
        from smart_media_manager.cli import ensure_raw_dependencies_for_files, MediaFile
        from pathlib import Path

        # Create non-RAW media files
        media1 = MediaFile(
            source=Path("photo.jpg"),
            kind="image",
            extension=".jpg",
            format_name="jpeg",
        )
        media2 = MediaFile(
            source=Path("video.mp4"),
            kind="video",
            extension=".mp4",
            format_name="mp4",
        )

        # Mock collect to return empty sets
        mock_collect.return_value = set()

        ensure_raw_dependencies_for_files([media1, media2])

        # Should NOT call install_raw_dependency_groups
        mock_install.assert_not_called()

    @patch("smart_media_manager.cli.install_raw_dependency_groups")
    @patch("smart_media_manager.cli.collect_raw_groups_from_extensions")
    def test_ensure_raw_dependencies_for_files_deduplicates_groups(self, mock_collect, mock_install):
        """Test ensure_raw_dependencies_for_files deduplicates groups from multiple files."""
        from smart_media_manager.cli import ensure_raw_dependencies_for_files, MediaFile
        from pathlib import Path

        # Create multiple Canon RAW files
        media1 = MediaFile(
            source=Path("IMG_001.CR3"),
            kind="raw",
            extension=".cr3",
            format_name="cr3",
        )
        media2 = MediaFile(
            source=Path("IMG_002.CR2"),
            kind="raw",
            extension=".cr2",
            format_name="cr2",
        )

        # Both return canon group
        mock_collect.return_value = {"canon"}

        ensure_raw_dependencies_for_files([media1, media2])

        # Should install only once (deduplicated)
        mock_install.assert_called_once()
        installed_groups = mock_install.call_args[0][0]
        assert installed_groups == {"canon"}

    @patch("smart_media_manager.cli.install_raw_dependency_groups")
    @patch("smart_media_manager.cli.collect_raw_groups_from_extensions")
    def test_ensure_raw_dependencies_for_files_handles_empty_list(self, mock_collect, mock_install):
        """Test ensure_raw_dependencies_for_files handles empty media list."""
        from smart_media_manager.cli import ensure_raw_dependencies_for_files

        ensure_raw_dependencies_for_files([])

        # Should not call install
        mock_install.assert_not_called()
