"""
Minimal CI tests using small sample files.

These tests run in CI with samples under 300KB to verify basic functionality
without requiring large test fixtures.
"""

import pytest
from pathlib import Path


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
