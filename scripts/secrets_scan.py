#!/usr/bin/env python3
"""
Custom secrets scanner for Smart Media Manager.

Tailored for this project with:
- Known public info allowlist (GitHub user info from CLAUDE.md)
- Patterns for API keys, tokens, passwords, private keys
- Git diff support for scanning only changed files
- CI-friendly output with GitHub Actions annotations

Usage:
    # Scan all tracked files
    python scripts/secrets_scan.py

    # Scan only staged changes
    python scripts/secrets_scan.py --staged

    # Scan specific commit range
    python scripts/secrets_scan.py --commits HEAD~5..HEAD

    # Scan specific files
    python scripts/secrets_scan.py --files src/config.py src/auth.py
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass  # For future type imports


# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

# Files/patterns to skip entirely
SKIP_PATTERNS = [
    r"\.git/",
    r"\.venv/",
    r"__pycache__/",
    r"\.pyc$",
    r"node_modules/",
    r"\.lock$",
    r"uv\.lock$",
    r"poetry\.lock$",
    r"package-lock\.json$",
    r"\.min\.js$",
    r"\.min\.css$",
    r"dist/",
    r"build/",
    r"\.egg-info/",
    r"\.whl$",
    r"\.tar\.gz$",
    r"docs_dev/",
    r"scripts_dev/",
    r"samples_dev/",
    r"\.DS_Store$",
    # Skip self (contains regex patterns that look like secrets)
    r"scripts/secrets_scan\.py$",
    # Binary files
    r"\.(png|jpg|jpeg|gif|ico|webp|mp4|mov|avi|mkv|mp3|wav|pdf|zip|gz|tar|bz2)$",
]

# Known public/safe values that should NOT trigger alerts
# These are intentionally public (from CLAUDE.md)
ALLOWLIST = [
    # Public GitHub noreply email
    "713559+Emasoft@users.noreply.github.com",
    # Public GitHub username
    "Emasoft",
    # Public GitHub profile URL
    "https://github.com/Emasoft",
    # Common test/example values
    "example.com",
    "test@example.com",
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    # Documentation examples
    "your-api-key-here",
    "YOUR_API_KEY",
    "your_token_here",
    "xxx",
    "***",
    "REDACTED",
    # PyPI/GitHub Actions tokens (placeholders)
    "${{ secrets.",
    "secrets.GITHUB_TOKEN",
    "secrets.PYPI_TOKEN",
]

# Entropy threshold for high-entropy string detection
MIN_ENTROPY_THRESHOLD = 4.0
MIN_SECRET_LENGTH = 16


@dataclass
class SecretPattern:
    """A pattern to detect potential secrets."""

    name: str
    pattern: re.Pattern
    severity: str  # "high", "medium", "low"
    description: str


# Secret detection patterns
SECRET_PATTERNS = [
    # API Keys
    SecretPattern(
        name="Generic API Key",
        pattern=re.compile(r"""(?i)(api[_-]?key|apikey)\s*[=:]\s*["']?([a-zA-Z0-9_\-]{20,})["']?"""),
        severity="high",
        description="Potential API key detected",
    ),
    SecretPattern(
        name="Generic Secret",
        pattern=re.compile(r"""(?i)(secret|password|passwd|pwd)\s*[=:]\s*["']?([^\s"']{8,})["']?"""),
        severity="high",
        description="Potential secret/password detected",
    ),
    SecretPattern(
        name="Generic Token",
        pattern=re.compile(r"""(?i)(token|auth[_-]?token|access[_-]?token)\s*[=:]\s*["']?([a-zA-Z0-9_\-]{20,})["']?"""),
        severity="high",
        description="Potential token detected",
    ),
    # AWS
    SecretPattern(
        name="AWS Access Key ID",
        pattern=re.compile(r"""(?<![A-Z0-9])AKIA[0-9A-Z]{16}(?![A-Z0-9])"""),
        severity="high",
        description="AWS Access Key ID detected",
    ),
    SecretPattern(
        name="AWS Secret Access Key",
        pattern=re.compile(r"""(?i)aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*["']?([A-Za-z0-9/+=]{40})["']?"""),
        severity="high",
        description="AWS Secret Access Key detected",
    ),
    # GitHub
    SecretPattern(
        name="GitHub Personal Access Token",
        pattern=re.compile(r"""ghp_[a-zA-Z0-9]{36}"""),
        severity="high",
        description="GitHub Personal Access Token detected",
    ),
    SecretPattern(
        name="GitHub OAuth Token",
        pattern=re.compile(r"""gho_[a-zA-Z0-9]{36}"""),
        severity="high",
        description="GitHub OAuth Token detected",
    ),
    SecretPattern(
        name="GitHub App Token",
        pattern=re.compile(r"""(ghu|ghs)_[a-zA-Z0-9]{36}"""),
        severity="high",
        description="GitHub App Token detected",
    ),
    SecretPattern(
        name="GitHub Fine-grained PAT",
        pattern=re.compile(r"""github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}"""),
        severity="high",
        description="GitHub Fine-grained Personal Access Token detected",
    ),
    # Private Keys
    SecretPattern(
        name="RSA Private Key",
        pattern=re.compile(r"""-----BEGIN RSA PRIVATE KEY-----"""),
        severity="high",
        description="RSA private key detected",
    ),
    SecretPattern(
        name="SSH Private Key",
        pattern=re.compile(r"""-----BEGIN OPENSSH PRIVATE KEY-----"""),
        severity="high",
        description="SSH private key detected",
    ),
    SecretPattern(
        name="PGP Private Key",
        pattern=re.compile(r"""-----BEGIN PGP PRIVATE KEY BLOCK-----"""),
        severity="high",
        description="PGP private key detected",
    ),
    SecretPattern(
        name="EC Private Key",
        pattern=re.compile(r"""-----BEGIN EC PRIVATE KEY-----"""),
        severity="high",
        description="EC private key detected",
    ),
    # Google/GCP
    SecretPattern(
        name="Google API Key",
        pattern=re.compile(r"""AIza[0-9A-Za-z\-_]{35}"""),
        severity="high",
        description="Google API key detected",
    ),
    SecretPattern(
        name="Google OAuth Client Secret",
        pattern=re.compile(r"""(?i)client[_-]?secret\s*[=:]\s*["']?([a-zA-Z0-9_\-]{24})["']?"""),
        severity="medium",
        description="Potential OAuth client secret",
    ),
    # Slack
    SecretPattern(
        name="Slack Token",
        pattern=re.compile(r"""xox[baprs]-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*"""),
        severity="high",
        description="Slack token detected",
    ),
    SecretPattern(
        name="Slack Webhook",
        pattern=re.compile(r"""https://hooks\.slack\.com/services/T[a-zA-Z0-9_]{8,}/B[a-zA-Z0-9_]{8,}/[a-zA-Z0-9_]{24}"""),
        severity="high",
        description="Slack webhook URL detected",
    ),
    # Stripe
    SecretPattern(
        name="Stripe API Key",
        pattern=re.compile(r"""(?:sk|pk)_(test|live)_[0-9a-zA-Z]{24,}"""),
        severity="high",
        description="Stripe API key detected",
    ),
    # Database URLs
    SecretPattern(
        name="Database URL with credentials",
        pattern=re.compile(r"""(?i)(postgres|mysql|mongodb|redis)://[^:]+:[^@]+@"""),
        severity="high",
        description="Database URL with credentials detected",
    ),
    # Bearer tokens
    SecretPattern(
        name="Bearer Token",
        pattern=re.compile(r"""(?i)bearer\s+[a-zA-Z0-9_\-\.=]{20,}"""),
        severity="medium",
        description="Bearer token detected",
    ),
    # JWT
    SecretPattern(
        name="JWT Token",
        pattern=re.compile(r"""eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*"""),
        severity="medium",
        description="JWT token detected (may be test data)",
    ),
    # PyPI
    SecretPattern(
        name="PyPI API Token",
        pattern=re.compile(r"""pypi-[a-zA-Z0-9_]{100,}"""),
        severity="high",
        description="PyPI API token detected",
    ),
    # npm
    SecretPattern(
        name="npm Token",
        pattern=re.compile(r"""(?i)npm[_-]?token\s*[=:]\s*["']?([a-zA-Z0-9_\-]{36})["']?"""),
        severity="high",
        description="npm token detected",
    ),
    # Heroku
    SecretPattern(
        name="Heroku API Key",
        pattern=re.compile(r"""(?i)heroku[_-]?api[_-]?key\s*[=:]\s*["']?([a-f0-9\-]{36})["']?"""),
        severity="high",
        description="Heroku API key detected",
    ),
    # Generic high-entropy detection (Base64-encoded secrets)
    SecretPattern(
        name="Base64 Encoded Secret",
        pattern=re.compile(r"""(?i)(secret|key|token|password|auth)\s*[=:]\s*["']?([A-Za-z0-9+/=]{40,})["']?"""),
        severity="medium",
        description="Potential base64-encoded secret",
    ),
]


