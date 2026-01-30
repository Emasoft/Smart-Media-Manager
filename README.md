```
┏┓┳┳┓┏┓┳┓┏┳┓  ┳┳┓┏┓┳┓┳┏┓  ┳┳┓┏┓┳┓┏┓┏┓┏┓┳┓
┗┓┃┃┃┣┫┣┫ ┃   ┃┃┃┣ ┃┃┃┣┫  ┃┃┃┣┫┃┃┣┫┃┓┣ ┣┫
┗┛┛ ┗┛┗┛┗ ┻   ┛ ┗┗┛┻┛┻┛┗  ┛ ┗┛┗┛┗┛┗┗┛┗┛┛┗
```

# Smart Media Manager

> [!WARNING]
> **⚠ Alpha Software - Do Not Use in Production**
>
> This project is currently in **alpha stage** and under active development. It may contain bugs, incomplete features, or unexpected behavior. **Do not use this tool on your only copy of important media files.** Always maintain backups before running this software.

<p align="center">
  <strong>A macOS-first CLI that audits folders of photos and videos, fixes mismatched extensions, stages compatible media, and imports everything into Apple Photos without manual clicking.</strong>
</p>

<p align="center">
  <a href="#-understanding-the-three-modes">How It Works</a> •
  <a href="#-requirements">Requirements</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-development">Development</a>
</p>

---

## 📸 What Does This Tool Do? (Simple Explanation)

Imagine you have a big box full of photos and videos scattered everywhere on your computer. Some are in the wrong format, some have weird names, and you want to get them ALL into Apple Photos neatly organized.

**Smart Media Manager is like a smart helper that:**

1. **Finds** all your photos and videos (even in subfolders)
2. **Checks** each file to make sure it's a real photo or video (not a broken file)
3. **Fixes** files that have problems (like wrong file extensions or incompatible formats)
4. **Imports** everything into Apple Photos automatically

**Without this tool**, you would have to:
- Drag and drop each file manually into Photos
- Figure out which files Apple Photos can't open
- Convert incompatible videos yourself using complicated software
- Rename files with wrong extensions one by one

**With this tool**, you just point it at a folder and it does everything for you!

---

### Technical Summary (For Advanced Users)

Smart Media Manager normalizes filenames, validates files via multiple signature detectors (libmagic, PureMagic, PyFSig, binwalk, ffprobe), auto-installs transcode dependencies, converts incompatible formats, and keeps a skip log so nothing silently disappears.

---

## ✦ Understanding the Three Modes

Think of Smart Media Manager like a helpful assistant that moves your photos and videos into Apple Photos. There are three different ways to use it, depending on how much control you want:

### 🟢 Quick Mode (Fully Automated)

**What it does:** Finds all your photos and videos, prepares them, and adds them to Apple Photos — all in one go!

**Perfect for:** When you trust the tool and want everything done automatically.

**How to use it:**
```bash
smart-media-manager ~/Pictures/Inbox --recursive -y
```

**Think of it like:** Asking someone to clean your room and put everything away without asking you about each item. Fast and easy!

---

### 🟡 Review Mode (Two Steps: Prepare, Then Import)

**What it does:** First, it finds your photos and videos and puts them in a special folder (called a "staging folder"). Then it STOPS and waits for you. You can look through the files, remove any you don't want, and only then tell it to continue.

**Perfect for:** When you want to double-check what will be imported before it happens.

**How to use it:**

**Step 1 — Prepare the files:**
```bash
smart-media-manager ~/Pictures/Inbox --recursive
```
The tool creates a folder like `FOUND_MEDIA_FILES_20250122140530/` with all your media files inside.

**Step 2 — Look through the folder:**
Open the folder in Finder. Delete any files you don't want imported into Apple Photos.

**Step 3 — Continue the import:**
```bash
smart-media-manager --resume FOUND_MEDIA_FILES_20250122140530
```
Or simply use `--resume last` to pick up where you left off:
```bash
smart-media-manager --resume last
```

**Think of it like:** Asking someone to gather all the toys into a box, showing you the box, letting you take out anything you don't want to keep, and THEN putting the rest on the shelf.

> **📌 Important:** All the settings you used in Step 1 are automatically saved in a special file (`.smm_state.json`) inside the staging folder. When you resume in Step 3, the tool remembers exactly how you wanted things done!
>
> **Settings that are saved and restored:**
> - Filter settings (images only, videos only, RAW only, size limits)
> - Quality settings (video quality, image quality, codec preferences)
> - RAW processing options (output format)
> - Safety options (skip conversions, skip renaming, verification modes)
> - Cleanup options (keep backups, delete originals)
> - Logging preferences (log file, format, progress bars)

