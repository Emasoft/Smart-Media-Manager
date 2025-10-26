# CI/CD Setup for Claude Code Integration

## Overview

This repository uses GitHub Actions for CI/CD with optimized integration for Claude Code. The setup provides:

- **Automated testing** on every push and PR
- **Code quality checks** (linting, formatting, type checking)
- **Security scanning** with gitleaks
- **Build verification**
- **Comprehensive reports** viewable in GitHub Actions UI and summaries

## GitHub Actions Workflow

### File: `.github/workflows/ci.yml`

This workflow runs on:
- Every push to `main` branch
- Every pull request to `main`
- Manual trigger via `workflow_dispatch`

### Jobs

1. **Test** (macOS)
   - Tests on Python 3.12 and 3.13
   - Runs full pytest suite
   - Generates test reports
   - Uploads results as artifacts (30-day retention)

2. **Lint**
   - Runs `ruff check` on codebase
   - Checks formatting compliance
   - Reports in GitHub-native format (clickable file links)

3. **Type Check**
   - Runs mypy for static type analysis
   - Shows type errors with context

4. **Security**
   - Runs gitleaks to detect secrets
   - Prevents accidental credential commits

5. **Build**
   - Builds wheel and sdist
   - Verifies package structure
   - Uploads build artifacts

6. **Summary**
   - Aggregates all job results
   - Provides overall pipeline status

## Claude Code Integration

### How Claude Code Can Use CI Results

#### 1. Via GitHub CLI (`gh`)

Claude Code can fetch workflow runs and logs directly:

```bash
# Get latest workflow run
gh run list --limit 1

# Get specific run details
gh run view <run-id>

# Download logs
gh run download <run-id>

# View workflow summary
gh run view <run-id> --log
```

#### 2. Via GitHub API

Claude Code has direct GitHub API access:

```bash
# Get workflow runs
gh api repos/Emasoft/Smart-Media-Manager/actions/runs

# Get specific run
gh api repos/Emasoft/Smart-Media-Manager/actions/runs/<run-id>

# Get run logs
gh api repos/Emasoft/Smart-Media-Manager/actions/runs/<run-id>/logs
```

#### 3. Via Artifacts

All test results, lint reports, and build artifacts are uploaded and can be downloaded:

```bash
# List artifacts
gh api repos/Emasoft/Smart-Media-Manager/actions/artifacts

# Download specific artifact
gh api repos/Emasoft/Smart-Media-Manager/actions/artifacts/<artifact-id>/zip > artifact.zip
```

### Automated Checks for PRs

When Claude Code creates a PR, the workflow automatically:
1. Runs all tests
2. Checks code quality
3. Verifies build succeeds
4. Posts results to the PR

Claude can check PR status:

```bash
# Get PR checks
gh pr checks <pr-number>

# View PR status
gh pr view <pr-number> --json statusCheckRollup
```

## Optimal Setup for Claude Code Workflow

### Recommended Pattern

1. **Before Committing:**
   ```bash
   # Run tests locally
   uv run pytest

   # Check formatting
   uv run ruff format --check smart_media_manager/ tests/

   # Check linting
   uv run ruff check smart_media_manager/ tests/
   ```

2. **After Pushing:**
   ```bash
   # Wait for workflow to complete
   gh run watch

   # Check results
   gh run view --log
   ```

3. **If CI Fails:**
   ```bash
   # Download failure logs
   gh run download

   # Analyze and fix
   # Re-run workflow
   gh workflow run ci.yml
   ```

### Setting Up Repository Secrets

For advanced features, you may want to add:

```bash
# Add PyPI token (for automated publishing)
gh secret set PYPI_TOKEN

# Add other secrets as needed
gh secret set SLACK_WEBHOOK  # For notifications
```

## GitHub Actions App

### Is It Installed?

Check if GitHub Actions is enabled:

```bash
gh api repos/Emasoft/Smart-Media-Manager --jq '.has_actions'
```

### Permissions

The workflow uses `GITHUB_TOKEN` which is automatically provided by GitHub Actions. No additional setup needed.

## Monitoring CI Status

### From Command Line

```bash
# Watch current run in real-time
gh run watch

# List recent runs
gh run list --limit 10

# View specific run
gh run view <run-id>
```

### From GitHub UI

Visit: https://github.com/Emasoft/Smart-Media-Manager/actions

### Job Summaries

Each job writes to `$GITHUB_STEP_SUMMARY`, which appears in the Actions UI as markdown-formatted output. This includes:
- Test results with pass/fail counts
- Lint errors with file links
- Type check errors
- Build artifact listing

## Customization Options

### Add More Python Versions

Edit `.github/workflows/ci.yml`:

```yaml
matrix:
  python-version: ["3.12", "3.13", "3.14"]  # Add more versions
```

### Add Coverage Reports

Install coverage tools:

```bash
uv add --dev coverage pytest-cov
```

Update workflow:

```yaml
- name: Run tests with coverage
  run: uv run pytest --cov=smart_media_manager --cov-report=html
```

### Add Notifications

Use GitHub Actions Slack integration or email notifications:

```yaml
- name: Notify on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## Troubleshooting

### Workflow Not Running

1. Check if workflow file is valid YAML
2. Verify it's in `.github/workflows/` directory
3. Check repository Actions settings (Settings → Actions)

### CI Failing on macOS

The test job runs on macOS because this is a macOS-specific tool. If macOS runners are unavailable:

```yaml
runs-on: macos-latest  # or macos-13, macos-12
```

### Artifacts Not Uploading

Ensure artifacts exist before upload:

```yaml
- name: Upload results
  if: always()  # Upload even if tests fail
  uses: actions/upload-artifact@v4
```

## Best Practices for Claude Code

1. **Always run tests locally first** before pushing
2. **Monitor CI status** after pushing with `gh run watch`
3. **Download artifacts** for detailed analysis if CI fails
4. **Use workflow summaries** for quick status checks
5. **Keep CI green** - fix failures promptly

## Future Enhancements

Consider adding:
- **Codecov integration** for coverage tracking
- **Dependabot** for dependency updates (already active!)
- **Release automation** with semantic versioning
- **Docker builds** if containerization is needed
- **Performance benchmarks** for regression testing
- **Auto-merge** for passing Dependabot PRs

## Claude Code Commands

Quick reference for CI operations:

```bash
# Check latest CI status
gh run list --limit 1

# Trigger workflow manually
gh workflow run ci.yml

# Download all artifacts from latest run
gh run download

# View logs from failed job
gh run view --log-failed

# Re-run failed jobs
gh run rerun --failed
```

## Summary

This CI setup is optimized for:
- ✅ Fast feedback (parallel jobs)
- ✅ Detailed reporting (summaries + artifacts)
- ✅ Easy access (GitHub CLI integration)
- ✅ Security (secrets scanning)
- ✅ Quality (linting + type checking)
- ✅ Claude Code integration (CLI-first design)

The workflow runs automatically on every push and PR, providing comprehensive quality checks before code is merged.
