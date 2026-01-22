"""
Minimal CI tests using small sample files.

These tests run in CI with samples under 300KB to verify basic functionality
without requiring large test fixtures.

Uses test_set.yaml configuration to locate samples:
- samples/test_set.yaml (public, for CI)
- samples_dev/test_set.yaml (local, for comprehensive testing)
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest

if TYPE_CHECKING:
    from conftest import TestSetConfig


@pytest.mark.minimal
def test_ci_samples_exist(test_set_config: TestSetConfig):
    """Verify test set sample files exist and are accessible."""
    image_file = test_set_config.get_sample("image", "jpeg")
    video_file = test_set_config.get_sample("video", "mp4_h264")

    assert image_file is not None, "Test image should exist in test set"
    assert video_file is not None, "Test video should exist in test set"
    assert image_file.exists(), f"Test image should exist at {image_file}"
    assert video_file.exists(), f"Test video should exist at {video_file}"

    # Verify they're small enough for CI (only applies to public test set)
    if test_set_config.max_total_size_bytes is not None:
        assert image_file.stat().st_size < 300 * 1024, "Test image should be under 300KB"
        assert video_file.stat().st_size < 300 * 1024, "Test video should be under 300KB"


@pytest.mark.minimal
def test_image_file_readable(sample_image: Path | None):
    """Test that sample image is readable as a valid image."""
    from PIL import Image

    if sample_image is None:
        pytest.skip("No image sample available in current test set")

    # Verify we can open and read the image
    with Image.open(sample_image) as img:
        assert img.format in ("JPEG", "PNG", "WEBP", "BMP", "TIFF"), f"Should be a valid image format, got {img.format}"
        assert img.size[0] > 0 and img.size[1] > 0, "Should have valid dimensions"


@pytest.mark.minimal
def test_video_file_exists_and_small(sample_video: Path | None, test_set_config: TestSetConfig):
    """Test that sample video exists and is appropriately sized."""
    if sample_video is None:
        pytest.skip("No video sample available in current test set")

    # Basic file validation without requiring ffprobe
    assert sample_video.exists(), "Video file should exist"
    assert sample_video.suffix in (".mp4", ".mov", ".mkv"), f"Should have video extension, got {sample_video.suffix}"
    assert sample_video.stat().st_size > 1000, "Should be larger than 1KB (not empty)"

    # Size limit only applies to public test set
    if test_set_config.max_total_size_bytes is not None:
        assert sample_video.stat().st_size < 300 * 1024, "Should be under 300KB for CI"


# =============================================================================
# Bootstrap and Dependency Installation Tests
# =============================================================================


@pytest.mark.minimal
def test_homebrew_detection_already_installed():
    """Test that ensure_homebrew detects existing Homebrew installation."""
    from smart_media_manager.cli import ensure_homebrew

    with patch("shutil.which") as mock_which:
        mock_which.return_value = "/opt/homebrew/bin/brew"

        result = ensure_homebrew()

        assert result == "/opt/homebrew/bin/brew"
        mock_which.assert_called_once_with("brew")


@pytest.mark.minimal
def test_brew_package_installed_check():
    """Test that brew_package_installed correctly checks package presence."""
    from smart_media_manager.cli import brew_package_installed

    with patch("subprocess.run") as mock_run:
        # Test package is installed
        mock_run.return_value = Mock(returncode=0)
        assert brew_package_installed("/opt/homebrew/bin/brew", "ffmpeg") is True

        # Test package is not installed
        mock_run.return_value = Mock(returncode=1)
        assert brew_package_installed("/opt/homebrew/bin/brew", "ffmpeg") is False

        # Verify correct command was called (with timeout for subprocess safety)
        mock_run.assert_called_with(
            ["/opt/homebrew/bin/brew", "list", "ffmpeg"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
        )


@pytest.mark.minimal
def test_ensure_brew_package_installs_missing_package():
    """Test that ensure_brew_package installs a missing package."""
    from smart_media_manager.cli import ensure_brew_package

    with (
        patch("smart_media_manager.cli.brew_package_installed") as mock_installed,
        patch("smart_media_manager.cli.run_command_with_progress") as mock_run,
    ):
        # Package not installed
        mock_installed.return_value = False

        ensure_brew_package("/opt/homebrew/bin/brew", "ffmpeg")

        # Should attempt to install
        mock_run.assert_called_once_with(
            ["/opt/homebrew/bin/brew", "install", "--quiet", "ffmpeg"],
            "Installing ffmpeg",
        )


@pytest.mark.minimal
def test_ensure_brew_package_skips_existing_package():
    """Test that ensure_brew_package skips already installed packages (no upgrade)."""
    from smart_media_manager.cli import ensure_brew_package

    with (
        patch("smart_media_manager.cli.brew_package_installed") as mock_installed,
        patch("smart_media_manager.cli.run_command_with_progress") as mock_run,
    ):
        # Package already installed
        mock_installed.return_value = True

        ensure_brew_package("/opt/homebrew/bin/brew", "ffmpeg")

        # Should NOT run anything - package is already installed and we skip upgrades
        mock_run.assert_not_called()


@pytest.mark.minimal
def test_ensure_system_dependencies_installs_all_required_packages():
    """Test that ensure_system_dependencies installs all 6 required packages."""
    from smart_media_manager.cli import ensure_system_dependencies

    with (
        patch("smart_media_manager.cli.ensure_homebrew") as mock_ensure_brew,
        patch("smart_media_manager.cli.ensure_brew_package") as mock_ensure_pkg,
    ):
        mock_ensure_brew.return_value = "/opt/homebrew/bin/brew"

        ensure_system_dependencies()

        # Verify all 6 required packages are installed
        expected_packages = [
            "ffmpeg",
            "jpeg-xl",
            "libheif",
            "imagemagick",
            "webp",
            "exiftool",
        ]
        assert mock_ensure_pkg.call_count == 6

        # Verify each package was called
        for package in expected_packages:
            mock_ensure_pkg.assert_any_call("/opt/homebrew/bin/brew", package)


@pytest.mark.minimal
def test_raw_dependency_group_canon():
    """Test Canon RAW dependency group installation."""
    from smart_media_manager.cli import (
        install_raw_dependency_groups,
        _INSTALLED_RAW_GROUPS,
    )

    # Clear any previously installed groups
    _INSTALLED_RAW_GROUPS.clear()

    with (
        patch("smart_media_manager.cli.ensure_homebrew") as mock_ensure_brew,
        patch("smart_media_manager.cli.ensure_brew_package") as mock_ensure_pkg,
        patch("smart_media_manager.cli.ensure_brew_cask") as mock_ensure_cask,
    ):
        mock_ensure_brew.return_value = "/opt/homebrew/bin/brew"

        install_raw_dependency_groups(["canon"])

        # Canon requires: libraw (brew), adobe-dng-converter (cask)
        # NOTE: pip packages (rawpy) are NOT installed at runtime
        mock_ensure_pkg.assert_called_once_with("/opt/homebrew/bin/brew", "libraw")
        mock_ensure_cask.assert_called_once_with("/opt/homebrew/bin/brew", "adobe-dng-converter")


@pytest.mark.minimal
def test_raw_dependency_group_nikon():
    """Test Nikon RAW dependency group installation."""
    from smart_media_manager.cli import (
        install_raw_dependency_groups,
        _INSTALLED_RAW_GROUPS,
    )

    # Clear any previously installed groups
    _INSTALLED_RAW_GROUPS.clear()

    with (
        patch("smart_media_manager.cli.ensure_homebrew") as mock_ensure_brew,
        patch("smart_media_manager.cli.ensure_brew_package") as mock_ensure_pkg,
        patch("smart_media_manager.cli.ensure_brew_cask") as mock_ensure_cask,
    ):
        mock_ensure_brew.return_value = "/opt/homebrew/bin/brew"

        install_raw_dependency_groups(["nikon"])

        # Nikon requires: libraw (brew), no cask
        # NOTE: pip packages (rawpy) are NOT installed at runtime
        mock_ensure_pkg.assert_called_once_with("/opt/homebrew/bin/brew", "libraw")
        mock_ensure_cask.assert_not_called()


@pytest.mark.minimal
def test_raw_dependency_group_sony():
    """Test Sony RAW dependency group installation."""
    from smart_media_manager.cli import (
        install_raw_dependency_groups,
        _INSTALLED_RAW_GROUPS,
    )

    # Clear any previously installed groups
    _INSTALLED_RAW_GROUPS.clear()

    with (
        patch("smart_media_manager.cli.ensure_homebrew") as mock_ensure_brew,
        patch("smart_media_manager.cli.ensure_brew_package") as mock_ensure_pkg,
        patch("smart_media_manager.cli.ensure_brew_cask") as mock_ensure_cask,
    ):
        mock_ensure_brew.return_value = "/opt/homebrew/bin/brew"

        install_raw_dependency_groups(["sony"])

        # Sony requires: libraw (brew), no cask
        # NOTE: pip packages (rawpy) are NOT installed at runtime
        mock_ensure_pkg.assert_called_once_with("/opt/homebrew/bin/brew", "libraw")
        mock_ensure_cask.assert_not_called()


@pytest.mark.minimal
def test_raw_dependency_group_sigma_with_multiple_brew_packages():
    """Test Sigma RAW dependency group with multiple brew packages."""
    from smart_media_manager.cli import (
        install_raw_dependency_groups,
        _INSTALLED_RAW_GROUPS,
    )

    # Clear any previously installed groups
    _INSTALLED_RAW_GROUPS.clear()

    with (
        patch("smart_media_manager.cli.ensure_homebrew") as mock_ensure_brew,
        patch("smart_media_manager.cli.ensure_brew_package") as mock_ensure_pkg,
        patch("smart_media_manager.cli.ensure_brew_cask") as mock_ensure_cask,
    ):
        mock_ensure_brew.return_value = "/opt/homebrew/bin/brew"

        install_raw_dependency_groups(["sigma"])

        # Sigma requires: libraw + libopenraw (brew), no cask
        # NOTE: pip packages (rawpy) are NOT installed at runtime
        assert mock_ensure_pkg.call_count == 2
        mock_ensure_pkg.assert_any_call("/opt/homebrew/bin/brew", "libraw")
        mock_ensure_pkg.assert_any_call("/opt/homebrew/bin/brew", "libopenraw")
        mock_ensure_cask.assert_not_called()


@pytest.mark.minimal
def test_raw_dependency_group_multiple_cameras():
    """Test installing multiple camera RAW dependency groups at once."""
    from smart_media_manager.cli import (
        install_raw_dependency_groups,
        _INSTALLED_RAW_GROUPS,
    )

    # Clear any previously installed groups
    _INSTALLED_RAW_GROUPS.clear()

    with (
        patch("smart_media_manager.cli.ensure_homebrew") as mock_ensure_brew,
        patch("smart_media_manager.cli.ensure_brew_package") as mock_ensure_pkg,
        patch("smart_media_manager.cli.ensure_brew_cask") as mock_ensure_cask,
    ):
        mock_ensure_brew.return_value = "/opt/homebrew/bin/brew"

        # Install Canon, Nikon, Sony
        install_raw_dependency_groups(["canon", "nikon", "sony"])

        # All three use libraw (brew), Canon also uses adobe-dng-converter cask
        # NOTE: pip packages (rawpy) are NOT installed at runtime
        # Verify at least 3 brew packages (libraw for each camera)
        assert mock_ensure_pkg.call_count >= 3
        # Canon requires adobe-dng-converter cask
        assert mock_ensure_cask.call_count >= 1


@pytest.mark.minimal
def test_raw_dependency_group_skips_already_installed():
    """Test that already installed RAW dependency groups are skipped."""
    from smart_media_manager.cli import (
        install_raw_dependency_groups,
        _INSTALLED_RAW_GROUPS,
    )

    # Clear and mark canon as already installed
    _INSTALLED_RAW_GROUPS.clear()
    _INSTALLED_RAW_GROUPS.add("canon")

    with (
        patch("smart_media_manager.cli.ensure_homebrew") as mock_ensure_brew,
        patch("smart_media_manager.cli.ensure_brew_package") as mock_ensure_pkg,
    ):
        mock_ensure_brew.return_value = "/opt/homebrew/bin/brew"

        # Try to install canon again
        install_raw_dependency_groups(["canon"])

        # Should not call ensure_homebrew or ensure_brew_package since already installed
        mock_ensure_brew.assert_not_called()
        mock_ensure_pkg.assert_not_called()
