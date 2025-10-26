from __future__ import annotations

import argparse
import datetime as dt
import importlib
import logging
import math
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Optional

import json

import filetype
import puremagic
from PIL import Image, UnidentifiedImageError
from isbinary import is_binary_file
from smart_media_manager import __version__
from smart_media_manager.format_rules import FormatRule, match_rule

try:
    import magic
except ImportError:  # pragma: no cover - optional runtime dependency
    magic = None  # type: ignore

try:
    from pyfsig import interface as pyfsig_interface
except ImportError:  # pragma: no cover - optional runtime dependency
    pyfsig_interface = None  # type: ignore

LOG = logging.getLogger("smart_media_manager")
_FILE_LOG_HANDLER: Optional[logging.Handler] = None
LOG_SUBDIR = ".smm_logs"

SAFE_NAME_PATTERN = re.compile(r"[^A-Za-z0-9_.-]")
MAX_APPLESCRIPT_ARGS = 200
MAX_APPLESCRIPT_CHARS = 20000
MAX_SAFE_STEM_LENGTH = 120
APPLE_PHOTOS_IMPORT_TIMEOUT = 600  # seconds

BINWALK_EXECUTABLE = shutil.which("binwalk")

_MAGIC_MIME = None
_MAGIC_DESC = None

TOOL_PRIORITY = [
    "libmagic",
    "binwalk",
    "puremagic",
    "pyfsig",
]

TOOL_WEIGHTS = {
    "libmagic": 1.4,
    "binwalk": 1.2,
    "puremagic": 1.1,
    "pyfsig": 1.0,
}

RAW_DEPENDENCY_GROUPS = {
    "canon": {
        "extensions": {".crw", ".cr2", ".cr3", ".crm", ".crx"},
        "brew": ["libraw"],
        "pip": ["rawpy"],
        "cask": ["adobe-dng-converter"],
    },
    "nikon": {
        "extensions": {".nef", ".nrw"},
        "brew": ["libraw"],
        "pip": ["rawpy"],
        "cask": [],
    },
    "sony": {
        "extensions": {".arw", ".srf", ".sr2"},
        "brew": ["libraw"],
        "pip": ["rawpy"],
        "cask": [],
    },
    "fujifilm": {
        "extensions": {".raf"},
        "brew": ["libraw"],
        "pip": ["rawpy"],
        "cask": [],
    },
    "olympus": {
        "extensions": {".orf"},
        "brew": ["libraw"],
        "pip": ["rawpy"],
        "cask": [],
    },
    "panasonic": {
        "extensions": {".rw2", ".raw"},
        "brew": ["libraw"],
        "pip": ["rawpy"],
        "cask": [],
    },
    "pentax": {
        "extensions": {".pef", ".dng"},
        "brew": ["libraw"],
        "pip": ["rawpy"],
        "cask": [],
    },
    "leica": {
        "extensions": {".dng", ".rwl"},
        "brew": ["libraw"],
        "pip": ["rawpy"],
        "cask": ["adobe-dng-converter"],
    },
    "phaseone": {
        "extensions": {".iiq", ".cap"},
        "brew": ["libraw"],
        "pip": ["rawpy"],
        "cask": ["adobe-dng-converter"],
    },
    "hasselblad": {
        "extensions": {".3fr", ".fff"},
        "brew": ["libraw"],
        "pip": ["rawpy"],
        "cask": ["adobe-dng-converter"],
    },
    "sigma": {
        "extensions": {".x3f"},
        "brew": ["libraw", "libopenraw"],
        "pip": ["rawpy"],
        "cask": [],
    },
    "gopro": {
        "extensions": {".gpr"},
        "brew": ["libraw"],
        "pip": ["rawpy"],
        "cask": [],
    },
    "dji": {
        "extensions": {".dng"},
        "brew": ["libraw"],
        "pip": ["rawpy"],
        "cask": [],
    },
}

RAW_EXTENSION_TO_GROUPS: dict[str, set[str]] = {}
for group_name, config in RAW_DEPENDENCY_GROUPS.items():
    for ext in config["extensions"]:
        normalized = ext.lower()
        RAW_EXTENSION_TO_GROUPS.setdefault(normalized, set()).add(group_name)

_BREW_PATH_CACHE: Optional[str] = None
_PIP_PACKAGE_CACHE: set[str] = set()
_INSTALLED_RAW_GROUPS: set[str] = set()
_RAWPY_MODULE: Optional[Any] = None
_RAWPY_IMPORT_ERROR: Optional[Exception] = None

REQUIRED_BREW_PACKAGES = {
    "ffmpeg": "ffmpeg",
    "libjxl": "jpeg-xl",
    "libheif": "libheif",
    "imagemagick": "imagemagick",
    "webp": "webp",
    "exiftool": "exiftool",
}

IMAGE_EXTENSION_MAP = {
    "jpeg": ".jpg",
    "jpg": ".jpg",
    "png": ".png",
    "tiff": ".tiff",
    "tif": ".tiff",
    "gif": ".gif",
    "bmp": ".bmp",
    "webp": ".webp",
    "heic": ".heic",
    "heif": ".heic",
}

COMPATIBLE_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".tiff", ".gif"}
COMPATIBLE_VIDEO_CONTAINERS = {"mp4", "mov", "quicktime", "m4v"}
COMPATIBLE_VIDEO_CODECS = {"h264", "hevc", "avc1", "h265"}
COMPATIBLE_AUDIO_CODECS = {
    "aac",
    "mp3",
    "alac",
    "pcm_s16le",
    "pcm_s24le",
    "pcm_s16be",
    "pcm_f32le",
    "ac3",
    "eac3",
}

ARCHIVE_EXTENSIONS = {
    "zip",
    "rar",
    "7z",
    "tar",
    "gz",
    "bz2",
    "xz",
    "lz",
    "lzma",
    "cab",
    "iso",
    "dmg",
    "tgz",
    "tbz2",
    "txz",
    "apk",
    "jar",
    "war",
    "ear",
}

ARCHIVE_MIME_TYPES = {
    "application/zip",
    "application/x-zip-compressed",
    "application/x-7z-compressed",
    "application/x-tar",
    "application/x-rar",
    "application/vnd.rar",
    "application/gzip",
    "application/x-gzip",
    "application/x-bzip2",
    "application/x-xz",
    "application/x-lzip",
    "application/x-lzma",
    "application/x-iso9660-image",
    "application/vnd.android.package-archive",
    "application/java-archive",
}

TEXTUAL_MIME_HINTS = {
    "application/x-typescript",
    "application/javascript",
    "application/x-javascript",
    "application/json",
    "application/xml",
    "text/javascript",
    "text/typescript",
    "text/x-python",
    "text/x-shellscript",
    "text/x-c",
    "text/x-c++",
    "text/x-go",
    "text/x-ruby",
    "text/x-php",
    "text/markdown",
    "text/plain",
}

TEXT_ONLY_HINT_EXTENSIONS = {
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".py",
    ".pyw",
    ".java",
    ".cs",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hpp",
    ".go",
    ".rs",
    ".rb",
    ".php",
    ".sh",
    ".bash",
    ".zsh",
    ".ps1",
    ".bat",
    ".sql",
    ".swift",
    ".kt",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
    ".md",
    ".rst",
    ".txt",
    ".log",
}

VIDEO_EXTENSION_MAP = {
    "mp4": ".mp4",
    "m4v": ".m4v",
    "mov": ".mov",
    "qt": ".mov",
    "avi": ".avi",
    "mkv": ".mkv",
    "webm": ".webm",
    "flv": ".flv",
    "wmv": ".wmv",
    "mpg": ".mpg",
    "mpeg": ".mpg",
    "3gp": ".3gp",
    "3g2": ".3g2",
    "ts": ".ts",
    "m2ts": ".ts",
    "mts": ".ts",
}

VIDEO_EXTENSION_HINTS = set(VIDEO_EXTENSION_MAP.keys())

VIDEO_MIME_EXTENSION_MAP = {
    "video/mp4": ".mp4",
    "video/x-m4v": ".m4v",
    "video/quicktime": ".mov",
    "video/x-quicktime": ".mov",
    "video/x-msvideo": ".avi",
    "video/x-matroska": ".mkv",
    "video/webm": ".webm",
    "video/x-flv": ".flv",
    "video/x-ms-wmv": ".wmv",
    "video/mpeg": ".mpg",
    "video/MP2T": ".ts",
    "video/3gpp": ".3gp",
    "video/3gpp2": ".3g2",
}

IMAGE_MIME_EXTENSION_MAP = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/tiff": ".tiff",
    "image/gif": ".gif",
    "image/bmp": ".bmp",
    "image/webp": ".webp",
    "image/heif": ".heic",
    "image/heic": ".heic",
}

ALL_IMAGE_EXTENSIONS = set(IMAGE_EXTENSION_MAP.keys())
HACHOIR_IMAGE_EXTENSIONS = set()


@dataclass
class MediaFile:
    source: Path
    kind: str
    extension: str
    format_name: str
    stage_path: Optional[Path] = None
    compatible: bool = False
    video_codec: Optional[str] = None
    audio_codec: Optional[str] = None
    original_suffix: str = ""
    backup_path: Optional[Path] = None
    rule_id: str = ""
    action: str = "import"
    requires_processing: bool = False
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SkipLogger:
    path: Path
    entries: int = 0

    def log(self, file_path: Path, reason: str) -> None:
        LOG.warning("Skipping %s (%s)", file_path, reason)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(f"{file_path}\t{reason}\n")
        self.entries += 1

    def has_entries(self) -> bool:
        return self.entries > 0


