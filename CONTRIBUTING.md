# Contributing to Smart Media Manager

Thanks for helping keep photo libraries tidy! This guide outlines how to work on the project without accidentally committing large media files or sensitive data.

## Getting Started
1. **Clone the repo** (sdists/wheels exclude docs/tests):
   ```bash
   git clone https://github.com/<org>/SMART_MEDIA_MANAGER.git
   cd SMART_MEDIA_MANAGER
   ```
2. **Install dependencies** (including dev tooling):
   ```bash
   uv sync --extra dev
   ```
3. **Verify the installation**:
   ```bash
   uv run smart-media-manager --version
   uv run pytest
   ```
4. **Protect local-only docs**: enable the bundled hooks so `docs_dev/` is backed up before risky operations and restored automatically after checkouts/merges.

   ```bash
   git config core.hooksPath githooks
   ```

   The hooks invoke `scripts/protect_docs_dev.sh`. You can also run `./scripts/protect_docs_dev.sh backup` (or `restore`) manually, and hooks will abort operations such as rebases if `docs_dev/` is missing without a backup, preventing accidental loss.

## Coding Standards
- Python 3.12, four-space indentation, and PEP 8 naming.
- Prefer `pathlib.Path`, structured logging, and the helpers in `smart_media_manager.cli` (e.g., `build_safe_stem`, `sanitize_stage_paths`).
- Preserve and extend the type hints/dataclasses; the detection pipeline relies on them for validation.
- Optional dependencies (binwalk, pyfsig, rawpy) must stay optional—guard imports and log actionable errors.

## Tests
- Place new tests in `tests/` using `pytest` naming (`test_*.py`).
- Use fixtures/monkeypatching to avoid calling Apple Photos or touching real media.
- Run `uv run pytest` before opening a PR.

## Commit & PR Checklist
- `uv run pytest`
- `uv run smart-media-manager --version` (ensures the version metadata is wired up)
- Update docs/CHANGELOG when changing behaviour.
- Redact or remove any personal media paths from logs or examples.
- Run a secrets scan (`uv tool run gitleaks detect --no-banner` or equivalent) before pushing.
- Confirm `git status` shows only intentional changes.

## Release Process
1. Update CHANGELOG and docs for the upcoming release.
2. Bump the version via `uv version --bump minor --bump alpha` (mirrors the requested `uv bump minor` + `uv bump minor --alpha`).
3. Tag the release and build artifacts:
   ```bash
   uv build
   ```
4. Optional: publish to PyPI with `uv publish`.
5. Verify that sdists/wheels exclude docs/tests (default setuptools config already restricts packages to `smart_media_manager`).

## Reporting Issues
Include:
- macOS version and Apple Photos build
- CLI output (with personal paths redacted)
- Steps to reproduce
- Any skip log excerpts that illustrate the failure

Thanks again for contributing!
