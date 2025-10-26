# Smart Media Manager

> [!WARNING]
> **🚧 Alpha Software - Do Not Use in Production**
>
> This project is currently in **alpha stage** and under active development. It may contain bugs, incomplete features, or unexpected behavior. **Do not use this tool on your only copy of important media files.** Always maintain backups before running this software.

<p align="center">
  <strong>A macOS-first CLI that audits folders of photos and videos, fixes mismatched extensions, stages compatible media, and imports everything into Apple Photos without manual clicking.</strong>
</p>

<p align="center">
  <a href="#highlights">Highlights</a> •
  <a href="#requirements">Requirements</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#development-workflow">Development</a> •
  <a href="#testing">Testing</a>
</p>

---

Smart Media Manager normalizes filenames, validates files via multiple signature detectors, auto-installs transcode dependencies, and keeps a skip log so nothing silently disappears.

## ✨ Highlights

- 🔍 **Deterministic detection pipeline** — Powered by libmagic, PureMagic, PyFSig, binwalk, and ffprobe consensus voting plus RAW refinement
- 🔄 **Self-healing conversions** — Including PNG/HEIC transcodes, HEVC rewraps, GIF/APNG animation handling, and safe fallbacks when Apple Photos rejects a batch
- 📦 **Dependency bootstrapper** — Installs Homebrew formulas (`ffmpeg`, `libheif`, `imagemagick`, etc.) and RAW codecs only when the current camera family needs them
- 🍎 **Apple Photos automation** — Batched AppleScript commands with retry logic and metadata preservation using `exiftool`
- 📊 **Comprehensive statistics** — Color-coded summary with detailed metrics for scanned, converted, imported, and skipped files
- 🔁 **Interactive retry** — Prompt to retry failed imports without re-running the entire pipeline
- 📝 **Transparent skip logging** — Corrupt files, archives, vector artwork, and unsupported assets are called out with remediation guidance

## 📋 Requirements

| Requirement | Details |
|-------------|---------|
| **Operating System** | macOS 12 (Monterey) or newer with stock Photos app<br>⚠️ Does **not** work on Windows or Linux |
| **Package Manager** | Homebrew (auto-installs dependencies) |
| **Python** | 3.12+ (managed by `uv`) |
| **Disk Space** | Sufficient for staging folders and logs |

### ⚙️ Configuration Notes

<details>
<summary><b>Skipping dependency bootstrap</b></summary>

If you prefer to manage Homebrew/pip packages yourself, pass `--skip-bootstrap` (or set `SMART_MEDIA_MANAGER_SKIP_BOOTSTRAP=1`). The CLI will trust your environment and skip auto-installs, but will fail if required tools are missing.
</details>

<details>
<summary><b>No automatic fallbacks</b></summary>

When Apple Photos refuses a file, the CLI logs it to `smm_skipped_files_<timestamp>.log` and moves on. It never attempts emergency conversions that could explode disk usage.
</details>

## 🚀 Installation

### 📦 From a published release (recommended for end users)

Once wheels/sdists are available on PyPI or via GitHub Releases you can install the CLI globally with uv:

```bash
uv tool install smart-media-manager
```

Pass a version pin (e.g., `==0.3.1a1`) if you need a specific build.

### 🔨 From local build artifacts

If you have cloned the repo and want to install the latest source snapshot without dev-only files:

```bash
uv build                        # creates dist/smart_media_manager-<ver>-py3-none-any.whl
uv tool install dist/smart_media_manager-<ver>-py3-none-any.whl
```

Replace `<ver>` with the wheel filename emitted under `dist/`.

### 🛠️ From source in editable mode (active development)

Keep the CLI on your PATH while editing the codebase:

```bash
uv tool install --editable .
```

This symlinks the working tree, so `smart-media-manager --version` immediately reflects local changes. Re-run the command after pulling new dependencies.

---

## 👨‍💻 Development Workflow

### 1️⃣ Clone the repository

```bash
git clone https://github.com/Emasoft/Smart-Media-Manager.git
cd Smart-Media-Manager
```

### 2️⃣ Install dependencies

```bash
uv sync --extra dev
```

> **💡 Tip:** If you prefer to manage Homebrew packages yourself, set `SMART_MEDIA_MANAGER_SKIP_BOOTSTRAP=1` or pass `--skip-bootstrap`

### 3️⃣ Register the editable CLI (optional)

```bash
uv tool install --editable .
```

### 4️⃣ Enable safety hooks

```bash
git config core.hooksPath githooks
```

This protects `docs_dev/` from accidental deletion during git operations.

### 5️⃣ Run tests

```bash
uv run pytest
```

---

## 💻 Usage

### Basic command

Scan a directory (recursively) and stage/import media:

```bash
uv run smart-media-manager --path "$HOME/Pictures/Inbox" --recursive
```

### Command-line flags

