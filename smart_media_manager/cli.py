from __future__ import annotations

import argparse
import datetime as dt
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
import uuid
from collections import Counter
from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Optional

import json

import filetype  # type: ignore[import-not-found]
import puremagic  # type: ignore[import-not-found]
from PIL import Image  # type: ignore[import-not-found]
from isbinary import is_binary_file  # type: ignore[import-not-found]
from smart_media_manager import __version__
from smart_media_manager.format_rules import FormatRule, match_rule
from smart_media_manager import format_registry
from smart_media_manager import metadata_registry
from pyfsig import interface as pyfsig_interface  # type: ignore[import-not-found]
import rawpy  # type: ignore[import-not-found]

# python-magic requires libmagic system library (installed via Homebrew during bootstrap)
# Must be lazy-loaded so script can start and run bootstrap code
try:
    import magic  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - system dependency
    magic = None

LOG = logging.getLogger("smart_media_manager")
_FILE_LOG_HANDLER: Optional[logging.Handler] = None
SMM_LOGS_SUBDIR = ".smm__runtime_logs_"  # Unique prefix for timestamped log directories (created in CWD, excluded from scanning)


def _log_directory() -> Optional[Path]:
    if _FILE_LOG_HANDLER is None:
        return None
    base = getattr(_FILE_LOG_HANDLER, "baseFilename", None)
    if not base:
        return None
    return Path(base).resolve().parent


SAFE_NAME_PATTERN = re.compile(r"[^A-Za-z0-9_.-]")
MAX_APPLESCRIPT_CHARS = 20000  # Max characters for AppleScript arguments
MAX_SAFE_STEM_LENGTH = 120  # Max length for safe filename stems
MAX_PHOTOS_FILENAME_LENGTH = 60  # Apple Photos filename limit (including extension)
APPLE_PHOTOS_FOLDER_IMPORT_TIMEOUT = 1800  # seconds (30 min) - timeout for single folder import of large collections

STAGING_TOKEN_PREFIX = "__SMM"
STAGING_TOKEN_PATTERN = re.compile(r"SMM([A-Za-z0-9]+)")
MAX_IMAGE_PIXELS_UNSET = object()

# Namespace used to generate deterministic UUIDs for previously unknown mappings
UNKNOWN_UUID_NAMESPACE = uuid.UUID("9a3e9b14-25f0-4e37-bc8e-cc3ad0e59bce")

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
COMPATIBLE_VIDEO_CODECS = {
    # H.264 / AVC
    "h264",
    "avc1",
    # HEVC / H.265
    "hevc",
    "h265",
    "hvc1",
    # Apple ProRes Family (all variants supported by Photos)
    "apco",  # ProRes 422 Proxy
    "apcs",  # ProRes 422 LT
    "apcn",  # ProRes 422
    "apch",  # ProRes 422 HQ
    "ap4h",  # ProRes 4444
    "ap4x",  # ProRes 4444 XQ
    # Note: ProRes RAW cannot be imported (requires Final Cut Pro)
}
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
    # Standard archives
    "zip",
    "rar",
    "7z",
    "tar",
    "gz",
    "bz2",
    "xz",
    "lz",
    "lzma",
    "zst",  # Zstandard (used by Homebrew, etc.)
    "zstd",
    "cab",
    "iso",
    "tgz",
    "tbz2",
    "txz",
    "cpio",
    "sit",  # StuffIt
    "sitx",
    # macOS packages/disk images
    "dmg",
    "pkg",  # macOS installer package (XAR archive)
    "xar",  # eXtensible ARchive format
    "mpkg",  # macOS meta-package
    "sparseimage",
    "sparsebundle",
    # Linux packages
    "deb",
    "rpm",
    # Windows packages
    "msi",
    "msix",
    "appx",
    # Java/Android
    "apk",
    "jar",
    "war",
    "ear",
    "aar",  # Android library
    # Browser extensions
    "xpi",  # Firefox/Mozilla extension
    "crx",  # Chrome extension
    # Application packages (zip-based)
    "apkg",  # Anki flashcard package
    "sketch",  # Sketch design files
    "figma",
    # Office documents (zip-based XML)
    "docx",
    "xlsx",
    "pptx",
    "odt",
    "ods",
    "odp",
    "odg",
    # Ebooks
    "epub",
    "mobi",
    "azw",
    "azw3",
    # ML/AI model files
    "safetensors",
    "gguf",  # llama.cpp models
    "onnx",
    # Virtual disk images
    "vhd",
    "vhdx",
    "vmdk",
    "qcow2",
    # Fonts
    "ttf",
    "otf",
    "woff",
    "woff2",
    "eot",
    "ttc",  # TrueType Collection
    # Executables (not archives but should skip)
    "exe",
    "dll",
    "so",
    "dylib",
    # Documents
    "pdf",
    "rtf",
    "doc",  # Legacy Word
    "xls",  # Legacy Excel
    "ppt",  # Legacy PowerPoint
}

ARCHIVE_MIME_TYPES = {
    # Standard archives
    "application/zip",
    "application/x-zip-compressed",
    "application/x-7z-compressed",
    "application/x-tar",
    "application/x-rar",
    "application/x-rar-compressed",
    "application/vnd.rar",
    "application/gzip",
    "application/x-gzip",
    "application/x-bzip2",
    "application/x-xz",
    "application/x-lzip",
    "application/x-lzma",
    "application/zstd",
    "application/x-cpio",
    "application/x-stuffit",
    "application/x-stuffitx",
    # Disk images
    "application/x-iso9660-image",
    "application/x-apple-diskimage",
    # Packages
    "application/x-xar",  # macOS XAR archive (.pkg, .xar)
    "application/vnd.android.package-archive",
    "application/java-archive",
    "application/x-debian-package",
    "application/x-rpm",
    "application/x-msi",
    # Office documents
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.oasis.opendocument.text",
    "application/vnd.oasis.opendocument.spreadsheet",
    "application/vnd.oasis.opendocument.presentation",
    # Ebooks
    "application/epub+zip",
    "application/x-mobipocket-ebook",
    # Fonts
    "font/otf",
    "font/ttf",
    "font/woff",
    "font/woff2",
    "application/font-sfnt",
    "application/x-font-ttf",
    "application/x-font-otf",
    # Documents
    "application/pdf",
    "application/rtf",
    "application/msword",
    "application/vnd.ms-excel",
    "application/vnd.ms-powerpoint",
    # Executables
    "application/x-msdownload",
    "application/x-executable",
    "application/x-mach-binary",
    "application/x-sharedlib",
}

NON_MEDIA_REASON_KEYWORDS = (
    "archive",
    "unsupported format",
    "format not identified",
    "non-media",
    "uuid detection failed",
    "rawpy unsupported",
    "document",
    "pdf",
    "installer",
    "binary check failed",
)

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
    audio_sample_rate: Optional[int] = None
    audio_sample_fmt: Optional[str] = None
    original_suffix: str = ""
    rule_id: str = ""
    action: str = "import"
    requires_processing: bool = False
    was_converted: bool = False  # Tracks if file was actually converted (for stats)
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    detected_compatible: bool = False  # Detection-time compatibility prior to conversions
    detected_compatible: bool = False


@dataclass
class SkipLogger:
    path: Path
    entries: int = 0

    def log(self, file_path: Path, reason: str) -> None:
        # Log to file only - avoid flooding console with skip messages
        reason_lower = reason.lower()
        # Non-media files are silently ignored to avoid gigantic logs
        if reason_lower.startswith("non-media"):
            return
        LOG.debug("Skipping %s (%s)", file_path, reason)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(f"{file_path}\t{reason}\n")
        self.entries += 1

    def has_entries(self) -> bool:
        return self.entries > 0


class UnknownMappingCollector:
    """Collects missing format UUID mappings and emits an update JSON.

    The collector keeps only one sample per (tool, token, kind) triple
    to avoid bloating memory when thousands of files share the same
    missing mapping.
    """

    def __init__(self) -> None:
        self._entries: dict[tuple[str, str, str], str] = {}

    def register(self, tool: str, token: str, kind: str, sample: Path) -> None:
        key = (tool, token, kind)
        if key not in self._entries:
            self._entries[key] = str(sample)
            LOG.info("Captured missing UUID mapping: %s -> %s (%s)", tool, token, kind)

    def has_entries(self) -> bool:
        return bool(self._entries)

    def _generated_uuid(self, token: str, kind: str) -> str:
        suffix = {
            "video": "V",
            "audio": "A",
            "image": "I",
            "container": "C",
        }.get(kind, "U")
        base = uuid.uuid5(UNKNOWN_UUID_NAMESPACE, f"{kind}:{token}")
        return f"{base}-{suffix}"

    def write_updates(self, output_dir: Path) -> Optional[Path]:
        if not self._entries:
            return None

        update = {
            "format_names": {},
            "tool_mappings": {},
            "apple_photos_compatible": {
                "images": {"needs_conversion": []},
                "videos": {
                    "needs_rewrap": [],
                    "needs_transcode_video": [],
                    "needs_transcode_audio": [],
                    "compatible_containers": [],
                    "compatible_video_codecs": [],
                },
            },
            "generated_from": "smart-media-manager auto-run",
        }

        for (tool, token, kind), sample in sorted(self._entries.items()):
            mapped_uuid = self._generated_uuid(token, kind)
            update.setdefault("tool_mappings", {}).setdefault(tool, {})[token] = mapped_uuid
            update["format_names"][mapped_uuid] = {
                "canonical": token,
                "extensions": [],
                "kind": kind,
                "sample": sample,
            }

            if kind == "video":
                update["apple_photos_compatible"]["videos"]["needs_transcode_video"].append(mapped_uuid)
            elif kind == "audio":
                update["apple_photos_compatible"]["videos"]["needs_transcode_audio"].append(mapped_uuid)
            elif kind == "image":
                update["apple_photos_compatible"]["images"]["needs_conversion"].append(mapped_uuid)

        run_ts = timestamp()
        out_path = output_dir / f"format_registry_updates_{run_ts}.json"
        try:
            with out_path.open("w", encoding="utf-8") as handle:
                json.dump(update, handle, indent=2, sort_keys=True)
            LOG.info("Wrote %d missing mapping(s) to %s", len(self._entries), out_path)
            return out_path
        except Exception as exc:  # noqa: BLE001
            LOG.error("Failed to write format registry updates: %s", exc)
            return None


# Global collector shared across the run
UNKNOWN_MAPPINGS = UnknownMappingCollector()


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
    skipped_non_media: int = 0
    skipped_other: int = 0
    staging_total: int = 0
    staging_expected: int = 0

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
        total_skipped = self.skipped_errors + self.skipped_unknown_format + self.skipped_corrupt_or_empty + self.skipped_non_media + self.skipped_other
        if total_skipped > 0:
            print(f"{BOLD}{BLUE}Skipped Files:{RESET}")
            print(f"  Due to errors:              {self.skipped_errors:>6}")
            print(f"  Unknown format:             {self.skipped_unknown_format:>6}")
            print(f"  Corrupt or empty:           {self.skipped_corrupt_or_empty:>6}")
            if self.skipped_non_media:
                print(f"  Non-media files:            {self.skipped_non_media:>6}")
            print(f"  Other reasons:              {self.skipped_other:>6}")
            print(f"  Total skipped:              {YELLOW}{total_skipped:>6}{RESET}\n")

        print(f"  Total Files In The STAGING FOLDER: {self.staging_total:>6}")
        print(f"  Expected Files In The STAGING FOLDER: {self.staging_expected:>6}\n")

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
        LOG.info(
            "Scanning: total=%d, binary=%d, text=%d",
            self.total_files_scanned,
            self.total_binary_files,
            self.total_text_files,
        )
        LOG.info(
            "Media Detection: detected=%d, compatible=%d, incompatible=%d (with_rule=%d)",
            self.total_media_detected,
            self.media_compatible,
            self.media_incompatible,
            self.incompatible_with_conversion_rule,
        )
        LOG.info(
            "Conversion: attempted=%d, succeeded=%d, failed=%d",
            self.conversion_attempted,
            self.conversion_succeeded,
            self.conversion_failed,
        )
        LOG.info(
            "Import: converted=%d, direct=%d, total=%d, refused=%d",
            self.imported_after_conversion,
            self.imported_without_conversion,
            self.total_imported,
            self.refused_by_apple_photos,
        )
        if self.total_imported + self.refused_by_apple_photos > 0:
            success_rate = (self.total_imported / (self.total_imported + self.refused_by_apple_photos)) * 100
            LOG.info("Success rate: %.1f%%", success_rate)
        LOG.info(
            "Skipped: errors=%d, unknown=%d, corrupt=%d, non_media=%d, other=%d",
            self.skipped_errors,
            self.skipped_unknown_format,
            self.skipped_corrupt_or_empty,
            self.skipped_non_media,
            self.skipped_other,
        )
        LOG.info("Staging: total=%d, expected=%d", self.staging_total, self.staging_expected)
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
        # Install system dependencies (Homebrew packages and casks)
        for package in config.get("brew", []):
            ensure_brew_package(brew_path, package)
        for cask in config.get("cask", []):
            ensure_brew_cask(brew_path, cask)
        # NOTE: Python packages (rawpy) are NOT installed at runtime
        # Users must install with: uv tool install smart-media-manager[enhanced]
        # Or manually: pip install rawpy
        # RAW files will be skipped if rawpy is unavailable (detected via import)
    _INSTALLED_RAW_GROUPS.update(needed)


def refine_raw_media(path: Path, extension_candidates: Iterable[Optional[str]]) -> tuple[Optional[MediaFile], Optional[str]]:
    try:
        with rawpy.imread(str(path)) as raw:
            make = (raw.metadata.camera_make or "").strip()
            model = (raw.metadata.camera_model or "").strip()
            format_name = " ".join(part for part in [make, model] if part) or "raw"
    except rawpy.LibRawFileUnsupportedError:
        return None, "non-media: rawpy unsupported raw"
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
    media.detected_compatible = media.compatible
    return media, None


