"""
Minimal CI tests using small sample files.

These tests run in CI with samples under 300KB to verify basic functionality
without requiring large test fixtures.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import subprocess


@pytest.mark.minimal
def test_ci_samples_exist():
    """Verify CI sample files exist and are accessible."""
    ci_samples = Path(__file__).parent / "samples" / "ci"

    image_file = ci_samples / "images" / "test_image.jpg"
    video_file = ci_samples / "videos" / "test_video.mp4"

    assert ci_samples.exists(), "CI samples directory should exist"
    assert image_file.exists(), "Test image should exist"
    assert video_file.exists(), "Test video should exist"

    # Verify they're small enough for CI
    assert image_file.stat().st_size < 300 * 1024, "Test image should be under 300KB"
    assert video_file.stat().st_size < 300 * 1024, "Test video should be under 300KB"


@pytest.mark.minimal
def test_image_file_readable():
    """Test that CI image sample is readable as a valid image."""
    from pathlib import Path
    from PIL import Image

    ci_samples = Path(__file__).parent / "samples" / "ci"
    image_file = ci_samples / "images" / "test_image.jpg"

    # Verify we can open and read the image
    with Image.open(image_file) as img:
        assert img.format == "JPEG", "Should be a valid JPEG file"
        assert img.size[0] > 0 and img.size[1] > 0, "Should have valid dimensions"


@pytest.mark.minimal
def test_video_file_exists_and_small():
    """Test that CI video sample exists and is appropriately sized."""
    from pathlib import Path

    ci_samples = Path(__file__).parent / "samples" / "ci"
    video_file = ci_samples / "videos" / "test_video.mp4"

    # Basic file validation without requiring ffprobe
    assert video_file.exists(), "Video file should exist"
    assert video_file.suffix == ".mp4", "Should have .mp4 extension"
    assert video_file.stat().st_size > 1000, "Should be larger than 1KB (not empty)"
    assert video_file.stat().st_size < 300 * 1024, "Should be under 300KB for CI"


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

        # Verify correct command was called
        mock_run.assert_called_with(["/opt/homebrew/bin/brew", "list", "ffmpeg"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


@pytest.mark.minimal
def test_ensure_brew_package_installs_missing_package():
    """Test that ensure_brew_package installs a missing package."""
    from smart_media_manager.cli import ensure_brew_package

    with patch("smart_media_manager.cli.brew_package_installed") as mock_installed, patch("smart_media_manager.cli.run_command_with_progress") as mock_run:
        # Package not installed
        mock_installed.return_value = False

        ensure_brew_package("/opt/homebrew/bin/brew", "ffmpeg")

        # Should attempt to install
        mock_run.assert_called_once_with(["/opt/homebrew/bin/brew", "install", "--quiet", "ffmpeg"], "Installing ffmpeg")


@pytest.mark.minimal
def test_ensure_brew_package_upgrades_existing_package():
    """Test that ensure_brew_package upgrades an already installed package."""
    from smart_media_manager.cli import ensure_brew_package

    with patch("smart_media_manager.cli.brew_package_installed") as mock_installed, patch("smart_media_manager.cli.run_command_with_progress") as mock_run:
        # Package already installed
        mock_installed.return_value = True

        ensure_brew_package("/opt/homebrew/bin/brew", "ffmpeg")

        # Should attempt to upgrade
        mock_run.assert_called_once_with(["/opt/homebrew/bin/brew", "upgrade", "--quiet", "ffmpeg"], "Updating ffmpeg")


@pytest.mark.minimal
def test_ensure_system_dependencies_installs_all_required_packages():
    """Test that ensure_system_dependencies installs all 6 required packages."""
    from smart_media_manager.cli import ensure_system_dependencies

    with patch("smart_media_manager.cli.ensure_homebrew") as mock_ensure_brew, patch("smart_media_manager.cli.ensure_brew_package") as mock_ensure_pkg:
        mock_ensure_brew.return_value = "/opt/homebrew/bin/brew"

        ensure_system_dependencies()

        # Verify all 6 required packages are installed
        expected_packages = ["ffmpeg", "jpeg-xl", "libheif", "imagemagick", "webp", "exiftool"]
        assert mock_ensure_pkg.call_count == 6

        # Verify each package was called
        for package in expected_packages:
            mock_ensure_pkg.assert_any_call("/opt/homebrew/bin/brew", package)


@pytest.mark.minimal
def test_raw_dependency_group_canon():
    """Test Canon RAW dependency group installation."""
    from smart_media_manager.cli import install_raw_dependency_groups

    with patch("smart_media_manager.cli.ensure_homebrew") as mock_ensure_brew, patch("smart_media_manager.cli.ensure_brew_package") as mock_ensure_pkg, patch("smart_media_manager.cli.ensure_brew_cask") as mock_ensure_cask, patch("smart_media_manager.cli.ensure_pip_package") as mock_ensure_pip:
        mock_ensure_brew.return_value = "/opt/homebrew/bin/brew"

        install_raw_dependency_groups(["canon"])

        # Canon requires: libraw (brew), rawpy (pip), adobe-dng-converter (cask)
        mock_ensure_pkg.assert_called_once_with("/opt/homebrew/bin/brew", "libraw")
        mock_ensure_pip.assert_called_once_with("rawpy")
        mock_ensure_cask.assert_called_once_with("/opt/homebrew/bin/brew", "adobe-dng-converter")


@pytest.mark.minimal
def test_raw_dependency_group_nikon():
    """Test Nikon RAW dependency group installation."""
    from smart_media_manager.cli import install_raw_dependency_groups, _INSTALLED_RAW_GROUPS

    # Clear any previously installed groups
    _INSTALLED_RAW_GROUPS.clear()

    with patch("smart_media_manager.cli.ensure_homebrew") as mock_ensure_brew, patch("smart_media_manager.cli.ensure_brew_package") as mock_ensure_pkg, patch("smart_media_manager.cli.ensure_brew_cask") as mock_ensure_cask, patch("smart_media_manager.cli.ensure_pip_package") as mock_ensure_pip:
        mock_ensure_brew.return_value = "/opt/homebrew/bin/brew"

        install_raw_dependency_groups(["nikon"])

        # Nikon requires: libraw (brew), rawpy (pip), no cask
        mock_ensure_pkg.assert_called_once_with("/opt/homebrew/bin/brew", "libraw")
        mock_ensure_pip.assert_called_once_with("rawpy")
        mock_ensure_cask.assert_not_called()


@pytest.mark.minimal
def test_raw_dependency_group_sony():
    """Test Sony RAW dependency group installation."""
    from smart_media_manager.cli import install_raw_dependency_groups, _INSTALLED_RAW_GROUPS

    # Clear any previously installed groups
    _INSTALLED_RAW_GROUPS.clear()

    with patch("smart_media_manager.cli.ensure_homebrew") as mock_ensure_brew, patch("smart_media_manager.cli.ensure_brew_package") as mock_ensure_pkg, patch("smart_media_manager.cli.ensure_pip_package") as mock_ensure_pip:
        mock_ensure_brew.return_value = "/opt/homebrew/bin/brew"

        install_raw_dependency_groups(["sony"])

        # Sony requires: libraw (brew), rawpy (pip)
        mock_ensure_pkg.assert_called_once_with("/opt/homebrew/bin/brew", "libraw")
        mock_ensure_pip.assert_called_once_with("rawpy")


@pytest.mark.minimal
def test_raw_dependency_group_sigma_with_multiple_brew_packages():
    """Test Sigma RAW dependency group with multiple brew packages."""
    from smart_media_manager.cli import install_raw_dependency_groups, _INSTALLED_RAW_GROUPS

    # Clear any previously installed groups
    _INSTALLED_RAW_GROUPS.clear()

    with patch("smart_media_manager.cli.ensure_homebrew") as mock_ensure_brew, patch("smart_media_manager.cli.ensure_brew_package") as mock_ensure_pkg, patch("smart_media_manager.cli.ensure_pip_package") as mock_ensure_pip:
        mock_ensure_brew.return_value = "/opt/homebrew/bin/brew"

        install_raw_dependency_groups(["sigma"])

        # Sigma requires: libraw + libopenraw (brew), rawpy (pip)
        assert mock_ensure_pkg.call_count == 2
        mock_ensure_pkg.assert_any_call("/opt/homebrew/bin/brew", "libraw")
        mock_ensure_pkg.assert_any_call("/opt/homebrew/bin/brew", "libopenraw")
        mock_ensure_pip.assert_called_once_with("rawpy")


@pytest.mark.minimal
def test_raw_dependency_group_multiple_cameras():
    """Test installing multiple camera RAW dependency groups at once."""
    from smart_media_manager.cli import install_raw_dependency_groups, _INSTALLED_RAW_GROUPS

    # Clear any previously installed groups
    _INSTALLED_RAW_GROUPS.clear()

    with patch("smart_media_manager.cli.ensure_homebrew") as mock_ensure_brew, patch("smart_media_manager.cli.ensure_brew_package") as mock_ensure_pkg, patch("smart_media_manager.cli.ensure_brew_cask") as mock_ensure_cask, patch("smart_media_manager.cli.ensure_pip_package") as mock_ensure_pip:
        mock_ensure_brew.return_value = "/opt/homebrew/bin/brew"

        # Install Canon, Nikon, Sony
        install_raw_dependency_groups(["canon", "nikon", "sony"])

        # All three use libraw and rawpy, Canon also uses adobe-dng-converter cask
        # Verify at least 3 brew packages (libraw for each camera)
        assert mock_ensure_pkg.call_count >= 3
        # Verify at least 3 pip packages (rawpy for each camera)
        assert mock_ensure_pip.call_count >= 3
        # Canon requires adobe-dng-converter cask
        assert mock_ensure_cask.call_count >= 1


@pytest.mark.minimal
def test_raw_dependency_group_skips_already_installed():
    """Test that already installed RAW dependency groups are skipped."""
    from smart_media_manager.cli import install_raw_dependency_groups, _INSTALLED_RAW_GROUPS

    # Clear and mark canon as already installed
    _INSTALLED_RAW_GROUPS.clear()
    _INSTALLED_RAW_GROUPS.add("canon")

    with patch("smart_media_manager.cli.ensure_homebrew") as mock_ensure_brew, patch("smart_media_manager.cli.ensure_brew_package") as mock_ensure_pkg:
        mock_ensure_brew.return_value = "/opt/homebrew/bin/brew"

        # Try to install canon again
        install_raw_dependency_groups(["canon"])

        # Should not call ensure_homebrew or ensure_brew_package since already installed
        mock_ensure_brew.assert_not_called()
        mock_ensure_pkg.assert_not_called()