| Flag | Description |
| --- | --- |
| `--path PATH` | Folder to scan (defaults to the current directory). |
| `--recursive` | Descend into subdirectories. |
| `--follow-symlinks` | Follow symlinks instead of skipping them. |
| `--delete` | Remove the `FOUND_MEDIA_FILES_<timestamp>` staging folder after a successful import. |
| `--version` | Print the CLI name and version (auto-updated via `uv version --bump ...`). |
| `--skip-bootstrap` | Skip automatic Homebrew/pip dependency installation (requires tools pre-installed). |

### 📊 Output & Logging

- **Console output:** Progress bars with ETA + color-coded statistics summary
- **Detailed logs:** Saved to `.smm_logs/smm_run_<timestamp>.log` in the scanned folder
- **Skip logs:** Failed/skipped files listed in `smm_skipped_files_<timestamp>.log`
- **Batching:** Apple Photos imports sent in batches of ≤200 files (10-minute timeout per batch)
- **Filename preservation:** Only sanitized when necessary (unsafe characters, duplicates)

### 🔄 Interactive Features

After the import completes, if any files failed:
- **Statistics summary** shows detailed breakdown with color coding
- **Retry prompt** allows you to retry just the failed imports
- **Updated results** displayed after retry attempt

---

## 🧪 Testing

All tests live under `tests/` (tracked in Git but excluded from wheels). After `uv sync --extra dev`, run:

```bash
uv run pytest
```

Fixtures include lightweight sample media and monkeypatched detectors so most scenarios run without Apple Photos.

---

## 📦 Release & Publishing Checklist

1. ✅ Update code/docs and add a CHANGELOG entry
2. ✅ Bump version: `uv version --bump minor --bump alpha`
3. ✅ Verify version: `uv run smart-media-manager --version`
4. ✅ Run tests: `uv run pytest`
5. ✅ Scan for secrets: `uv tool run gitleaks detect --no-banner`
6. ✅ Build artifacts: `uv build`
7. ✅ Inspect `dist/` contents
8. ✅ Verify git status and push/publish: `uv publish`

---

## 🔒 Privacy & Data Hygiene

> [!CAUTION]
> **Sensitive Data Warning**

- **Skip logs** (`smm_skipped_files_<timestamp>.log`) may contain partial paths — redact before sharing publicly
- **Staging directories** (`FOUND_MEDIA_FILES_*`) are large and gitignored — delete after confirming imports
- **Always scan for secrets** (gitleaks, detect-secrets) before opening PRs or releases

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

---

## 🗂️ Local-only Documentation

Anything in `docs_dev/` is intentionally gitignored and never published. The project includes safeguard hooks that automatically backup and restore this folder during git operations (checkout, rebase, merge).

**Backup location:** `.git/local_backups/docs_dev.tar.gz`

Enable the hooks once per clone:

```bash
git config core.hooksPath githooks
```

The hooks invoke `scripts/protect_docs_dev.sh`. You can also trigger it manually:

```bash
# snapshot docs_dev immediately
./scripts/protect_docs_dev.sh backup

# restore from the latest local backup
./scripts/protect_docs_dev.sh restore
```

If a risky operation (e.g., `git rebase`) discovers that `docs_dev/` is missing **and** no backup exists, the guard aborts with a warning so you can rescue the files before proceeding.

## Licensing & Acknowledgments
- Smart Media Manager’s source is provided under the MIT License (see [LICENSE](LICENSE)).
- Runtime functionality depends on third-party tools; redistribute their licenses when shipping binaries:

| Component | License | Notes |
| --- | --- | --- |
| `filetype` 1.2.0 | MIT | https://pypi.org/project/filetype/ |
| `puremagic` 1.30 | MIT | Keep copyright notice in docs. |
| `isbinary` 1.0.1 | BSD-3-Clause | Include attribution if redistributed. |
| `python-magic` 0.4.27 | MIT | Wraps libmagic; requires system `libmagic`. |
| `pyfsig` 1.1.1 | MIT | Used for signature voting. |
| `pillow` 12.0.0 | HPND/MIT-CMU | License file bundled in wheels; retain when redistributing. |
| `hachoir` 3.3.0 | GPL-2.0-only | Because the CLI imports hachoir, any binary distribution must satisfy GPL v2 obligations (provide corresponding source, preserve notices). |
| `binwalk` 2.1.0 | MIT (per upstream project) | PyPI metadata omits the license; copy the upstream LICENSE into release assets to meet attribution requirements. |

External executables installed via Homebrew (`ffmpeg`, `ffprobe`, `imagemagick`, `exiftool`, `heif-enc`, `djxl`, `libraw`, etc.) each ship under their own licenses; refer to Homebrew’s caveats when publishing packaged installers.

## License
Smart Media Manager is distributed under the MIT License. See [LICENSE](LICENSE) for details.

## Support
Please open an issue or discussion in the repository for bugs, feature requests, or Apple Photos compatibility updates.