@dataclass
class Finding:
    """A secret finding."""

    file: str
    line_number: int
    line_content: str
    pattern_name: str
    severity: str
    description: str
    matched_text: str


def calculate_entropy(s: str) -> float:
    """Calculate Shannon entropy of a string."""
    import math
    from collections import Counter

    if not s:
        return 0.0

    counter = Counter(s)
    length = len(s)
    entropy = 0.0

    for count in counter.values():
        if count > 0:
            freq = count / length
            entropy -= freq * math.log2(freq)

    return entropy


def should_skip_file(filepath: str) -> bool:
    """Check if file should be skipped based on patterns."""
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, filepath, re.IGNORECASE):
            return True
    return False


def is_allowlisted(text: str) -> bool:
    """Check if text contains an allowlisted value."""
    for allowed in ALLOWLIST:
        if allowed.lower() in text.lower():
            return True
    return False


def scan_line(line: str, line_number: int, filepath: str) -> list[Finding]:
    """Scan a single line for secrets."""
    findings: list[Finding] = []

    # Skip if line is a comment
    stripped = line.strip()
    if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("*"):
        # Still check for actual secrets in comments
        pass

    for secret_pattern in SECRET_PATTERNS:
        matches = secret_pattern.pattern.finditer(line)
        for match in matches:
            matched_text = match.group(0)

            # Skip if allowlisted
            if is_allowlisted(matched_text):
                continue

            # Skip if it's a placeholder pattern
            if any(placeholder in matched_text.lower() for placeholder in ["example", "placeholder", "your_", "your-", "<", ">", "xxx", "test"]):
                continue

            # For patterns that capture groups, check the captured value
            if match.lastindex and match.lastindex >= 1:
                captured = match.group(match.lastindex)
                if is_allowlisted(captured):
                    continue
                # Check entropy for captured secrets
                if len(captured) >= MIN_SECRET_LENGTH:
                    entropy = calculate_entropy(captured)
                    if entropy < MIN_ENTROPY_THRESHOLD:
                        continue

            findings.append(
                Finding(
                    file=filepath,
                    line_number=line_number,
                    line_content=line.strip()[:100],  # Truncate long lines
                    pattern_name=secret_pattern.name,
                    severity=secret_pattern.severity,
                    description=secret_pattern.description,
                    matched_text=matched_text[:50],  # Truncate matched text
                )
            )

    return findings