@dataclass
class RunStatistics:
    """Tracks comprehensive statistics for a Smart Media Manager run."""

    total_files_scanned: int = 0
    total_binary_files: int = 0
    total_text_files: int = 0
    total_media_detected: int = 0
    media_compatible: int = 0
    media_incompatible: int = 0
    incompatible_with_conversion_rule: int = 0
    conversion_attempted: int = 0
    conversion_succeeded: int = 0
    conversion_failed: int = 0
    imported_after_conversion: int = 0
    imported_without_conversion: int = 0
    total_imported: int = 0
    refused_by_apple_photos: int = 0
    refused_filenames: list[tuple[Path, str]] = field(default_factory=list)
    skipped_errors: int = 0
    skipped_unknown_format: int = 0
    skipped_corrupt_or_empty: int = 0
    skipped_other: int = 0

    def print_summary(self) -> None:
        """Print a colored, formatted summary of the run statistics."""
        # ANSI color codes
        BOLD = "\033[1m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        RED = "\033[91m"
        BLUE = "\033[94m"
        CYAN = "\033[96m"
        RESET = "\033[0m"

        print(f"\n{BOLD}{'=' * 80}{RESET}")
        print(f"{BOLD}{CYAN}Smart Media Manager - Run Summary{RESET}")
        print(f"{BOLD}{'=' * 80}{RESET}\n")

        # Scanning section
        print(f"{BOLD}{BLUE}Scanning:{RESET}")
        print(f"  Total files scanned:        {self.total_files_scanned:>6}")
        print(f"  Binary files:               {self.total_binary_files:>6}")
        print(f"  Text files:                 {self.total_text_files:>6}\n")

        # Detection section
        print(f"{BOLD}{BLUE}Media Detection:{RESET}")
        print(f"  Media files detected:       {self.total_media_detected:>6}")
        print(f"  Compatible (no conversion): {GREEN}{self.media_compatible:>6}{RESET}")
        print(f"  Incompatible:               {YELLOW}{self.media_incompatible:>6}{RESET}")
        print(f"    └─ With conversion rule:  {self.incompatible_with_conversion_rule:>6}\n")

        # Conversion section
        if self.conversion_attempted > 0:
            print(f"{BOLD}{BLUE}Conversion:{RESET}")
            print(f"  Attempted:                  {self.conversion_attempted:>6}")
            print(f"  Succeeded:                  {GREEN}{self.conversion_succeeded:>6}{RESET}")
            print(f"  Failed:                     {RED}{self.conversion_failed:>6}{RESET}\n")

        # Import section
        print(f"{BOLD}{BLUE}Apple Photos Import:{RESET}")
        print(f"  Imported (after conversion):{GREEN}{self.imported_after_conversion:>6}{RESET}")
        print(f"  Imported (direct):          {GREEN}{self.imported_without_conversion:>6}{RESET}")
        print(f"  Total imported:             {BOLD}{GREEN}{self.total_imported:>6}{RESET}")
        print(f"  Refused by Apple Photos:    {RED}{self.refused_by_apple_photos:>6}{RESET}")

        if self.total_imported + self.refused_by_apple_photos > 0:
            success_rate = (self.total_imported / (self.total_imported + self.refused_by_apple_photos)) * 100
            color = GREEN if success_rate >= 95 else YELLOW if success_rate >= 80 else RED
            print(f"  Success rate:               {color}{success_rate:>5.1f}%{RESET}\n")
        else:
            print()

        # Skipped section
        total_skipped = self.skipped_errors + self.skipped_unknown_format + self.skipped_corrupt_or_empty + self.skipped_other
        if total_skipped > 0:
            print(f"{BOLD}{BLUE}Skipped Files:{RESET}")
            print(f"  Due to errors:              {self.skipped_errors:>6}")
            print(f"  Unknown format:             {self.skipped_unknown_format:>6}")
            print(f"  Corrupt or empty:           {self.skipped_corrupt_or_empty:>6}")
            print(f"  Other reasons:              {self.skipped_other:>6}")
            print(f"  Total skipped:              {YELLOW}{total_skipped:>6}{RESET}\n")

        # Failed imports detail
        if self.refused_filenames:
            print(f"{BOLD}{RED}Files Refused by Apple Photos:{RESET}")
            for path, reason in self.refused_filenames[:10]:  # Show first 10
                print(f"  • {path.name}")
                print(f"    Reason: {reason}")
            if len(self.refused_filenames) > 10:
                print(f"  ... and {len(self.refused_filenames) - 10} more (see log for full list)\n")
            else:
                print()

        print(f"{BOLD}{'=' * 80}{RESET}\n")

    def log_summary(self) -> None:
        """Log the summary to the file logger."""
        LOG.info("=" * 80)
        LOG.info("Run Summary Statistics")
        LOG.info("=" * 80)
        LOG.info("Scanning: total=%d, binary=%d, text=%d", self.total_files_scanned, self.total_binary_files, self.total_text_files)
        LOG.info("Media Detection: detected=%d, compatible=%d, incompatible=%d (with_rule=%d)", self.total_media_detected, self.media_compatible, self.media_incompatible, self.incompatible_with_conversion_rule)
        LOG.info("Conversion: attempted=%d, succeeded=%d, failed=%d", self.conversion_attempted, self.conversion_succeeded, self.conversion_failed)
        LOG.info("Import: converted=%d, direct=%d, total=%d, refused=%d", self.imported_after_conversion, self.imported_without_conversion, self.total_imported, self.refused_by_apple_photos)
        if self.total_imported + self.refused_by_apple_photos > 0:
            success_rate = (self.total_imported / (self.total_imported + self.refused_by_apple_photos)) * 100
            LOG.info("Success rate: %.1f%%", success_rate)
        LOG.info("Skipped: errors=%d, unknown=%d, corrupt=%d, other=%d", self.skipped_errors, self.skipped_unknown_format, self.skipped_corrupt_or_empty, self.skipped_other)
        if self.refused_filenames:
            LOG.info("Refused files:")
            for path, reason in self.refused_filenames:
                LOG.info("  %s: %s", path, reason)
        LOG.info("=" * 80)


@dataclass
class FormatVote:
    tool: str
    mime: Optional[str] = None
    extension: Optional[str] = None
    description: Optional[str] = None
    kind: Optional[str] = None
    error: Optional[str] = None


def find_executable(*candidates: str) -> Optional[str]:
    for candidate in candidates:
        path = shutil.which(candidate)
        if path:
            return path
    return None


def resolve_imagemagick_command() -> str:
    cmd = find_executable("magick", "convert")
    if not cmd:
        raise RuntimeError("ImageMagick (magick/convert) not found. Please install imagemagick.")
    return cmd


def ensure_ffmpeg_path() -> str:
    cmd = find_executable("ffmpeg")
    if not cmd:
        raise RuntimeError("ffmpeg not found. Please install ffmpeg.")
    return cmd


def is_animated_gif(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            data = handle.read()
    except OSError:
        return False
    return data.count(b"\x2c") > 1 and b"NETSCAPE2.0" in data


def is_animated_png(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            data = handle.read()
    except OSError:
        return False
    return b"acTL" in data


def is_animated_webp(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            data = handle.read(65536)
    except OSError:
        return False
    return b"ANIM" in data


def get_psd_color_mode(path: Path) -> Optional[str]:
    try:
        with path.open("rb") as handle:
            header = handle.read(26)
    except OSError:
        return None
    if len(header) < 26 or header[:4] != b"8BPS":
        return None
    color_mode = int.from_bytes(header[24:26], "big")
    mapping = {
        0: "bitmap",
        1: "grayscale",
        2: "indexed",
        3: "rgb",
        4: "cmyk",
        7: "lab",
        8: "multichannel",
        9: "duotone",
    }
    return mapping.get(color_mode)


@dataclass
class Signature:
    extension: Optional[str] = None
    mime: Optional[str] = None

    def is_empty(self) -> bool:
        return not self.extension and not self.mime


def normalize_extension(ext: Optional[str]) -> Optional[str]:
    if not ext:
        return None
    normalized = ext.strip().lower()
    if not normalized:
        return None
    if normalized.startswith("."):
        normalized = normalized[1:]
    return normalized


def looks_like_text_file(path: Path, max_bytes: int = 4096) -> bool:
    try:
        with path.open("rb") as handle:
            sample = handle.read(max_bytes)
    except OSError:
        return False
    if not sample:
        return True
    if b"\x00" in sample:
        return False
    printable = sum(1 for byte in sample if 32 <= byte <= 126 or byte in (9, 10, 13))
    return printable / len(sample) > 0.9


def timestamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d%H%M%S")


def tool_rank(tool: str) -> int:
    try:
        return TOOL_PRIORITY.index(tool)
    except ValueError:
        return len(TOOL_PRIORITY)


def vote_weight(vote: FormatVote) -> float:
    return TOOL_WEIGHTS.get(vote.tool, 1.0)


def collect_raw_groups_from_extensions(exts: Iterable[Optional[str]]) -> set[str]:
    groups: set[str] = set()
    for ext in exts:
        normalized = ensure_dot_extension(ext)
        if not normalized:
            continue
        groups.update(RAW_EXTENSION_TO_GROUPS.get(normalized.lower(), set()))
    return groups


def is_raw_extension(ext: Optional[str]) -> bool:
    normalized = ensure_dot_extension(ext)
    return bool(normalized and normalized.lower() in RAW_EXTENSION_TO_GROUPS)


def install_raw_dependency_groups(groups: Iterable[str]) -> None:
    needed = set(groups) - _INSTALLED_RAW_GROUPS
    if not needed:
        return
    brew_path = ensure_homebrew()
    for group in sorted(needed):
        config = RAW_DEPENDENCY_GROUPS.get(group)
        if not config:
            continue
        for package in config.get("brew", []):
            ensure_brew_package(brew_path, package)
        for cask in config.get("cask", []):
            ensure_brew_cask(brew_path, cask)
        for package in config.get("pip", []):
            ensure_pip_package(package)
    _INSTALLED_RAW_GROUPS.update(needed)


def get_rawpy() -> Optional[Any]:
    global _RAWPY_MODULE, _RAWPY_IMPORT_ERROR
    if _RAWPY_MODULE is not None:
        return _RAWPY_MODULE
    try:
        module = importlib.import_module("rawpy")
    except ImportError as exc:  # pragma: no cover - optional dependency
        _RAWPY_IMPORT_ERROR = exc
        return None
    _RAWPY_MODULE = module
    _RAWPY_IMPORT_ERROR = None
    return module


def refine_raw_media(path: Path, extension_candidates: Iterable[Optional[str]]) -> tuple[Optional[MediaFile], Optional[str]]:
    rawpy_module = get_rawpy()
    if rawpy_module is None:
        return None, "rawpy unavailable"
    try:
        with rawpy_module.imread(str(path)) as raw:
            make = (raw.metadata.camera_make or "").strip()
            model = (raw.metadata.camera_model or "").strip()
            format_name = " ".join(part for part in [make, model] if part) or "raw"
    except rawpy_module.LibRawFileUnsupportedError:  # type: ignore[attr-defined]
        return None, "rawpy unsupported raw"
    except Exception as exc:  # pragma: no cover - safeguard
        return None, f"rawpy failed: {exc}"

    chosen_extension: Optional[str] = None
    for candidate in extension_candidates:
        normalized = ensure_dot_extension(candidate)
        if normalized and normalized.lower() in RAW_EXTENSION_TO_GROUPS:
            chosen_extension = normalized
            break
    if not chosen_extension:
        chosen_extension = ensure_dot_extension(path.suffix) or ".raw"

    media = MediaFile(
        source=path,
        kind="raw",
        extension=chosen_extension,
        format_name=format_name,
        compatible=True,
        original_suffix=path.suffix,
    )
    return media, None


def refine_image_media(media: MediaFile) -> tuple[Optional[MediaFile], Optional[str]]:
    try:
        with Image.open(media.source) as img:
            img.verify()
            media.metadata["image_size"] = img.size
            media.metadata["image_mode"] = img.mode
    except FileNotFoundError:
        return None, "image missing"
    except UnidentifiedImageError as exc:
        return None, f"corrupt image: {exc}"
    except Exception as exc:  # noqa: BLE001
        return None, f"image validation failed: {exc}"
    return media, None


def refine_video_media(media: MediaFile) -> tuple[Optional[MediaFile], Optional[str]]:
    ffprobe_path = shutil.which("ffprobe")
    if not ffprobe_path:
        return media, None
    cmd = [
        ffprobe_path,
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=codec_name,width,height,duration",
        "-of",
        "default=noprint_wrappers=1",
        str(media.source),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None, "video validation failed"
    media.metadata["ffprobe_info"] = result.stdout.strip()
    return media, None


def run_command_with_progress(command: list[str], message: str, env: Optional[dict] = None) -> None:
    bar_length = 28
    start = time.time()
    with subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env or os.environ.copy(),
    ) as proc:
        while True:
            ret = proc.poll()
            elapsed = time.time() - start
            progress = (elapsed % bar_length) / (bar_length - 1)
            filled = int(progress * bar_length)
            bar = "#" * filled + "-" * (bar_length - filled)
            sys.stdout.write(f"\r{message} [{bar}]")
            sys.stdout.flush()
            if ret is not None:
                break
            time.sleep(0.2)
    sys.stdout.write("\r" + " " * (len(message) + bar_length + 3) + "\r")
    sys.stdout.flush()
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(command)}")


def ensure_homebrew() -> str:
    global _BREW_PATH_CACHE
    if _BREW_PATH_CACHE and Path(_BREW_PATH_CACHE).exists():
        return _BREW_PATH_CACHE
    brew_path = shutil.which("brew")
    if brew_path:
        _BREW_PATH_CACHE = brew_path
        return brew_path
    install_cmd = [
        "/bin/bash",
        "-lc",
        'NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
    ]
    run_command_with_progress(install_cmd, "Installing Homebrew")
    possible_paths = ["/opt/homebrew/bin/brew", "/usr/local/bin/brew"]
    for candidate in possible_paths:
        if Path(candidate).exists():
            os.environ["PATH"] = f"{Path(candidate).parent}:{os.environ.get('PATH', '')}"
            _BREW_PATH_CACHE = str(Path(candidate))
            return _BREW_PATH_CACHE
    brew_path = shutil.which("brew")
    if not brew_path:
        raise RuntimeError("Homebrew installation succeeded but brew binary not found in PATH.")
    _BREW_PATH_CACHE = brew_path
    return brew_path


def brew_package_installed(brew_path: str, package: str) -> bool:
    check_cmd = [brew_path, "list", package]
    result = subprocess.run(check_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0


def ensure_brew_package(brew_path: str, package: str) -> None:
    if not brew_package_installed(brew_path, package):
        try:
            run_command_with_progress([brew_path, "install", "--quiet", package], f"Installing {package}")
        except RuntimeError as exc:  # pragma: no cover - depends on user env
            raise RuntimeError(f"Failed to install {package} via Homebrew. Install it manually (brew install {package}) or rerun with --skip-bootstrap.") from exc
    else:
        try:
            run_command_with_progress([brew_path, "upgrade", "--quiet", package], f"Updating {package}")
        except RuntimeError as exc:  # pragma: no cover - depends on user env
            raise RuntimeError(f"Failed to update {package} via Homebrew. Try 'brew upgrade {package}' manually or rerun with --skip-bootstrap.") from exc


def brew_cask_installed(brew_path: str, cask: str) -> bool:
    check_cmd = [brew_path, "list", "--cask", cask]
    result = subprocess.run(check_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0


def ensure_brew_cask(brew_path: str, cask: str) -> None:
    if not brew_cask_installed(brew_path, cask):
        try:
            run_command_with_progress([brew_path, "install", "--cask", "--quiet", cask], f"Installing {cask}")
        except RuntimeError as exc:  # pragma: no cover
            raise RuntimeError(f"Failed to install {cask} via Homebrew. Install it manually (brew install --cask {cask}) or rerun with --skip-bootstrap.") from exc
    else:
        try:
            run_command_with_progress([brew_path, "upgrade", "--cask", "--quiet", cask], f"Updating {cask}")
        except RuntimeError as exc:  # pragma: no cover
            raise RuntimeError(f"Failed to update {cask} via Homebrew. Try 'brew upgrade --cask {cask}' manually or rerun with --skip-bootstrap.") from exc


def pip_package_installed(package: str) -> bool:
    if package in _PIP_PACKAGE_CACHE:
        return True
    check_cmd = [sys.executable, "-m", "pip", "show", package]
    result = subprocess.run(check_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode == 0:
        _PIP_PACKAGE_CACHE.add(package)
        return True
    return False


def ensure_pip_package(package: str) -> None:
    if not pip_package_installed(package):
        run_command_with_progress([sys.executable, "-m", "pip", "install", "--upgrade", package], f"Installing {package}")
        _PIP_PACKAGE_CACHE.add(package)
    else:
        run_command_with_progress([sys.executable, "-m", "pip", "install", "--upgrade", package], f"Updating {package}")
    if package == "rawpy":
        global _RAWPY_MODULE, _RAWPY_IMPORT_ERROR
        _RAWPY_MODULE = None
        _RAWPY_IMPORT_ERROR = None


def ensure_system_dependencies() -> None:
    brew_path = ensure_homebrew()
    for package in REQUIRED_BREW_PACKAGES.values():
        ensure_brew_package(brew_path, package)


def copy_metadata_from_source(source: Path, target: Path) -> None:
    exiftool = find_executable("exiftool")
    if not exiftool or not source.exists() or not target.exists():
        return
    cmd = [
        exiftool,
        "-overwrite_original",
        "-TagsFromFile",
        str(source),
        str(target),
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        LOG.debug("Exiftool metadata copy failed for %s -> %s", source, target)


def ensure_raw_dependencies_for_files(media_files: Iterable[MediaFile]) -> None:
    required_groups: set[str] = set()
    for media in media_files:
        required_groups.update(collect_raw_groups_from_extensions([media.extension, media.original_suffix]))
    if not required_groups:
        return
    install_raw_dependency_groups(required_groups)


def normalize_mime_value(mime: Optional[str]) -> Optional[str]:
    if not mime:
        return None
    normalized = mime.strip().lower()
    return normalized or None


def is_textual_mime(mime: Optional[str]) -> bool:
    mime_val = normalize_mime_value(mime)
    if not mime_val:
        return False
    if mime_val.startswith("text/"):
        return True
    return mime_val in TEXTUAL_MIME_HINTS


def ensure_dot_extension(ext: Optional[str]) -> Optional[str]:
    if not ext:
        return None
    normalized = ext.strip().lower()
    if not normalized:
        return None
    if not normalized.startswith("."):
        normalized = f".{normalized}"
    return normalized


def kind_from_mime(mime: Optional[str]) -> Optional[str]:
    mime_val = normalize_mime_value(mime)
    if not mime_val:
        return None
    if mime_val.startswith("image/"):
        return "image"
    if mime_val.startswith("video/"):
        return "video"
    if mime_val.startswith("audio/"):
        return "audio"
    return None


def kind_from_extension(ext: Optional[str]) -> Optional[str]:
    norm = normalize_extension(ext)
    if not norm:
        return None
    ext_with_dot = ensure_dot_extension(norm)
    if ext_with_dot and ext_with_dot.lower() in RAW_EXTENSION_TO_GROUPS:
        return "raw"
    if ext_with_dot in COMPATIBLE_IMAGE_EXTENSIONS or norm in ALL_IMAGE_EXTENSIONS:
        return "image"
    if ext_with_dot in VIDEO_EXTENSION_MAP.values():
        return "video"
    return None


def kind_from_description(description: Optional[str]) -> Optional[str]:
    if not description:
        return None
    lowered = description.lower()
    if "disk image" not in lowered and any(word in lowered for word in ("image", "jpeg", "jpg", "png", "photo", "bitmap")):
        return "image"
    if any(word in lowered for word in ("video", "movie", "mpeg", "quicktime", "mp4", "h264", "h.264")):
        return "video"
    if any(word in lowered for word in ("audio", "sound", "mp3", "aac", "alac")):
        return "audio"
    if any(word in lowered for word in ("raw", "cr2", "cr3", "nef", "arw", "raf", "orf", "rw2", "dng", "iiq", "3fr", "x3f")):
        return "raw"
    return None


def extension_from_mime(mime: Optional[str]) -> Optional[str]:
    mime_val = normalize_mime_value(mime)
    if not mime_val:
        return None
    ext = IMAGE_MIME_EXTENSION_MAP.get(mime_val)
    if not ext:
        ext = VIDEO_MIME_EXTENSION_MAP.get(mime_val)
    if not ext:
        ext = mimetypes.guess_extension(mime_val)
    return ensure_dot_extension(ext)


def extension_from_description(description: Optional[str]) -> Optional[str]:
    if not description:
        return None
    lowered = description.lower()
    mapping = {
        ".jpg": ("jpeg", "jpg"),
        ".png": ("png",),
        ".gif": ("gif",),
        ".bmp": ("bitmap", "bmp"),
        ".tiff": ("tiff", "tif"),
        ".heic": ("heic", "heif"),
        ".mp4": ("mp4", "mpeg-4", "h.264", "h264"),
        ".mov": ("quicktime", "mov"),
        ".m4v": ("m4v",),
        ".webm": ("webm",),
        ".avi": ("avi",),
        ".mkv": ("matroska", "mkv"),
    }
    for ext, keywords in mapping.items():
        if any(keyword in lowered for keyword in keywords):
            return ext
    return None


def is_supported_video_codec(codec: Optional[str]) -> bool:
    if not codec:
        return False
    codec_lower = codec.lower()
    return codec_lower in COMPATIBLE_VIDEO_CODECS


def choose_vote_by_priority(
    votes: Iterable[FormatVote],
    predicate: Callable[[FormatVote], bool],
) -> Optional[FormatVote]:
    for tool in TOOL_PRIORITY:
        for vote in votes:
            if vote.tool == tool and predicate(vote):
                return vote
    return None


def select_consensus_vote(votes: list[FormatVote]) -> Optional[FormatVote]:
    valid_votes = [vote for vote in votes if not vote.error and (vote.mime or vote.extension or vote.description)]
    if not valid_votes:
        return None

    mime_weights: dict[str, float] = {}
    for vote in valid_votes:
        mime_val = normalize_mime_value(vote.mime)
        if mime_val:
            mime_weights[mime_val] = mime_weights.get(mime_val, 0.0) + vote_weight(vote)
    if mime_weights:
        top_weight = max(mime_weights.values())
        top_mimes = {mime for mime, weight in mime_weights.items() if math.isclose(weight, top_weight, rel_tol=1e-9, abs_tol=1e-9)}
        choice = choose_vote_by_priority(valid_votes, lambda v: normalize_mime_value(v.mime) in top_mimes)
        if choice:
            return choice

    ext_weights: dict[str, float] = {}
    for vote in valid_votes:
        ext_val = ensure_dot_extension(vote.extension)
        if ext_val:
            ext_weights[ext_val] = ext_weights.get(ext_val, 0.0) + vote_weight(vote)
    if ext_weights:
        top_weight = max(ext_weights.values())
        top_exts = {ext for ext, weight in ext_weights.items() if math.isclose(weight, top_weight, rel_tol=1e-9, abs_tol=1e-9)}
        choice = choose_vote_by_priority(valid_votes, lambda v: ensure_dot_extension(v.extension) in top_exts)
        if choice:
            return choice

    return max(
        valid_votes,
        key=lambda v: (vote_weight(v), -tool_rank(v.tool)),
        default=None,
    )


def determine_media_kind(votes: list[FormatVote], consensus: Optional[FormatVote]) -> Optional[str]:
    kind_weights: dict[str, float] = {}
    candidate_votes: list[FormatVote] = []
    for vote in votes:
        if vote.error:
            continue
        inferred = vote.kind or kind_from_mime(vote.mime) or kind_from_extension(vote.extension) or kind_from_description(vote.description)
        if inferred:
            weight = vote_weight(vote)
            kind_weights[inferred] = kind_weights.get(inferred, 0.0) + weight
            candidate_votes.append(vote)

    if kind_weights:
        top_weight = max(kind_weights.values())
        top_kinds = {kind for kind, weight in kind_weights.items() if math.isclose(weight, top_weight, rel_tol=1e-9, abs_tol=1e-9)}
        if consensus:
            consensus_kind = consensus.kind or kind_from_mime(consensus.mime) or kind_from_extension(consensus.extension) or kind_from_description(consensus.description)
            if consensus_kind and consensus_kind in top_kinds:
                return consensus_kind
        choice = choose_vote_by_priority(
            candidate_votes,
            lambda v: (v.kind or kind_from_mime(v.mime) or kind_from_extension(v.extension) or kind_from_description(v.description)) in top_kinds,
        )
        if choice:
            return choice.kind or kind_from_mime(choice.mime) or kind_from_extension(choice.extension) or kind_from_description(choice.description)

    if consensus:
        return consensus.kind or kind_from_mime(consensus.mime) or kind_from_extension(consensus.extension) or kind_from_description(consensus.description)
    return None


def votes_error_summary(votes: list[FormatVote]) -> str:
    error_messages = [f"{vote.tool}: {vote.error}" for vote in votes if vote.error]
    if error_messages:
        return "; ".join(error_messages)
    return "detectors could not agree on a media format"


def collect_format_votes(path: Path, puremagic_signature: Optional[Signature] = None) -> list[FormatVote]:
    return [
        classify_with_libmagic(path),
        classify_with_puremagic(path, puremagic_signature),
        classify_with_pyfsig(path),
        classify_with_binwalk(path),
    ]


def classify_with_libmagic(path: Path) -> FormatVote:
    if magic is None:
        return FormatVote(tool="libmagic", error="python-magic unavailable")
    global _MAGIC_MIME, _MAGIC_DESC
    try:
        if _MAGIC_MIME is None:
            _MAGIC_MIME = magic.Magic(mime=True)
        if _MAGIC_DESC is None:
            _MAGIC_DESC = magic.Magic()
        raw_mime = _MAGIC_MIME.from_file(str(path)) if _MAGIC_MIME else None
        mime = normalize_mime_value(raw_mime)
        description = _MAGIC_DESC.from_file(str(path)) if _MAGIC_DESC else None
        extension = extension_from_mime(mime) or extension_from_description(description)
        kind = kind_from_mime(mime) or kind_from_description(description)
        if not mime and not description:
            return FormatVote(tool="libmagic", error="no match")
        return FormatVote(
            tool="libmagic",
            mime=mime,
            description=description,
            extension=extension,
            kind=kind,
        )
    except Exception as exc:  # pragma: no cover - runtime safety
        return FormatVote(tool="libmagic", error=str(exc))


def classify_with_puremagic(path: Path, signature: Optional[Signature] = None) -> FormatVote:
    if signature is None:
        signature = safe_puremagic_guess(path)
    if signature.is_empty():
        return FormatVote(tool="puremagic", error="no match")
    extension = None
    if signature.extension:
        image_ext = canonical_image_extension(signature.extension)
        video_ext = canonical_video_extension(signature.extension)
        extension = image_ext or video_ext or ensure_dot_extension(signature.extension)
    mime = normalize_mime_value(signature.mime)
    kind = kind_from_mime(mime) or kind_from_extension(extension)
    description = None
    if signature.mime:
        description = signature.mime
    return FormatVote(
        tool="puremagic",
        mime=mime,
        extension=extension,
        description=description,
        kind=kind,
    )


def classify_with_pyfsig(path: Path) -> FormatVote:
    if pyfsig_interface is None:
        return FormatVote(tool="pyfsig", error="pyfsig unavailable")
    try:
        matches = pyfsig_interface.find_matches_for_file_path(str(path))
    except Exception as exc:  # pragma: no cover - runtime safety
        return FormatVote(tool="pyfsig", error=str(exc))
    if not matches:
        return FormatVote(tool="pyfsig", error="no signature match")
    match = matches[0]
    extension = ensure_dot_extension(match.file_extension)
    description = match.description
    kind = kind_from_extension(extension) or kind_from_description(description)
    return FormatVote(
        tool="pyfsig",
        extension=extension,
        description=description,
        kind=kind,
    )


def classify_with_binwalk(path: Path) -> FormatVote:
    if not BINWALK_EXECUTABLE:
        return FormatVote(tool="binwalk", error="binwalk executable not found")
    try:
        result = subprocess.run(
            [BINWALK_EXECUTABLE, "--signature", "--length", "0", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:  # pragma: no cover - runtime safety
        return FormatVote(tool="binwalk", error=str(exc))
    if result.returncode not in (0, 1):  # binwalk returns 1 when no signatures match
        return FormatVote(tool="binwalk", error=result.stderr.strip() or f"exit code {result.returncode}")
    description = None
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if not stripped or stripped.upper().startswith("DECIMAL") or stripped.startswith("--"):
            continue
        parts = stripped.split(None, 2)
        if len(parts) == 3:
            description = parts[2]
            break
    if not description:
        return FormatVote(tool="binwalk", error="no signature match")
    extension = extension_from_description(description)
    kind = kind_from_description(description) or kind_from_extension(extension)
    return FormatVote(
        tool="binwalk",
        description=description,
        extension=extension,
        kind=kind,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan and import media into Apple Photos, fixing extensions and compatibility.")
    parser.add_argument(
        "path",
        nargs="?",
        default=Path.cwd(),
        type=Path,
        help="Folder to scan (defaults to current working directory).",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete the temporary FOUND_MEDIA_FILES_<timestamp> folder after a successful import.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively scan the folder for media files.",
    )
    parser.add_argument(
        "--follow-symlinks",
        action="store_true",
        help="Follow symbolic links when scanning.",
    )
    parser.add_argument(
        "--skip-bootstrap",
        action="store_true",
        help="Skip automatic dependency installation (requires prerequisites already installed).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the smart-media-manager version and exit.",
    )
    return parser.parse_args()


def ensure_dependency(name: str) -> None:
    if shutil.which(name) is None:
        raise RuntimeError(f"Required dependency '{name}' is not available on PATH.")


def ffprobe(path: Path) -> Optional[dict]:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_streams",
        "-show_format",
        str(path),
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def is_video_corrupt_or_truncated(path: Path) -> tuple[bool, Optional[str]]:
    """
    Check if a video file is corrupt or truncated.
    Returns (is_corrupt, reason).
    """
    # Quick check: can ffprobe read the file?
    probe = ffprobe(path)
    if probe is None:
        return True, "ffprobe cannot read file"

    # Check for streams
    streams = probe.get("streams", [])
    if not streams:
        return True, "no streams found"

    # Check for video stream
    has_video = any(s.get("codec_type") == "video" for s in streams)
    if not has_video:
        return True, "no video stream found"

    # Check format info
    format_info = probe.get("format", {})
    if not format_info:
        return True, "no format information"

    # Check duration (truncated files often have no duration or very short duration)
    try:
        duration = float(format_info.get("duration", 0))
        if duration <= 0:
            return True, "invalid or missing duration"
    except (ValueError, TypeError):
        return True, "cannot parse duration"

    # Try to verify the file can be decoded (read first frame)
    cmd = ["ffmpeg", "-v", "error", "-i", str(path), "-vframes", "1", "-f", "null", "-"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    if result.returncode != 0 and result.stderr:
        # Check for common corruption indicators
        stderr_lower = result.stderr.lower()
        if any(indicator in stderr_lower for indicator in ["invalid", "corrupt", "truncat", "error", "moov atom not found"]):
            return True, f"video corruption detected: {result.stderr[:100]}"

    return False, None


def extract_container(format_name: str) -> str:
    return format_name.split(",")[0].strip().lower()


def is_skippable_file(path: Path) -> Optional[str]:
    try:
        if path.stat().st_size == 0:
            return "file is empty"
    except OSError as exc:
        return f"stat failed: {exc.strerror or exc.args[0]}"

    try:
        with path.open("rb") as handle:
            with suppress(AttributeError, OSError):
                os.posix_fadvise(handle.fileno(), 0, 0, os.POSIX_FADV_RANDOM)
            handle.read(1)
    except PermissionError as exc:
        return f"permission denied: {exc.filename or path}"
    except OSError as exc:
        return f"io error: {exc.strerror or exc.args[0]}"

    suffix = path.suffix.lower()
    if suffix in TEXT_ONLY_HINT_EXTENSIONS and looks_like_text_file(path):
        return "text file"

    try:
        if not is_binary_file(str(path)):
            return "text file"
    except Exception as exc:  # noqa: BLE001
        return f"binary check failed: {exc}"

    return None


def detect_media(path: Path) -> tuple[Optional[MediaFile], Optional[str]]:
    filetype_signature = safe_filetype_guess(path)
    puremagic_signature = safe_puremagic_guess(path)
    signatures = [filetype_signature, puremagic_signature]

    if any(is_archive_signature(sig) for sig in signatures):
        return None, "archive file"

    if any(is_textual_mime(sig.mime) for sig in signatures):
        return None, "text file"

    votes = collect_format_votes(path, puremagic_signature)
    consensus = select_consensus_vote(votes)
    if not consensus:
        return None, votes_error_summary(votes)

    detected_kind = determine_media_kind(votes, consensus)
    if detected_kind not in {"image", "video", "raw"}:
        reason = consensus.mime or consensus.description or votes_error_summary(votes)
        return None, reason or "non-media file"
    size_bytes = None
    try:
        size_bytes = path.stat().st_size
    except OSError:
        size_bytes = None

    suffix = path.suffix.lower() if path.suffix else ""

    animated = False
    if suffix in {".gif"}:
        animated = is_animated_gif(path)
    elif suffix in {".png"}:
        animated = is_animated_png(path)
    elif suffix in {".webp"}:
        animated = is_animated_webp(path)

    psd_color_mode = get_psd_color_mode(path) if suffix == ".psd" else None
    if suffix == ".psd" and not psd_color_mode:
        psd_color_mode = "unknown"

    def vote_for(tool: str) -> Optional[FormatVote]:
        for vote in votes:
            if vote.tool == tool:
                return vote
        return None

    libmagic_vote = vote_for("libmagic")
    puremagic_vote = vote_for("puremagic")
    pyfsig_vote = vote_for("pyfsig")
    binwalk_vote = vote_for("binwalk")

    libmagic_values = [val for val in (libmagic_vote.mime, libmagic_vote.description) if val] if libmagic_vote else []
    puremagic_values: list[str] = []
    if puremagic_vote:
        if puremagic_vote.mime:
            puremagic_values.append(puremagic_vote.mime)
        if puremagic_vote.extension:
            puremagic_values.append(puremagic_vote.extension)
            if puremagic_vote.extension.startswith("."):
                puremagic_values.append(puremagic_vote.extension.lstrip("."))
        if puremagic_vote.description:
            puremagic_values.append(puremagic_vote.description)
    pyfsig_values: list[str] = []
    if pyfsig_vote:
        if pyfsig_vote.description:
            pyfsig_values.append(pyfsig_vote.description)
        if pyfsig_vote.extension:
            pyfsig_values.append(pyfsig_vote.extension)
            if pyfsig_vote.extension.startswith("."):
                pyfsig_values.append(pyfsig_vote.extension.lstrip("."))
    binwalk_values = [binwalk_vote.description] if binwalk_vote and binwalk_vote.description else []

    video_codec = None
    audio_codec = None
    audio_channels = None
    audio_layout = None
    container = None
    ffprobe_tokens: list[str] = []

    if detected_kind == "video":
        # Check for corruption before further processing
        is_corrupt, corrupt_reason = is_video_corrupt_or_truncated(path)
        if is_corrupt:
            return None, f"corrupt or truncated video: {corrupt_reason}"

        probe = ffprobe(path)
        if not probe:
            return None, "video probe failed"
        streams = probe.get("streams", [])
        format_info = probe.get("format", {})
        format_name = format_info.get("format_name", "").lower()
        if not format_name:
            return None, "unsupported video container"
        container = extract_container(format_name)
        for stream in streams:
            codec_type = stream.get("codec_type")
            if codec_type == "video" and not video_codec:
                video_codec = (stream.get("codec_name") or "").lower() or None
            elif codec_type == "audio" and not audio_codec:
                audio_codec = (stream.get("codec_name") or "").lower() or None
                audio_channels = stream.get("channels")
                audio_layout = stream.get("channel_layout")
        if container:
            ffprobe_tokens.append(f"container:{container}")
        if video_codec:
            ffprobe_tokens.append(f"video:{video_codec}")
        if audio_codec:
            ffprobe_tokens.append(f"audio:{audio_codec}")

    extension_candidates: list[Optional[str]] = []
    if consensus:
        consensus_ext = ensure_dot_extension(consensus.extension)
        if consensus_ext:
            extension_candidates.append(consensus_ext)
    suffix_ext = ensure_dot_extension(path.suffix)
    if suffix_ext and suffix_ext not in extension_candidates:
        extension_candidates.append(suffix_ext)
    extension_candidates.append(None)

    rule: Optional[FormatRule] = None
    for candidate in extension_candidates:
        rule = match_rule(
            extension=candidate,
            libmagic=libmagic_values,
            puremagic=puremagic_values,
            pyfsig=pyfsig_values,
            binwalk=binwalk_values,
            rawpy=None,
            ffprobe_streams=ffprobe_tokens,
            animated=animated,
            size_bytes=size_bytes,
            psd_color_mode=psd_color_mode,
        )
        if rule:
            break

    if not rule:
        return None, "format not recognised"

    if rule.action.startswith("skip"):
        reason = rule.notes or "unsupported format"
        return None, reason

    if rule.category == "vector":
        return None, "vector formats are not supported by Apple Photos"

    metadata: dict[str, Any] = {"rule_conditions": rule.conditions, "rule_notes": rule.notes}

    if rule.category == "raw":
        raw_extensions = [path.suffix] + list(rule.extensions)
        install_raw_dependency_groups(collect_raw_groups_from_extensions(raw_extensions))
        raw_media, raw_reason = refine_raw_media(path, raw_extensions)
        if not raw_media:
            return None, raw_reason or "unsupported raw format"
        raw_media.rule_id = rule.rule_id
        raw_media.action = rule.action
        raw_media.requires_processing = rule.action != "import"
        raw_media.notes = rule.notes
        raw_media.metadata.update(metadata)
        return raw_media, None

    preferred_extension = rule.extensions[0] if rule.extensions else None
    consensus_extension = ensure_dot_extension(consensus.extension) if consensus else None
    extension = preferred_extension or consensus_extension or ensure_dot_extension(path.suffix) or ".media"
    if detected_kind == "image":
        media = MediaFile(
            source=path,
            kind="image",
            extension=extension or ".img",
            format_name=(extension or ".img").lstrip("."),
            compatible=rule.action == "import",
            original_suffix=path.suffix,
            rule_id=rule.rule_id,
            action=rule.action,
            requires_processing=rule.action != "import",
            notes=rule.notes,
            metadata=metadata,
        )
        media.metadata.update(
            {
                "animated": animated,
                "size_bytes": size_bytes,
                "psd_color_mode": psd_color_mode,
            }
        )
        refined, reason = refine_image_media(media)
        if not refined:
            return None, reason or "image validation failed"
        return refined, None

    if detected_kind == "video":
        media = MediaFile(
            source=path,
            kind="video",
            extension=extension or ".mp4",
            format_name=container or "video",
            compatible=rule.action == "import",
            video_codec=video_codec,
            audio_codec=audio_codec,
            original_suffix=path.suffix,
            rule_id=rule.rule_id,
            action=rule.action,
            requires_processing=rule.action != "import",
            notes=rule.notes,
            metadata=metadata,
        )
        media.metadata.update(
            {
                "container": container,
                "size_bytes": size_bytes,
                "audio_channels": audio_channels,
                "audio_layout": audio_layout,
            }
        )
        refined, reason = refine_video_media(media)
        if not refined:
            return None, reason or "video validation failed"
        return refined, None

    return None, "unsupported format"


def safe_filetype_guess(path: Path) -> Signature:
    try:
        guess = filetype.guess(str(path))
    except Exception:  # noqa: BLE001
        return Signature()
    if not guess:
        return Signature()
    extension = normalize_extension(guess.extension)
    mime = guess.mime.lower() if guess.mime else None
    return Signature(extension=extension, mime=mime)


def safe_puremagic_guess(path: Path) -> Signature:
    extension = None
    mime = None
    try:
        extension = normalize_extension(puremagic.from_file(str(path)))
    except puremagic.PureError:
        extension = None
    except Exception:  # noqa: BLE001
        extension = None
    try:
        mime_guess = puremagic.from_file(str(path), mime=True)
        mime = mime_guess.lower() if mime_guess else None
    except puremagic.PureError:
        mime = None
    except Exception:  # noqa: BLE001
        mime = None
    return Signature(extension=extension, mime=mime)


def canonical_image_extension(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    key = name.lower().lstrip(".")
    return IMAGE_EXTENSION_MAP.get(key)


def canonical_video_extension(name: Optional[str]) -> Optional[str]:
    key = normalize_extension(name)
    if not key:
        return None
    return VIDEO_EXTENSION_MAP.get(key)


def is_archive_signature(sig: Signature) -> bool:
    if not sig or sig.is_empty():
        return False
    if sig.extension and sig.extension in ARCHIVE_EXTENSIONS:
        return True
    if sig.mime and sig.mime in ARCHIVE_MIME_TYPES:
        return True
    return False


def is_image_signature(sig: Signature) -> bool:
    if not sig or sig.is_empty():
        return False
    if sig.mime and sig.mime.startswith("image/"):
        return True
    if sig.extension and sig.extension in ALL_IMAGE_EXTENSIONS:
        return True
    return False


def is_video_signature(sig: Signature) -> bool:
    if not sig or sig.is_empty():
        return False
    if sig.mime and sig.mime.startswith("video/"):
        return True
    if sig.extension and sig.extension in VIDEO_EXTENSION_HINTS:
        return True
    return False


def choose_image_extension(signatures: Iterable[Signature]) -> Optional[str]:
    for sig in signatures:
        ext = canonical_image_extension(sig.extension)
        if ext:
            return ext
    for sig in signatures:
        if sig.mime:
            mapped = IMAGE_MIME_EXTENSION_MAP.get(sig.mime)
            if mapped:
                return mapped
    return None


def choose_video_extension(signatures: Iterable[Signature]) -> Optional[str]:
    for sig in signatures:
        ext = canonical_video_extension(sig.extension)
        if ext:
            return ext
    for sig in signatures:
        if sig.mime:
            mapped = VIDEO_MIME_EXTENSION_MAP.get(sig.mime)
            if mapped:
                return mapped
    return None


def guess_extension(container: str, kind: str) -> Optional[str]:
    container = container.lower()
    if kind == "image":
        return IMAGE_EXTENSION_MAP.get(container)
    video_map = {
        "mov": ".mov",
        "quicktime": ".mov",
        "mp4": ".mp4",
        "m4v": ".m4v",
        "matroska": ".mkv",
        "webm": ".webm",
        "avi": ".avi",
        "3gpp": ".3gp",
        "mpegts": ".ts",
        "flv": ".flv",
    }
    return video_map.get(container)


def gather_media_files(
    root: Path,
    recursive: bool,
    follow_symlinks: bool,
    skip_logger: SkipLogger,
    stats: RunStatistics,
) -> list[MediaFile]:
    media_files: list[MediaFile] = []

    def should_ignore(entry: Path) -> bool:
        name = entry.name
        if name.startswith("FOUND_MEDIA_FILES_"):
            return True
        if name == LOG_SUBDIR or name.startswith("smm_run_") or name.startswith("smm_skipped_files_"):
            return True
        if name == ".DS_Store":
            return True
        return False

    def iter_candidate_files() -> list[Path]:
        candidates: list[Path] = []
        if recursive:
            for dirpath, dirnames, filenames in os.walk(root, followlinks=follow_symlinks):
                dirnames[:] = [d for d in dirnames if not should_ignore(Path(dirpath) / d)]
                for filename in filenames:
                    entry = Path(dirpath) / filename
                    if should_ignore(entry):
                        continue
                    if entry.is_dir():
                        continue
                    candidates.append(entry)
        else:
            for entry in root.iterdir():
                if should_ignore(entry) or entry.is_dir():
                    continue
                candidates.append(entry)
        return candidates

    candidates = iter_candidate_files()
    scan_progress = ProgressReporter(len(candidates), "Scanning files")
    scan_progress.update(step=0)

    def handle_file(file_path: Path) -> None:
        stats.total_files_scanned += 1

        if file_path.is_symlink() and not follow_symlinks:
            skip_logger.log(file_path, "symlink (use --follow-symlinks to allow)")
            stats.skipped_other += 1
            return
        if not file_path.is_file():
            return

        skippable_reason = is_skippable_file(file_path)
        if skippable_reason:
            skip_logger.log(file_path, skippable_reason)
            if "text file" in skippable_reason.lower():
                stats.total_text_files += 1
            elif "empty" in skippable_reason.lower() or "corrupt" in skippable_reason.lower():
                stats.skipped_corrupt_or_empty += 1
            else:
                stats.skipped_other += 1
            return

        # File is binary
        stats.total_binary_files += 1

        media, reject_reason = detect_media(file_path)
        if media:
            stats.total_media_detected += 1
            if media.compatible and media.action == "import":
                stats.media_compatible += 1
            else:
                stats.media_incompatible += 1
                if media.action and not media.action.startswith("skip"):
                    stats.incompatible_with_conversion_rule += 1
            media_files.append(media)
            return
        if reject_reason:
            skip_logger.log(file_path, reject_reason)
            if "unknown" in reject_reason.lower() or "not recognised" in reject_reason.lower():
                stats.skipped_unknown_format += 1
            elif "corrupt" in reject_reason.lower() or "empty" in reject_reason.lower():
                stats.skipped_corrupt_or_empty += 1
            else:
                stats.skipped_errors += 1
            return

        suffix = normalize_extension(file_path.suffix)
        signatures = [safe_filetype_guess(file_path), safe_puremagic_guess(file_path)]
        if (suffix and (suffix in ALL_IMAGE_EXTENSIONS or suffix in VIDEO_EXTENSION_HINTS)) or any(is_image_signature(sig) or is_video_signature(sig) for sig in signatures):
            skip_logger.log(file_path, "corrupt or unsupported media")
            stats.skipped_corrupt_or_empty += 1

    for file_path in candidates:
        handle_file(file_path)
        scan_progress.update()

    scan_progress.finish()
    return media_files


def next_available_name(directory: Path, stem: str, extension: str) -> Path:
    counter = 0
    while True:
        suffix = "" if counter == 0 else f"_{counter}"
        candidate = directory / f"{stem}{suffix}{extension}"
        if not candidate.exists():
            return candidate
        counter += 1


def build_safe_stem(original_stem: str, run_token: str, sequence: int) -> str:
    normalized = unicodedata.normalize("NFKD", original_stem)
    ascii_stem = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_stem = SAFE_NAME_PATTERN.sub("_", ascii_stem)
    ascii_stem = re.sub(r"_+", "_", ascii_stem).strip("._- ")
    if not ascii_stem:
        ascii_stem = "media"

    run_fragment = run_token[-6:] if len(run_token) >= 6 else run_token
    run_fragment = run_fragment or "run"
    unique_suffix = f"{run_fragment}{sequence:04d}"

    base_limit = max(10, MAX_SAFE_STEM_LENGTH - len(unique_suffix) - 1)
    if len(ascii_stem) > base_limit:
        ascii_stem = ascii_stem[:base_limit].rstrip("._- ") or "media"

    safe_stem = f"{ascii_stem}_{unique_suffix}"
    return safe_stem[:MAX_SAFE_STEM_LENGTH]


def stem_needs_sanitization(stem: str) -> bool:
    if not stem:
        return True
    if SAFE_NAME_PATTERN.search(stem):
        return True
    if len(stem) > MAX_SAFE_STEM_LENGTH:
        return True
    if stem.strip() != stem:
        return True
    return False


def move_to_staging(media_files: Iterable[MediaFile], staging: Path) -> None:
    originals_dir = staging / "ORIGINALS"
    originals_dir.mkdir(parents=True, exist_ok=True)
    media_list = list(media_files)
    progress = ProgressReporter(len(media_list), "Staging media")
    for media in media_list:
        stem = media.source.stem
        destination = next_available_name(staging, stem, media.extension)
        LOG.info("Moving %s -> %s", media.source, destination)
        shutil.move(str(media.source), str(destination))
        media.stage_path = destination
        media.backup_path = None
        if media.requires_processing:
            original_target = next_available_name(originals_dir, stem, media.original_suffix or media.extension)
            try:
                shutil.copy2(destination, original_target)
                media.metadata["original_archive"] = str(original_target)
            except Exception as exc:  # noqa: BLE001
                LOG.warning("Failed to archive original %s: %s", destination, exc)
        progress.update()
    progress.finish()


def create_stage_backup(path: Path) -> Path:
    backup = path.with_name(f"{path.name}.bak")
    counter = 1
    while backup.exists():
        backup = path.with_name(f"{path.name}.bak{counter}")
        counter += 1
    path.rename(backup)
    return backup


def restore_media_file(media: MediaFile) -> None:
    restore_path = resolve_restore_path(media.source)
    restore_path.parent.mkdir(parents=True, exist_ok=True)
    if media.backup_path and media.backup_path.exists():
        media.backup_path.rename(restore_path)
    elif media.stage_path and media.stage_path.exists():
        media.stage_path.rename(restore_path)
    media.stage_path = None
    media.backup_path = None


def convert_image(media: MediaFile) -> None:
    assert media.stage_path is not None
    original_stage = media.stage_path
    backup_path = create_stage_backup(original_stage)
    media.backup_path = backup_path
    parent = backup_path.parent
    target = next_available_name(parent, original_stage.stem, ".jpg")
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(backup_path),
        "-map_metadata",
        "0",
        "-c:v",
        "mjpeg",
        "-qscale:v",
        "2",
        str(target),
    ]
    try:
        run_checked(cmd)
    except Exception:
        with suppress(OSError):
            if target.exists():
                target.unlink()
        with suppress(OSError):
            backup_path.rename(original_stage)
        media.stage_path = original_stage
        media.backup_path = None
        raise
    media.stage_path = target
    media.extension = ".jpg"
    media.format_name = "jpeg"
    media.compatible = True


def convert_video(media: MediaFile) -> None:
    assert media.stage_path is not None
    original_stage = media.stage_path
    backup_path = create_stage_backup(original_stage)
    media.backup_path = backup_path
    parent = backup_path.parent
    target = next_available_name(parent, original_stage.stem, ".mp4")
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(backup_path),
        "-map_metadata",
        "0",
        "-map",
        "0:v:0",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-vf",
        "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
    ]
    if media.audio_codec:
        cmd.extend(["-map", "0:a:0", "-c:a", "aac", "-b:a", "192k"])
    else:
        cmd.append("-an")
    cmd.append(str(target))
    try:
        run_checked(cmd)
    except Exception:
        with suppress(OSError):
            if target.exists():
                target.unlink()
        with suppress(OSError):
            backup_path.rename(original_stage)
        media.stage_path = original_stage
        media.backup_path = None
        raise
    media.stage_path = target
    media.extension = ".mp4"
    media.format_name = "mp4"
    media.video_codec = "h264"
    media.audio_codec = "aac" if media.audio_codec else None
    media.compatible = True


def remove_backups(media_files: Iterable[MediaFile]) -> None:
    for media in media_files:
        if media.backup_path and media.backup_path.exists():
            with suppress(OSError):
                media.backup_path.unlink()
        media.backup_path = None


def revert_conversion(backup_path: Optional[Path], original_path: Path, target_path: Path) -> None:
    if backup_path and backup_path.exists():
        with suppress(OSError):
            if target_path.exists():
                target_path.unlink()
        with suppress(OSError):
            backup_path.rename(original_path)


def convert_to_png(media: MediaFile) -> None:
    """Convert image to PNG format (lossless, widely supported)."""
    if media.stage_path is None:
        raise RuntimeError("Stage path missing for PNG conversion")
    original_stage = media.stage_path
    backup_path = create_stage_backup(original_stage)
    media.backup_path = backup_path
    target = next_available_name(backup_path.parent, original_stage.stem, ".png")

    # Use ffmpeg for conversion (handles more formats than ImageMagick)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(backup_path),
        "-pix_fmt",
        "rgba",
        str(target),
    ]
    try:
        run_command_with_progress(cmd, "Converting to PNG")
    except Exception as exc:
        revert_conversion(backup_path, original_stage, target)
        raise exc
    copy_metadata_from_source(backup_path, target)
    media.stage_path = target
    media.extension = ".png"
    media.format_name = "png"
    media.requires_processing = False
    media.compatible = True


def convert_to_tiff(media: MediaFile) -> None:
    if media.stage_path is None:
        raise RuntimeError("Stage path missing for TIFF conversion")
    original_stage = media.stage_path
    backup_path = create_stage_backup(original_stage)
    media.backup_path = backup_path
    target = next_available_name(backup_path.parent, original_stage.stem, ".tiff")
    cmd = [
        resolve_imagemagick_command(),
        str(backup_path),
        "-alpha",
        "on",
        "-depth",
        "16",
        "-flatten",
        str(target),
    ]
    try:
        run_command_with_progress(cmd, "Converting to TIFF")
    except Exception as exc:
        revert_conversion(backup_path, original_stage, target)
        raise exc
    copy_metadata_from_source(backup_path, target)
    media.stage_path = target
    media.extension = ".tiff"
    media.format_name = "tiff"
    media.requires_processing = False
    media.compatible = True


def convert_to_heic_lossless(media: MediaFile) -> None:
    if media.stage_path is None:
        raise RuntimeError("Stage path missing for HEIC conversion")
    original_stage = media.stage_path
    backup_path = create_stage_backup(original_stage)
    media.backup_path = backup_path
    target = next_available_name(backup_path.parent, original_stage.stem, ".heic")

    intermediate: Optional[Path] = None
    try:
        if backup_path.suffix.lower() == ".jxl":
            djxl = find_executable("djxl")
            if not djxl:
                LOG.warning("djxl not available; falling back to TIFF conversion")
                revert_conversion(backup_path, original_stage, target)
                convert_to_tiff(media)
                return
            fd, tmp_path = tempfile.mkstemp(suffix=".png", prefix="smm_jxl_")
            os.close(fd)
            intermediate = Path(tmp_path)
            run_command_with_progress(
                [djxl, str(backup_path), str(intermediate), "--lossless"],
                "Decoding JPEG XL",
            )
            source_for_heic = intermediate
        else:
            source_for_heic = backup_path

        heif_enc = find_executable("heif-enc")
        if heif_enc and source_for_heic.suffix.lower() in {".png", ".tif", ".tiff", ".jpg", ".jpeg", ".bmp"}:
            cmd = [heif_enc, "--lossless", str(source_for_heic), str(target)]
            run_command_with_progress(cmd, "Encoding HEIC (lossless)")
        else:
            ffmpeg = ensure_ffmpeg_path()
            cmd = [
                ffmpeg,
                "-y",
                "-i",
                str(source_for_heic),
                "-c:v",
                "libx265",
                "-preset",
                "slow",
                "-x265-params",
                "lossless=1",
                "-pix_fmt",
                "yuv444p10le",
                str(target),
            ]
            run_command_with_progress(cmd, "Encoding HEIC via ffmpeg")
    except Exception as exc:
        revert_conversion(backup_path, original_stage, target)
        raise exc
    finally:
        if intermediate and intermediate.exists():
            with suppress(OSError):
                intermediate.unlink()
    copy_metadata_from_source(backup_path, target)
    media.stage_path = target
    media.extension = ".heic"
    media.format_name = "heic"
    media.requires_processing = False
    media.compatible = True


def convert_animation_to_hevc_mp4(media: MediaFile) -> None:
    if media.stage_path is None:
        raise RuntimeError("Stage path missing for animation conversion")
    original_stage = media.stage_path
    backup_path = create_stage_backup(original_stage)
    media.backup_path = backup_path
    target = next_available_name(backup_path.parent, original_stage.stem, ".mp4")
    ffmpeg = ensure_ffmpeg_path()
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(backup_path),
        "-vf",
        "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        "-c:v",
        "libx265",
        "-preset",
        "slow",
        "-x265-params",
        "lossless=1",
        "-pix_fmt",
        "yuv444p10le",
        "-an",
        str(target),
    ]
    try:
        run_command_with_progress(cmd, "Converting animation to HEVC")
    except Exception as exc:
        revert_conversion(backup_path, original_stage, target)
        raise exc
    media.stage_path = target
    media.extension = ".mp4"
    media.format_name = "mp4"
    media.video_codec = "hevc"
    media.audio_codec = None
    media.kind = "video"
    media.requires_processing = False
    media.compatible = True


def rewrap_to_mp4(media: MediaFile) -> None:
    if media.stage_path is None:
        raise RuntimeError("Stage path missing for rewrap")
    original_stage = media.stage_path
    backup_path = create_stage_backup(original_stage)
    media.backup_path = backup_path
    target = next_available_name(backup_path.parent, original_stage.stem, ".mp4")
    ffmpeg = ensure_ffmpeg_path()
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(backup_path),
        "-c",
        "copy",
        "-map",
        "0",
        "-map_metadata",
        "0",
        "-movflags",
        "+faststart",
        str(target),
    ]
    try:
        run_command_with_progress(cmd, "Rewrapping container")
    except Exception as exc:
        revert_conversion(backup_path, original_stage, target)
        raise exc
    media.stage_path = target
    media.extension = ".mp4"
    media.format_name = "mp4"
    media.requires_processing = False
    media.compatible = True


def transcode_to_hevc_mp4(media: MediaFile, copy_audio: bool = False) -> None:
    if media.stage_path is None:
        raise RuntimeError("Stage path missing for transcode")
    original_stage = media.stage_path
    backup_path = create_stage_backup(original_stage)
    media.backup_path = backup_path
    target = next_available_name(backup_path.parent, original_stage.stem, ".mp4")
    ffmpeg = ensure_ffmpeg_path()
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(backup_path),
        "-c:v",
        "libx265",
        "-preset",
        "slow",
        "-x265-params",
        "lossless=1",
        "-pix_fmt",
        "yuv420p10le",
        "-map_metadata",
        "0",
    ]
    if copy_audio:
        cmd.extend(["-c:a", "copy"])
    else:
        cmd.extend(["-c:a", "aac", "-b:a", "256k"])
    cmd.append(str(target))
    try:
        run_command_with_progress(cmd, "Transcoding to HEVC")
    except Exception as exc:
        revert_conversion(backup_path, original_stage, target)
        raise exc
    media.stage_path = target
    media.extension = ".mp4"
    media.format_name = "mp4"
    media.video_codec = "hevc"
    media.audio_codec = media.audio_codec if copy_audio else "aac"
    media.requires_processing = False
    media.compatible = True


def transcode_audio_to_supported(media: MediaFile) -> None:
    if media.stage_path is None:
        raise RuntimeError("Stage path missing for audio transcode")
    original_stage = media.stage_path
    backup_path = create_stage_backup(original_stage)
    media.backup_path = backup_path
    target = next_available_name(backup_path.parent, original_stage.stem, ".mp4")
    ffmpeg = ensure_ffmpeg_path()
    channels = int(media.metadata.get("audio_channels", 0) or 0)
    layout = str(media.metadata.get("audio_layout", "") or "").lower()
    if channels >= 6 or "7.1" in layout or "5.1" in layout:
        audio_codec = "eac3"
        audio_args = ["-c:a", "eac3", "-b:a", "768k"]
    else:
        audio_codec = "aac"
        audio_args = ["-c:a", "aac", "-b:a", "256k"]
    cmd = (
        [
            ffmpeg,
            "-y",
            "-i",
            str(backup_path),
            "-c:v",
            "copy",
        ]
        + audio_args
        + [
            "-map_metadata",
            "0",
            str(target),
        ]
    )
    try:
        run_command_with_progress(cmd, "Normalising audio codec")
    except Exception as exc:
        revert_conversion(backup_path, original_stage, target)
        raise exc
    media.stage_path = target
    media.extension = ".mp4"
    media.format_name = "mp4"
    media.audio_codec = audio_codec
    media.requires_processing = False
    media.compatible = True


def rewrap_or_transcode_to_mp4(media: MediaFile) -> None:
    try:
        rewrap_to_mp4(media)
    except Exception:
        transcode_to_hevc_mp4(media, copy_audio=False)


def skip_unknown_video(media: MediaFile, skip_logger: SkipLogger) -> bool:
    skip_logger.log(media.source, "unsupported video format")
    restore_media_file(media)
    return False


def resolve_restore_path(path: Path) -> Path:
    if not path.exists():
        return path
    return next_available_name(path.parent, path.stem, path.suffix)


def revert_media_files(media_files: Iterable[MediaFile], staging: Optional[Path]) -> None:
    for media in media_files:
        original = media.source
        try:
            if media.backup_path and media.backup_path.exists():
                if media.stage_path and media.stage_path.exists():
                    with suppress(OSError):
                        media.stage_path.unlink()
                restore_path = resolve_restore_path(original)
                restore_path.parent.mkdir(parents=True, exist_ok=True)
                media.backup_path.rename(restore_path)
                media.backup_path = None
                media.stage_path = None
            elif media.stage_path and media.stage_path.exists():
                restore_path = resolve_restore_path(original)
                restore_path.parent.mkdir(parents=True, exist_ok=True)
                media.stage_path.rename(restore_path)
                media.stage_path = None
        except Exception as exc:  # noqa: BLE001
            LOG.warning("Failed to restore %s: %s", original, exc)
    if staging and staging.exists():
        shutil.rmtree(staging, ignore_errors=True)


def sanitize_stage_paths(media_files: Iterable[MediaFile], staging: Path, run_token: str) -> None:
    for index, media in enumerate(media_files, start=1):
        if not media.stage_path or not media.stage_path.exists():
            continue
        stem = media.stage_path.stem
        if not stem_needs_sanitization(stem):
            continue
        safe_stem = build_safe_stem(stem, run_token, index)
        target = next_available_name(staging, safe_stem, media.stage_path.suffix)
        LOG.info("Sanitizing filename %s -> %s", media.stage_path.name, target.name)
        media.stage_path.rename(target)
        media.stage_path = target


def ensure_compatibility(media_files: list[MediaFile], skip_logger: SkipLogger, stats: RunStatistics) -> None:
    retained: list[MediaFile] = []
    progress = ProgressReporter(len(media_files), "Ensuring compatibility")

    for media in media_files:
        if media.stage_path is None or not media.stage_path.exists():
            skip_logger.log(media.source, "staged file missing before processing")
            if media.backup_path and media.backup_path.exists():
                restore_media_file(media)
            progress.update()
            continue

        if media.action == "skip_vector":
            skip_logger.log(media.source, "vector artwork not supported")
            restore_media_file(media)
            progress.update()
            continue

        if media.action == "skip_unknown_video":
            if not skip_unknown_video(media, skip_logger):
                progress.update()
                continue

        try:
            if media.action == "import":
                media.requires_processing = False
                media.compatible = True
            elif media.action == "convert_to_png":
                stats.conversion_attempted += 1
                convert_to_png(media)
                stats.conversion_succeeded += 1
            elif media.action == "convert_to_tiff":
                stats.conversion_attempted += 1
                convert_to_tiff(media)
                stats.conversion_succeeded += 1
            elif media.action == "convert_to_heic_lossless":
                stats.conversion_attempted += 1
                convert_to_heic_lossless(media)
                stats.conversion_succeeded += 1
            elif media.action == "convert_animation_to_hevc_mp4":
                stats.conversion_attempted += 1
                convert_animation_to_hevc_mp4(media)
                stats.conversion_succeeded += 1
            elif media.action == "rewrap_to_mp4":
                stats.conversion_attempted += 1
                rewrap_to_mp4(media)
                stats.conversion_succeeded += 1
            elif media.action == "transcode_to_hevc_mp4":
                stats.conversion_attempted += 1
                transcode_to_hevc_mp4(media, copy_audio=False)
                stats.conversion_succeeded += 1
            elif media.action == "transcode_video_to_lossless_hevc":
                stats.conversion_attempted += 1
                transcode_to_hevc_mp4(media, copy_audio=True)
                stats.conversion_succeeded += 1
            elif media.action == "transcode_audio_to_aac_or_eac3":
                stats.conversion_attempted += 1
                transcode_audio_to_supported(media)
                stats.conversion_succeeded += 1
            elif media.action == "rewrap_or_transcode_to_mp4":
                stats.conversion_attempted += 1
                rewrap_or_transcode_to_mp4(media)
                stats.conversion_succeeded += 1
            else:
                # Default: keep and log unknown action
                skip_logger.log(media.source, f"unhandled action {media.action}, treating as import")
                media.requires_processing = False
                media.compatible = True
        except Exception as exc:  # noqa: BLE001
            stats.conversion_failed += 1
            skip_logger.log(media.source, f"processing failed: {exc}")
            restore_media_file(media)
            progress.update()
            continue

        retained.append(media)
        progress.update()

    media_files[:] = retained
    progress.finish()


def enforce_safe_fallback(media_files: list[MediaFile], skip_logger: SkipLogger, stats: RunStatistics) -> None:
    mutated = False
    for media in media_files:
        if media.kind == "image":
            media.action = "convert_to_png"
            media.requires_processing = True
            media.metadata["safe_fallback"] = True
            mutated = True
        elif media.kind == "video":
            media.action = "transcode_to_hevc_mp4"
            media.requires_processing = True
            media.metadata["safe_fallback"] = True
            mutated = True
    if mutated:
        ensure_compatibility(media_files, skip_logger, stats)


def run_checked(cmd: list[str]) -> None:
    LOG.debug("Executing command: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        LOG.error("Command failed: %s", result.stderr.strip())
        raise RuntimeError(f"Command '{cmd[0]}' failed with exit code {result.returncode}.")


def import_into_photos(media_files: list[MediaFile], stats: RunStatistics) -> tuple[int, list[tuple[MediaFile, str]]]:
    staged_media = [media for media in media_files if media.stage_path and media.stage_path.exists()]
    if not staged_media:
        return 0, []
    script = """
on run argv
    if (count of argv) is 0 then return "0"
    set importedCount to 0
    set failedPaths to {}
    tell application "Photos"
        activate
        repeat with itemPath in argv
            try
                set mediaAlias to my alias_from_posix(itemPath)
                set importedItems to import mediaAlias with skip check duplicates
                if importedItems is missing value then
                    set importedItems to {}
                end if
                if (count of importedItems) = 0 then
                    set end of failedPaths to itemPath
                else
                    set importedCount to importedCount + (count of importedItems)
                end if
            on error errMsg number errNum
                set end of failedPaths to (itemPath & "|ERROR:" & errMsg)
            end try
        end repeat
    end tell

    -- Return format: "imported_count|failed_path1|failed_path2|..."
    set resultStr to importedCount as text
    repeat with failedPath in failedPaths
        set resultStr to resultStr & "|" & failedPath
    end repeat
    return resultStr
end run

on alias_from_posix(itemPath)
    set posixPath to itemPath as text
    try
        return POSIX file posixPath
    on error errMsg number errNum
        error "Unable to resolve path: " & posixPath number -1728
    end try
end alias_from_posix
"""
    batches: list[tuple[list[MediaFile], list[str]]] = []
    current_media: list[MediaFile] = []
    current_batch: list[str] = []
    current_length = 0
    for media in staged_media:
        arg = str(media.stage_path)
        prospective = current_length + len(arg) + 1
        if current_batch and (len(current_batch) >= MAX_APPLESCRIPT_ARGS or prospective > MAX_APPLESCRIPT_CHARS):
            batches.append((current_media, current_batch))
            current_batch = []
            current_media = []
            current_length = 0
        current_batch.append(arg)
        current_media.append(media)
        current_length += len(arg) + 1
    if current_batch:
        batches.append((current_media, current_batch))

    total_imported = 0
    failed: list[tuple[MediaFile, str]] = []
    progress = ProgressReporter(len(staged_media), "Importing into Photos")
    for batch_media, batch_args in batches:
        cmd = ["osascript", "-", *batch_args]
        reason: Optional[str] = None
        try:
            result = subprocess.run(
                cmd,
                input=script,
                text=True,
                capture_output=True,
                check=False,
                timeout=APPLE_PHOTOS_IMPORT_TIMEOUT,
            )
            if result.returncode != 0:
                reason = result.stderr.strip() or "AppleScript import failed"
            else:
                try:
                    total_imported += int(result.stdout.strip() or "0")
                except ValueError:
                    reason = "Unexpected response from AppleScript import"
        except subprocess.TimeoutExpired:
            reason = f"AppleScript import timed out after {APPLE_PHOTOS_IMPORT_TIMEOUT} seconds"
        except Exception as exc:  # pragma: no cover - subprocess errors
            reason = str(exc)

        if reason:
            # Generic error for entire batch
            failed.extend((media, reason) for media in batch_media)
            stats.refused_by_apple_photos += len(batch_media)
            for media in batch_media:
                stats.refused_filenames.append((media.source, reason))
        else:
            # Parse the enhanced result format: "imported_count|failed_path1|failed_path2|..."
            result_str = result.stdout.strip()
            parts = result_str.split("|")
            try:
                batch_imported = int(parts[0])
                total_imported += batch_imported

                # Build a map of stage_path to media
                media_by_path = {str(m.stage_path): m for m in batch_media if m.stage_path}

                # Process failures reported by AppleScript
                for i in range(1, len(parts)):
                    failed_info = parts[i]
                    if "|ERROR:" in failed_info:
                        path_part, error_part = failed_info.split("|ERROR:", 1)
                        media_obj = media_by_path.get(path_part)
                        if media_obj:
                            failed.append((media_obj, error_part))
                            stats.refused_by_apple_photos += 1
                            stats.refused_filenames.append((media_obj.source, error_part))
                    else:
                        # No error message, just failed to import
                        media_obj = media_by_path.get(failed_info)
                        if media_obj:
                            failed.append((media_obj, "import returned 0 items (file may be unsupported)"))
                            stats.refused_by_apple_photos += 1
                            stats.refused_filenames.append((media_obj.source, "import returned 0 items"))

                # Track successful imports
                successful_media = [m for m in batch_media if m not in [f[0] for f in failed]]
                for media in successful_media:
                    if media.requires_processing or media.backup_path:
                        stats.imported_after_conversion += 1
                    else:
                        stats.imported_without_conversion += 1
            except (ValueError, IndexError) as exc:
                # Fallback: if parsing fails, treat as generic error
                reason = f"failed to parse AppleScript result: {exc}"
                failed.extend((media, reason) for media in batch_media)
                stats.refused_by_apple_photos += len(batch_media)
                for media in batch_media:
                    stats.refused_filenames.append((media.source, reason))

        progress.update(len(batch_media))
    progress.finish()
    stats.total_imported = total_imported
    return total_imported, failed


def prompt_retry_failed_imports() -> bool:
    """Prompt the user whether to retry failed Apple Photos imports."""
    while True:
        try:
            response = input("\nWould you like to retry importing the failed files? (y/n): ").strip().lower()
            if response in ("y", "yes"):
                return True
            elif response in ("n", "no"):
                return False
            else:
                print("Please enter 'y' or 'n'.")
        except (KeyboardInterrupt, EOFError):
            print("\nNo retry.")
            return False


def cleanup_staging(staging: Path) -> None:
    if staging.exists():
        LOG.info("Deleting staging folder %s", staging)
        shutil.rmtree(staging)


def configure_logging() -> None:
    LOG.setLevel(logging.INFO)
    LOG.handlers.clear()
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    console.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    LOG.addHandler(console)


def attach_file_logger(root: Path, run_ts: str) -> Path:
    global _FILE_LOG_HANDLER
    if _FILE_LOG_HANDLER is not None:
        return _FILE_LOG_HANDLER.baseFilename  # type: ignore[attr-defined]
    log_dir = root / LOG_SUBDIR
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / f"smm_run_{run_ts}.log"
    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    LOG.addHandler(handler)
    _FILE_LOG_HANDLER = handler
    return path


def validate_root(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.exists():
        raise RuntimeError(f"Path does not exist: {resolved}")
    if not resolved.is_dir():
        raise RuntimeError(f"Path must be a directory: {resolved}")
    return resolved


def main() -> int:
    configure_logging()
    args = parse_args()
    LOG.info("smart-media-manager %s", __version__)
    skip_bootstrap = args.skip_bootstrap or bool(os.environ.get("SMART_MEDIA_MANAGER_SKIP_BOOTSTRAP"))
    if skip_bootstrap:
        LOG.info("Skipping dependency bootstrap (manual mode).")
    else:
        ensure_system_dependencies()
    media_files: list[MediaFile] = []
    staging_root: Optional[Path] = None
    skip_log: Optional[Path] = None
    skip_logger: Optional[SkipLogger] = None
    stats = RunStatistics()
    try:
        root = validate_root(args.path)
        run_ts = timestamp()
        log_path = attach_file_logger(root, run_ts)
        for dependency in ("ffprobe", "ffmpeg", "osascript"):
            ensure_dependency(dependency)
        LOG.info("Scanning %s for media files...", root)
        print(f"Scanning {root}...")
        skip_log = root / f"smm_skipped_files_{run_ts}.log"
        if skip_log.exists():
            skip_log.unlink()
        skip_logger = SkipLogger(skip_log)
        media_files = gather_media_files(root, args.recursive, args.follow_symlinks, skip_logger, stats)
        if not media_files:
            LOG.info("No media files detected.")
            if skip_logger and not skip_logger.has_entries() and skip_log.exists():
                skip_log.unlink()
            return 0
        ensure_raw_dependencies_for_files(media_files)
        staging_root = root / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_root.mkdir(parents=True, exist_ok=False)
        move_to_staging(media_files, staging_root)
        ensure_compatibility(media_files, skip_logger, stats)
        sanitize_stage_paths(media_files, staging_root, run_ts)

        missing_media: list[MediaFile] = [media for media in media_files if not media.stage_path or not media.stage_path.exists()]

        if missing_media:
            missing_listing = ", ".join(str((m.stage_path or m.source)) for m in missing_media[:5])
            raise RuntimeError(f"Missing staged file(s): {missing_listing}")

        staged_count = len(media_files)
        LOG.info("Importing %d file(s) into Apple Photos...", staged_count)
        imported_count, failed_imports = import_into_photos(media_files, stats)
        if failed_imports:
            if skip_logger is None:
                skip_logger = SkipLogger(skip_log or root / f"smm_skipped_files_{run_ts}.log")
            for media, reason in failed_imports:
                skip_logger.log(media.source, f"Apple Photos import failed: {reason}")
            LOG.warning("Apple Photos rejected %d file(s); see skip log.", len(failed_imports))

        # Print statistics summary
        stats.print_summary()
        stats.log_summary()

        # Retry prompt if there were failures
        if failed_imports and prompt_retry_failed_imports():
            LOG.info("Retrying import for %d failed file(s)...", len(failed_imports))
            print(f"\nRetrying {len(failed_imports)} failed import(s)...")
            failed_media = [media for media, _ in failed_imports]
            retry_imported, retry_failed = import_into_photos(failed_media, stats)
            LOG.info("Retry: imported %d, still failed %d", retry_imported, len(retry_failed))
            if retry_imported > 0:
                print(f"Successfully imported {retry_imported} file(s) on retry.")
            if retry_failed:
                print(f"{len(retry_failed)} file(s) still failed after retry.")
                for media, reason in retry_failed:
                    skip_logger.log(media.source, f"Apple Photos import retry failed: {reason}")
            # Update final statistics
            stats.print_summary()
            stats.log_summary()

        remove_backups(media_files)
        LOG.info("Successfully imported %d media file(s) into Apple Photos.", stats.total_imported)
        if args.delete:
            cleanup_staging(staging_root)
        else:
            LOG.info("Staging folder retained at %s", staging_root)
        if skip_log and skip_log.exists():
            if skip_logger and skip_logger.has_entries():
                LOG.info("Skipped file log saved at %s", skip_log)
            else:
                skip_log.unlink()
        print(f"\nDetailed log: {log_path}")
        return 0
    except Exception as exc:  # noqa: BLE001
        LOG.error("Error: %s", exc)
        revert_media_files(media_files, staging_root)
        if skip_log and skip_log.exists():
            if skip_logger and skip_logger.has_entries():
                LOG.info("Skipped file log saved at %s", skip_log)
            else:
                skip_log.unlink()
        if "log_path" in locals():
            print(f"See detailed log: {log_path}")
        return 1


def run() -> None:
    sys.exit(main())


class ProgressReporter:
    def __init__(self, total: int, label: str) -> None:
        self.total = max(total, 1)
        self.label = label
        self.start = time.time()
        self.completed = 0
        self.last_render = 0.0

    def update(self, step: int = 1) -> None:
        self.completed += step
        now = time.time()
        if now - self.last_render < 0.1 and self.completed < self.total:
            return
        self.last_render = now
        percent = min(self.completed / self.total, 1.0)
        elapsed = now - self.start
        rate = self.completed / elapsed if elapsed > 0 else 0
        remaining = (self.total - self.completed) / rate if rate > 0 else float("inf")
        bar_len = 30
        filled = int(bar_len * percent)
        bar = "#" * filled + "-" * (bar_len - filled)
        eta = "--:--" if remaining == float("inf") else time.strftime("%M:%S", time.gmtime(int(remaining)))
        sys.stdout.write(f"\r{self.label}: [{bar}] {percent * 100:5.1f}% ETA {eta}")
        sys.stdout.flush()

    def finish(self) -> None:
        self.completed = self.total
        self.update(step=0)
        sys.stdout.write("\n")
        sys.stdout.flush()
