from __future__ import annotations

import argparse
import datetime as dt
import logging
import os
import re
import shutil
import subprocess
import sys
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import json

import filetype
import puremagic


LOG = logging.getLogger("smart_media_manager")

SAFE_NAME_PATTERN = re.compile(r"[^A-Za-z0-9_.-]")
MAX_APPLESCRIPT_ARGS = 50
MAX_APPLESCRIPT_CHARS = 20000

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
COMPATIBLE_VIDEO_CODECS = {"h264", "hevc"}
COMPATIBLE_AUDIO_CODECS = {"aac", "mp3", "alac", "pcm_s16le", "pcm_s24le"}

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
    original_suffix: str = ""
    backup_path: Optional[Path] = None


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


def timestamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d%H%M%S")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan and import media into Apple Photos, fixing extensions and compatibility."
    )
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

    return None


def detect_media(path: Path) -> Optional[MediaFile]:
    signatures = [safe_filetype_guess(path), safe_puremagic_guess(path)]

    if any(is_archive_signature(sig) for sig in signatures):
        return None

    image_hint = any(is_image_signature(sig) for sig in signatures)
    video_hint = any(is_video_signature(sig) for sig in signatures)

    if image_hint:
        extension = choose_image_extension(signatures)
        if extension:
            compatible = extension in COMPATIBLE_IMAGE_EXTENSIONS
            format_name = extension.lstrip(".")
            return MediaFile(
                source=path,
                kind="image",
                extension=extension,
                format_name=format_name,
                compatible=compatible,
                original_suffix=path.suffix,
            )

    probe = ffprobe(path)
    if not probe:
        if video_hint:
            extension = choose_video_extension(signatures) or ".mp4"
            return MediaFile(
                source=path,
                kind="video",
                extension=extension,
                format_name="unknown",
                compatible=False,
                original_suffix=path.suffix,
            )
        return None

    streams = probe.get("streams", [])
    format_info = probe.get("format", {})
    format_name = format_info.get("format_name", "").lower()
    if not format_name:
        return None

    kind = None
    video_codec = None
    audio_codec = None
    for stream in streams:
        codec_type = stream.get("codec_type")
        if codec_type == "video":
            kind = "video"
            video_codec = stream.get("codec_name")
        elif codec_type == "image":
            kind = "image"
            video_codec = stream.get("codec_name")
        elif codec_type == "audio" and audio_codec is None:
            audio_codec = stream.get("codec_name")

    if kind is None:
        return None

    container = extract_container(format_name)
    extension = guess_extension(container, kind)
    if not extension and video_hint:
        extension = choose_video_extension(signatures)
    if not extension:
        return None

    compatible = False
    if kind == "image":
        compatible = extension in COMPATIBLE_IMAGE_EXTENSIONS
    elif kind == "video":
        container_names = {part.strip().lower() for part in format_name.split(",")}
        container_ok = bool(container_names & COMPATIBLE_VIDEO_CONTAINERS)
        if not container_ok and not video_hint:
            return None
        video_ok = video_codec in COMPATIBLE_VIDEO_CODECS if video_codec else False
        audio_ok = audio_codec in COMPATIBLE_AUDIO_CODECS or audio_codec is None
        compatible = container_ok and video_ok and audio_ok
        if extension not in {".mp4", ".mov", ".m4v", ".3gp", ".ts", ".mkv", ".webm", ".avi", ".flv", ".mpg", ".mpeg", ".wmv"}:
            return None

    return MediaFile(
        source=path,
        kind=kind,
        extension=extension,
        format_name=container,
        video_codec=video_codec,
        audio_codec=audio_codec,
        compatible=compatible,
        original_suffix=path.suffix,
    )


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
    skip_log: Path,
) -> list[MediaFile]:
    media_files: list[MediaFile] = []

    def log_skip(file_path: Path, reason: str) -> None:
        LOG.warning("Skipping %s (%s)", file_path, reason)
        with skip_log.open("a", encoding="utf-8") as handle:
            handle.write(f"{file_path}\t{reason}\n")

    def handle_file(file_path: Path) -> None:
        if file_path.is_symlink() and not follow_symlinks:
            log_skip(file_path, "symlink (use --follow-symlinks to allow)")
            return
        if not file_path.is_file():
            return

        skippable_reason = is_skippable_file(file_path)
        if skippable_reason:
            log_skip(file_path, skippable_reason)
            return

        media = detect_media(file_path)
        if media:
            media_files.append(media)
            return

        suffix = normalize_extension(file_path.suffix)
        signatures = [safe_filetype_guess(file_path), safe_puremagic_guess(file_path)]
        if (suffix and (suffix in ALL_IMAGE_EXTENSIONS or suffix in VIDEO_EXTENSION_HINTS)) or any(
            is_image_signature(sig) or is_video_signature(sig) for sig in signatures
        ):
            log_skip(file_path, "corrupt or unsupported media")

    if recursive:
        for dirpath, dirnames, filenames in os.walk(root, followlinks=follow_symlinks):
            dirnames[:] = [
                d for d in dirnames if not d.startswith("FOUND_MEDIA_FILES_")
            ]
            for filename in filenames:
                handle_file(Path(dirpath) / filename)
    else:
        for entry in root.iterdir():
            if entry.name.startswith("FOUND_MEDIA_FILES_"):
                continue
            if entry.is_dir():
                continue
            handle_file(entry)
    return media_files


