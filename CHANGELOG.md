# Changelog
All notable changes to this project will be documented here, following [Keep a Changelog](https://keepachangelog.com/) and Semantic Versioning (pre-release identifiers included).

## [0.5.44] - 2026-01-30
### Fixed
- **Bug #9**: Fixed `--recursive` not detecting all files in nested folders
  - Added `onerror` callback to `os.walk()` to log permission errors instead of silently skipping directories
  - Added debug logging for directory traversal progress

- **Bug #10**: Fixed files rejected by Apple Photos due to codec verification issues
  - Changed `refine_video_media()` to flag incompatible codecs for transcoding instead of rejecting
  - Incompatible video tags (avc3, hev1, dvhe) now flag for remux/transcode
  - Dolby Vision content now flags for standard HEVC transcode
  - Unsupported audio codecs (FLAC, Opus, DTS, Vorbis, TrueHD) now flag for AAC transcode
  - Fixed `is_already_photos_compatible()` overriding UUID-based transcode decisions

- **Bug #13**: Fixed Photos dialogs not being auto-dismissed during import
  - Added `dismiss_photos_dialog()` function using System Events AppleScript
  - Automatically clicks Import, Import All, OK, Allow, Continue, Done, Skip buttons
  - Falls back to user prompt only if System Events automation fails

- **Audit**: Fixed remaining rejection patterns in refinement functions
  - Audio sample rate check now flags for transcode (AAC resamples to 48kHz)
  - PSD CMYK/LAB/multichannel/duotone modes now flag for TIFF conversion instead of rejection

### Added
- **Feature #11**: Added `--include-staged` option to include previously staged files and FOUND_MEDIA_FILES_* directories in scan
- **Feature #12**: Added `--save-formats-report` option to control saving unknown format mappings JSON (now opt-in)
- Custom secrets scanner (`scripts/secrets_scan.py`) replacing gitleaks
  - 20+ detection patterns for API keys, tokens, private keys, database URLs
  - Project-specific allowlist for public GitHub user info
  - Entropy-based detection for base64-encoded secrets
  - Supports `--staged`, `--commits`, `--files` modes
  - GitHub Actions annotations for inline error display

### Changed
- Replaced gitleaks-action with custom secrets scanner in CI (fixes issue_comment event failures)

**Note**: This release includes all changes from 0.5.44a1, 0.5.44a2, and 0.5.44a3 alpha versions:
- AppleScript 24-hour timeout for Photos dialogs
- Graceful Ctrl+C handling with log preservation
- Fail-fast imports for pyfsig/rawpy (removed lazy loading)
- VP8 codec support in format compatibility database
- Fixed import statistics miscounting converted files
- ORIGINALS folder moved outside staging to prevent Photos importing source files

## [0.5.43a2] - 2025-01-05
### Fixed
- Fixed 6 failing tests:
  - `test_ensure_brew_cask_skips_when_present`: Fixed to expect no-op when cask already installed
  - `test_refine_video_media_rejects_opus_audio`: Added audio_codec field to MediaFile
  - `test_typescript_file_is_skipped`: Created missing tests/samples/use-database.ts
  - `test_run_command_with_progress_raises_for_failed_command`: Fixed regex pattern
  - `test_sequential_suffix_preserves_extensions`: Fixed suffix format `_(1)` not `(1)`
  - `test_import_folder_to_photos_trimmed_suffix`: Updated staging name regex

### Added
- New test samples infrastructure with YAML-based configuration:
  - `samples/` directory with real media files for CI testing
  - `samples/test_set.yaml` defining test sets and file checksums
  - `scripts/validate_samples.sh` for sample integrity checks
  - `githooks/pre-commit` for pre-commit validation
  - `tests/__init__.py` for proper package structure

### Removed
- Moved obsolete dev docs to docs_dev/ (TODO.md, COOLDOWN_FIX.md, etc.)
- Removed format_analysis/ (moved to docs_dev/)

## [0.5.40a2] - 2025-12-22
### Changed
- Canonicalized the format registry to `smart_media_manager/format_registry.json` and updated the generator to write there.
- Tracked compatibility tester sources under `scripts_dev/` and narrowed git hooks to protect only `docs_dev/`.
- Added macOS minimal CI workflow and made CI fail on lint/tests/type-check/security issues.
- Added a tag-triggered GitHub release workflow to attach `dist/*` artifacts.

### Fixed
- Marked sample-dependent end-to-end tests as `@pytest.mark.e2e` to keep default runs green without large fixtures.
- Disabled Pillow decompression-bomb limit by default and added `--max-image-pixels`/`SMART_MEDIA_MANAGER_MAX_IMAGE_PIXELS` overrides.

## [0.5.8a1] - 2025-10-31
### Fixed
- **CRITICAL**: Import count reconciliation now uses simple count-based matching instead of complex per-file filename matching
  - Root cause: Previous reconciliation logic tried to match Photos-returned filenames against staged filenames, but Photos returns ORIGINAL filenames for duplicate media (not current filenames with accumulated sequential suffixes)
  - This caused false "skipped" reports: 434 of 4,561 files incorrectly marked as skipped despite all files being successfully imported
  - Empirical evidence: 7 test runs with 4,561 files each showed 100% import success rate - Photos NEVER skips files in practice
  - Fix: Replaced complex filename matching with simple count comparison: if Photos returns N items and we staged N files, all N were imported successfully
  - Per-file matching is unnecessary and error-prone due to Photos' duplicate detection behavior and filename normalization
  - Result: Reconciliation now correctly reports "4,561 imported, 0 skipped" when Photos imports all files

- **CRITICAL**: Removed runtime pip installation and moved rawpy to main dependencies - fixes crash when RAW files encountered
  - Root cause: Script attempted runtime `pip install rawpy` into uv-managed tool environment when RAW files detected
  - This conflicts with package management and fails due to: C extension compilation, uv environment isolation, missing libraw
  - Previous behavior: Script crashes with "Error: Command failed: python -m pip install --upgrade rawpy"
  - Fix:
    - Removed runtime pip installation logic entirely
    - Moved rawpy from optional `[enhanced]` extras to main dependencies in pyproject.toml
    - RAW support now included by default in all installations
  - System dependencies (libraw, adobe-dng-converter) still auto-installed via Homebrew when RAW files detected
  - If rawpy import fails, RAW files are gracefully skipped with helpful error message

## [0.5.1a5] - 2025-10-31
### Added
- Detailed reconciliation debug logging
  - Logs first 5 filenames returned by Photos (with repr() for exact format)
  - Logs first 5 mismatched filenames between Photos output and staged files
  - Helps diagnose why 365 files are being marked as "skipped" when Photos imported 4561 of 4562 files

## [0.5.1a4] - 2025-10-31
### Added
- Debug timestamps for import function execution tracking
  - Added 4 timestamped log markers (WARNING level, visible in console and log):
    - 🚨 Before calling `import_folder_to_photos` in main()
    - ✅ Function execution start
    - 📸 Before AppleScript execution
    - 📸 After AppleScript completion
  - Helps identify if any code attempts Photos import before the official function call
  - Timestamps include millisecond precision for accurate timeline analysis

## [0.5.1a3] - 2025-10-31
### Fixed
- Import count reconciliation: Fixed critical bug where reconciliation compared Photos' returned filenames against SOURCE basenames instead of STAGED basenames
  - Source files: `file (1234).png` → Staged files: `file (1234) (5678).png` (sequential suffix added for uniqueness)
  - Photos returns: `file (1234) (5678).png` (correct staged name)
  - Bug: v0.5.1a2 compared against `file (1234).png`, causing 578 false "skipped" reports
  - Fix: Now correctly compares against `media.stage_path.name` instead of `media.source.name`
  - Result: Accurate reconciliation of which files were actually imported vs skipped

## [0.5.1a2] - 2025-10-31
### Fixed
- Console output flooding: Changed SkipLogger to use LOG.info instead of LOG.warning, moving skip messages to log files only
- Duplicate check logic: Fixed backwards logic - now defaults to showing duplicate prompt (as in original bash script)
- Added progress message before Photos import to prevent appearance of hanging

### Changed
- Renamed `--check-duplicates` flag to `--skip-duplicate-check` for clearer semantics
- By default, Photos.app now prompts for duplicate handling instead of auto-skipping

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
- Guidance for cloning the repo with `uv sync`, secret-scanning requirements, and release checklist documentation.
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

[0.3.0a1]: https://github.com/Emasoft/Smart-Media-Manager/releases/tag/v0.3.0a1