---

### 🔴 Quiet Mode (For Scripts and Automation)

**What it does:** Runs silently without progress bars or interactive prompts. Perfect for running in the background or from automated scripts.

**Perfect for:** Advanced users who want to run the tool from a script, cron job, or CI system.

**How to use it:**
```bash
smart-media-manager ~/Pictures/Inbox --recursive -y --no-progress --quiet
```

**Think of it like:** A robot that does the work silently in another room and only tells you when it's completely finished.

---

### Which Mode Should I Use?

| I want to... | Use this mode |
|--------------|---------------|
| Just import everything quickly | 🟢 **Quick Mode** with `-y` |
| Check what will be imported before it happens | 🟡 **Review Mode** (no `-y`) |
| Run it automatically from a script | 🔴 **Quiet Mode** with `-y --no-progress` |
| Be asked before each file is processed | 🟡 **Review Mode** with `--confirm-each` |

---

## ✦ Highlights

- **Deterministic detection pipeline** — Consensus voting from libmagic, PureMagic, PyFSig, binwalk, and ffprobe with RAW format refinement
- **Fail-fast conversions** — Direct source→target conversion with automatic cleanup on failure
- **Extension correction** — Fixes mismatched extensions based on actual file content
- **Dependency bootstrapper** — Auto-installs Homebrew formulas (`ffmpeg`, `libheif`, `imagemagick`, etc.) and RAW codecs on demand
- **Apple Photos automation** — Batched AppleScript imports with rate-limiting, retry logic, and metadata preservation via `exiftool`
- **Comprehensive statistics** — Color-coded summary with metrics for scanned, converted, imported, and skipped files
- **Interactive retry** — Retry failed imports without re-running the entire pipeline
- **Transparent skip logging** — Corrupt files, archives, and unsupported assets logged with remediation guidance
- **Progress tracking** — Real-time progress bars with ETA for each pipeline stage
- **Corrupt media detection** — Validates images and videos before staging
- **Smart conversions** — Remuxing for compatible codecs, transcoding only when necessary
- **Dry-run mode** — Preview what would happen without making changes (`--dry-run`)

## ▣ Requirements

| Requirement | Details |
|-------------|---------|
| **Operating System** | macOS 12 (Monterey) or newer with stock Photos app<br>⚠ Does **not** work on Windows or Linux |
| **Package Manager** | Homebrew (auto-installs dependencies) |
| **Python** | 3.12+ (managed by `uv`) |
| **Disk Space** | Sufficient for staging folders and logs |

### ⚙ Configuration Notes

<details>
<summary><b>Skipping dependency bootstrap</b></summary>

If you prefer to manage Homebrew/pip packages yourself, pass `--skip-bootstrap` (or set `SMART_MEDIA_MANAGER_SKIP_BOOTSTRAP=1`). The CLI will trust your environment and skip auto-installs, but will fail if required tools are missing.
</details>

<details>
<summary><b>No automatic fallbacks</b></summary>

When Apple Photos refuses a file, the CLI logs it to `smm_skipped_files_<timestamp>.log` and moves on. It never attempts emergency conversions that could explode disk usage.
</details>

## ⬇ Installation

### Recommended: Install as a tool

Install globally with `uv tool` (creates `smart-media-manager` executable on your PATH):

```bash
uv tool install smart-media-manager --python 3.12
```

> **Note:** The `--python 3.12` flag is required because `rawpy` (used for RAW image processing) only has wheels for Python 3.9-3.13. Without this flag, systems with Python 3.14+ as default will fail to resolve dependencies.

This is the recommended method. The executable will be available system-wide as `smart-media-manager`.

To install a specific version:

```bash
uv tool install smart-media-manager==0.5.44a1 --python 3.12
```

### Alternative: Install as a package

Install into a project or virtual environment:

```bash
# Add to project dependencies
uv add smart-media-manager

# Or install in current venv
uv pip install smart-media-manager
```

When installed as a package, run with: `uv run smart-media-manager` or activate the venv first.

---

## ▶ Usage

### Quick start

Import all media from the current directory:

```bash
smart-media-manager
```

### Common examples

Scan a specific folder recursively:

```bash
smart-media-manager ~/Pictures/Inbox --recursive
```

Scan and delete staging folder after successful import:

```bash
smart-media-manager ~/Downloads/Photos --recursive --delete
```

Import a single file:

```bash
smart-media-manager ~/Downloads/photo.jpg
```

Import into a specific album (non-interactive):