def next_available_name(directory: Path, stem: str, extension: str) -> Path:
    counter = 0
    while True:
        suffix = "" if counter == 0 else f"_{counter}"
        candidate = directory / f"{stem}{suffix}{extension}"
        if not candidate.exists():
            return candidate
        counter += 1


def move_to_staging(media_files: Iterable[MediaFile], staging: Path) -> None:
    for media in media_files:
        stem = media.source.stem
        destination = next_available_name(staging, stem, media.extension)
        LOG.info("Moving %s -> %s", media.source, destination)
        shutil.move(str(media.source), str(destination))
        media.stage_path = destination
        media.backup_path = None


def create_stage_backup(path: Path) -> Path:
    backup = path.with_name(f"{path.name}.bak")
    counter = 1
    while backup.exists():
        backup = path.with_name(f"{path.name}.bak{counter}")
        counter += 1
    path.rename(backup)
    return backup


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
    run_checked(cmd)
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
    run_checked(cmd)
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


def sanitize_stage_paths(media_files: Iterable[MediaFile], staging: Path) -> None:
    for media in media_files:
        if not media.stage_path or not media.stage_path.exists():
            continue
        stem = media.stage_path.stem
        safe_stem = SAFE_NAME_PATTERN.sub("_", stem)
        if not safe_stem:
            safe_stem = "media"
        if safe_stem == stem:
            continue
        target = next_available_name(staging, safe_stem, media.stage_path.suffix)
        LOG.info("Sanitizing filename %s -> %s", media.stage_path.name, target.name)
        media.stage_path.rename(target)
        media.stage_path = target


def ensure_compatibility(media_files: Iterable[MediaFile]) -> None:
    for media in media_files:
        if media.stage_path is None:
            continue
        if media.kind == "image" and media.extension not in COMPATIBLE_IMAGE_EXTENSIONS:
            LOG.info("Converting image %s to JPEG", media.stage_path)
            convert_image(media)
        elif media.kind == "video" and not media.compatible:
            LOG.info("Converting video %s to MP4 (H.264/AAC)", media.stage_path)
            convert_video(media)