def refine_image_media(media: MediaFile, skip_compatibility_check: bool = False) -> tuple[Optional[MediaFile], Optional[str]]:
    """
    FAST corruption detection for image files (<10ms for most images).

    Strategy:
    1. Format-specific quick checks (EOF markers) - microseconds
    2. PIL load() to decode pixels - catches truncation - milliseconds

    Args:
        media: MediaFile to validate
        skip_compatibility_check: If True, skip all validation (for testing)
    """
    # Skip all validation if flag is set (for format testing)
    if skip_compatibility_check:
        return media, None

    # FAST CHECK: Format-specific validation (very quick!)
    path = media.source

    # JPEG: Check SOI and EOI markers (2 reads, <1ms)
    if media.extension in (".jpg", ".jpeg"):
        try:
            with open(path, "rb") as f:
                # Check Start of Image marker (FFD8)
                soi = f.read(2)
                if soi != b"\xff\xd8":
                    return None, "invalid JPEG: missing SOI marker (FFD8)"

                # Check End of Image marker (FFD9)
                if path.stat().st_size >= 4:  # Must have at least SOI + EOI
                    f.seek(-2, 2)
                    eoi = f.read()
                    if eoi != b"\xff\xd9":
                        return None, "truncated JPEG: missing EOI marker (FFD9)"
        except OSError as e:
            return None, f"cannot read JPEG markers: {e}"

    # PNG: Check signature and IEND chunk (2 reads, <1ms)
    elif media.extension == ".png":
        try:
            with open(path, "rb") as f:
                # Check PNG signature
                sig = f.read(8)
                if sig != b"\x89PNG\r\n\x1a\n":
                    return None, "invalid PNG: missing signature"

                # Check for IEND chunk at end (last 12 bytes)
                file_size = path.stat().st_size
                if file_size >= 20:  # Minimum valid PNG size
                    f.seek(-12, 2)
                    chunk_data = f.read(12)
                    if b"IEND" not in chunk_data:
                        return None, "truncated PNG: missing IEND chunk"
        except OSError as e:
            return None, f"cannot read PNG chunks: {e}"

    # SPECIAL CHECK: PSD color mode validation
    # Apple Photos only supports RGB PSD, not CMYK or other modes
    if media.extension == ".psd":
        psd_color_mode = media.metadata.get("psd_color_mode", "unknown")
        if psd_color_mode == "cmyk":
            return (
                None,
                "CMYK PSD not supported by Photos (requires RGB TIFF conversion)",
            )
        elif psd_color_mode in ("lab", "multichannel", "duotone"):
            return (
                None,
                f"{psd_color_mode.upper()} PSD not supported by Photos (requires RGB TIFF conversion)",
            )

    # COMPREHENSIVE CHECK: Actually decode the image (catches all corruption)
    # This is still fast (<10ms for most images) but thorough
    try:
        # First pass: verify headers
        with Image.open(path) as img:
            img.verify()

        # CRITICAL: Second pass - actually decode pixel data
        # Must reopen because verify() invalidates the image!
        with Image.open(path) as img:
            img.load()  # Force full decode - catches truncation

            # Sanity check dimensions
            width, height = img.size
            if width <= 0 or height <= 0:
                return None, "invalid image dimensions"

    except Image.DecompressionBombError as e:
        max_pixels = Image.MAX_IMAGE_PIXELS
        if max_pixels:
            return (
                None,
                f"image exceeds Pillow pixel limit ({max_pixels} pixels): {e}. Set --max-image-pixels none or SMART_MEDIA_MANAGER_MAX_IMAGE_PIXELS=none to disable.",
            )
        return (
            None,
            f"image exceeds Pillow pixel limit: {e}. Set --max-image-pixels none or SMART_MEDIA_MANAGER_MAX_IMAGE_PIXELS=none to disable.",
        )
    except (OSError, SyntaxError, ValueError) as e:
        error_msg = str(e).lower()

        # Classify error type for clear messaging
        if "truncated" in error_msg:
            return None, f"truncated or corrupt image data: {e}"
        elif "cannot identify" in error_msg:
            return None, f"invalid image format: {e}"
        else:
            return None, f"image corruption detected: {e}"

    return media, None