```bash
smart-media-manager ~/Pictures/Vacation --recursive --album "Summer 2024" -y
```

### Command-line options

#### Basic Options

| Option | Description |
|--------|-------------|
| `PATH` | Directory to scan (default: current directory) or path to a single file |
| `-r, --recursive` | Recursively scan subdirectories |
| `--follow-symlinks` | Follow symbolic links when scanning |
| `-d, --delete` | Delete staging folder after successful import |
| `--album NAME` | Photos album name to import into (default: 'Smart Media Manager') |
| `-c, --copy` | Copy files to staging instead of moving (originals untouched) |
| `-y, --yes, --assume-yes` | Skip confirmation prompt (useful for automation) |
| `--version` | Show version and exit |
| `--resume [PATH]` | Resume from staging folder (path, "last", or interactive selector) |

#### Filter Options

| Option | Description |
|--------|-------------|
| `--include-types TYPES` | Only process these media types (comma-separated: image, video, raw) |
| `--exclude-types TYPES` | Exclude these media types (comma-separated: image, video, raw) |
| `--images-only` | Shortcut: only import images (equivalent to `--include-types image`) |
| `--videos-only` | Shortcut: only import videos and animations (equivalent to `--include-types video`) |
| `--only-raw, --raw-only` | Shortcut: only import RAW camera files (equivalent to `--include-types raw`) |
| `--min-size SIZE` | Skip files smaller than SIZE (e.g., 100KB, 1MB, 500B) |
| `--max-size SIZE` | Skip files larger than SIZE (e.g., 4GB, 100MB) |
| `--exclude-pattern PATTERN` | Skip files matching glob pattern (can be repeated) |
| `--include-staged` | Include previously staged files and FOUND_MEDIA_FILES_* directories in scan |

#### Conversion Options

| Option | Description |
|--------|-------------|
| `--video-quality QUALITY` | Video encoding quality: ultrafast, fast, medium (default), slow, veryslow |
| `--image-quality QUALITY` | Image conversion quality: 1-100 (default: 95) |
| `--prefer-hevc` | Prefer HEVC/H.265 codec for video conversions (default) |
| `--prefer-h264` | Prefer H.264/AVC codec for video conversions (wider compatibility) |

#### RAW Processing Options

