# Claude Code CI Integration Guide

## Quick Reference

### Trigger CI Manually

```bash
# Full run (all checks)
gh workflow run ci.yml

# Tests only (fastest for development)
gh workflow run ci.yml -f run_type=tests-only

# Lint + format check only
gh workflow run ci.yml -f run_type=lint-only

# Quick run (tests + lint, skip expensive checks)
gh workflow run ci.yml -f run_type=quick
```

### Monitor CI Status

```bash
# Watch current run in real-time
gh run watch

# Check latest run status
gh run list --limit 1

# View detailed logs
gh run view --log

# View only failures
gh run view --log-failed

# Check exit status (for scripting)
gh run view <run-id> --exit-status
```

### Download Results

```bash
# Download all artifacts from latest run
gh run download

# Download specific artifact
gh run download <run-id> -n pytest-results-3.12

# List available artifacts
gh api repos/Emasoft/Smart-Media-Manager/actions/artifacts
```

## Event-Driven Triggers

### Automatic Triggers

1. **Push to main** - Runs full CI when code changes
   - Skips for: .md files, docs/, LICENSE
   - Runs for: Python code, tests, configs

2. **Pull Requests** - Runs full CI on PRs
   - Same exclusions as push
   - Posts results to PR

3. **Issue Comments** - Reserved for future automation
   - Could trigger specific checks via comments
   - Currently not used

### No Scheduled Runs

✅ **All triggers are on-demand or event-based**
❌ **No cron jobs or scheduled runs**

This means:
- CI only runs when you push code or manually trigger it
- No surprise CI runs consuming resources
- Predictable and controllable execution

## Run Types

### Full (default)

Runs everything:
- ✅ Tests (Python 3.12 & 3.13)
- ✅ Lint (ruff check + format)
- ✅ Type Check (mypy)
- ✅ Security Scan (gitleaks)
- ✅ Build (package artifacts)

**Use when:** Preparing for release, final checks before merge

### Tests Only

Runs only:
- ✅ Tests (Python 3.12 & 3.13)
- ❌ Skips all other jobs

**Use when:** Rapid testing during development, quick validation

```bash
gh workflow run ci.yml -f run_type=tests-only
```

### Lint Only

Runs:
- ✅ Lint (ruff check)
- ✅ Format Check (ruff format)
- ✅ Type Check (mypy)
- ❌ Skips tests, security, build

**Use when:** Checking code quality without running tests

```bash
gh workflow run ci.yml -f run_type=lint-only
```

### Quick

Runs:
- ✅ Tests (Python 3.12 & 3.13)
- ✅ Lint (ruff check + format)
- ❌ Skips type check, security, build

**Use when:** Fast validation during active development

```bash
gh workflow run ci.yml -f run_type=quick
```

## Typical Workflows

### During Development

```bash
# Make changes
vim smart_media_manager/cli.py

# Run tests locally first
uv run pytest

# Push changes (triggers CI automatically)
git push

# Watch CI in real-time
gh run watch
```

### Before Committing

```bash
# Check formatting
uv run ruff format --check smart_media_manager/ tests/

# Fix formatting
uv run ruff format smart_media_manager/ tests/

# Check lint
uv run ruff check smart_media_manager/ tests/

# Fix lint issues
uv run ruff check --fix smart_media_manager/ tests/

# Run tests
uv run pytest

# Commit and push
git commit -m "Fix bug in media detection"
git push
```

### After CI Failure

```bash
# View what failed
gh run view --log-failed

# Download failure logs
gh run download

# Analyze logs
cat pytest-results-3.12/pytest-output.txt

# Fix and push
# CI runs automatically
```

### Manual Validation

```bash
# Trigger quick check without pushing
gh workflow run ci.yml -f run_type=quick

# Wait for completion
gh run watch

# Check results
gh run view --log
```

## Accessing CI Results in Claude Code

### Example: Check if tests passed

```bash
# Get latest run
RUN_ID=$(gh run list --limit 1 --json databaseId -q '.[0].databaseId')

# Check status
gh run view $RUN_ID --json conclusion -q '.conclusion'
# Returns: success, failure, cancelled, or skipped
```

### Example: Get test output

```bash
# Download pytest results
gh run download --name pytest-results-3.12

# Read results
cat pytest-results-3.12/pytest-output.txt
```

### Example: Check lint errors

```bash
# Download lint results
gh run download --name lint-results

# View ruff check output
cat lint-results/ruff-check.txt
```

## Job Dependencies

```
should-run (determines what runs)
    ├─> test (if run-tests=true)
    ├─> lint (if run-lint=true)
    ├─> type-check (if run-typecheck=true)
    ├─> security (if run-security=true)
    └─> build (if run-build=true AND tests+lint passed)
        └─> summary (always runs)
```

## Path Filters

CI skips on changes to:
- `**.md` - All markdown files
- `docs/**` - Documentation folder
- `docs_dev/**` - Local development docs
- `LICENSE` - License file

CI runs on changes to:
- `**/*.py` - Python source files
- `pyproject.toml` - Dependencies
- `uv.lock` - Lock file
- `.github/workflows/**` - CI config
- Everything else

## Artifact Retention

All artifacts kept for **30 days**:
- Test results (pytest outputs)
- Lint results (ruff check/format outputs)
- Type check results (mypy outputs)
- Build artifacts (wheels, sdists)

## GitHub Actions Permissions

The workflow uses `GITHUB_TOKEN` with these permissions:
- `contents: read` - Read repository files
- `security-events: write` - Write security scan results
- `pull-requests: write` - Comment on PRs (future use)

## Tips for Claude Code

1. **Always run local checks first** - Faster feedback
   ```bash
   uv run pytest && uv run ruff check .
   ```

2. **Use quick runs during development** - Save time
   ```bash
   gh workflow run ci.yml -f run_type=quick
   ```

3. **Watch runs in real-time** - Immediate feedback
   ```bash
   gh run watch
   ```

4. **Download artifacts for debugging** - Full context
   ```bash
   gh run download
   ```

5. **Check status programmatically** - For automation
   ```bash
   gh run view --exit-status && echo "CI passed"
   ```

## Troubleshooting

### Workflow not triggering

**Check:** Does your change modify filtered paths?
- Changes to only .md files won't trigger CI
- Update code files to trigger

### Job skipped unexpectedly

**Check:** Run type configuration
```bash
# This only runs tests
gh workflow run ci.yml -f run_type=tests-only
# Lint/build/etc will be skipped
```

### Can't find artifacts

**Check:** Artifact retention (30 days)
```bash
gh api repos/Emasoft/Smart-Media-Manager/actions/artifacts
```

### Build fails but tests pass

**Check:** Build only runs if tests AND lint pass
- Fix lint errors first
- Or use `tests-only` to skip build

## Future Enhancements

Possible additions (not implemented):
- Comment-triggered runs via issue_comment
- Automatic PR updates with test results
- Benchmark tracking
- Coverage reporting
- Performance regression detection

All of these would be **event-driven**, not scheduled.

## Summary

✅ **Event-Driven** - No cron/scheduled jobs
✅ **On-Demand** - Manual triggers with options
✅ **Smart Filtering** - Skips on doc changes
✅ **Conditional Execution** - Run only what you need
✅ **CLI-First** - Optimized for `gh` command
✅ **Fast Feedback** - Parallel jobs
✅ **Comprehensive** - Tests, lint, type-check, security, build

Perfect for Claude Code integration!