def refine_video_media(media: MediaFile, skip_compatibility_check: bool = False) -> tuple[Optional[MediaFile], Optional[str]]:
    """
    Validate video file compatibility with Apple Photos.

    Checks:
    - Video codec and codec tag (Dolby Vision, avc3/hev1, 10-bit)
    - Audio codec compatibility (FLAC, Opus, DTS, etc.)
    - Audio sample rate (must be standard rate)
    - Audio channel configuration

    Args:
        media: MediaFile to validate
        skip_compatibility_check: If True, skip all validation (for testing)
    """
    # Skip all validation if flag is set (for format testing)
    if skip_compatibility_check:
        return media, None

    ffprobe_path = shutil.which("ffprobe")
    if not ffprobe_path:
        return media, None

    # Get BOTH video and audio stream info
    # Note: Don't fail if audio stream missing, just get what's available
    cmd = [
        ffprobe_path,
        "-v",
        "error",
        "-show_entries",
        "stream=codec_type,codec_name,codec_tag_string,width,height,duration,pix_fmt,profile,sample_rate,channels,channel_layout",
        "-of",
        "default=noprint_wrappers=1",
        str(media.source),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None, "video validation failed"

    output = result.stdout.strip()
    output_lower = output.lower()
    media.metadata["ffprobe_info"] = output

    # === VIDEO STREAM VALIDATION ===

    # CRITICAL: Check for incompatible codec tags
    # Apple requires parameter sets in container (stsd), not in-stream
    # Look for codec_tag_string field specifically to avoid false positives
    codec_tag_string = ""
    for line in output.split("\n"):
        if "codec_tag_string=" in line.lower():
            codec_tag_string = line.split("=")[1].strip().lower()
            break

    incompatible_tags = {
        "avc3": "H.264 with in-stream parameters (avc3) not compatible; requires avc1",
        "hev1": "HEVC with in-stream parameters (hev1) not compatible; requires hvc1",
        "dvhe": "Dolby Vision with in-stream parameters (dvhe) not compatible; requires dvh1",
    }

    for tag, error_msg in incompatible_tags.items():
        if tag in codec_tag_string:
            return None, error_msg

    # Check for Dolby Vision (even dvh1 may have import issues)
    # Only check codec tag, not entire output (to avoid false positives)
    if any(tag in codec_tag_string for tag in ["dvh1", "dvav", "dva1"]):
        return (
            None,
            "Dolby Vision HEVC not compatible with Photos (requires standard HEVC transcode)",
        )

    # Also check for "dolby" in entire output as a backup check
    if "dolby" in output_lower and "vision" in output_lower:
        return (
            None,
            "Dolby Vision HEVC not compatible with Photos (requires standard HEVC transcode)",
        )

    # Check for 10-bit color depth
    if "10le" in output_lower or "10be" in output_lower:
        return (
            None,
            "10-bit color depth not fully compatible with Photos (requires 8-bit transcode)",
        )

    # === AUDIO STREAM VALIDATION ===

    audio_codec_value = (media.audio_codec or "").lower()
    if audio_codec_value:
        unsupported_audio = {
            "flac": "FLAC audio not supported by Photos (requires AAC transcode)",
            "opus": "Opus audio not supported by Photos (requires AAC transcode)",
            "dts": "DTS audio not supported by Photos (requires AC-3/EAC-3 transcode)",
            "dts-hd": "DTS-HD audio not supported by Photos (requires AC-3/EAC-3 transcode)",
            "truehd": "Dolby TrueHD audio not supported by Photos (requires AC-3/EAC-3 transcode)",
            "vorbis": "Vorbis audio not supported by Photos (requires AAC transcode)",
        }

        for unsupported_codec, error_msg in unsupported_audio.items():
            if unsupported_codec in audio_codec_value:
                return None, error_msg

        sample_rate = media.audio_sample_rate
        if sample_rate is None:
            current_stream_type = None
            for line in output.split("\n"):
                lower = line.lower()
                if lower.startswith("codec_type="):
                    current_stream_type = lower.split("=", 1)[1].strip()
                elif current_stream_type == "audio" and lower.startswith("sample_rate="):
                    try:
                        sample_rate = int(lower.split("=", 1)[1].strip())
                    except (ValueError, IndexError):
                        sample_rate = None
                    break

        if sample_rate:
            standard_rates = {
                8000,
                11025,
                12000,
                16000,
                22050,
                24000,
                32000,
                44100,
                48000,
                88200,
                96000,
                176400,
                192000,
            }

            if sample_rate not in standard_rates:
                return None, f"Unsupported audio sample rate {sample_rate} Hz (requires resampling to 48000 Hz)"

    return media, None


def run_command_with_progress(command: list[str], message: str, env: Optional[dict[str, str]] = None) -> None:
    bar_length = 28
    start = time.time()
    fd, tmp_name = tempfile.mkstemp(prefix="smm_cmd_", suffix=".log")
    os.close(fd)
    capture_path = Path(tmp_name)
    try:
        with capture_path.open("w", encoding="utf-8") as capture_writer:
            with subprocess.Popen(
                command,
                stdout=capture_writer,
                stderr=subprocess.STDOUT,
                text=True,
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
            output_tail = ""
            try:
                with capture_path.open("r", encoding="utf-8") as capture_reader:
                    data = capture_reader.read()
                    output_tail = data[-4000:].strip()
            except Exception:
                output_tail = "(failed to read command output)"
            error_message = f"Command '{command[0]}' failed with exit code {proc.returncode}."
            if output_tail:
                LOG.error("%s Output:\n%s", error_message, output_tail)
            raise RuntimeError(error_message)
    finally:
        with suppress(OSError):
            capture_path.unlink()


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
        LOG.debug("Package %s already installed; skipping upgrade to avoid repeated downloads.", package)


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
        LOG.debug("Cask %s already installed; skipping upgrade to avoid repeated downloads.", cask)


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
    try:
        if not pip_package_installed(package):
            run_command_with_progress(
                [sys.executable, "-m", "pip", "install", "--upgrade", package],
                f"Installing {package}",
            )
            _PIP_PACKAGE_CACHE.add(package)
        else:
            run_command_with_progress(
                [sys.executable, "-m", "pip", "install", "--upgrade", package],
                f"Updating {package}",
            )
    except RuntimeError as exc:
        # Pip install failed (likely compilation issues for packages with C extensions like rawpy)
        # Log warning and continue - files requiring this package will be skipped
        LOG.warning(
            "Failed to install Python package '%s': %s. Files requiring this package will be skipped. Try installing manually with 'pip install %s' or use --skip-bootstrap to bypass.",
            package,
            exc,
            package,
        )


def ensure_system_dependencies() -> None:
    brew_path = ensure_homebrew()
    for package in REQUIRED_BREW_PACKAGES.values():
        ensure_brew_package(brew_path, package)


def copy_metadata_from_source(source: Path, target: Path) -> None:
    """Copy all metadata from source to target using exiftool with comprehensive field translation.

    Uses exiftool's built-in metadata translation to handle cross-format field mapping:
    - EXIF:DateTimeOriginal → XMP:CreateDate (when needed)
    - IPTC:Caption → XMP:Description (when needed)
    - Preserves GPS, copyright, camera info, etc.

    ExifTool automatically normalizes field names across EXIF, IPTC, and XMP standards,
    acting as a metadata translation layer similar to our UUID system for format names.
    """
    exiftool = find_executable("exiftool")
    if not exiftool or not source.exists() or not target.exists():
        return
    cmd = [
        exiftool,
        "-overwrite_original",
        "-TagsFromFile",
        str(source),
        "-all:all",  # Copy all writable tags preserving group structure
        "-unsafe",  # Include normally unsafe tags (needed for some JPEG repairs)
        str(target),
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        LOG.debug("Metadata copied from %s to %s via exiftool", source.name, target.name)
    except Exception as e:
        LOG.debug("Exiftool metadata copy failed for %s -> %s: %s", source, target, e)


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


def canonicalize_extension(ext: Optional[str]) -> Optional[str]:
    """
    Canonicalize media file extension variants to preferred forms.

    Examples:
        .jfif, .jpeg → .jpg
        .tif → .tiff

    This ensures consistent extension naming regardless of which detection tool
    returned the extension. Only handles media files (image/video/RAW formats).
    Non-media files (HTML, text, etc.) are filtered out before this function is called.
    """
    if not ext:
        return None

    # Ensure normalized form (lowercase, with dot)
    normalized = ensure_dot_extension(ext)
    if not normalized:
        return None

    # Canonical extension mappings for MEDIA FILES ONLY
    # Format: variant → canonical
    CANONICAL_EXTENSIONS = {
        # JPEG variants → .jpg
        ".jfif": ".jpg",
        ".jpeg": ".jpg",
        ".jpe": ".jpg",
        # TIFF variants → .tiff
        ".tif": ".tiff",
        # Add more media format variants as needed based on detection tool outputs
    }

    return CANONICAL_EXTENSIONS.get(normalized, normalized)


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
    if any(
        word in lowered
        for word in (
            "raw",
            "cr2",
            "cr3",
            "nef",
            "arw",
            "raf",
            "orf",
            "rw2",
            "dng",
            "iiq",
            "3fr",
            "x3f",
        )
    ):
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
        return FormatVote(tool="libmagic", error="libmagic not yet installed")
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
        return FormatVote(
            tool="binwalk",
            error=result.stderr.strip() or f"exit code {result.returncode}",
        )
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


def sanitize_path_string(path_str: str) -> str:
    """Clean and normalize path string, handling unicode and control characters.

    Args:
        path_str: Raw path string that may contain unicode, diacritics, or control characters

    Returns:
        Sanitized path string with normalized unicode and stripped control characters
    """
    import re
    import unicodedata

    # Remove leading/trailing whitespace
    cleaned = path_str.strip()

    # Strip control characters (U+0000 to U+001F and U+007F to U+009F)
    # but preserve path separators and valid unicode characters
    control_chars = "".join(chr(i) for i in range(0, 32)) + "".join(chr(i) for i in range(127, 160))
    cleaned = cleaned.translate(str.maketrans("", "", control_chars))

    # Normalize unicode to NFC (Canonical Decomposition, followed by Canonical Composition)
    # This handles diacritics and other language-specific characters consistently
    try:
        cleaned = unicodedata.normalize("NFC", cleaned)
    except (ValueError, TypeError) as e:
        # If normalization fails, try NFKC (compatibility normalization)
        try:
            cleaned = unicodedata.normalize("NFKC", cleaned)
        except (ValueError, TypeError):
            # If both fail, continue with the cleaned string
            LOG.warning(f"Unicode normalization failed for path: {e}")

    # Remove any remaining invalid or problematic characters for file paths
    # Keep: letters, digits, spaces, and common path characters (. - _ / \\ :)
    # This is more permissive to allow international file names
    cleaned = re.sub(r'[<>"|?*\x00-\x1f\x7f-\x9f]', "", cleaned)

    # Final strip to remove any whitespace that may have been exposed
    cleaned = cleaned.strip()

    return cleaned


def validate_path_argument(path_str: str) -> Path:
    """Validate and convert path string to Path object with comprehensive error checking.

    Args:
        path_str: Path string from command line argument

    Returns:
        Validated Path object

    Raises:
        argparse.ArgumentTypeError: If path is invalid, doesn't exist, is empty,
                                   has permission issues, or is on an unmounted volume
    """
    # Sanitize the path string
    cleaned_str = sanitize_path_string(path_str)

    if not cleaned_str:
        raise argparse.ArgumentTypeError("Path cannot be empty after sanitization")

    # Convert to Path object
    try:
        path = Path(cleaned_str).expanduser().resolve()
    except (ValueError, RuntimeError, OSError) as e:
        raise argparse.ArgumentTypeError(f"Invalid path: {e}")

    # Check if path exists
    if not path.exists():
        # Check if it's on an unmounted volume or network path
        parent = path.parent
        if parent.exists():
            # Parent exists but file/dir doesn't - likely deleted/moved
            raise argparse.ArgumentTypeError(f"Path does not exist: {path}")
        else:
            # Parent doesn't exist - might be unmounted volume
            raise argparse.ArgumentTypeError(f"Path does not exist (unmounted volume or network path?): {path}")

    # Check if we have read permissions
    try:
        # For directories, try to list contents
        if path.is_dir():
            try:
                next(path.iterdir(), None)
            except PermissionError:
                raise argparse.ArgumentTypeError(f"Permission denied: Cannot read directory {path}")
            except OSError as e:
                raise argparse.ArgumentTypeError(f"Cannot access directory {path}: {e}")
        # For files, try to open and read
        else:
            try:
                # Check if file is readable
                with path.open("rb") as f:
                    # Try to read first byte to check if file is accessible
                    f.read(1)
            except PermissionError:
                raise argparse.ArgumentTypeError(f"Permission denied: Cannot read file {path}")
            except OSError as e:
                # Could be corrupt, on unmounted volume, or other I/O error
                raise argparse.ArgumentTypeError(f"Cannot read file {path}: {e}")

            # Check if file is empty (warn but don't fail - might be intentional for testing)
            if path.stat().st_size == 0:
                # Note: We don't raise an error here because empty files might be intentional
                # The CLI will handle this later in the processing pipeline
                LOG.warning(f"File is empty: {path}")

    except argparse.ArgumentTypeError:
        # Re-raise our custom errors
        raise
    except Exception as e:
        # Catch any other unexpected errors
        raise argparse.ArgumentTypeError(f"Error validating path {path}: {e}")

    return path


def check_write_permission(directory: Path, operation_name: str = "write") -> None:
    """Check if we have write permissions in the given directory.

    Args:
        directory: Directory to check for write permissions
        operation_name: Description of the operation needing write access (for error messages)

    Raises:
        PermissionError: If directory is not writable with a clear error message
        OSError: If directory cannot be accessed for other reasons
    """
    import tempfile

    if not directory.exists():
        raise OSError(f"Directory does not exist: {directory}")

    if not directory.is_dir():
        raise OSError(f"Path is not a directory: {directory}")

    # Try to create a temporary file to test write permissions
    try:
        with tempfile.NamedTemporaryFile(dir=directory, delete=True) as tmp:
            # Successfully created and can write
            tmp.write(b"test")
    except PermissionError:
        raise PermissionError(f"Permission denied: Cannot {operation_name} in directory {directory}\nPlease check that you have write permissions for this location.")
    except OSError as e:
        raise OSError(f"Cannot {operation_name} in directory {directory}: {e}")


def parse_max_image_pixels(value: str) -> Optional[int]:
    normalized = value.strip().lower()
    if normalized in {"none", "disable", "disabled", "off", "0"}:
        return None
    try:
        pixels = int(normalized)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("max image pixels must be a positive integer or 'none' to disable") from exc
    if pixels <= 0:
        raise argparse.ArgumentTypeError("max image pixels must be a positive integer or 'none' to disable")
    return pixels


def configure_pillow_max_image_pixels(max_image_pixels: Optional[int]) -> None:
    Image.MAX_IMAGE_PIXELS = max_image_pixels
    if max_image_pixels is None:
        LOG.info("Pillow decompression-bomb protection disabled.")
    else:
        LOG.info("Pillow MAX_IMAGE_PIXELS set to %s", max_image_pixels)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="smart-media-manager",
        description="Scan and import media into Apple Photos, fixing extensions and compatibility.",
        epilog="Examples:\n  %(prog)s /path/to/media --recursive\n  %(prog)s /path/to/image.jpg\n  %(prog)s  # scans current directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=None,  # Changed from Path.cwd() to allow special handling
        type=validate_path_argument,  # Use custom validation function
        metavar="PATH",
        help="Directory to scan (default: current directory) or path to a single file",
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
        "--skip-convert",
        action="store_true",
        help="Skip format conversion/transcoding. Files must already be Photos-compatible. Useful for testing raw compatibility.",
    )
    parser.add_argument(
        "--skip-compatibility-check",
        action="store_true",
        help="Skip all compatibility validation checks. ⚠️ WARNING: May cause Photos import errors! Use only for format testing.",
    )
    parser.add_argument(
        "--max-image-pixels",
        type=parse_max_image_pixels,
        default=MAX_IMAGE_PIXELS_UNSET,
        help="Set Pillow image pixel limit; use 'none' to disable (default: none).",
    )
    parser.add_argument(
        "--album",
        type=str,
        default="Smart Media Manager",
        help="Photos album name to import into (default: 'Smart Media Manager').",
    )
    parser.add_argument(
        "--skip-duplicate-check",
        action="store_true",
        default=False,
        help="Skip duplicate checking during import (faster but may import duplicates). Default: check for duplicates and prompt user.",
    )
    parser.add_argument(
        "--copy",
        dest="copy_mode",
        action="store_true",
        help="Copy files into staging instead of moving them (originals are left untouched).",
    )
    parser.add_argument(
        "-y",
        "--yes",
        "--assume-yes",
        dest="assume_yes",
        action="store_true",
        help="Skip confirmation prompt before scanning. Useful for automation and tests.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the smart-media-manager version and exit.",
    )

    args = parser.parse_args()

    # Environment override to avoid interactive prompt (CI/testing)
    if not args.assume_yes:
        env_assume = os.environ.get("SMART_MEDIA_MANAGER_ASSUME_YES")
        if env_assume and env_assume.strip().lower() not in {"0", "false", "no"}:
            args.assume_yes = True

    if args.max_image_pixels is MAX_IMAGE_PIXELS_UNSET:
        env_max_pixels = os.environ.get("SMART_MEDIA_MANAGER_MAX_IMAGE_PIXELS")
        if env_max_pixels and env_max_pixels.strip():
            try:
                args.max_image_pixels = parse_max_image_pixels(env_max_pixels)
            except argparse.ArgumentTypeError as exc:
                parser.error(f"Invalid SMART_MEDIA_MANAGER_MAX_IMAGE_PIXELS: {exc}")
        else:
            args.max_image_pixels = None

    # Handle default path (current directory) if no path provided
    if args.path is None:
        args.path = Path.cwd()

    # In copy mode the user likely wants to keep originals; implicit yes to prompt if flag set
    if args.copy_mode:
        args.assume_yes = True

    return args


def ensure_dependency(name: str) -> None:
    if shutil.which(name) is None:
        raise RuntimeError(f"Required dependency '{name}' is not available on PATH.")


def ffprobe(path: Path) -> Optional[dict[str, Any]]:
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
        return json.loads(result.stdout)  # type: ignore[no-any-return]
    except json.JSONDecodeError:
        return None


def extract_and_normalize_metadata(probe_data: dict[str, Any]) -> dict[str, Any]:
    """
    Extract metadata from ffprobe JSON and normalize field names to UUIDs.

    Extracts metadata from both format-level and stream-level tags, then uses
    the metadata registry to translate ffprobe field names to canonical UUIDs.

    Args:
        probe_data: FFprobe JSON output with 'format' and 'streams' keys

    Returns:
        Dictionary with UUID keys mapping to metadata values

    Example:
        >>> probe = {"format": {"tags": {"creation_time": "2024-01-15"}}}
        >>> metadata = extract_and_normalize_metadata(probe)
        >>> # Returns: {'3d4f8a9c-1e7b-5c3d-9a2f-4e8c1b7d3a9f-M': '2024-01-15'}
    """
    raw_metadata: dict[str, Any] = {}

    # Extract format-level tags (creation_time, artist, title, etc.)
    format_info = probe_data.get("format", {})
    format_tags = format_info.get("tags", {})
    if format_tags:
        # FFprobe tags can have mixed case, normalize to lowercase keys
        for key, value in format_tags.items():
            # Store with lowercase key for consistency
            raw_metadata[key.lower()] = value

    # Extract stream-level tags (for multi-stream files)
    streams = probe_data.get("streams", [])
    for stream in streams:
        stream_tags = stream.get("tags", {})
        if stream_tags:
            for key, value in stream_tags.items():
                # Only add if not already present (format-level takes precedence)
                lower_key = key.lower()
                if lower_key not in raw_metadata:
                    raw_metadata[lower_key] = value

    # Normalize metadata using UUID translation layer
    # This converts ffprobe field names to canonical UUIDs
    if raw_metadata:
        normalized = metadata_registry.normalize_metadata_dict("ffprobe", raw_metadata)
        LOG.debug(f"Extracted and normalized {len(normalized)} metadata fields from ffprobe")
        return normalized

    return {}


def is_video_corrupt_or_truncated(path: Path) -> tuple[bool, Optional[str]]:
    """
    FAST corruption detection for video files (<1 second for most files).

    Strategy: Decode first 5 seconds with error detection enabled.
    This catches 99% of corruption while being very fast.

    For truncated files: The corruption usually manifests early when
    decoder hits missing/invalid data, even if file claims full duration.
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

    # Check duration
    try:
        duration = float(format_info.get("duration", 0))
        if duration <= 0:
            return True, "invalid or missing duration"
    except (ValueError, TypeError):
        return True, "cannot parse duration"

    # FAST CHECK: Decode first 5 seconds with explode on errors
    # This is MUCH faster than full decode but catches most corruption
    # Timeout after 5 seconds to prevent hanging
    cmd = [
        "ffmpeg",
        "-v",
        "error",
        "-err_detect",
        "explode",  # Exit on first error
        "-t",
        "5",  # Only decode first 5 seconds
        "-i",
        str(path),
        "-vframes",
        "60",  # Max 60 frames (2.5s at 24fps)
        "-f",
        "null",
        "-",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
    except subprocess.TimeoutExpired:
        return True, "validation timeout - likely corrupted or very slow codec"

    # CRITICAL: Check stderr REGARDLESS of exit code!
    # ffmpeg returns 0 even when it detects corruption
    stderr = result.stderr.lower() if result.stderr else ""

    corruption_indicators = [
        "partial file",
        "invalid nal",
        "invalid data",
        "decoding error",
        "error splitting",
        "corrupt",
        "truncat",
        "moov atom not found",
        "incomplete",
        "unexpected end",
        "end of file",
        "premature end",
        "failed to decode",
        "invalid bitstream",
        "error decoding",
    ]

    for indicator in corruption_indicators:
        if indicator in stderr:
            return True, f"corruption detected: {stderr[:200]}"

    # Also check return code for fatal errors
    if result.returncode != 0:
        return True, f"decode failed: {stderr[:200]}"

    # ADDITIONAL CHECK: For longer videos, check near the end too
    # This catches truncation that doesn't manifest in first 5s
    if duration > 10:
        # Try to seek near end and decode a few frames
        seek_time = max(0, duration - 2)
        cmd_end = [
            "ffmpeg",
            "-v",
            "error",
            "-ss",
            str(seek_time),
            "-i",
            str(path),
            "-vframes",
            "5",
            "-f",
            "null",
            "-",
        ]

        try:
            result_end = subprocess.run(cmd_end, capture_output=True, text=True, timeout=3)
            stderr_end = result_end.stderr.lower() if result_end.stderr else ""

            for indicator in corruption_indicators:
                if indicator in stderr_end:
                    return True, f"truncated at end: {result_end.stderr[:150]}"
        except subprocess.TimeoutExpired:
            # End-check timeout is acceptable for very large files
            pass

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
                os.posix_fadvise(handle.fileno(), 0, 0, os.POSIX_FADV_RANDOM)  # type: ignore[attr-defined]
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


def detect_media(path: Path, skip_compatibility_check: bool = False) -> tuple[Optional[MediaFile], Optional[str]]:
    filetype_signature = safe_filetype_guess(path)
    puremagic_signature = safe_puremagic_guess(path)
    signatures = [filetype_signature, puremagic_signature]

    if any(is_archive_signature(sig) for sig in signatures):
        return None, "non-media: archive file"

    if any(is_textual_mime(sig.mime) for sig in signatures):
        return None, "non-media: text file"

    votes = collect_format_votes(path, puremagic_signature)
    consensus = select_consensus_vote(votes)
    if not consensus:
        return None, votes_error_summary(votes)

    # UUID-based format detection for early filtering
    tool_results = {}
    for vote in votes:
        if vote.tool and not vote.error:
            # Collect tool outputs for UUID lookup
            if vote.description:
                tool_results[vote.tool] = vote.description
            elif vote.mime:
                tool_results[vote.tool] = vote.mime

    # Try UUID-based detection
    detected_uuid = format_registry.format_detection_result(tool_results) if tool_results else None
    uuid_compatible = format_registry.is_apple_photos_compatible(detected_uuid) if detected_uuid else None
    uuid_canonical_name = format_registry.get_canonical_name(detected_uuid) if detected_uuid else None

    # Register any tool outputs that lack a mapping to help expand the registry
    if tool_results:
        suffix = path.suffix.lower() if path.suffix else ""

        def infer_kind() -> str:
            if is_image_signature(Signature(extension=suffix)) or any(is_image_signature(sig) for sig in signatures):
                return "image"
            if is_video_signature(Signature(extension=suffix)) or any(is_video_signature(sig) for sig in signatures):
                return "video"
            return "container"

        for tool_name, token in tool_results.items():
            if not token:
                continue
            if format_registry.lookup_format_uuid(tool_name, token) is None:
                UNKNOWN_MAPPINGS.register(tool_name, token, infer_kind(), path)

    # Log UUID detection for debugging
    if detected_uuid:
        LOG.debug(f"UUID detection for {path.name}: uuid={detected_uuid}, canonical={uuid_canonical_name}, compatible={uuid_compatible}")

    detected_kind = determine_media_kind(votes, consensus)
    if detected_kind not in {"image", "video", "raw"}:
        reason = consensus.mime or consensus.description or votes_error_summary(votes)
        if reason:
            return None, f"non-media: {reason}"
        return None, "non-media: unidentified format"
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
    # Format parameters for expanded UUID generation
    video_bit_depth = None
    video_pix_fmt = None
    video_profile = None
    audio_sample_rate = None
    audio_sample_fmt = None
    # Initialize UUID variables for all file types (not just videos)
    video_codec_uuid = None
    audio_codec_uuid = None

    if detected_kind == "video":
        # Check for corruption before further processing
        is_corrupt, corrupt_reason = is_video_corrupt_or_truncated(path)
        if is_corrupt:
            return None, f"corrupt or truncated video: {corrupt_reason}"

        probe = ffprobe(path)
        if not probe:
            return None, "video probe failed"

        # Extract and normalize metadata fields using UUID translation layer
        # This converts ffprobe field names (creation_time, artist, etc.) to UUIDs
        normalized_metadata = extract_and_normalize_metadata(probe)

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
                # Extract format parameters for expanded UUID generation
                video_bit_depth = stream.get("bits_per_raw_sample")  # Bit depth (8, 10, 12, 16)
                if not video_bit_depth:
                    # Fallback: try bits_per_component or pix_fmt parsing
                    video_bit_depth = stream.get("bits_per_component")
                video_pix_fmt = stream.get("pix_fmt")  # Pixel format (yuv420p, yuv422p, etc.)
                video_profile = stream.get("profile")  # Profile (High, Main, Main 10, etc.)
            elif codec_type == "audio" and not audio_codec:
                audio_codec = (stream.get("codec_name") or "").lower() or None
                audio_channels = stream.get("channels")
                audio_layout = stream.get("channel_layout")
                # Extract audio format parameters
                sample_rate_val = stream.get("sample_rate")
                try:
                    audio_sample_rate = int(sample_rate_val) if sample_rate_val is not None else None
                except (TypeError, ValueError):
                    audio_sample_rate = None
                audio_sample_fmt = stream.get("sample_fmt")
        if container:
            ffprobe_tokens.append(f"container:{container}")
        if video_codec:
            ffprobe_tokens.append(f"video:{video_codec}")
        if audio_codec:
            ffprobe_tokens.append(f"audio:{audio_codec}")

        # Generate expanded UUID for video codec with format parameters
        # This provides granular format identification (e.g., H.264 8-bit vs 10-bit)
        # IMPORTANT: Use the translation layer to get the base codec UUID
        if video_codec:
            try:
                # Translate ffprobe codec name to base UUID using the unified translation layer
                base_codec_uuid = format_registry.lookup_format_uuid("ffprobe", video_codec)
                if base_codec_uuid:
                    # Extract the base UUID (everything before the type suffix)
                    # E.g., "b2e62c4a-6122-548c-9bfa-0fcf3613942a-V" → "b2e62c4a-6122-548c-9bfa-0fcf3613942a"
                    base_uuid_parts = base_codec_uuid.split("-")
                    if len(base_uuid_parts) >= 5:
                        base_uuid = "-".join(base_uuid_parts[:5])

                        # Convert bit_depth to int if it's a string
                        bit_depth_int = None
                        if video_bit_depth:
                            bit_depth_int = int(video_bit_depth) if isinstance(video_bit_depth, str) else video_bit_depth

                        # Build expanded UUID with format parameters
                        # Start with base UUID, append parameters, then type suffix
                        params = []
                        if bit_depth_int:
                            params.append(f"{bit_depth_int}bit")
                        if video_pix_fmt:
                            params.append(video_pix_fmt)
                        if video_profile:
                            params.append(video_profile.lower())

                        if params:
                            param_suffix = "-".join(params)
                            video_codec_uuid = f"{base_uuid}-{param_suffix}-V"
                        else:
                            # No parameters, use base UUID with type suffix
                            video_codec_uuid = base_codec_uuid

                        LOG.debug(f"Generated expanded video codec UUID for {path.name}: {video_codec_uuid} (base={base_uuid}, codec={video_codec}, bit_depth={bit_depth_int}, pix_fmt={video_pix_fmt}, profile={video_profile})")
                    else:
                        LOG.warning(f"Base codec UUID has unexpected format for {path.name}: {base_codec_uuid}")
                        video_codec_uuid = base_codec_uuid  # Use as-is
                else:
                    UNKNOWN_MAPPINGS.register("ffprobe", video_codec, "video", path)
                    LOG.info("No UUID mapping found for ffprobe codec '%s' for %s", video_codec, path.name)
            except Exception as e:
                LOG.warning(f"Failed to generate expanded video codec UUID for {path.name}: {e}")
                # Fall back to base UUID without parameters
                video_codec_uuid = None

        # Generate expanded UUID for audio codec with format parameters
        # This provides granular format identification (e.g., AAC 48kHz vs 6kHz)
        # IMPORTANT: Use the translation layer to get the base codec UUID
        audio_codec_uuid = None
        if audio_codec:
            try:
                # Translate ffprobe codec name to base UUID using the unified translation layer
                base_audio_uuid = format_registry.lookup_format_uuid("ffprobe", audio_codec)
                if base_audio_uuid:
                    # Extract the base UUID (everything before the type suffix)
                    # E.g., "501331ba-42ea-561c-e5df-8a824df17e3f-A" → "501331ba-42ea-561c-e5df-8a824df17e3f"
                    base_uuid_parts = base_audio_uuid.split("-")
                    if len(base_uuid_parts) >= 5:
                        base_uuid = "-".join(base_uuid_parts[:5])

                        # Build expanded UUID with format parameters
                        # Start with base UUID, append parameters, then type suffix
                        params = []
                        if audio_sample_rate:
                            params.append(str(audio_sample_rate))
                        if audio_sample_fmt:
                            params.append(audio_sample_fmt)

                        if params:
                            param_suffix = "-".join(params)
                            audio_codec_uuid = f"{base_uuid}-{param_suffix}-A"
                        else:
                            # No parameters, use base UUID with type suffix
                            audio_codec_uuid = base_audio_uuid

                        LOG.debug(f"Generated expanded audio codec UUID for {path.name}: {audio_codec_uuid} (base={base_uuid}, codec={audio_codec}, sample_rate={audio_sample_rate}, sample_fmt={audio_sample_fmt})")
                    else:
                        LOG.warning(f"Base audio codec UUID has unexpected format for {path.name}: {base_audio_uuid}")
                        audio_codec_uuid = base_audio_uuid  # Use as-is
                else:
                    UNKNOWN_MAPPINGS.register("ffprobe", audio_codec, "audio", path)
                    LOG.info("No UUID mapping found for ffprobe audio codec '%s' for %s", audio_codec, path.name)
            except Exception as e:
                LOG.warning(f"Failed to generate expanded audio codec UUID for {path.name}: {e}")
                # Fall back to None
                audio_codec_uuid = None

    extension_candidates: list[Optional[str]] = []
    if consensus:
        consensus_ext = canonicalize_extension(consensus.extension)  # Apply canonicalization to detected extension
        if consensus_ext:
            extension_candidates.append(consensus_ext)
    suffix_ext = canonicalize_extension(path.suffix)  # Apply canonicalization to file suffix
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

    # CRITICAL: JSON file is the SOLE source of truth for format identification
    # If UUID detection fails, the file is unidentified and must be rejected
    if not detected_uuid:
        LOG.debug(f"UUID detection failed for {path.name} - file not identified")
        return None, "non-media: format not identified by UUID system"

    # For video files, pass both container UUID and video codec UUID
    # This provides granular format identification (e.g., H.264 8-bit vs 10-bit)
    # while also checking container compatibility (MP4/MOV vs MKV)
    primary_uuid = detected_uuid
    container_uuid_param = None
    if detected_kind == "video" and "video_codec_uuid" in locals() and video_codec_uuid:
        # Use expanded video codec UUID as primary, pass container UUID separately
        primary_uuid = video_codec_uuid
        container_uuid_param = detected_uuid
        LOG.debug(f"Using expanded video codec UUID for {path.name}: {video_codec_uuid} (container UUID: {detected_uuid})")

    # UUID detected - determine action from JSON
    # Pass audio_codec_uuid instead of audio_codec to use UUID-based compatibility checking
    uuid_action = format_registry.get_format_action(primary_uuid, video_codec, audio_codec_uuid, container_uuid_param)
    if not uuid_action:
        # UUID identified but format is unsupported
        LOG.debug(f"UUID {primary_uuid} identified but unsupported for {path.name}")
        return None, f"non-media: unsupported format (UUID={primary_uuid})"

    # UUID system says this format is supported - use its action
    LOG.debug(f"UUID-based action for {path.name}: {uuid_action} (UUID={primary_uuid}, container={container_uuid_param})")

    # JSON is the sole source of truth - we already have uuid_action from above
    # Keep rule for metadata only (rule_id, notes, extensions for legacy compatibility)
    if not rule:
        # No rule found - but UUID system already approved it, so create a minimal rule
        # This shouldn't happen often as most formats should have rules
        LOG.warning(f"UUID {detected_uuid} approved but no format rule found for {path.name}")

    # Use uuid_action as the effective action (JSON is authoritative)
    effective_action = uuid_action

    if rule.category == "vector":
        return None, "vector formats are not supported by Apple Photos"

    metadata: dict[str, Any] = {
        "rule_conditions": rule.conditions,
        "rule_notes": rule.notes,
        "detected_uuid": detected_uuid,
        "uuid_canonical_name": uuid_canonical_name,
        "uuid_compatible": uuid_compatible,
    }

    if rule.category == "raw":
        raw_extensions = [path.suffix] + list(rule.extensions)
        install_raw_dependency_groups(collect_raw_groups_from_extensions(raw_extensions))
        raw_media, raw_reason = refine_raw_media(path, raw_extensions)
        if not raw_media:
            return None, raw_reason or "unsupported raw format"
        raw_media.rule_id = rule.rule_id
        raw_media.action = effective_action
        raw_media.requires_processing = effective_action != "import"
        raw_media.notes = rule.notes
        raw_media.metadata.update(metadata)
        return raw_media, None

    original_extension = canonicalize_extension(path.suffix)  # Apply canonicalization
    consensus_extension = canonicalize_extension(consensus.extension) if consensus else None  # Apply canonicalization
    preferred_extension = canonicalize_extension(rule.extensions[0]) if rule.extensions else None  # Apply canonicalization

    # NEVER change extension unless format detected differs from file extension
    # Priority: always keep original if valid, only use detected format if no extension or wrong extension
    if original_extension and rule.extensions and original_extension in rule.extensions:
        # Original extension is valid for the detected format - keep it!
        extension = original_extension
    elif original_extension:
        # File has extension but it doesn't match detected format - use detected format
        extension = consensus_extension or preferred_extension or original_extension or ".media"
    else:
        # File has no extension - use detected format
        extension = consensus_extension or preferred_extension or ".media"
    if detected_kind == "image":
        media = MediaFile(
            source=path,
            kind="image",
            extension=extension or ".img",
            format_name=(extension or ".img").lstrip("."),
            compatible=effective_action == "import",
            original_suffix=path.suffix,
            rule_id=rule.rule_id,
            action=effective_action,
            requires_processing=effective_action != "import",
            notes=rule.notes,
            metadata=metadata,
        )
        media.detected_compatible = media.compatible
        media.metadata.update(
            {
                "animated": animated,
                "size_bytes": size_bytes,
                "psd_color_mode": psd_color_mode,
            }
        )
        refined_media, refine_reason = refine_image_media(media, skip_compatibility_check)
        if refined_media is None:
            return None, refine_reason or "image validation failed"
        return refined_media, None

    if detected_kind == "video":
        media = MediaFile(
            source=path,
            kind="video",
            extension=extension or ".mp4",
            format_name=container or "video",
            compatible=effective_action == "import",
            video_codec=video_codec,
            audio_codec=audio_codec,
            audio_sample_rate=audio_sample_rate,
            audio_sample_fmt=audio_sample_fmt,
            original_suffix=path.suffix,
            rule_id=rule.rule_id,
            action=effective_action,
            requires_processing=effective_action != "import",
            notes=rule.notes,
            metadata=metadata,
        )
        media.detected_compatible = media.compatible
        media.metadata.update(
            {
                "container": container,
                "size_bytes": size_bytes,
                "audio_channels": audio_channels,
                "audio_layout": audio_layout,
                "audio_sample_rate": audio_sample_rate,
                "audio_sample_fmt": audio_sample_fmt,
            }
        )
        # Add normalized metadata from ffprobe (UUID-keyed fields)
        # This includes creation_time, artist, title, etc. with UUID keys
        if normalized_metadata:
            media.metadata.update(normalized_metadata)
        refined_media, refine_reason = refine_video_media(media, skip_compatibility_check)
        if refined_media is None:
            return None, refine_reason or "video validation failed"
        return refined_media, None

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


def should_ignore(entry: Path) -> bool:
    """Check if file/directory should be excluded from scanning.

    Excludes:
    - FOUND_MEDIA_FILES_* staging directories
    - .smm__runtime_logs_* log directories (timestamped, in CWD)
    - smm_run_* and smm_skipped_files_* log files
    - .DS_Store system files
    - Files with __SMM token (already processed by SMM)
    - Files managed by Apple Photos (have assetsd xattrs)
    """
    name = entry.name
    # Exclude staging directories
    if name.startswith("FOUND_MEDIA_FILES_"):
        return True
    # Exclude timestamped log directories (new pattern)
    if name.startswith(SMM_LOGS_SUBDIR):
        return True
    if name.startswith("DEBUG_raw_applescript_output_") or name.startswith("DEBUG_photos_output_"):
        return True
    if name.startswith("Photos_rejections_"):
        return True
    # Exclude individual log files and skip logs (legacy/backward compat)
    if name.startswith("smm_run_") or name.startswith("smm_skipped_files_"):
        return True
    # Exclude macOS metadata
    if name == ".DS_Store":
        return True
    # Exclude files already processed by SMM (have __SMM token in filename)
    if STAGING_TOKEN_PREFIX in name:
        LOG.debug("Skipping already-processed file: %s", name)
        return True
    return False


def is_photos_managed_file(path: Path) -> bool:
    """Check if a file is managed by Apple Photos (has assetsd xattrs).

    Files imported into Apple Photos get extended attributes from the assetsd
    daemon. These files are locked by the Photos database and cannot be moved
    or modified without causing sync issues or permission errors.

    Args:
        path: Path to check

    Returns:
        True if file has com.apple.assetsd.UUID xattr (managed by Photos)
    """
    try:
        import xattr

        attrs = xattr.listxattr(str(path))
        # Check for the UUID attribute which definitively marks Photos-managed files
        return "com.apple.assetsd.UUID" in attrs
    except ImportError:
        # xattr module not available, fall back to subprocess
        # Use xattr without -l to list only attribute names (avoids binary value decoding issues)
        try:
            result = subprocess.run(
                ["xattr", str(path)],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return "com.apple.assetsd.UUID" in result.stdout
        except Exception:
            return False
    except Exception:
        return False


def extract_live_photo_content_id(path: Path) -> Optional[str]:
    """
    Extract Live Photo content identifier from HEIC/MOV file using exiftool.

    Live Photos have a content identifier that links the HEIC photo and MOV video.
    This function extracts that identifier to enable pairing detection.

    Args:
        path: Path to HEIC or MOV file

    Returns:
        Content identifier string if found, None otherwise
    """
    exiftool = find_executable("exiftool")
    if not exiftool:
        LOG.debug("exiftool not available, skipping Live Photo content ID extraction")
        return None

    try:
        result = subprocess.run(
            [exiftool, "-ContentIdentifier", "-b", str(path)],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            content_id = result.stdout.strip()
            LOG.debug("Extracted Live Photo content ID from %s: %s", path.name, content_id)
            return content_id
    except Exception as exc:
        LOG.debug("Failed to extract Live Photo content ID from %s: %s", path.name, exc)
    return None


def is_panoramic_photo(path: Path) -> bool:
    """
    Detect if a photo is a panoramic image using EXIF metadata.

    Panoramic photos have special metadata tags that identify them as panoramas.
    Common indicators include ProjectionType, UsePanoramaViewer, or PoseHeadingDegrees.

    Args:
        path: Path to image file

    Returns:
        True if panoramic metadata detected, False otherwise
    """
    exiftool = find_executable("exiftool")
    if not exiftool:
        LOG.debug("exiftool not available, skipping panoramic photo detection")
        return False

    try:
        result = subprocess.run(
            [exiftool, "-ProjectionType", "-UsePanoramaViewer", "-PoseHeadingDegrees", "-b", str(path)],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            # Check for common panoramic indicators
            if output and any(indicator in output.lower() for indicator in ["equirectangular", "cylindrical", "spherical", "true", "360"]):
                LOG.debug("Detected panoramic photo: %s", path.name)
                return True
    except Exception as exc:
        LOG.debug("Failed to check panoramic metadata for %s: %s", path.name, exc)
    return False


def detect_live_photo_pairs(media_files: list[MediaFile]) -> dict[str, tuple[MediaFile, MediaFile]]:
    """
    Detect Live Photo pairs (HEIC + MOV) by matching stems and content identifiers.

    Live Photos consist of:
    - A HEIC/JPG still image
    - A MOV video clip
    - Both files share the same stem (e.g., IMG_1234.HEIC + IMG_1234.MOV)
    - Both files have matching ContentIdentifier metadata

    Args:
        media_files: List of detected media files

    Returns:
        Dictionary mapping content_id -> (image_file, video_file) for each Live Photo pair
    """
    # Group files by stem
    files_by_stem: dict[str, list[MediaFile]] = {}
    for media in media_files:
        stem = media.source.stem
        if stem not in files_by_stem:
            files_by_stem[stem] = []
        files_by_stem[stem].append(media)

    live_photo_pairs: dict[str, tuple[MediaFile, MediaFile]] = {}

    # Check each stem group for Live Photo patterns
    for stem, files in files_by_stem.items():
        if len(files) < 2:
            continue

        # Find HEIC/JPG and MOV candidates
        image_candidates = [f for f in files if f.kind == "image" and f.extension.lower() in {".heic", ".heif", ".jpg", ".jpeg"}]
        video_candidates = [f for f in files if f.kind == "video" and f.extension.lower() == ".mov"]

        if not image_candidates or not video_candidates:
            continue

        # Try to match by content identifier
        for img in image_candidates:
            img_content_id = extract_live_photo_content_id(img.source)
            if not img_content_id:
                continue

            for vid in video_candidates:
                vid_content_id = extract_live_photo_content_id(vid.source)
                if vid_content_id and vid_content_id == img_content_id:
                    # Found a Live Photo pair!
                    LOG.debug("Detected Live Photo pair: %s + %s (content ID: %s)", img.source.name, vid.source.name, img_content_id)
                    live_photo_pairs[img_content_id] = (img, vid)

                    # Store pairing metadata in both files
                    img.metadata["is_live_photo"] = True
                    img.metadata["live_photo_pair"] = str(vid.source)
                    img.metadata["live_photo_content_id"] = img_content_id

                    vid.metadata["is_live_photo"] = True
                    vid.metadata["live_photo_pair"] = str(img.source)
                    vid.metadata["live_photo_content_id"] = vid_content_id
                    break

    return live_photo_pairs


def gather_media_files(
    root: Path,
    recursive: bool,
    follow_symlinks: bool,
    skip_logger: SkipLogger,
    stats: RunStatistics,
    skip_compatibility_check: bool = False,
) -> list[MediaFile]:
    media_files: list[MediaFile] = []

    def iter_candidate_files() -> Iterable[Path]:
        if recursive:
            for dirpath, dirnames, filenames in os.walk(root, followlinks=follow_symlinks):
                dirnames[:] = [d for d in dirnames if not should_ignore(Path(dirpath) / d)]
                for filename in filenames:
                    entry = Path(dirpath) / filename
                    if should_ignore(entry) or entry.is_dir():
                        continue
                    yield entry
        else:
            for entry in root.iterdir():
                if should_ignore(entry) or entry.is_dir():
                    continue
                yield entry

    scan_progress = ProgressReporter(0, "Scanning files")

    def handle_file(file_path: Path) -> None:
        stats.total_files_scanned += 1

        if file_path.is_symlink() and not follow_symlinks:
            skip_logger.log(file_path, "symlink (use --follow-symlinks to allow)")
            stats.skipped_other += 1
            return
        if not file_path.is_file():
            return

        # Skip files managed by Apple Photos - they're already imported and locked
        if is_photos_managed_file(file_path):
            LOG.debug("Skipping Photos-managed file: %s", file_path.name)
            stats.skipped_other += 1
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

        media, reject_reason = detect_media(file_path, skip_compatibility_check)
        if media:
            stats.total_media_detected += 1
            if media.compatible and media.action == "import":
                stats.media_compatible += 1
            else:
                stats.media_incompatible += 1
                if media.action and not media.action.startswith("skip"):
                    stats.incompatible_with_conversion_rule += 1

            # Check for panoramic photos
            if media.kind == "image" and media.extension.lower() in {".heic", ".heif", ".jpg", ".jpeg"}:
                if is_panoramic_photo(file_path):
                    media.metadata["is_panoramic"] = True
                    LOG.debug("Detected panoramic photo: %s", file_path.name)

            media_files.append(media)
            return
        if reject_reason:
            reason_lower = reject_reason.lower()
            is_non_media = reason_lower.startswith("non-media:")
            if not is_non_media:
                is_non_media = any(keyword in reason_lower for keyword in NON_MEDIA_REASON_KEYWORDS)
            if "unknown" in reason_lower or "not recognised" in reason_lower:
                stats.skipped_unknown_format += 1
                log_reason = reject_reason
            elif "corrupt" in reason_lower or "empty" in reason_lower:
                stats.skipped_corrupt_or_empty += 1
                log_reason = reject_reason
            elif is_non_media:
                stats.skipped_non_media += 1
                if reason_lower.startswith("non-media:") and ":" in reject_reason:
                    log_reason = reject_reason.split(":", 1)[1].strip()
                    if not log_reason:
                        log_reason = "non-media file"
                else:
                    log_reason = reject_reason
            else:
                stats.skipped_errors += 1
                log_reason = reject_reason
            if not is_non_media:
                skip_logger.log(file_path, log_reason)
            return

        suffix = normalize_extension(file_path.suffix)
        signatures = [safe_filetype_guess(file_path), safe_puremagic_guess(file_path)]
        if (suffix and (suffix in ALL_IMAGE_EXTENSIONS or suffix in VIDEO_EXTENSION_HINTS)) or any(is_image_signature(sig) or is_video_signature(sig) for sig in signatures):
            skip_logger.log(file_path, "corrupt or unsupported media")
            stats.skipped_corrupt_or_empty += 1

    for file_path in iter_candidate_files():
        handle_file(file_path)
        scan_progress.update()

    scan_progress.finish()

    # Detect Live Photo pairs after all files are scanned
    if media_files:
        live_photo_pairs = detect_live_photo_pairs(media_files)
        if live_photo_pairs:
            LOG.debug("Found %d Live Photo pair(s)", len(live_photo_pairs))

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


def move_to_staging(
    media_files: Iterable[MediaFile],
    staging: Path,
    originals_dir: Path,
    copy_files: bool = False,
) -> None:
    """Stage media files with unique sequential suffix for folder import.

    Every file gets a suffix like " (1)", " (2)", etc. before extension.
    This enables deterministic filename reconciliation after Photos import,
    eliminating the need for separate sanitization passes.

    The sequential suffix ensures every file has a unique, predictable name
    that can be matched against Photos' returned filenames to determine
    which files were imported vs skipped.

    Examples:
        photo.jpg → photo (1).jpg
        photo.jpg (from different subfolder) → photo (2).jpg
        video.mov → video (1).mov
        IMG_1234.HEIC (Live Photo) → IMG_1234 (1).HEIC
        IMG_1234.MOV (paired) → IMG_1234 (2).MOV

    Args:
        media_files: Iterable of MediaFile objects to stage
        staging: Path to staging directory (FOUND_MEDIA_FILES_*)
        originals_dir: Path to originals archive directory (SEPARATE from staging, not a subdirectory)

    Note:
        Live Photo pairs maintain consistent stems but get different suffixes
        since they are separate files.
    """
    originals_dir.mkdir(parents=True, exist_ok=True)
    media_list = list(media_files)

    # Global sequence counter for ALL files (starts at 1)
    sequence_counter = 1
    run_token = uuid.uuid4().hex

    # Track Live Photo pairs to ensure consistent naming
    live_photo_stems: dict[str, str] = {}  # Maps content_id -> chosen_stem

    progress = ProgressReporter(len(media_list), "Staging media")
    for media in media_list:
        stem = media.source.stem.replace(" ", "_")  # Replace spaces to avoid Photos/import quirks

        if stem_needs_sanitization(stem):
            stem = build_safe_stem(stem, run_token, sequence_counter)

        token = uuid.uuid4().hex[:8]
        token_component = f"{STAGING_TOKEN_PREFIX}{token}__"

        # Precompute suffix now to enforce Apple Photos filename length limit; no spaces
        suffix = f"_({sequence_counter})"

        # Enforce both safe-stem limit and Apple Photos filename length (60 chars)
        max_base_len = max(
            5,
            min(
                MAX_SAFE_STEM_LENGTH - len(token_component),
                MAX_PHOTOS_FILENAME_LENGTH - len(token_component) - len(suffix) - len(media.extension),
            ),
        )
        if len(stem) > max_base_len:
            stem = stem[:max_base_len].rstrip("._- ") or "media"

        tokenized_stem = f"{stem}{token_component}"

        # Handle Live Photo pairs with consistent naming
        if media.metadata.get("is_live_photo"):
            content_id = media.metadata.get("live_photo_content_id")
            if content_id:
                if content_id in live_photo_stems:
                    # Use the same stem as the paired file
                    live_stem = live_photo_stems[content_id]
                    if stem != live_stem:
                        stem = live_stem
                        max_base_len = max(
                            5,
                            min(
                                MAX_SAFE_STEM_LENGTH - len(token_component),
                                MAX_PHOTOS_FILENAME_LENGTH - len(token_component) - len(suffix) - len(media.extension),
                            ),
                        )
                        if len(stem) > max_base_len:
                            stem = stem[:max_base_len].rstrip("._- ") or "media"
                        tokenized_stem = f"{stem}{token_component}"
                    LOG.debug("Using paired stem %s for Live Photo %s", stem, media.source.name)
                else:
                    # First file of the pair - store the sanitized stem for the paired file
                    live_photo_stems[content_id] = stem
                    LOG.debug("Set stem %s for Live Photo pair (content ID: %s)", stem, content_id)

        unique_name = f"{tokenized_stem}{suffix}{media.extension}"
        destination = staging / unique_name

        # Handle collision (very unlikely with global counter, but safety net)
        collision_counter = 1
        while destination.exists():
            collision_counter += 1
            unique_name = f"{stem}_({sequence_counter}-{collision_counter}){media.extension}"
            destination = staging / unique_name

        media.metadata.setdefault("original_source", str(media.source))
        LOG.debug("%s %s -> %s", "Copying" if copy_files else "Moving", media.source, destination)
        try:
            if copy_files:
                shutil.copy2(str(media.source), str(destination))
            else:
                shutil.move(str(media.source), str(destination))
        except PermissionError as exc:
            # File might be locked by Apple Photos or another process
            LOG.warning(
                "Permission denied for %s (may be locked by Photos): %s",
                media.source.name,
                exc,
            )
            media.stage_path = None
            media.metadata["staging_error"] = f"Permission denied: {exc}"
            progress.update()
            continue
        except OSError as exc:
            if exc.errno == 1:  # EPERM - Operation not permitted
                LOG.warning(
                    "Operation not permitted for %s (may be locked by Photos): %s",
                    media.source.name,
                    exc,
                )
                media.stage_path = None
                media.metadata["staging_error"] = f"Operation not permitted: {exc}"
                progress.update()
                continue
            raise
        media.stage_path = destination
        media.metadata["staging_stem"] = stem
        media.metadata["staging_suffix"] = suffix
        media.metadata["staging_name"] = destination.name
        media.metadata["staging_token"] = token
        media.metadata["staging_tokenized_stem"] = tokenized_stem
        media.metadata["copy_mode"] = copy_files
        sequence_counter += 1  # Increment for next file

        # Archive original if processing is required (before conversion)
        if media.requires_processing and not copy_files:
            # Use next_available_name for originals since they don't need reconciliation
            original_target = next_available_name(originals_dir, stem, media.original_suffix or media.extension)
            try:
                shutil.copy2(destination, original_target)
                media.metadata["original_archive"] = str(original_target)
            except Exception as exc:  # noqa: BLE001
                LOG.warning("Failed to archive original %s: %s", destination, exc)

        progress.update()
    progress.finish()


def restore_media_file(media: MediaFile) -> None:
    """Restore media file to original location.

    Used when reverting changes due to errors.
    No backups are used - the staged file is simply moved back.
    """
    if media.metadata.get("copy_mode"):
        # In copy mode the source is untouched; simply remove staged copy
        if media.stage_path and media.stage_path.exists():
            media.stage_path.unlink()
        media.stage_path = None
        return
    restore_path = resolve_restore_path(media.source)
    restore_path.parent.mkdir(parents=True, exist_ok=True)
    if media.stage_path and media.stage_path.exists():
        media.stage_path.rename(restore_path)
    media.stage_path = None


def convert_image(media: MediaFile) -> None:
    """Convert image to JPEG format using ffmpeg.

    Converts directly from source to target without creating backups.
    If conversion fails, the original file is preserved.
    """
    assert media.stage_path is not None
    source = media.stage_path
    target = next_available_name(source.parent, source.stem, ".jpg")

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
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
        # Conversion succeeded - delete original, use converted file
        source.unlink()
        media.stage_path = target
        media.extension = ".jpg"
        media.format_name = "jpeg"
        media.compatible = True
    except Exception:
        # Conversion failed - clean up partial target, keep original
        with suppress(OSError):
            if target.exists():
                target.unlink()
        raise


def convert_video(media: MediaFile) -> None:
    """Convert video to H.264 MP4 format.

    Converts directly from source to target without creating backups.
    If conversion fails, the original file is preserved.
    """
    assert media.stage_path is not None
    source = media.stage_path
    target = next_available_name(source.parent, source.stem, ".mp4")

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
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
        # Conversion succeeded - delete original, use converted file
        source.unlink()
        media.stage_path = target
        media.extension = ".mp4"
        media.format_name = "mp4"
        media.video_codec = "h264"
        media.audio_codec = "aac" if media.audio_codec else None
        media.compatible = True
    except Exception:
        # Conversion failed - clean up partial target, keep original
        with suppress(OSError):
            if target.exists():
                target.unlink()
        raise


def convert_to_png(media: MediaFile) -> None:
    """Convert image to PNG format (lossless, widely supported).

    Uses fail-fast approach: no backups, no fallbacks.
    On success: original file is deleted and media.stage_path updated.
    On failure: partial target is cleaned up, original remains, exception propagates.
    """
    if media.stage_path is None:
        raise RuntimeError("Stage path missing for PNG conversion")
    source = media.stage_path
    target = next_available_name(source.parent, source.stem, ".png")

    # Use ffmpeg for conversion (handles more formats than ImageMagick)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
        "-pix_fmt",
        "rgba",
        str(target),
    ]
    try:
        run_command_with_progress(cmd, "Converting to PNG")
        copy_metadata_from_source(source, target)
        source.unlink()  # Delete original after successful conversion
        media.stage_path = target
        media.extension = ".png"
        media.format_name = "png"
        media.requires_processing = False
        media.compatible = True
    except Exception:
        # Clean up partial target, keep original
        with suppress(OSError):
            if target.exists():
                target.unlink()
        raise


def convert_to_tiff(media: MediaFile) -> None:
    """Convert image to TIFF format (lossless, 16-bit depth).

    Uses fail-fast approach: no backups, no fallbacks.
    On success: original file is deleted and media.stage_path updated.
    On failure: partial target is cleaned up, original remains, exception propagates.
    """
    if media.stage_path is None:
        raise RuntimeError("Stage path missing for TIFF conversion")
    source = media.stage_path
    target = next_available_name(source.parent, source.stem, ".tiff")

    # Use ImageMagick for conversion with 16-bit depth
    cmd = [
        resolve_imagemagick_command(),
        str(source),
        "-alpha",
        "on",
        "-depth",
        "16",
        "-flatten",
        str(target),
    ]
    try:
        run_command_with_progress(cmd, "Converting to TIFF")
        copy_metadata_from_source(source, target)
        source.unlink()  # Delete original after successful conversion
        media.stage_path = target
        media.extension = ".tiff"
        media.format_name = "tiff"
        media.requires_processing = False
        media.compatible = True
    except Exception:
        # Clean up partial target, keep original
        with suppress(OSError):
            if target.exists():
                target.unlink()
        raise


def convert_to_heic_lossless(media: MediaFile) -> None:
    """
    Convert media to lossless HEIC format using heif-enc or ffmpeg.

    Handles JPEG XL sources by first decoding to PNG via djxl, then encoding to HEIC.
    If djxl is unavailable for JXL input, falls back to TIFF conversion.

    Uses fail-fast approach: no backups, no fallbacks.
    On success: original file is deleted and media.stage_path updated.
    On failure: partial target and intermediate files are cleaned up, original remains, exception propagates.
    """
    if media.stage_path is None:
        raise RuntimeError("Stage path missing for HEIC conversion")
    source = media.stage_path
    target = next_available_name(source.parent, source.stem, ".heic")

    intermediate: Optional[Path] = None
    try:
        if source.suffix.lower() == ".jxl":
            djxl = find_executable("djxl")
            if not djxl:
                # djxl not available - fall back to TIFF conversion instead
                LOG.warning("djxl not available; falling back to TIFF conversion")
                convert_to_tiff(media)
                return
            # Decode JXL to intermediate PNG for HEIC encoding
            fd, tmp_path = tempfile.mkstemp(suffix=".png", prefix="smm_jxl_")
            os.close(fd)
            intermediate = Path(tmp_path)
            run_command_with_progress(
                [djxl, str(source), str(intermediate), "--lossless"],
                "Decoding JPEG XL",
            )
            source_for_heic = intermediate
        else:
            source_for_heic = source

        # Encode to HEIC using heif-enc or ffmpeg
        heif_enc = find_executable("heif-enc")
        if heif_enc and source_for_heic.suffix.lower() in {
            ".png",
            ".tif",
            ".tiff",
            ".jpg",
            ".jpeg",
            ".bmp",
        }:
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

        # Conversion succeeded - copy metadata, delete original, update media
        copy_metadata_from_source(source, target)
        source.unlink()
        media.stage_path = target
        media.extension = ".heic"
        media.format_name = "heic"
        media.requires_processing = False
        media.compatible = True
    except Exception:
        # Clean up partial target and intermediate files, keep original
        with suppress(OSError):
            if target.exists():
                target.unlink()
        raise
    finally:
        # Always clean up intermediate file if created
        if intermediate and intermediate.exists():
            with suppress(OSError):
                intermediate.unlink()


def convert_animation_to_hevc_mp4(media: MediaFile) -> None:
    """Convert animated media (GIF, APNG, etc.) to HEVC-encoded MP4 for Photos compatibility.

    Uses lossless HEVC encoding with 10-bit YUV444 color space to preserve visual quality.
    Removes audio tracks as Photos does not support audio in animated images.
    Converts in-place by overwriting the original stage file.
    Fails fast on any error - no backups, no rollbacks.

    Args:
        media: MediaFile object with stage_path set to the file to convert

    Raises:
        RuntimeError: If stage_path is None
        CalledProcessError: If ffmpeg conversion fails
    """
    if media.stage_path is None:
        raise RuntimeError("Stage path missing for animation conversion")
    original_stage = media.stage_path  # Source file to convert in-place
    target = next_available_name(original_stage.parent, original_stage.stem, ".mp4")  # Target extension is .mp4
    ffmpeg = ensure_ffmpeg_path()
    cmd = [
        ffmpeg,
        "-y",  # Overwrite output file
        "-i",
        str(original_stage),  # Use original stage directly as input
        "-vf",
        "scale=trunc(iw/2)*2:trunc(ih/2)*2",  # Ensure even dimensions for HEVC
        "-c:v",
        "libx265",  # HEVC video codec
        "-preset",
        "slow",  # Better compression at cost of encoding time
        "-x265-params",
        "lossless=1",  # Lossless encoding to preserve quality
        "-pix_fmt",
        "yuv444p10le",  # 10-bit color for animations
        "-an",  # Remove audio tracks
        str(target),
    ]
    run_command_with_progress(cmd, "Converting animation to HEVC")  # No try-except, fail fast
    original_stage.unlink()  # Delete original file after successful conversion
    media.stage_path = target  # Update to new converted file
    media.extension = ".mp4"  # Target extension
    media.format_name = "mp4"  # Format name for mp4 container
    media.video_codec = "hevc"
    media.audio_codec = None  # Audio removed
    media.kind = "video"
    media.requires_processing = False
    media.compatible = True


def rewrap_to_mp4(media: MediaFile) -> None:
    """Rewrap media file to MP4 container without re-encoding.

    Converts the container format to MP4 while copying all streams and metadata
    without transcoding. Uses faststart flag for web-optimized playback.
    Fails fast on any error - no backups, no rollbacks.

    Args:
        media: MediaFile instance with valid stage_path

    Raises:
        RuntimeError: If stage_path is missing
        subprocess.CalledProcessError: If ffmpeg command fails
    """
    if media.stage_path is None:
        raise RuntimeError("Stage path missing for rewrap")
    original_stage = media.stage_path
    target = next_available_name(original_stage.parent, original_stage.stem, ".mp4")
    ffmpeg = ensure_ffmpeg_path()
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(original_stage),
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
    run_command_with_progress(cmd, "Rewrapping container")
    original_stage.unlink()  # Delete original after successful rewrap
    media.stage_path = target
    media.extension = ".mp4"
    media.format_name = "mp4"
    media.requires_processing = False
    media.compatible = True


def transcode_to_hevc_mp4(media: MediaFile, copy_audio: bool = False) -> None:
    """Transcode video to HEVC (H.265) in MP4 container with optional audio handling.

    Converts the staged media file to HEVC video codec with lossless encoding parameters.
    Audio can either be copied from source or re-encoded to AAC 256k.
    Updates the media object with new format metadata and marks it as compatible.

    Uses fail-fast approach: no backups, no fallbacks.
    On success: original file is deleted and media.stage_path updated to target.
    On failure: partial target is cleaned up, original remains, exception propagates.

    Args:
        media: MediaFile object with valid stage_path to be transcoded
        copy_audio: If True, copy audio stream as-is; if False, transcode to AAC 256k

    Raises:
        RuntimeError: If media.stage_path is None
        Exception: If ffmpeg transcoding fails (failure propagates after cleanup)
    """
    if media.stage_path is None:
        raise RuntimeError("Stage path missing for transcode")
    source = media.stage_path
    target = next_available_name(source.parent, source.stem, ".mp4")
    ffmpeg = ensure_ffmpeg_path()
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(source),
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
        # Transcoding succeeded - delete original, use transcoded file
        source.unlink()
        media.stage_path = target
        media.extension = ".mp4"
        media.format_name = "mp4"
        media.video_codec = "hevc"
        media.audio_codec = media.audio_codec if copy_audio else "aac"
        media.requires_processing = False
        media.compatible = True
    except Exception:
        # Transcoding failed - clean up partial target, keep original
        with suppress(OSError):
            if target.exists():
                target.unlink()
        raise


def transcode_audio_to_supported(media: MediaFile) -> None:
    """Transcode audio to supported codec (AAC or EAC3) in MP4 container.

    Converts directly from source to target without creating backups.
    If conversion fails, the original file is preserved.
    Uses EAC3 for 5.1/7.1 surround sound, AAC for stereo/mono.
    """
    assert media.stage_path is not None
    source = media.stage_path
    target = next_available_name(source.parent, source.stem, ".mp4")
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
            str(source),
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
        # Conversion succeeded - delete original, use converted file
        source.unlink()
        media.stage_path = target
        media.extension = ".mp4"
        media.format_name = "mp4"
        media.audio_codec = audio_codec
        media.requires_processing = False
        media.compatible = True
    except Exception:
        # Conversion failed - clean up partial target, keep original
        with suppress(OSError):
            if target.exists():
                target.unlink()
        raise


def rewrap_or_transcode_to_mp4(media: MediaFile) -> None:
    """Rewrap video to MP4 container, transcode to HEVC on failure.

    Uses fail-fast approach: no backups, no fallbacks.
    First attempts fast rewrap (copy streams), if that fails tries transcode.
    On success: original file is deleted and media.stage_path updated.
    On failure: partial target is cleaned up, original remains, exception propagates.
    """
    if media.stage_path is None:
        raise RuntimeError("Stage path missing for rewrap/transcode")
    source = media.stage_path
    target = next_available_name(source.parent, source.stem, ".mp4")
    ffmpeg = ensure_ffmpeg_path()

    # First attempt: fast rewrap (copy all streams)
    rewrap_cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(source),
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
        run_command_with_progress(rewrap_cmd, "Rewrapping to MP4")
        source.unlink()  # Delete original after successful rewrap
        media.stage_path = target
        media.extension = ".mp4"
        media.format_name = "mp4"
        media.requires_processing = False
        media.compatible = True
        return
    except Exception:
        # Rewrap failed, clean up and try transcode
        with suppress(OSError):
            if target.exists():
                target.unlink()

    # Second attempt: transcode to HEVC
    target = next_available_name(source.parent, source.stem, ".mp4")
    transcode_cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(source),
        "-c:v",
        "libx265",
        "-preset",
        "medium",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        str(target),
    ]

    try:
        run_command_with_progress(transcode_cmd, "Transcoding to HEVC MP4")
        source.unlink()  # Delete original after successful transcode
        media.stage_path = target
        media.extension = ".mp4"
        media.format_name = "mp4"
        media.requires_processing = False
        media.compatible = True
    except Exception:
        # Clean up partial target, keep original
        with suppress(OSError):
            if target.exists():
                target.unlink()
        raise


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
            if media.stage_path and media.stage_path.exists():
                if media.metadata.get("copy_mode"):
                    media.stage_path.unlink(missing_ok=True)
                    media.stage_path = None
                    continue
                restore_path = resolve_restore_path(original)
                restore_path.parent.mkdir(parents=True, exist_ok=True)
                media.stage_path.rename(restore_path)
                media.stage_path = None
        except Exception as exc:  # noqa: BLE001
            LOG.warning("Failed to restore %s: %s", original, exc)
    if staging and staging.exists():
        shutil.rmtree(staging, ignore_errors=True)


def ensure_compatibility(
    media_files: list[MediaFile],
    skip_logger: SkipLogger,
    stats: RunStatistics,
    skip_convert: bool = False,
) -> None:
    retained: list[MediaFile] = []
    progress = ProgressReporter(len(media_files), "Ensuring compatibility")

    def is_already_photos_compatible(media: MediaFile) -> bool:
        if media.kind == "image":
            return media.extension.lower() in COMPATIBLE_IMAGE_EXTENSIONS
        if media.kind == "video":
            container = (media.metadata.get("container") or media.format_name or "").lower()
            video_codec = (media.video_codec or "").lower()
            audio_codec = (media.audio_codec or "").lower()
            return container in COMPATIBLE_VIDEO_CONTAINERS and video_codec in COMPATIBLE_VIDEO_CODECS and (not audio_codec or audio_codec in COMPATIBLE_AUDIO_CODECS)
        return False

    for media in media_files:
        if media.stage_path is None or not media.stage_path.exists():
            skip_logger.log(media.source, "staged file missing before processing")
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

        # Skip all conversions if flag is set (for format testing)
        if skip_convert:
            # Mark as compatible and treat as import-ready
            media.requires_processing = False
            media.compatible = True
            retained.append(media)
            progress.update()
            continue

        try:
            # Do not process files the detector already marked as compatible
            if media.detected_compatible and media.action != "import":
                LOG.debug("Bypassing processing for compatible media %s (action %s)", media.stage_path, media.action)
                media.requires_processing = False
                media.compatible = True
                media.action = "import"
                retained.append(media)
                progress.update()
                continue

            # Extra guard: heuristically skip conversion if container/codec are Photos-compatible
            if is_already_photos_compatible(media):
                media.requires_processing = False
                media.compatible = True
                media.action = "import"
                retained.append(media)
                progress.update()
                continue

            if media.action == "import":
                media.requires_processing = False
                media.compatible = True
            elif media.action == "convert_to_png":
                LOG.debug("Converting %s to PNG: %s", media.format_name, media.stage_path)
                stats.conversion_attempted += 1
                convert_to_png(media)
                stats.conversion_succeeded += 1
                media.was_converted = True
                LOG.debug("Successfully converted to PNG: %s", media.stage_path)
            elif media.action == "convert_to_tiff":
                LOG.debug("Converting %s to TIFF: %s", media.format_name, media.stage_path)
                stats.conversion_attempted += 1
                convert_to_tiff(media)
                stats.conversion_succeeded += 1
                media.was_converted = True
                LOG.debug("Successfully converted to TIFF: %s", media.stage_path)
            elif media.action == "convert_to_heic_lossless":
                LOG.debug("Converting %s to lossless HEIC: %s", media.format_name, media.stage_path)
                stats.conversion_attempted += 1
                convert_to_heic_lossless(media)
                stats.conversion_succeeded += 1
                media.was_converted = True
                LOG.debug("Successfully converted to HEIC: %s", media.stage_path)
            elif media.action == "convert_animation_to_hevc_mp4":
                LOG.debug("Converting animated %s to HEVC MP4: %s", media.format_name, media.stage_path)
                stats.conversion_attempted += 1
                convert_animation_to_hevc_mp4(media)
                stats.conversion_succeeded += 1
                media.was_converted = True
                LOG.debug("Successfully converted animation to HEVC MP4: %s", media.stage_path)
            elif media.action == "rewrap_to_mp4":
                LOG.debug("Rewrapping %s (%s/%s) to MP4 container: %s", media.format_name, media.video_codec or "unknown", media.audio_codec or "unknown", media.stage_path)
                stats.conversion_attempted += 1
                rewrap_to_mp4(media)
                stats.conversion_succeeded += 1
                media.was_converted = True
                LOG.debug("Successfully rewrapped to MP4: %s", media.stage_path)
            elif media.action == "transcode_to_hevc_mp4":
                LOG.debug("Transcoding %s (%s/%s) to HEVC MP4: %s", media.format_name, media.video_codec or "unknown", media.audio_codec or "unknown", media.stage_path)
                stats.conversion_attempted += 1
                transcode_to_hevc_mp4(media, copy_audio=False)
                stats.conversion_succeeded += 1
                media.was_converted = True
                LOG.debug("Successfully transcoded to HEVC MP4: %s", media.stage_path)
            elif media.action == "transcode_video_to_lossless_hevc":
                LOG.debug("Transcoding %s (%s/%s) to lossless HEVC MP4: %s", media.format_name, media.video_codec or "unknown", media.audio_codec or "unknown", media.stage_path)
                stats.conversion_attempted += 1
                transcode_to_hevc_mp4(media, copy_audio=True)
                stats.conversion_succeeded += 1
                media.was_converted = True
                LOG.debug("Successfully transcoded to lossless HEVC MP4: %s", media.stage_path)
            elif media.action == "transcode_audio_to_aac_or_eac3":
                LOG.debug("Transcoding audio in %s (%s) to AAC/EAC-3: %s", media.format_name, media.audio_codec or "unknown", media.stage_path)
                stats.conversion_attempted += 1
                transcode_audio_to_supported(media)
                stats.conversion_succeeded += 1
                media.was_converted = True
                LOG.debug("Successfully transcoded audio: %s", media.stage_path)
            elif media.action == "rewrap_or_transcode_to_mp4":
                LOG.debug("Rewrapping/transcoding %s (%s/%s) to MP4: %s", media.format_name, media.video_codec or "unknown", media.audio_codec or "unknown", media.stage_path)
                stats.conversion_attempted += 1
                rewrap_or_transcode_to_mp4(media)
                stats.conversion_succeeded += 1
                media.was_converted = True
                LOG.debug("Successfully converted to MP4: %s", media.stage_path)
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


def update_stats_after_compatibility(stats: RunStatistics, media_files: list[MediaFile]) -> None:
    stats.total_media_detected = len(media_files)
    detected_compatible = sum(1 for media in media_files if media.detected_compatible)
    stats.media_compatible = detected_compatible
    stats.media_incompatible = stats.total_media_detected - detected_compatible
    stats.incompatible_with_conversion_rule = sum(1 for media in media_files if not media.detected_compatible and media.was_converted)
    stats.staging_total = sum(1 for media in media_files if media.stage_path and media.stage_path.exists())
    stats.staging_expected = detected_compatible + stats.incompatible_with_conversion_rule


def run_checked(cmd: list[str]) -> None:
    LOG.debug("Executing command: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        LOG.error("Command failed: %s", result.stderr.strip())
        raise RuntimeError(f"Command '{cmd[0]}' failed with exit code {result.returncode}.")


def import_folder_to_photos(
    staging_dir: Path,
    media_files: list[MediaFile],
    album_name: str,
    skip_duplicates: bool = True,
) -> tuple[int, int, list[MediaFile]]:
    """Import entire staging folder in a single Photos.app call.

    Uses Photos' native folder import which handles queue management natively.
    Returns imported filenames and reconciles against staged files to determine
    which files were imported vs skipped.

    This eliminates ALL timing dependencies and batch management complexity.
    Photos.app manages its own import queue, preventing resource exhaustion.

    Args:
        staging_dir: Path to staging folder containing all media files
        media_files: List of MediaFile objects with stage_path set
        album_name: Photos album name to import into
        skip_duplicates: If True, skip duplicate checking (default: True)

    Returns:
        Tuple of (imported_count, skipped_count, skipped_media_files)

    Raises:
        RuntimeError: If Photos.app import fails with error
    """
    # DEBUG: Timestamp when function execution begins
    function_start_timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    LOG.debug("✅ TIMESTAMP %s - import_folder_to_photos function EXECUTION STARTED", function_start_timestamp)

    staged_media = [media for media in media_files if media.stage_path and media.stage_path.exists()]
    if not staged_media:
        return 0, 0, []

    # Build AppleScript for folder import (based on import2photos.sh)
    # Uses 24-hour timeout to prevent AppleEvent timeout (-1712) when Photos shows dialogs
    applescript = """
on run argv
    if (count of argv) < 3 then return "ERR\\t0\\tMissing arguments"
    set albumName to item 1 of argv
    set skipDup to ((item 2 of argv) is "true")
    set dirPath to item 3 of argv

    script util
        on sanitizeText(srcText)
            set oldTIDs to AppleScript's text item delimiters
            set AppleScript's text item delimiters to {return, linefeed, tab}
            set parts to text items of srcText
            set AppleScript's text item delimiters to " "
            set out to parts as text
            set AppleScript's text item delimiters to oldTIDs
            return out
        end sanitizeText
    end script

    try
        set folderAlias to POSIX file (dirPath as text)
    on error errMsg number errNum
        return "ERR\\t" & (errNum as text) & "\\t" & errMsg
    end try

    set outLines to {}
    tell application id "com.apple.Photos"
        activate
        -- Use very long timeout (24 hours) to allow user interaction with Photos dialogs
        with timeout of 86400 seconds
            try
                if (count of (albums whose name is albumName)) = 0 then
                    make new album named albumName
                end if
                set tgtAlbum to first album whose name is albumName

                -- SINGLE folder import call - Photos manages the queue natively
                set importedItems to import folderAlias skip check duplicates skipDup

                if (count of importedItems) > 0 then
                    add importedItems to tgtAlbum
                end if

                -- Return filenames of imported items for reconciliation
                repeat with mi in importedItems
                    try
                        set fn to filename of mi
                        set fn2 to util's sanitizeText(fn)
                        set end of outLines to "FN\\t" & fn2
                    end try
                end repeat
            on error errMsg number errNum
                return "ERR\\t" & (errNum as text) & "\\t" & errMsg
            end try
        end timeout
    end tell

    set oldTIDs to AppleScript's text item delimiters
    set AppleScript's text item delimiters to linefeed
    set outText to outLines as text
    set AppleScript's text item delimiters to oldTIDs
    return outText
end run
"""

    # Execute AppleScript with folder import - with retry logic for Photos dialogs
    LOG.info("Importing staging folder into Photos album '%s'...", album_name)

    def run_import_applescript() -> subprocess.CompletedProcess:
        """Execute the import AppleScript. No timeout - AppleScript has its own 24h timeout."""
        return subprocess.run(
            ["osascript", "-", album_name, str(skip_duplicates).lower(), str(staging_dir)],
            input=applescript,
            capture_output=True,
            text=True,
            check=False,
        )

    # Retry loop for AppleEvent timeout (-1712) when Photos shows dialogs
    max_retries = 10
    for attempt in range(max_retries):
        # DEBUG: Timestamp when AppleScript execution begins
        applescript_start_timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        LOG.debug("📸 TIMESTAMP %s - About to execute AppleScript (osascript) to import folder to Photos.app (attempt %d/%d)", applescript_start_timestamp, attempt + 1, max_retries)

        result = run_import_applescript()

        # DEBUG: Timestamp when AppleScript execution completes
        applescript_end_timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        LOG.debug("📸 TIMESTAMP %s - AppleScript execution COMPLETED", applescript_end_timestamp)

        output = result.stdout.strip()

        if LOG.isEnabledFor(logging.DEBUG):
            debug_parent = _log_directory() or staging_dir.parent
            timestamp_segment = dt.datetime.now().strftime("%Y%m%d%H%M%S")
            debug_parent.mkdir(parents=True, exist_ok=True)
            raw_output_file = debug_parent / f"DEBUG_raw_applescript_output_{timestamp_segment}.txt"
            with raw_output_file.open("wb") as handle:
                handle.write(result.stdout.encode("utf-8"))
            LOG.debug("DEBUG: Raw AppleScript output saved to %s (%d bytes)", raw_output_file, len(result.stdout))

        # Check for AppleEvent timeout error (-1712) - Photos was showing a dialog
        if output.startswith("ERR\t"):
            parts = output.split("\t")
            err_code = parts[1] if len(parts) > 1 else "0"
            err_msg = parts[2] if len(parts) > 2 else "Unknown error"

            # Error -1712 is "AppleEvent timed out" - Photos was waiting for user interaction
            if err_code == "-1712":
                print("\n⚠️  Apple Photos is waiting for user interaction (dialog open)")
                print("   Please close any Photos dialogs and press Enter to retry...")
                print("   Or type 'abort' to cancel the import.")
                try:
                    user_input = input(f"   [Attempt {attempt + 1}/{max_retries}] Press Enter to retry or 'abort' to cancel: ").strip().lower()
                    if user_input == "abort":
                        raise RuntimeError(f"Photos import aborted by user after AppleEvent timeout [{err_code}]: {err_msg}")
                    LOG.info("Retrying Photos import after user closed dialog...")
                    continue  # Retry the import
                except (KeyboardInterrupt, EOFError):
                    raise RuntimeError(f"Photos import cancelled by user [{err_code}]: {err_msg}")

            # Other errors are fatal
            raise RuntimeError(f"Photos import failed [{err_code}]: {err_msg}")

        # Success - no error, break out of retry loop
        break
    else:
        # Exhausted all retries
        raise RuntimeError(f"Photos import failed after {max_retries} attempts due to repeated AppleEvent timeouts")

    # Parse imported filenames from AppleScript output
    # Format: "FN\t<filename>" per line
    imported_names = []
    line_count = 0
    for line in output.split("\n"):
        line_count += 1
        line = line.strip()
        if line.startswith("FN\t"):
            filename = line[3:]  # Remove "FN\t" prefix
            imported_names.append(filename)

    LOG.debug(f"DEBUG: Parsed {len(imported_names)} filenames from {line_count} total lines")

    LOG.debug("Photos returned %d imported filenames", len(imported_names))

    if LOG.isEnabledFor(logging.DEBUG):
        debug_parent = _log_directory() or staging_dir.parent
        timestamp_segment = dt.datetime.now().strftime("%Y%m%d%H%M%S")
        debug_parent.mkdir(parents=True, exist_ok=True)
        photos_output_file = debug_parent / f"DEBUG_photos_output_{timestamp_segment}.txt"
        with photos_output_file.open("w", encoding="utf-8") as handle:
            handle.write("FILENAMES RETURNED BY PHOTOS.APP:\n")
            handle.write("=" * 80 + "\n")
            for name in sorted(imported_names):
                handle.write(f"{name}\n")
        LOG.debug("DEBUG: Photos output saved to %s", photos_output_file)

    # DEBUG: Log first 5 filenames returned by Photos
    LOG.debug("DEBUG: First 5 filenames returned by Photos:")
    for i, name in enumerate(imported_names[:5]):
        LOG.debug(f"  [{i}] {repr(name)}")

    photos_imported_count = len(imported_names)
    staged_count = len(staged_media)

    LOG.debug("Reconciliation: Photos returned %d items, staged %d files", photos_imported_count, staged_count)

    token_to_media: dict[str, MediaFile] = {}
    for media in staged_media:
        token_value = media.metadata.get("staging_token")
        if token_value:
            token_to_media[token_value] = media

    imported_media: list[MediaFile] = []
    skipped_media: list[MediaFile] = []
    matched_media_ids: set[int] = set()
    unmatched_names: list[str] = []

    for name in imported_names:
        tokens = [match.group(1) for match in STAGING_TOKEN_PATTERN.finditer(name)]
        assigned = False
        for token_value in tokens:
            media = token_to_media.get(token_value)
            if media and id(media) not in matched_media_ids:
                token_to_media.pop(token_value, None)
                matched_media_ids.add(id(media))
                media.metadata["photos_returned_name"] = name
                imported_media.append(media)
                assigned = True
                break
        if not assigned:
            unmatched_names.append(name)

    remaining_media = [media for media in staged_media if id(media) not in matched_media_ids]
    imported_counter: Counter[str] = Counter(unmatched_names)

    def consume_exact(name: str) -> Optional[str]:
        if imported_counter.get(name, 0) > 0:
            imported_counter[name] -= 1
            if imported_counter[name] == 0:
                del imported_counter[name]
            return name
        return None

    def consume_casefold(name: str) -> Optional[str]:
        lowered = name.casefold()
        for candidate in list(imported_counter.keys()):
            if imported_counter[candidate] > 0 and candidate.casefold() == lowered:
                imported_counter[candidate] -= 1
                if imported_counter[candidate] == 0:
                    del imported_counter[candidate]
                return candidate
        return None

    def consume_name(name: str) -> Optional[str]:
        return consume_exact(name) or consume_casefold(name)

    name_suffix_pattern = re.compile(r"^(.*)[ _]?\([0-9-]+\)(\.[^.]+)$")

    def strip_staging_suffix(name: str) -> Optional[str]:
        match = name_suffix_pattern.match(name)
        if match:
            return f"{match.group(1)}{match.group(2)}"
        return None

    for media in remaining_media:
        stage_path = media.stage_path
        if stage_path is None:
            skipped_media.append(media)
            continue
        stage_name = stage_path.name
        candidates = [stage_name]
        staging_stem = media.metadata.get("staging_stem")
        if staging_stem:
            base_candidate = f"{staging_stem}{media.extension}" if media.extension else staging_stem
            if base_candidate not in candidates:
                candidates.append(base_candidate)
        tokenized_stem = media.metadata.get("staging_tokenized_stem")
        if tokenized_stem:
            token_base = f"{tokenized_stem}{media.extension}" if media.extension else tokenized_stem
            if token_base not in candidates:
                candidates.append(token_base)
            if tokenized_stem.endswith("__"):
                single_variant = tokenized_stem[:-1]
                token_base_single = f"{single_variant}{media.extension}" if media.extension else single_variant
                if token_base_single not in candidates:
                    candidates.append(token_base_single)
                single_stage = stage_name.replace(tokenized_stem, single_variant)
                if single_stage not in candidates:
                    candidates.append(single_stage)
        trimmed_candidate = strip_staging_suffix(stage_name)
        if trimmed_candidate and trimmed_candidate not in candidates:
            candidates.append(trimmed_candidate)

        matched_name = None
        for candidate in candidates:
            matched_name = consume_name(candidate)
            if matched_name:
                break

        if matched_name:
            media.metadata["photos_returned_name"] = matched_name
            imported_media.append(media)
            matched_media_ids.add(id(media))
        else:
            skipped_media.append(media)

    leftover_imported = list(imported_counter.elements())

    if leftover_imported:
        LOG.warning(
            "Photos returned %d filename(s) that did not match staged files; first entries: %s",
            len(leftover_imported),
            leftover_imported[:5],
        )

    if skipped_media:
        LOG.warning("Photos did not report %d staged file(s); treating them as skipped.", len(skipped_media))
        rejection_parent = _log_directory() or staging_dir.parent
        rejection_parent.mkdir(parents=True, exist_ok=True)
        rejection_path = rejection_parent / f"Photos_rejections_{dt.datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        with rejection_path.open("w", encoding="utf-8") as handle:
            handle.write("FILES REJECTED OR MISSING FROM PHOTOS IMPORT\n")
            handle.write("=" * 80 + "\n")
            for media in skipped_media:
                stage_name = media.stage_path.name if media.stage_path else "<missing>"
                original_source = media.metadata.get("original_source") or str(media.source)
                handle.write(f"Staged: {stage_name}\tOriginal: {original_source}\n")
            if leftover_imported:
                handle.write("\nFILENAMES RETURNED BY PHOTOS WITH NO MATCH\n")
                handle.write("=" * 80 + "\n")
                for name in leftover_imported:
                    handle.write(f"{name}\n")
        LOG.info("Photos rejection details written to %s", rejection_path)
    else:
        LOG.info("All %d staged file(s) reported by Photos.", len(imported_media))

    imported_count = len(imported_media)
    skipped_count = len(skipped_media)

    LOG.info(
        "Folder import complete: %d imported, %d skipped (duplicates or rejected by Photos)",
        imported_count,
        skipped_count,
    )

    return imported_count, skipped_count, skipped_media


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


def confirm_scan(root: Path, output_dir: Path, assume_yes: bool) -> bool:
    """Ask user confirmation before scanning and staging.

    Args:
        root: directory or file being scanned
        output_dir: directory where staging/logs will be written
        assume_yes: skip prompt when True
    """

    if assume_yes:
        return True

    print("\nAbout to scan and import media with Smart Media Manager")
    print(f"  Scan root: {root}")
    print(f"  Logs/staging will be created under: {output_dir}")
    print("Press Enter to continue or 'n' to abort.")

    try:
        response = input("Proceed? [Y/n]: ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\nAborted by user.")
        return False

    if response in ("", "y", "yes"):  # default yes
        return True
    print("Aborted by user.")
    return False


def cleanup_staging(staging: Path) -> None:
    if staging.exists():
        LOG.debug("Deleting staging folder %s", staging)
        shutil.rmtree(staging)


def configure_logging() -> None:
    LOG.setLevel(logging.INFO)
    LOG.handlers.clear()
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    console.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    LOG.addHandler(console)


def attach_file_logger(root: Path, run_ts: str) -> Path:
    """Create timestamped log directory in CWD and attach file logger.

    Args:
        root: Scan root directory (not used for log location, kept for compatibility)
        run_ts: Timestamp string for this run

    Returns:
        Path to created log file

    Note:
        Log directory is created in current working directory (not scan root)
        with pattern: .smm__runtime_logs_YYYYMMDD_HHMMSS_<uuid>
        This prevents logs from being scanned as media files.
    """
    global _FILE_LOG_HANDLER
    if _FILE_LOG_HANDLER is not None:
        return Path(_FILE_LOG_HANDLER.baseFilename)  # type: ignore[attr-defined]

    # Create unique timestamped log directory in CWD (not scan root)
    # Format: .smm__runtime_logs_YYYYMMDD_HHMMSS_<short-uuid>
    short_uuid = str(uuid.uuid4())[:8]  # First 8 chars of UUID for uniqueness
    log_dir_name = f"{SMM_LOGS_SUBDIR}{run_ts}_{short_uuid}"
    log_dir = Path.cwd() / log_dir_name
    log_dir.mkdir(parents=True, exist_ok=True)

    # Log file inside the timestamped directory
    path = log_dir / f"smm_run_{run_ts}.log"
    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    LOG.addHandler(handler)
    _FILE_LOG_HANDLER = handler
    return path


def validate_root(path: Path, allow_file: bool = False) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.exists():
        raise RuntimeError(f"Path does not exist: {resolved}")
    if not resolved.is_dir() and not (allow_file and resolved.is_file()):
        raise RuntimeError(f"Path must be a {'file or ' if allow_file else ''}directory: {resolved}")
    return resolved


def main() -> int:
    configure_logging()
    args = parse_args()
    LOG.info("smart-media-manager %s", __version__)
    skip_bootstrap = args.skip_bootstrap or bool(os.environ.get("SMART_MEDIA_MANAGER_SKIP_BOOTSTRAP"))
    if skip_bootstrap:
        LOG.debug("Skipping dependency bootstrap (manual mode).")
    else:
        ensure_system_dependencies()
    media_files: list[MediaFile] = []
    staging_root: Optional[Path] = None
    skip_log: Optional[Path] = None
    skip_logger: Optional[SkipLogger] = None
    stats = RunStatistics()
    try:
        # Auto-detect if path is a file or directory
        is_single_file = args.path.is_file()

        # Warn if --recursive is used with a single file (it will be ignored)
        if is_single_file and args.recursive:
            LOG.warning("--recursive flag ignored when processing a single file")
            print("Warning: --recursive flag ignored when processing a single file")

        root = validate_root(args.path, allow_file=is_single_file)
        run_ts = timestamp()

        # For single file mode, use parent directory for outputs; otherwise use scan root
        output_dir = root.parent if is_single_file else root

        if not confirm_scan(root, output_dir, args.assume_yes):
            return 0

        # Check write permissions for both CWD (logs) and output_dir (skip logs, staging)
        try:
            check_write_permission(Path.cwd(), "create logs")
        except (PermissionError, OSError) as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1

        try:
            check_write_permission(output_dir, "create skip logs and staging directory")
        except (PermissionError, OSError) as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1

        log_path = attach_file_logger(root, run_ts)  # root arg kept for compatibility, not used for log location
        configure_pillow_max_image_pixels(args.max_image_pixels)

        for dependency in ("ffprobe", "ffmpeg", "osascript"):
            ensure_dependency(dependency)
        LOG.info("Scanning %s for media files...", root)
        print(f"Scanning {root}...")

        # Skip log goes in output directory (scan root or parent of single file)
        skip_log = output_dir / f"smm_skipped_files_{run_ts}.log"
        if skip_log.exists():
            skip_log.unlink()
        skip_logger = SkipLogger(skip_log)

        # Handle single file mode
        if is_single_file:
            media, reject_reason = detect_media(root, args.skip_compatibility_check)
            if media:
                media_files = [media]
                stats.total_files_scanned = 1
                stats.total_binary_files = 1
                stats.total_media_detected = 1
                if media.compatible:
                    stats.media_compatible = 1
                else:
                    stats.media_incompatible = 1
            elif reject_reason:
                skip_logger.log(root, reject_reason)
                LOG.debug("File rejected: %s", reject_reason)
                return 0
            else:
                LOG.debug("File is not a supported media format.")
                return 0
        else:
            media_files = gather_media_files(
                root,
                args.recursive,
                args.follow_symlinks,
                skip_logger,
                stats,
                args.skip_compatibility_check,
            )
        if not media_files:
            LOG.warning("No media files detected.")
            if skip_logger and not skip_logger.has_entries() and skip_log.exists():
                skip_log.unlink()
            return 0
        ensure_raw_dependencies_for_files(media_files)

        # Create staging directory in output directory (scan root or parent of single file)
        staging_root = output_dir / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_root.mkdir(parents=True, exist_ok=False)

        # Create originals directory OUTSIDE staging folder (sibling directory)
        # CRITICAL: Must NOT be inside staging_root or Photos will try to import incompatible original files!
        originals_root = output_dir / f"ORIGINALS_{run_ts}"

        move_to_staging(media_files, staging_root, originals_root, copy_files=args.copy_mode)
        ensure_compatibility(media_files, skip_logger, stats, args.skip_convert)
        # No sanitization needed - sequential suffix already ensures uniqueness
        update_stats_after_compatibility(stats, media_files)

        missing_media: list[MediaFile] = [media for media in media_files if not media.stage_path or not media.stage_path.exists()]

        if missing_media:
            missing_listing = ", ".join(str((m.stage_path or m.source)) for m in missing_media[:5])
            raise RuntimeError(f"Missing staged file(s): {missing_listing}")

        staged_count = len(media_files)
        LOG.info("Preparing to import %d staged file(s) into Apple Photos", staged_count)
        print(f"\nStaging completed: {staged_count} file(s) ready for Photos import.")

        update_stats_after_compatibility(stats, media_files)
        stats.log_summary()
        stats.print_summary()

        LOG.info("Importing %d file(s) into Apple Photos via folder import...", staged_count)
        print(f"Importing {staged_count} file(s) into Apple Photos...")

        # DEBUG: Timestamp when folder import is about to be called
        current_timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        LOG.debug("🚨 TIMESTAMP %s - The function 'import_folder_to_photos' was called now. No imports should have been attempted before this time!", current_timestamp)
        print(f"🚨 TIMESTAMP {current_timestamp} - Calling import_folder_to_photos NOW")

        # Single folder import replaces batch import - no timing dependencies
        # By default, Photos will check for duplicates and prompt the user
        imported_count, skipped_count, skipped_media = import_folder_to_photos(
            staging_dir=staging_root,
            media_files=media_files,
            album_name=args.album,
            skip_duplicates=args.skip_duplicate_check,
        )

        # Log skipped files (duplicates or rejected by Photos)
        if skipped_media:
            for media in skipped_media:
                log_target = media.stage_path or media.metadata.get("original_source") or media.source
                skip_logger.log(Path(log_target), "Skipped by Photos (duplicate or incompatible format)")
            LOG.warning("%d file(s) skipped by Photos (see skip log)", skipped_count)

        # Update statistics
        stats.total_imported = imported_count
        for media in media_files:
            if media not in skipped_media:
                if media.was_converted:
                    stats.imported_after_conversion += 1
                else:
                    stats.imported_without_conversion += 1

        # Print statistics summary
        stats.print_summary()
        stats.log_summary()

        LOG.info(
            "Successfully imported %d media file(s) into Apple Photos.",
            imported_count,
        )
        if args.delete:
            cleanup_staging(staging_root)
        else:
            LOG.debug("Staging folder retained at %s", staging_root)
        if skip_log and skip_log.exists():
            if skip_logger and skip_logger.has_entries():
                LOG.info("Skipped file log saved at %s", skip_log)
            else:
                skip_log.unlink()
        print(f"\nDetailed log: {log_path}")
        return 0
    except KeyboardInterrupt:
        # Graceful handling of Ctrl+C - save logs and exit cleanly
        LOG.warning("Operation interrupted by user (Ctrl+C)")
        print("\n\n" + "=" * 60)
        print("INTERRUPTED: Operation cancelled by user (Ctrl+C)")
        print("=" * 60)
        # Save skip log if it has entries
        if skip_log and skip_log.exists():
            if skip_logger and skip_logger.has_entries():
                LOG.info("Skipped file log saved at %s", skip_log)
                print(f"Skip log saved: {skip_log}")
            else:
                skip_log.unlink()
        # Point to detailed log
        if "log_path" in locals():
            LOG.info("Detailed log saved at %s", log_path)
            print(f"Detailed log: {log_path}")
        # Preserve staging folder for potential resume - don't revert
        if staging_root and staging_root.exists():
            print(f"Staging folder preserved: {staging_root}")
            print("(Files can be manually imported or removed)")
        print("=" * 60)
        return 130  # Standard exit code for Ctrl+C (128 + SIGINT=2)
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
    finally:
        if UNKNOWN_MAPPINGS.has_entries():
            updates_path = UNKNOWN_MAPPINGS.write_updates(Path.cwd())
            if updates_path:
                print(f"Unknown format mappings saved to {updates_path}")


def run() -> None:
    sys.exit(main())


class ProgressReporter:
    def __init__(self, total: int, label: str) -> None:
        self.total = max(total, 0)
        self.label = label
        self.start = time.time()
        self.completed = 0
        self.last_render = 0.0
        self.dynamic = self.total == 0

    def update(self, step: int = 1, force: bool = False) -> None:
        self.completed += step
        now = time.time()
        if not force and now - self.last_render < 0.1 and (not self.dynamic and self.completed < self.total):
            return
        self.last_render = now
        if self.dynamic:
            sys.stdout.write(f"\r{self.label}: processed {self.completed}")
        else:
            percent = min(self.completed / self.total if self.total else 1.0, 1.0)
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
        if not self.dynamic:
            self.completed = self.total
        self.update(step=0, force=True)
        sys.stdout.write("\n")
        sys.stdout.flush()