def scan_file(filepath: Path) -> list[Finding]:
    """Scan a file for secrets."""
    findings: list[Finding] = []

    if should_skip_file(str(filepath)):
        return findings

    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except (OSError, IOError) as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)
        return findings

    for line_number, line in enumerate(content.splitlines(), start=1):
        findings.extend(scan_line(line, line_number, str(filepath)))

    return findings


def get_staged_files() -> list[Path]:
    """Get list of staged files in git."""
    result = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"], capture_output=True, text=True)
    if result.returncode != 0:
        return []
    return [Path(f) for f in result.stdout.strip().split("\n") if f]


def get_commit_range_files(commit_range: str) -> list[Path]:
    """Get list of files changed in commit range."""
    result = subprocess.run(["git", "diff", "--name-only", commit_range], capture_output=True, text=True)
    if result.returncode != 0:
        return []
    return [Path(f) for f in result.stdout.strip().split("\n") if f]


def get_all_tracked_files() -> list[Path]:
    """Get all tracked files in the repository."""
    result = subprocess.run(["git", "ls-files"], capture_output=True, text=True)
    if result.returncode != 0:
        return []
    return [Path(f) for f in result.stdout.strip().split("\n") if f]


def format_github_annotation(finding: Finding) -> str:
    """Format finding as GitHub Actions annotation."""
    level = "error" if finding.severity == "high" else "warning"
    return f"::{level} file={finding.file},line={finding.line_number}::{finding.description}: {finding.pattern_name}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan for secrets in the codebase")
    parser.add_argument("--staged", action="store_true", help="Only scan staged files")
    parser.add_argument("--commits", type=str, help="Scan files changed in commit range (e.g., HEAD~5..HEAD)")
    parser.add_argument("--files", nargs="+", type=Path, help="Scan specific files")
    parser.add_argument("--github", action="store_true", help="Output GitHub Actions annotations")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    # Determine which files to scan
    if args.files:
        files = [f for f in args.files if f.exists()]
    elif args.staged:
        files = get_staged_files()
        if not files:
            print("No staged files to scan.")
            return 0
    elif args.commits:
        files = get_commit_range_files(args.commits)
        if not files:
            print(f"No files changed in {args.commits}.")
            return 0
    else:
        files = get_all_tracked_files()

    if args.verbose:
        print(f"Scanning {len(files)} files...")

    all_findings: list[Finding] = []

    for filepath in files:
        if not filepath.exists():
            continue
        findings = scan_file(filepath)
        all_findings.extend(findings)

    # Sort by severity (high first), then by file
    severity_order = {"high": 0, "medium": 1, "low": 2}
    all_findings.sort(key=lambda f: (severity_order.get(f.severity, 99), f.file, f.line_number))

    # Output results
    if all_findings:
        if args.github:
            for finding in all_findings:
                print(format_github_annotation(finding))
        else:
            print(f"\n{'=' * 60}")
            print(f"SECRETS SCAN RESULTS: {len(all_findings)} potential issue(s) found")
            print(f"{'=' * 60}\n")

            for finding in all_findings:
                severity_icon = {"high": "[HIGH]", "medium": "[MED]", "low": "[LOW]"}.get(finding.severity, "[?]")
                print(f"{severity_icon} {finding.file}:{finding.line_number}")
                print(f"       Pattern: {finding.pattern_name}")
                print(f"       {finding.description}")
                print(f"       Line: {finding.line_content}")
                print()

            print(f"{'=' * 60}")
            high_count = sum(1 for f in all_findings if f.severity == "high")
            med_count = sum(1 for f in all_findings if f.severity == "medium")
            print(f"Summary: {high_count} high, {med_count} medium severity issues")
            print(f"{'=' * 60}")

        # Return non-zero if high severity findings
        if any(f.severity == "high" for f in all_findings):
            return 1
    else:
        if args.verbose or not args.github:
            print("No secrets detected.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
