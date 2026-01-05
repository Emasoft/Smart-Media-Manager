# Contributing to Smart Media Manager

Thanks for helping keep photo libraries tidy! This guide outlines how to work on the project without accidentally committing large media files or sensitive data.

## For Users: Installing the Tool

**Recommended**: Install globally as a uv tool (creates `smart-media-manager` on your PATH):

```bash
uv tool install smart-media-manager
```

This is the recommended method for end users. The executable will be available system-wide.

To install a specific version:
```bash
uv tool install smart-media-manager==0.5.43a1
```

To upgrade to the latest version:
```bash
uv tool upgrade smart-media-manager
```

> **Note**: Installing via `uv pip install` or `uv add` into a project venv is discouraged for end users. The global tool installation ensures the CLI is always available and doesn't conflict with project-specific dependencies.

---

## For Developers: Setting Up the Development Environment

1. **Clone the repo**:
   ```bash
   git clone https://github.com/Emasoft/Smart-Media-Manager.git
   cd Smart-Media-Manager
   ```

2. **Install dependencies** (including dev tooling):
   ```bash
   uv sync
   ```
   This installs runtime dependencies plus dev tools (pytest, ruff, etc.) defined in `[dependency-groups]`.

3. **Install editable version** (optional but recommended for development):
   ```bash
   uv tool install --editable .
   ```
   This installs the CLI globally but linked to your local source, so changes take effect immediately.

4. **Verify the installation**:
   ```bash
   smart-media-manager --version
   uv run pytest
   ```

5. **Protect local-only docs**: Enable the bundled hooks so `docs_dev/` is backed up before risky operations and restored automatically after checkouts/merges.

   ```bash
   git config core.hooksPath githooks
   ```

   The hooks invoke `scripts/protect_docs_dev.sh`. You can also run `./scripts/protect_docs_dev.sh backup` (or `restore`) manually, and hooks will abort operations such as rebases if `docs_dev/` is missing without a backup, preventing accidental loss.

### Development Scripts

The `reinstall.sh` script automates version bumping, building, and reinstalling the tool:
```bash
./reinstall.sh
```
This bumps the patch version, builds a wheel, and reinstalls the tool globally. Use this after making changes to test them.

---

## Coding Standards

- Python 3.12, four-space indentation, and PEP 8 naming.
- Prefer `pathlib.Path`, structured logging, and the helpers in `smart_media_manager.cli` (e.g., `build_safe_stem`, `sanitize_stage_paths`).
- Preserve and extend the type hints/dataclasses; the detection pipeline relies on them for validation.
- Required dependencies (pyfsig, rawpy, python-magic, etc.) are imported at module level. Only python-magic is lazily imported because it requires libmagic from Homebrew.

### Code Quality Commands

```bash
# Format code (DO NOT use black)
uv run ruff format --line-length=320 smart_media_manager/ tests/

# Lint and auto-fix
uv run ruff check --fix smart_media_manager/ tests/

# Run tests
uv run pytest
```

---

## Tests

- Place new tests in `tests/` using `pytest` naming (`test_*.py`).
- Use fixtures/monkeypatching to avoid calling Apple Photos or touching real media.
- Run `uv run pytest` before opening a PR.
- Tests marked with `@pytest.mark.e2e` require large sample files and are skipped in CI.
- Tests marked with `@pytest.mark.minimal` are lightweight CI tests.

---

## Commit & PR Checklist

- [ ] `uv run pytest` passes
- [ ] `smart-media-manager --version` shows correct version
- [ ] Update CHANGELOG.md when changing behaviour
- [ ] Redact or remove any personal media paths from logs or examples
- [ ] Run secrets scan: `uv tool run gitleaks detect --no-banner`
- [ ] Confirm `git status` shows only intentional changes

---

## Release Process

1. Update CHANGELOG.md and docs for the upcoming release.
2. Bump the version:
   ```bash
   uv version --bump minor --bump alpha
   ```
3. Run tests and verify:
   ```bash
   uv run pytest
   smart-media-manager --version
   ```
4. Build artifacts:
   ```bash
   uv build
   ```
5. Tag and push:
   ```bash
   git tag vX.Y.ZaN
   git push origin vX.Y.ZaN
   ```
6. Publish to PyPI:
   ```bash
   uv publish
   ```
7. GitHub release is created automatically via workflow on tag push.

---

## Reporting Issues

Include:
- macOS version and Apple Photos build
- CLI output (with personal paths redacted)
- Steps to reproduce
- Any skip log excerpts that illustrate the failure

Thanks again for contributing!
