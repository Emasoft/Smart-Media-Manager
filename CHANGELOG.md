# Changelog
All notable changes to this project will be documented here, following [Keep a Changelog](https://keepachangelog.com/) and Semantic Versioning (pre-release identifiers included).

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
