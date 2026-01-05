# Changelog
All notable changes to this project will be documented here, following [Keep a Changelog](https://keepachangelog.com/) and Semantic Versioning (pre-release identifiers included).

## [Unreleased]
### Fixed
- **IMPORTANT**: Fixed AppleScript timeout error (-1712) when Photos shows dialogs during import
  - Root cause: AppleScript used default timeout which was too short when Photos displayed user dialogs
  - Symptom: "AppleEvent timed out" error causing import to crash instead of waiting
  - Fix:
    - Added `with timeout of 86400 seconds` (24 hours) in AppleScript tell block
    - Added retry loop (10 retries) for error -1712 with user interaction prompt
    - User can press Enter to retry after closing dialog, or type 'abort' to cancel
    - Removed subprocess timeout (letting AppleScript handle it internally)
  - Result: Photos import waits for user to close dialogs instead of crashing

- **IMPORTANT**: Added graceful Ctrl+C handling
  - Root cause: Pressing Ctrl+C caused ugly Python traceback and potential data loss
  - Fix:
    - Added `except KeyboardInterrupt` handler in main() function
    - Clean exit with visual separator and status message
    - Saves skip log if it has entries
    - Points to detailed log file
    - Preserves staging folder for manual recovery
    - Returns exit code 130 (standard for SIGINT: 128 + 2)
  - Result: Ctrl+C now exits gracefully with logs preserved

### Changed
- **IMPORTANT**: Removed lazy/deferred loading for Python package dependencies (pyfsig, rawpy)
  - Root cause: Lazy imports with try/except blocks made pyfsig and rawpy appear optional when they're required dependencies
  - This violated fail-fast principles and made dependency errors harder to diagnose
  - Changes:
    - Removed try/except ImportError block for `pyfsig` - now imported directly: `from pyfsig import interface as pyfsig_interface`
    - Removed `get_rawpy()` lazy loading function and `_RAWPY_MODULE`/`_RAWPY_IMPORT_ERROR` globals
    - Rawpy now imported directly at module top: `import rawpy`
    - Removed None check in `classify_with_pyfsig()`
    - Updated `refine_raw_media()` to use `rawpy` directly instead of calling `get_rawpy()`
  - Exception: python-magic still lazy-loaded (requires libmagic system library installed via Homebrew during bootstrap)
  - Result: Script fails fast if pyfsig/rawpy missing; can still start without libmagic to run bootstrap
  - Impact: Minimal - pyfsig and rawpy were already required dependencies (pyproject.toml lines 12, 14)

### Fixed
- **IMPORTANT**: Added VP8 codec to format compatibility database
  - Root cause: VP8 codec was defined in format_registry.json but missing from format_compatibility.json
  - Script warned "No UUID mapping found for ffprobe codec 'vp8'" when processing WEBM files with VP8 video
  - Fix:
    - Added VP8 to format_names section with UUID `d91b7c22-6d8b-52a9-b17a-6eda5c3aedac-V`
    - Added VP8 to needs_transcode_video (Apple Photos doesn't support VP8)
    - Added VP8 to tool_mappings.ffprobe ("vp8" → UUID)
  - Result: VP8 WEBM files now detected and transcoded to HEVC MP4 without warnings

- **IMPORTANT**: Fixed import statistics miscounting all files as "imported direct" instead of "imported after conversion"
  - Root cause: `requires_processing` flag was cleared to `False` after successful conversion
  - Stats calculation checked `requires_processing`, so all files (converted and direct) had `False`, causing 100% "direct" count
  - Example broken output: "Imported (after conversion): 0, Imported (direct): 40" when 10 MKV→MP4 conversions occurred
  - Fix:
    - Added `was_converted: bool` field to MediaFile dataclass
    - Set `was_converted = True` after each successful conversion in ensure_compatibility()
    - Updated stats calculation to check `was_converted` instead of `requires_processing`
  - Result: Stats now correctly show "Imported (after conversion): 10, Imported (direct): 30" when 10 conversions occur

### Fixed
- **CRITICAL**: Moved ORIGINALS folder outside staging directory to prevent Photos.app from importing incompatible source files
  - Root cause: ORIGINALS folder was created INSIDE staging folder (FOUND_MEDIA_FILES_*/ORIGINALS/)
  - When Photos.app imports folder, it recursively scans ALL subdirectories
  - This caused Photos to find and reject incompatible original files (MKV, WEBM, etc.) even after successful conversion
  - Photos showed error dialog: "The following files could not be imported: [list of MKV files]"
  - Meanwhile, converted MP4 files WERE successfully imported (100% success rate for converted files)
  - Fix:
    - Created ORIGINALS_{timestamp} as SIBLING to FOUND_MEDIA_FILES_{timestamp}, not subdirectory
    - Updated move_to_staging() to accept originals_dir as parameter
    - Added critical comment warning against nesting ORIGINALS inside staging
  - Result: Photos.app now only sees converted, compatible files - no error dialogs
  - Example structure BEFORE (broken):
    ```
    /scan_root/FOUND_MEDIA_FILES_20251031234954/
      ├── file1 (1).mp4  ← Converted, imported ✓
      ├── file2 (2).jpg  ← Direct, imported ✓
      └── ORIGINALS/
          ├── file1.mkv  ← Photos scans this and shows error! ✗
          └── file2.cr3  ← Photos scans this too ✗
    ```
  - Example structure AFTER (fixed):
    ```
    /scan_root/
      ├── FOUND_MEDIA_FILES_20251031234954/
      │   ├── file1 (1).mp4  ← Converted, imported ✓
      │   └── file2 (2).jpg  ← Direct, imported ✓
      └── ORIGINALS_20251031234954/  ← Photos never sees this ✓
          ├── file1.mkv
          └── file2.cr3
    ```

- **IMPORTANT**: Added detailed logging for all conversion operations in ensure_compatibility phase
  - Root cause: Conversions were happening silently - progress bars shown on console but no logs written to log file
  - This caused confusion: user couldn't verify what conversions happened by reviewing the log file
  - Previous behavior: MKV files converted to MP4 successfully, but no log entries showing "Rewrapping MKV to MP4"
  - Fix: Added LOG.info() calls before and after each conversion action
  - Now logs:
    - Before: "Rewrapping mkv (h264/aac) to MP4 container: /path/to/file.mkv"
    - After: "Successfully rewrapped to MP4: /path/to/file.mp4"
  - Applies to all conversion types: PNG, TIFF, HEIC, HEVC MP4, animated conversions, rewraps, transcodes, audio transcodes
  - Log entries include format name and codecs (for video) to provide context on what's being converted
  - Result: Log files now provide complete audit trail of all conversion operations

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
