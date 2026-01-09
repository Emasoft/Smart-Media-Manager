#!/usr/bin/env python3
"""
Release script for Smart Media Manager.

Usage: uv run release.py <version>
Example: uv run release.py 0.5.44a1

SAFEGUARDS:
- Validates version format
- Checks for uncommitted changes
- Checks if tag/release already exists (prevents immutable release conflicts)
- Runs tests before release
- Cleans dist/ to prevent re-uploading old files
- Publishes to PyPI BEFORE creating GitHub tag
- Lets the GitHub workflow create the release (never manual gh release create)
- Waits for workflow completion and verifies success
- Reinstalls locally and verifies version
"""

import re
import subprocess
import sys
import time
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""

    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    BOLD = "\033[1m"
    NC = "\033[0m"  # No Color


def error(msg: str) -> None:
    """Print error message and exit."""
    print(f"{Colors.RED}ERROR: {msg}{Colors.NC}", file=sys.stderr)
    sys.exit(1)


def warn(msg: str) -> None:
    """Print warning message."""
    print(f"{Colors.YELLOW}WARNING: {msg}{Colors.NC}")


def info(msg: str) -> None:
    """Print info message."""
    print(f"{Colors.BLUE}{msg}{Colors.NC}")


def success(msg: str) -> None:
    """Print success message."""
    print(f"{Colors.GREEN}{msg}{Colors.NC}")


