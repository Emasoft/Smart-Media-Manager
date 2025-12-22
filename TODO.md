# Smart Media Manager Fixes TODO

- [x] **Classify non-media binaries without inflating error statistics**
  - Implemented a dedicated `skipped_non_media` counter, tagged all non-media rejection reasons with a `non-media:` prefix, and updated summary/log output so real errors remain visible (`smart_media_manager/cli.py`).

- [x] **Keep Photos debug artifacts out of future scans**
  - Debug AppleScript dumps now write into the run log directory and `should_ignore` filters any lingering `DEBUG_*` files; normal scan roots stay clean.

- [x] **Reconcile Photos output with staged media accurately**
  - Replaced the count-based fallback with multiset reconciliation, logging unmatched entries and returning precise skipped media lists.

- [x] **Package format registry data with the module**
  - Added `smart_media_manager/format_registry.json` as the canonical registry and removed the repo-root duplicate.

- [x] **Update tests for new staging API**
  - Introduced `tests.helpers.stage_media` and switched all staging-related tests to the new helper so the additional originals directory requirement is exercised everywhere.

- [x] **Align duplicate-check CLI flag across code and tests**
  - Tests and docs now assert the `--skip-duplicate-check` behaviour, matching the CLI and preventing attr drift.

- [x] **Detect unsupported audio streams in video refinement**
  - Propagated ffprobe audio metadata into `MediaFile`, expanded validation to inspect the detected codec/sample rate, and retained fallback parsing for edge files.

- [x] **Resolve unused or dead configuration switches**
  - Removed the dormant `--skip-renaming` flag and the unused `HACHOIR_IMAGE_EXTENSIONS` stub from the CLI module.

- [x] **Improve large-scan performance**
  - `gather_media_files` now streams the filesystem walk and uses a dynamic progress reporter, avoiding large in-memory candidate lists.

- [x] **Surface bootstrap command failures**
  - `run_command_with_progress` captures combined stdout/stderr to a temp log, reports the tail on failure, and cleans up artifacts automatically.

- [x] **Ensure dev tooling dependencies remain installable**
  - Added Ruff to the dev dependency group and refreshed `uv.lock` so tool installation matches documentation.
