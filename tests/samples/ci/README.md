# Minimal CI Test Samples

This directory contains minimal test samples for CI/CD pipelines.

## Constraints

- All files must be under 300KB
- Files are tracked in git (not gitignored)
- Used for basic smoke tests in CI

## Contents

- `images/test_image.jpg` - 38KB JPEG image for basic image tests
- `videos/test_video.mp4` - 13KB MP4 video for basic video tests

## Usage

Tests marked with `@pytest.mark.minimal` will use these samples.

For comprehensive testing with full sample sets, run locally without the `minimal` marker.
