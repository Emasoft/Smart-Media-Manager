# Changelog
All notable changes to this project will be documented here, following [Keep a Changelog](https://keepachangelog.com/) and Semantic Versioning (pre-release identifiers included).

## [0.5.1a1] - 2025-10-31
### Added
- Optional dependencies for enhanced media detection (rawpy) in pyproject.toml
- Comprehensive development documentation in docs_dev/ (gitignored)
  - Metadata registry research findings and test results
  - Format compatibility test results (223MB empirical data)
  - Development scripts catalog and usage guides
- Minimal CI test suite with small samples (under 300KB) in tests/samples/ci/
  - Basic image and video detection tests
  - Comprehensive bootstrap and dependency installation tests (11 new tests)
    - Homebrew detection and installation logic
    - Brew package installation and upgrade verification
    - System dependencies installation (ffmpeg, jpeg-xl, libheif, imagemagick, webp, exiftool)
    - RAW dependency groups for camera families (Canon, Nikon, Sony, Sigma, etc.)
  - Pytest markers for test categorization (minimal, e2e, slow)
  - CI-tracked minimal samples: test_image.jpg (38KB), test_video.mp4 (13KB)

### Changed
- Reorganized repository structure with strict production/development separation
  - All development scripts moved from scripts/ to scripts_dev/ (gitignored)
  - Development documentation moved to docs_dev/ (gitignored)
  - Production directories (scripts/, docs/) now contain only distribution-ready files
  - Removed 15,822 binary test sample files from git history (99.997% size reduction)
- Migrated audio codec detection from string-based to UUID-based matching
  - Enhanced format_compatibility.json with audio codec UUIDs
  - Improved format_registry.py with flexible UUID pattern matching
- Updated CLAUDE.md with directory organization guidelines
- Updated CI workflow to run only minimal tests (excludes e2e tests requiring large samples)
- Refined gitignore: track tests/samples/ci/ but ignore tests/samples/media/ and tests/samples/format_tests/

### Fixed
- Cleaned up repository by removing old logs and misplaced development files
- Improved gitignore coverage for development artifacts (tests/samples/, tests/fixtures/, docs_dev/, scripts_dev/)
- Removed binwalk from optional dependencies (installed via Homebrew, not pip)
- Fixed duplicate dev dependency entries in pyproject.toml
- Fixed CI dependency resolution by using 'uv sync' instead of '--extra dev'

## [0.5.0] - 2025-10-30
### Changed
- Extension normalization improvements for MP4 files
- Removed backup system entirely (no more .bak files)

## [0.4.0] - 2025-10-29
### Changed
- Major refactor: backup system removed for simplicity
- Fixed .mp4 extension normalization bug

## [0.3.4] - 2025-10-29
### Fixed
- Skip .bak files during scanning to prevent double extension bug

## [0.3.0a1] - 2025-10-26
### Added
- Comprehensive README, CONTRIBUTING, LICENSE, and CHANGELOG plus expanded `.gitignore` coverage.
- CLI `--version` flag and startup banner so each run identifies the exact build.
- Guidance for cloning the repo with `uv sync --extra dev`, secret-scanning requirements, and release checklist documentation.
- Local docs safeguard (`docs_dev/` ignore rules, `scripts/protect_docs_dev.sh`, and Git hooks) that back up private files before risky operations and restore them automatically.
- README updates clarifying macOS-only support, installation flows (PyPI, local wheels, editable), and a dependency license table noting the GPLv2 implications of using `hachoir` plus MIT/BSD/HPND acknowledgments.
- Progress bars with ETA for staging/processing/import, while detailed logs are written to `smm_run_<timestamp>.log`.
- Apple Photos importer now runs in batches of ≤200 files with a generous timeout, logging per-file failures instead of triggering blanket conversions.

### Changed
- Package version bumped via `uv version --bump minor --bump alpha` to reflect the current alpha cycle.
- Detection pipeline now reuses the initial PureMagic signature to avoid double I/O.
- PSD files with unreadable headers now default to TIFF conversion for safety.
- Dotted puremagic identifiers are normalised in the rule matcher, improving coverage.
- JPEG-XL conversions close `mkstemp` handles immediately to prevent descriptor leaks.
- Automatic “safe fallback” conversions were removed to avoid unnecessary TIFF/HEVC churn; failed imports are logged instead of re-encoded.
- File sanitisation now leaves already-safe filenames untouched.

### Fixed
- `pyproject.toml` no longer lists dev/test dependencies in the main install requirements.

## [0.1.5] - 2025-09-??
### Added
- Initial public code drop with detection pipeline, staging/import workflow, and format rules.

[0.3.0a1]: https://github.com/<org>/SMART_MEDIA_MANAGER/releases/tag/v0.3.0a1
