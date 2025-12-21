# CI and Testing Guide

## Overview

Smart Media Manager has two testing tiers:

1. **Minimal CI Tests** - Run automatically on GitHub Actions
2. **E2E Tests** - Run locally by developers (require Apple Photos access)

## GitHub Actions Environment

### macOS Runners

Our CI runs on **GitHub-hosted macOS runners** (`macos-latest`):
- ✅ **macOS operating system** - Full macOS Sonoma/Ventura
- ✅ **Photos.app installed** - Available at `/System/Applications/Photos.app`
- ❌ **No GUI access** - Headless environment
- ❌ **No Photos library** - Photos.app hasn't been opened/initialized
- ❌ **No accessibility permissions** - AppleScript automation restricted

### What Works in CI

**✅ Can Test:**
- File detection and classification
- Format validation
- Metadata extraction
- File operations (copy, move, rename)
- Command-line tools (ffmpeg, exiftool, etc.)
- Unit tests with mocked dependencies

**❌ Cannot Test:**
- Apple Photos import (requires GUI + library)
- AppleScript automation (requires accessibility permissions)
- Photos album creation
- Actual import verification

## Test Markers

We use pytest markers to categorize tests:

```python
@pytest.mark.minimal  # Runs in CI - no Photos.app required
@pytest.mark.e2e      # Runs locally - requires Photos.app access
@pytest.mark.slow     # Long-running tests
```

### Minimal Tests (`@pytest.mark.minimal`)

**Purpose:** Smoke tests that verify basic functionality without requiring Photos.app

**Requirements:**
- Small test samples (under 300KB) in `tests/samples/ci/`
- No external dependencies beyond Python packages
- Fast execution (< 1 second per test)

**Examples:**
```python
@pytest.mark.minimal
def test_image_file_readable():
    """Verify we can read a JPEG file."""
    with Image.open("tests/samples/ci/images/test_image.jpg") as img:
        assert img.format == "JPEG"
```

**Location:** `tests/test_minimal_ci.py`

**Run in CI:** ✅ Yes - Automatically on every push

### E2E Tests (`@pytest.mark.e2e`)

**Purpose:** Full integration tests that actually import to Photos.app

**Requirements:**
- macOS with Photos.app
- Photos library initialized
- Large test samples in `tests/samples/media/` (gitignored)
- Accessibility permissions granted
- GUI session available

**Examples:**
```python
@pytest.mark.e2e
def test_import_photos_batch():
    """Actually import files into Photos.app."""
    imported_count, failed = import_into_photos(media_files, stats)
    assert imported_count > 0
```

**Location:** `tests/test_e2e_photos_import.py`

**Run in CI:** ❌ No - Skipped automatically (requires Photos library)

## Running Tests

### In CI (Automatic)

```bash
# Runs automatically on push - minimal tests only
pytest -m minimal
```

### Minimal CI Workflow

The `CI Minimal` GitHub Actions workflow runs `pytest -m minimal` on macOS and avoids any Photos.app integration.

**Result:** 14 minimal tests, 103 deselected (e2e + unmarked tests)

### Locally (Full Suite)

```bash
# Run ALL tests including e2e (requires Photos.app)
pytest

# Run only e2e tests
pytest -m e2e

# Run only minimal tests (same as CI)
pytest -m minimal

# Run with coverage
pytest --cov=smart_media_manager
```

### Test Samples

**CI Samples** (tracked in git):
- `tests/samples/ci/images/test_image.jpg` (38KB)
- `tests/samples/ci/videos/test_video.mp4` (13KB)
- Total: 51KB

**Local Samples** (gitignored):
- `tests/samples/media/` - Full test media collection
- `tests/samples/format_tests/` - Comprehensive format matrix
- `tests/fixtures/` - Large test files (1GB+)
- Total: ~15,000 files, multiple GB

### Compatibility Tester (Local Only)

The experimental compatibility tester lives under `scripts_dev/` and is tracked in git, but its generated samples and results are not. See `scripts_dev/README_TESTING.md` for the full pipeline and sample generation instructions.

## Why This Approach?

### ✅ Benefits

1. **Fast CI** - Minimal tests complete in ~1 minute
2. **No Large Files** - Repository stays lean (1.4MB)
3. **Reliable** - CI doesn't fail due to Photos.app issues
4. **Local Testing** - Developers can run full suite locally

### ⚠️ Limitations

1. **No Photos Integration in CI** - Can't verify actual import functionality
2. **Manual Testing Required** - Developers must run e2e tests locally before releases
3. **Split Test Coverage** - CI coverage doesn't include Photos.app code paths

## Adding New Tests

### For Minimal CI Tests

```python
import pytest
from pathlib import Path

@pytest.mark.minimal
def test_my_feature():
    """Test description."""
    # Use CI samples
    ci_samples = Path(__file__).parent / "samples" / "ci"
    # ... test code without Photos.app
```

**Rules:**
- ✅ Use only `tests/samples/ci/` files
- ✅ No external tools beyond Python packages
- ✅ Fast execution (< 1s)
- ❌ No Photos.app calls
- ❌ No large files
- ❌ No network access

### For E2E Tests

```python
import pytest

@pytest.mark.e2e
def test_photos_import():
    """Test description."""
    # Check Photos.app exists
    if not Path("/System/Applications/Photos.app").exists():
        pytest.skip("Photos.app required")

    # ... actual import test
```

**Rules:**
- ✅ Can use Photos.app
- ✅ Can use large samples
- ✅ Can be slow
- ❌ Won't run in CI

## Future Improvements

Potential enhancements to consider:

1. **Mocked Photos Tests** - Mock AppleScript calls for CI
2. **Docker Photos Emulation** - If possible (unlikely)
3. **Self-Hosted Runner** - macOS runner with Photos configured
4. **Manual Dispatch** - GitHub Actions manual trigger for e2e tests

## Troubleshooting

### CI Failing on Non-Minimal Tests

**Problem:** CI tries to run e2e tests
**Solution:** Ensure tests are marked with `@pytest.mark.e2e`

### Local Tests Skipping E2E

**Problem:** E2E tests skip due to missing Photos.app
**Solution:** Run on macOS with Photos.app installed

### Large Test Files in Git

**Problem:** Accidentally committed large test samples
**Solution:**
```bash
# Remove from git
git rm --cached tests/samples/media/*
git rm --cached tests/fixtures/*

# Update .gitignore
echo "tests/samples/media/" >> .gitignore
echo "tests/fixtures/" >> .gitignore
```

## References

- GitHub Actions macOS runners: https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners
- Pytest markers: https://docs.pytest.org/en/stable/example/markers.html
- AppleScript automation: https://developer.apple.com/library/archive/documentation/AppleScript/
