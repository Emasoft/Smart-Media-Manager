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
def test_image_detection_basic():
    """Test basic image detection with minimal CI samples."""
    from smart_media_manager.cli import detect_media
    from pathlib import Path

    ci_samples = Path(__file__).parent / "samples" / "ci"
    image_file = ci_samples / "images" / "test_image.jpg"

    media_file = detect_media(image_file)

    assert media_file is not None, "Should detect media file"
    assert media_file.kind == "image", "Should detect as image"
    assert media_file.extension == ".jpg", "Should identify JPG extension"


@pytest.mark.minimal
def test_video_detection_basic():
    """Test basic video detection with minimal CI samples."""
    from smart_media_manager.cli import detect_media
    from pathlib import Path

    ci_samples = Path(__file__).parent / "samples" / "ci"
    video_file = ci_samples / "videos" / "test_video.mp4"

    media_file = detect_media(video_file)

    assert media_file is not None, "Should detect media file"
    assert media_file.kind == "video", "Should detect as video"
    assert media_file.extension == ".mp4", "Should identify MP4 extension"