def run_checked(cmd: list[str]) -> None:
    LOG.debug("Executing command: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        LOG.error("Command failed: %s", result.stderr.strip())
        raise RuntimeError(f"Command '{cmd[0]}' failed with exit code {result.returncode}.")


def import_into_photos(paths: list[Path]) -> int:
    if not paths:
        return 0
    script = """
on run argv
    if (count of argv) is 0 then return 0
    set importedCount to 0
    tell application "Photos"
        activate
        repeat with itemPath in argv
            set mediaAlias to my alias_from_posix(itemPath)
            set importedItems to import mediaAlias with skip check duplicates
            if importedItems is missing value then
                set importedItems to {}
            end if
            set importedCount to importedCount + (count of importedItems)
        end repeat
    end tell
    return importedCount
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
    batches: list[list[str]] = []
    current_batch: list[str] = []
    current_length = 0
    for path in paths:
        arg = str(path)
        prospective = current_length + len(arg) + 1
        if (
            current_batch
            and (
                len(current_batch) >= MAX_APPLESCRIPT_ARGS
                or prospective > MAX_APPLESCRIPT_CHARS
            )
        ):
            batches.append(current_batch)
            current_batch = []
            current_length = 0
        current_batch.append(arg)
        current_length += len(arg) + 1
    if current_batch:
        batches.append(current_batch)

    total_imported = 0
    for batch in batches:
        cmd = ["osascript", "-", *batch]
        result = subprocess.run(
            cmd,
            input=script,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(f"AppleScript import failed: {result.stderr.strip()}")
        try:
            total_imported += int(result.stdout.strip())
        except ValueError as exc:
            raise RuntimeError("Unexpected response from AppleScript import.") from exc
    return total_imported


def cleanup_staging(staging: Path) -> None:
    if staging.exists():
        LOG.info("Deleting staging folder %s", staging)
        shutil.rmtree(staging)
def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")


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
    media_files: list[MediaFile] = []
    staging_root: Optional[Path] = None
    skip_log: Optional[Path] = None
    try:
        root = validate_root(args.path)
        for dependency in ("ffprobe", "ffmpeg", "osascript"):
            ensure_dependency(dependency)
        LOG.info("Scanning %s for media files...", root)
        run_ts = timestamp()
        skip_log = root / f"smm_skipped_files_{run_ts}.log"
        media_files = gather_media_files(root, args.recursive, args.follow_symlinks, skip_log)
        if not media_files:
            LOG.info("No media files detected.")
            if skip_log.exists() and skip_log.stat().st_size == 0:
                skip_log.unlink()
            return 0
        staging_root = root / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_root.mkdir(parents=True, exist_ok=False)
        move_to_staging(media_files, staging_root)
        ensure_compatibility(media_files)
        sanitize_stage_paths(media_files, staging_root)

        import_paths: list[Path] = []
        missing_media: list[MediaFile] = []
        for media in media_files:
            if media.stage_path and media.stage_path.exists():
                import_paths.append(media.stage_path.resolve())
            else:
                missing_media.append(media)

        if missing_media:
            missing_listing = ", ".join(str((m.stage_path or m.source)) for m in missing_media[:5])
            raise RuntimeError(f"Missing staged file(s): {missing_listing}")

        LOG.info("Importing %d file(s) into Apple Photos...", len(import_paths))
        imported_count = import_into_photos(import_paths)
        if imported_count != len(import_paths):
            raise RuntimeError(
                f"Apple Photos reported {imported_count} imported item(s) out of {len(import_paths)}."
            )
        remove_backups(media_files)
        LOG.info("Successfully imported %d media file(s) into Apple Photos.", imported_count)
        if args.delete:
            cleanup_staging(staging_root)
        else:
            LOG.info("Staging folder retained at %s", staging_root)
        if skip_log and skip_log.exists():
            if skip_log.stat().st_size == 0:
                skip_log.unlink()
            else:
                LOG.info("Skipped file log saved at %s", skip_log)
        return 0
    except Exception as exc:  # noqa: BLE001
        LOG.error("Error: %s", exc)
        revert_media_files(media_files, staging_root)
        if skip_log and skip_log.exists() and skip_log.stat().st_size == 0:
            skip_log.unlink()
        return 1


def run() -> None:
    sys.exit(main())