| Option | Description |
|--------|-------------|
| `--raw-output-format FORMAT` | Output format for RAW conversion: tiff (default), jpeg, png |
| `--skip-raw, --ignore-raw` | Skip all RAW camera files (don't import them) |

#### Logging Options

| Option | Description |
|--------|-------------|
| `--log-file PATH` | Write detailed log to custom file path |
| `--log-format FORMAT` | Log format: text (default), json |
| `--no-progress` | Disable progress bars (useful for CI/scripting) |
| `--save-formats-report` | Save JSON report of unknown format mappings (for developers extending format support) |

#### Safety & Verification Options

| Option | Description |
|--------|-------------|
| `--skip-duplicate-check` | Skip duplicate checking during import (faster but may import duplicates) |
| `--skip-bootstrap` | Skip automatic dependency installation (Homebrew/pip) |
| `--skip-convert` | Skip format conversion/transcoding (files must already be compatible) |
| `--skip-compatibility-check` | Skip all compatibility validation (may cause import errors) |
| `--no-conversions` | Skip files that need conversion (only import already-compatible files) |
| `--skip-renaming` | Skip files with wrong extensions (don't rename, just skip them) |
| `--skip-file-format-verification` | Trust extensions instead of analyzing file content; codec detection still runs |
| `--skip-both-format-and-codec-verification` | Trust extensions only, skip all verification (fastest, riskiest) |
| `--max-image-pixels VALUE` | Set Pillow image pixel limit; use `none` to disable (default) |

#### Cleanup Options

| Option | Description |
|--------|-------------|
| `--delete-originals` | Delete original files after successful staging (use with caution) |
| `--confirm-each` | Prompt for confirmation before each file operation |
| `--keep-backups` | Keep .bak backup files after successful conversion |
| `--skip-import` | Stage and convert files but skip Apple Photos import step |

### What happens during a run

1. **Scanning** — Discovers all files with real-time progress
2. **Detection** — Identifies media types using consensus voting
3. **Staging** — Moves files to `FOUND_MEDIA_FILES_<timestamp>` folder
4. **Conversion** — Processes incompatible formats (PNG, HEVC, etc.)
5. **Import** — Sends batches to Apple Photos via AppleScript
6. **Statistics** — Displays color-coded summary with success rates
7. **Retry prompt** — Option to retry failed imports (if any)

### Output and logging

| Output | Location | Description |
|--------|----------|-------------|
| **Console** | Terminal | Progress bars, warnings, statistics summary |
| **Run log** | `.smm_logs/smm_run_<timestamp>.log` | Detailed INFO-level logs |
| **Skip log** | `smm_skipped_files_<timestamp>.log` | Failed/skipped files with reasons |
| **Staging** | `FOUND_MEDIA_FILES_<timestamp>/` | Processed media (kept unless `--delete`) |

### Interactive features

After import completes, if any files failed:
- ✦ **Statistics summary** — Detailed breakdown with color coding
- ✦ **Retry prompt** — Option to retry just the failed imports
- ✦ **Updated results** — Final statistics after retry

During Photos import, if a dialog blocks:
- ✦ **Dialog detection** — Detects when Photos is waiting for user interaction
- ✦ **Retry prompt** — Close the dialog and press Enter to continue, or type 'abort' to cancel

### Graceful interruption

Press **Ctrl+C** at any time to cleanly interrupt the process:
- Logs are saved to the run log file
- Skip log is preserved if it has entries
- Staging folder is preserved for manual recovery
- Exit code 130 (standard SIGINT) is returned

---

## ⚙ Development

### Quick setup

```bash
# Clone and enter
git clone https://github.com/Emasoft/Smart-Media-Manager.git
cd Smart-Media-Manager

# Install dependencies (runtime + dev tools) and enable hooks
uv sync
git config core.hooksPath githooks

# Install editable version (optional)
uv tool install --editable . --python 3.12

# Run tests
uv run pytest
```

### Development workflow

1. **Make changes** to the codebase
2. **Run tests** with `uv run pytest`
3. **Format code** with `uv run ruff format --line-length=320 smart_media_manager/ tests/`
4. **Check linting** with `uv run ruff check smart_media_manager/ tests/`

### Version management

Bump version (dev only):

```bash
# Bump to next alpha version
uv version --bump minor --bump alpha

# Verify version
smart-media-manager --version
```

---

## ⊕ Testing

Run the test suite:

```bash
uv run pytest
```

Tests use lightweight sample media and monkeypatched detectors, so most scenarios run without Apple Photos.

---

## ▣ Privacy & Data Hygiene

> [!CAUTION]
> **Sensitive Data Warning**

- **Skip logs** (`smm_skipped_files_<timestamp>.log`) may contain partial paths — redact before sharing
- **Staging directories** (`FOUND_MEDIA_FILES_*`) are large and gitignored — delete after confirming imports
- **Always scan for secrets** before opening PRs or releases

---

## ▤ Release Checklist

1. Update CHANGELOG.md
2. Bump version: `uv version --bump minor --bump alpha`
3. Run tests: `uv run pytest`
4. Scan for secrets: `uv tool run gitleaks detect --no-banner`
5. Build: `uv build`
6. Inspect `dist/` contents
7. Tag and push: `git tag vX.Y.ZaN` then `git push origin vX.Y.ZaN`
8. Publish: `uv publish` (PyPI)
9. GitHub release: created automatically on tag push via workflow

---

## ▦ License

MIT License - see [LICENSE](LICENSE) file for details.

## ▧ Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## ▨ Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

## ▩ Local Documentation

The `docs_dev/` folder is gitignored and protected by hooks. It's automatically backed up to `.git/local_backups/docs_dev.tar.gz` during git operations.

Enable hooks once per clone:

```bash
git config core.hooksPath githooks
```

Manual backup/restore:

```bash
./scripts/protect_docs_dev.sh backup   # Create backup
./scripts/protect_docs_dev.sh restore  # Restore from backup
```

---

## ▤ Licensing & Dependencies

Smart Media Manager is MIT licensed. Runtime dependencies:

| Component | License | Notes |
|-----------|---------|-------|
| `filetype` 1.2.0 | MIT | https://pypi.org/project/filetype/ |
| `puremagic` 1.30 | MIT | Keep copyright notice |
| `isbinary` 1.0.1 | BSD-3-Clause | Include attribution if redistributed |
| `python-magic` 0.4.27 | MIT | Wraps system `libmagic` |
| `pyfsig` 1.1.1 | MIT | Signature detection |
| `pillow` 12.0.0 | HPND/MIT-CMU | Retain license when redistributing |
| `rawpy` 0.25.1 | MIT | RAW image processing via LibRaw |

External tools via Homebrew (binwalk, ffmpeg, imagemagick, exiftool, etc.) ship under their own licenses.

---

## ▦ Support

Open an issue or discussion in the repository for bugs, feature requests, or compatibility updates.