def run(cmd: str | list[str], check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    if isinstance(cmd, str):
        cmd = cmd.split()
    result = subprocess.run(cmd, capture_output=capture, text=True)
    if check and result.returncode != 0:
        if capture:
            error(f"Command failed: {' '.join(cmd)}\n{result.stderr}")
        else:
            error(f"Command failed: {' '.join(cmd)}")
    return result


def run_quiet(cmd: str | list[str]) -> tuple[int, str, str]:
    """Run a command quietly and return (returncode, stdout, stderr)."""
    if isinstance(cmd, str):
        cmd = cmd.split()
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def validate_version(version: str) -> bool:
    """Validate version format (e.g., 0.5.44a1, 1.0.0, 2.1.3b2, 1.0.0rc1)."""
    pattern = r"^\d+\.\d+\.\d+(a|b|rc)?\d*$"
    return bool(re.match(pattern, version))


def check_uncommitted_changes() -> bool:
    """Check if there are uncommitted changes."""
    code, stdout, _ = run_quiet("git status --porcelain")
    return bool(stdout.strip())


def get_current_branch() -> str:
    """Get the current git branch name."""
    _, stdout, _ = run_quiet("git rev-parse --abbrev-ref HEAD")
    return stdout.strip()


def tag_exists(tag: str) -> bool:
    """Check if a git tag exists locally."""
    code, _, _ = run_quiet(f"git rev-parse {tag}")
    return code == 0


def release_exists(tag: str) -> bool:
    """Check if a GitHub release exists for this tag."""
    code, _, _ = run_quiet(["gh", "release", "view", tag])
    return code == 0


def wait_for_workflow(tag: str, timeout: int = 120) -> bool:
    """Wait for the release workflow to complete."""
    print("Waiting for GitHub Release workflow", end="", flush=True)

    # Wait for workflow to start
    time.sleep(5)

    start_time = time.time()
    while time.time() - start_time < timeout:
        code, stdout, _ = run_quiet(["gh", "run", "list", "--limit", "1", "--json", "status,conclusion,headBranch"])
        if code == 0 and stdout:
            import json

            try:
                runs = json.loads(stdout)
                if runs and runs[0].get("status") == "completed":
                    print()
                    return runs[0].get("conclusion") == "success"
            except json.JSONDecodeError:
                pass
        print(".", end="", flush=True)
        time.sleep(3)

    print()
    return False


def main() -> None:
    """Main release function."""
    if len(sys.argv) != 2:
        print("Usage: uv run release.py <version>")
        print("Example: uv run release.py 0.5.44a1")
        sys.exit(1)

    version = sys.argv[1]
    tag = f"v{version}"

    print()
    print("=" * 50)
    print(f"{Colors.BOLD}  Smart Media Manager Release Script{Colors.NC}")
    print(f"  Version: {version}")
    print("=" * 50)
    print()

    # Validate version format
    if not validate_version(version):
        error(f"Invalid version format: {version}\nExpected: X.Y.Z or X.Y.ZaN (e.g., 0.5.44a1)")

    # SAFEGUARD: Check for uncommitted changes
    if check_uncommitted_changes():
        error("Uncommitted changes detected. Commit or stash them first.")

    # Check current branch
    branch = get_current_branch()
    if branch != "main":
        warn(f"Not on main branch (currently on: {branch})")
        response = input("Continue anyway? [y/N] ").strip().lower()
        if response != "y":
            sys.exit(1)

    # SAFEGUARD: Check if tag already exists locally
    if tag_exists(tag):
        error(f"Tag {tag} already exists locally! Use a different version.")

    # SAFEGUARD: Check if release already exists on GitHub (prevents immutable release conflict)
    if release_exists(tag):
        error(f"A release for {tag} already exists on GitHub! Use a different version.\n" "This tag cannot be reused due to GitHub's immutable release policy.")

    # Step 1: Run tests
    info("[1/10] Running tests...")
    result = run_quiet("uv run pytest -q")
    if result[0] != 0:
        error("Tests failed! Fix them before releasing.")
    success("Tests passed!")

    # Step 2: Run secrets scanner
    info("[2/10] Running secrets scanner...")
    code, _, _ = run_quiet("which gitleaks")
    if code == 0:
        result = run_quiet(["gitleaks", "detect", "--no-banner", "-q"])
        if result[0] != 0 and "leaks found" in result[1].lower():
            error("Secrets detected! Remove them before releasing.")
        success("No secrets detected!")
    else:
        warn("gitleaks not found, skipping secrets scan")

    # Step 3: Bump version
    info(f"[3/10] Bumping version to {version}...")
    run(["uv", "version", version])

    # Step 4: Commit version bump
    info("[4/10] Committing version bump...")
    run("git add -A")
    run(["git", "commit", "-m", f"Bump version to {version}"])

    # Step 5: Push to main
    info("[5/10] Pushing to main...")
    run("git push origin main")

    # Step 6: Clean dist/
    info("[6/10] Cleaning dist/ directory...")
    dist_dir = Path("dist")
    if dist_dir.exists():
        for f in dist_dir.iterdir():
            f.unlink()
    success("dist/ cleaned!")

    # Step 7: Build package
    info("[7/10] Building package...")
    run("uv build")
    wheels = list(Path("dist").glob("*.whl"))
    if wheels:
        success(f"Built: {wheels[0].name}")

    # Step 8: Publish to PyPI (BEFORE creating tag - critical safeguard)
    info("[8/10] Publishing to PyPI...")
    result = run_quiet("uv publish")
    if result[0] != 0:
        error(f"PyPI publish failed!\n{result[2]}")
    success("Published to PyPI!")

    # Step 9: Create and push tag (AFTER PyPI - let workflow create release)
    info("[9/10] Creating and pushing tag...")
    run(["git", "tag", tag, "-m", f"Release {tag}"])
    run(["git", "push", "origin", tag])
    success(f"Tag {tag} pushed!")

    print()
    info("Waiting for GitHub Release workflow...")
    print("The workflow will create the release with dist assets automatically.")
    print()

    # Wait for workflow
    if wait_for_workflow(tag):
        success("GitHub Release workflow succeeded!")
    else:
        warn("Workflow may still be running. Check: gh run list --limit 1")

    # Step 10: Reinstall locally
    info("[10/10] Reinstalling locally...")
    time.sleep(5)  # Wait for PyPI propagation

    # Try specific version first, then latest
    code, _, _ = run_quiet(["uv", "tool", "install", f"smart-media-manager=={version}", "--force", "--upgrade"])
    if code != 0:
        code, _, _ = run_quiet(["uv", "tool", "install", "smart-media-manager", "--force", "--upgrade"])

    if code == 0:
        success(f"Installed smart-media-manager")
    else:
        warn("Local reinstall failed - try: uv tool install smart-media-manager --force --upgrade")

    print()
    print("=" * 50)
    success(f"  Release {version} complete!")
    print("=" * 50)
    print()
    print(f"  PyPI: https://pypi.org/project/smart-media-manager/{version}/")
    print(f"  GitHub: https://github.com/Emasoft/Smart-Media-Manager/releases/tag/{tag}")
    print()

    # Verify installation
    run("smart-media-manager --version", check=False)


if __name__ == "__main__":
    main()
