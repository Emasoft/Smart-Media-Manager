"""Machine-readable Apple Photos format rules for SMART_MEDIA_MANAGER.

This module is generated from APPLE_PHOTOS_FORMAT_RULES.md. Each rule describes:

* rule_id: stable identifier (e.g., "R-IMG-001").
* category: high-level grouping (image, raw, video, vector).
* action: deterministic handler (import, convert, rewrap, skip, etc.).
* identifiers: canonical values emitted by detection tiers.
* conditions: optional constraints (e.g., animation, size thresholds).

Helper utilities provide lookup by extension/identifiers so the CLI can
automatically choose the correct processing path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class FormatRule:
    rule_id: str
    category: str
    action: str
    extensions: tuple[str, ...]
    libmagic: tuple[str, ...]
    puremagic: tuple[str, ...]
    pyfsig: tuple[str, ...]
    binwalk: tuple[str, ...]
    rawpy: tuple[str, ...]
    ffprobe: tuple[str, ...]
    conditions: dict[str, object]
    notes: str


def _rule(
    *,
    rule_id: str,
    category: str,
    action: str,
    extensions: Iterable[str],
    libmagic: Iterable[str] = (),
    puremagic: Iterable[str] = (),
    pyfsig: Iterable[str] = (),
    binwalk: Iterable[str] = (),
    rawpy: Iterable[str] = (),
    ffprobe: Iterable[str] = (),
    conditions: Optional[dict[str, object]] = None,
    notes: str = "",
) -> FormatRule:
    return FormatRule(
        rule_id=rule_id,
        category=category,
        action=action,
        extensions=tuple(sorted({ext.lower() for ext in extensions})),
        libmagic=tuple(sorted({ident.lower() for ident in libmagic})),
        puremagic=tuple(sorted({ident.lower() for ident in puremagic})),
        pyfsig=tuple(sorted({ident.lower() for ident in pyfsig})),
        binwalk=tuple(sorted({ident.lower() for ident in binwalk})),
        rawpy=tuple(sorted({ident.lower() for ident in rawpy})),
        ffprobe=tuple(sorted({ident.lower() for ident in ffprobe})),
        conditions=conditions or {},
        notes=notes,
    )


FORMAT_RULES: tuple[FormatRule, ...] = (
    _rule(
        rule_id="R-IMG-001",
        category="image",
        action="import",
        extensions=[".jpg", ".jpeg"],
        libmagic=["image/jpeg", "jpeg image data"],
        puremagic=["jpeg", "image/jpeg"],
        pyfsig=["jpeg image file"],
        binwalk=["jpeg image data"],
        notes="Standard JPEG",
    ),
    _rule(
        rule_id="R-IMG-002",
        category="image",
        action="import",
        extensions=[".png"],
        libmagic=["image/png"],
        puremagic=["png", "image/png"],
        pyfsig=["png image"],
        binwalk=["png image"],
        notes="Portable Network Graphics",
    ),
    _rule(
        rule_id="R-IMG-003",
        category="image",
        action="import",
        extensions=[".heic", ".heif"],
        libmagic=["image/heic", "iso media, heif"],
        puremagic=["heic", "image/heic"],
        pyfsig=["iso base media (heic)"],
        binwalk=["heif"],
        notes="HEIF/HEIC",
    ),
    _rule(
        rule_id="R-IMG-004",
        category="image",
        action="import",
        extensions=[".gif"],
        libmagic=["image/gif"],
        puremagic=["gif", "image/gif"],
        pyfsig=["gif image"],
        binwalk=["gif image data"],
        conditions={"animated": False},
        notes="Static GIF",
    ),
    _rule(
        rule_id="R-IMG-005",
        category="image",
        action="import",
        extensions=[".gif"],
        libmagic=["image/gif"],
        puremagic=["gif", "image/gif"],
        pyfsig=["gif image"],
        binwalk=["gif image data"],
        conditions={"animated": True, "max_size_mb": 100},
        notes="Animated GIF under Apple size limit",
    ),
    _rule(
        rule_id="R-IMG-006",
        category="image",
        action="convert_animation_to_hevc_mp4",
        extensions=[".gif"],
        libmagic=["image/gif"],
        puremagic=["gif", "image/gif"],
        pyfsig=["gif image"],
        binwalk=["gif image data"],
        conditions={"animated": True, "min_size_mb": 100},
        notes="Animated GIF above Photos limit",
    ),
    _rule(
        rule_id="R-IMG-007",
        category="image",
        action="import",
        extensions=[".tif", ".tiff"],
        libmagic=["image/tiff"],
        puremagic=["tiff", "image/tiff"],
        pyfsig=["tiff image"],
        binwalk=["tiff image data"],
        notes="Tagged Image File Format",
    ),
    _rule(
        rule_id="R-IMG-008",
        category="image",
        action="import",
        extensions=[".psd"],
        libmagic=["application/photoshop"],
        puremagic=["psd", "image/vnd.adobe.photoshop"],
        pyfsig=["adobe photoshop image"],
        binwalk=["photoshop image data"],
        conditions={"psd_color_mode": "rgb"},
        notes="Adobe Photoshop (RGB)",
    ),
    _rule(
        rule_id="R-IMG-009",
        category="image",
        action="convert_to_tiff",
        extensions=[".psd"],
        libmagic=["application/photoshop"],
        puremagic=["psd", "image/vnd.adobe.photoshop"],
        pyfsig=["adobe photoshop image"],
        binwalk=["photoshop image data"],
        conditions={"psd_color_mode": "non-rgb"},
        notes="PSD CMYK/multichannel - convert to TIFF for Photos compatibility",
    ),
    _rule(
        rule_id="R-IMG-010",
        category="image",
        action="convert_to_png",
        extensions=[".webp"],
        libmagic=["image/webp"],
        puremagic=["webp", "image/webp"],
        pyfsig=["google webp image"],
        binwalk=["webp"],
        notes="WebP still",
    ),
    _rule(
        rule_id="R-IMG-011",
        category="image",
        action="convert_animation_to_hevc_mp4",
        extensions=[".webp"],
        libmagic=["image/webp"],
        puremagic=["webp", "image/webp"],
        pyfsig=["google webp image"],
        binwalk=["webp"],
        conditions={"animated": True},
        notes="Animated WebP",
    ),
    _rule(
        rule_id="R-IMG-012",
        category="image",
        action="convert_to_png",
        extensions=[".avif"],
        libmagic=["image/avif"],
        puremagic=["avif", "image/avif"],
        pyfsig=["avif image"],
        binwalk=["avif"],
        notes="AVIF still",
    ),
    _rule(
        rule_id="R-IMG-013",
        category="image",
        action="convert_to_heic_lossless",
        extensions=[".jxl"],
        libmagic=["image/jxl"],
        puremagic=["jxl", "image/jxl"],
        pyfsig=["jpeg xl image"],
        binwalk=["jpeg xl"],
        notes="JPEG XL",
    ),
    _rule(
        rule_id="R-IMG-014",
        category="image",
        action="convert_animation_to_hevc_mp4",
        extensions=[".png"],
        libmagic=["image/png"],
        puremagic=["png", "image/png"],
        pyfsig=["png image"],
        binwalk=["png image"],
        conditions={"animated": True},
        notes="Animated PNG (APNG)",
    ),
    _rule(
        rule_id="R-IMG-015",
        category="image",
        action="import",
        extensions=[".bmp"],
        libmagic=["image/bmp"],
        puremagic=["bmp", "image/bmp"],
        pyfsig=["bmp image"],
        binwalk=["pc bitmap"],
        notes="Bitmap",
    ),
    _rule(
        rule_id="R-IMG-016",
        category="vector",
        action="skip_vector",
        extensions=[
            ".svg",
            ".ai",
            ".eps",
            ".ps",
            ".pdf",
            ".wmf",
            ".emf",
            ".drw",
            ".tex",
        ],
        libmagic=["image/svg+xml", "application/postscript", "application/pdf"],
        puremagic=["svg", "postscript", "pdf"],
        pyfsig=["postscript document", "pdf document", "svg document"],
        binwalk=["pdf document", "postscript"],
        notes="Vector formats unsupported by Photos",
    ),
    # RAW rules
    _rule(
        rule_id="R-RAW-001",
        category="raw",
        action="import",
        extensions=[".crw", ".cr2", ".cr3", ".crm", ".crx"],
        libmagic=["image/x-canon-cr2", "application/octet-stream"],
        puremagic=["cr2"],
        pyfsig=["canon cr2 raw image"],
        binwalk=["canon raw"],
        rawpy=["canon"],
        notes="Canon RAW",
    ),
    _rule(
        rule_id="R-RAW-002",
        category="raw",
        action="import",
        extensions=[".nef", ".nrw"],
        libmagic=["image/x-nikon-nef"],
        puremagic=["nef"],
        pyfsig=["nikon nef raw image"],
        binwalk=["nikon raw"],
        rawpy=["nikon"],
        notes="Nikon RAW",
    ),
    _rule(
        rule_id="R-RAW-003",
        category="raw",
        action="import",
        extensions=[".arw", ".srf", ".sr2"],
        libmagic=["image/x-sony-arw"],
        puremagic=["arw"],
        pyfsig=["sony arw raw image"],
        binwalk=["sony raw"],
        rawpy=["sony"],
        notes="Sony RAW",
    ),
    _rule(
        rule_id="R-RAW-004",
        category="raw",
        action="import",
        extensions=[".raf"],
        libmagic=["image/x-fuji-raf"],
        puremagic=["raf"],
        pyfsig=["fujifilm raf raw image"],
        binwalk=["fujifilm raw"],
        rawpy=["fujifilm"],
        notes="Fujifilm RAW",
    ),
    _rule(
        rule_id="R-RAW-005",
        category="raw",
        action="import",
        extensions=[".orf"],
        libmagic=["image/x-olympus-orf"],
        puremagic=["orf"],
        pyfsig=["olympus orf raw image"],
        binwalk=["olympus raw"],
        rawpy=["olympus"],
        notes="Olympus RAW",
    ),
    _rule(
        rule_id="R-RAW-006",
        category="raw",
        action="import",
        extensions=[".rw2", ".raw"],
        libmagic=["image/x-panasonic-rw2"],
        puremagic=["rw2"],
        pyfsig=["panasonic rw2 raw image"],
        binwalk=["panasonic raw"],
        rawpy=["panasonic"],
        notes="Panasonic RAW",
    ),
    _rule(
        rule_id="R-RAW-007",
        category="raw",
        action="import",
        extensions=[".pef", ".dng"],
        libmagic=["image/x-pentax-pef", "image/x-adobe-dng"],
        puremagic=["pef", "dng"],
        pyfsig=["pentax pef raw image", "adobe dng"],
        binwalk=["pentax raw", "dng image"],
        rawpy=["pentax", "ricoh", "adobe"],
        notes="Pentax/Adobe DNG",
    ),
    _rule(
        rule_id="R-RAW-008",
        category="raw",
        action="import",
        extensions=[".3fr", ".fff", ".iiq", ".cap"],
        libmagic=["image/x-hasselblad-3fr"],
        puremagic=["3fr", "iiq"],
        pyfsig=["hasselblad raw", "phaseone raw"],
        binwalk=["hasselblad raw"],
        rawpy=["hasselblad", "phase one"],
        notes="Medium-format RAW",
    ),
    _rule(
        rule_id="R-RAW-009",
        category="raw",
        action="import",
        extensions=[".x3f"],
        libmagic=["image/x-sigma-x3f"],
        puremagic=["x3f"],
        pyfsig=["sigma x3f raw"],
        binwalk=["sigma raw"],
        rawpy=["sigma"],
        notes="Sigma RAW",
    ),
    _rule(
        rule_id="R-RAW-010",
        category="raw",
        action="import",
        extensions=[".gpr"],
        libmagic=["image/x-gopro-gpr"],
        puremagic=["gpr"],
        pyfsig=["gopro gpr raw"],
        binwalk=["gopro raw"],
        rawpy=["gopro"],
        notes="GoPro RAW",
    ),
    _rule(
        rule_id="R-RAW-011",
        category="raw",
        action="import",
        extensions=[".dng"],
        libmagic=["image/x-adobe-dng"],
        puremagic=["dng"],
        pyfsig=["adobe dng"],
        binwalk=["dng image"],
        rawpy=["dji"],
        notes="DJI DNG",
    ),
    _rule(
        rule_id="R-RAW-012",
        category="raw",
        action="skip_raw_unsupported",
        extensions=[".raw", ".unknown"],
        libmagic=["application/octet-stream"],
        puremagic=["None"],
        pyfsig=["Unknown file type"],
        binwalk=["unknown"],
        notes="Unknown RAW",
    ),
    # Video rules
    _rule(
        rule_id="R-VID-001a",
        category="video",
        action="rewrap_to_mp4",
        extensions=[".m4v"],
        libmagic=["video/mp4", "video/x-m4v", "iso media, mp4 base media"],
        puremagic=["m4v", "video/x-m4v"],
        pyfsig=["iso base media"],
        binwalk=["mpeg-4 part 14"],
        ffprobe=[
            "video:h264",
            "audio:aac",
            "audio:ac3",
            "audio:eac3",
            "audio:alac",
            "audio:pcm",
        ],
        notes="M4V with compatible codecs - remux to MP4",
    ),
    _rule(
        rule_id="R-VID-001",
        category="video",
        action="import",
        extensions=[".mp4", ".mov", ".qt"],
        libmagic=["video/mp4", "iso media, mp4 base media"],
        puremagic=["mp4", "video/mp4"],
        pyfsig=["iso base media"],
        binwalk=["mpeg-4 part 14"],
        ffprobe=[
            "video:h264",
            "audio:aac",
            "audio:ac3",
            "audio:eac3",
            "audio:alac",
            "audio:pcm",
        ],
        notes="H.264 + AAC/AC-3/E-AC-3/ALAC/PCM",
    ),
    _rule(
        rule_id="R-VID-002",
        category="video",
        action="import",
        extensions=[".mp4", ".mov", ".hevc", ".qt"],
        libmagic=["video/h265", "iso media, mp4 base media"],
        puremagic=["hevc", "video/h265"],
        pyfsig=["iso base media"],
        binwalk=["hevc"],
        ffprobe=["video:hevc", "audio:aac", "audio:ac3", "audio:eac3", "audio:alac"],
        notes="HEVC + AAC/AC-3/E-AC-3/ALAC",
    ),
    _rule(
        rule_id="R-VID-003",
        category="video",
        action="import",
        extensions=[".mp4", ".mov", ".qt"],
        libmagic=["video/mp4"],
        puremagic=["mp4", "video/mp4"],
        pyfsig=["iso base media"],
        binwalk=["dolby vision"],
        ffprobe=["video:hevc", "dolby_vision", "audio:eac3"],
        notes="Dolby Vision + Atmos",
    ),
    _rule(
        rule_id="R-VID-004",
        category="video",
        action="transcode_video_to_lossless_hevc",
        extensions=[".mp4", ".mov", ".qt"],
        libmagic=["video/mp4", "iso media, mp4 base media"],
        puremagic=["mp4", "video/mp4"],
        pyfsig=["iso base media"],
        binwalk=["mpeg-4 part 14"],
        ffprobe=["video:vp9", "video:av1", "video:mpeg2video"],
        notes="Unsupported video codec inside MP4",
    ),
    _rule(
        rule_id="R-VID-005",
        category="video",
        action="transcode_audio_to_aac_or_eac3",
        extensions=[".mp4", ".mov", ".qt"],
        libmagic=["video/mp4"],
        puremagic=["mp4", "video/mp4"],
        pyfsig=["iso base media"],
        binwalk=["mpeg-4 part 14"],
        ffprobe=["audio:opus", "audio:dts", "audio:truehd"],
        notes="Unsupported audio codec inside MP4/MOV",
    ),
    _rule(
        rule_id="R-VID-006",
        category="video",
        action="rewrap_to_mp4",
        extensions=[".mkv"],
        libmagic=["video/x-matroska"],
        puremagic=["mkv", "video/x-matroska"],
        pyfsig=["matroska data"],
        binwalk=["matroska"],
        ffprobe=["video:h264", "video:hevc"],
        notes="Matroska container with compatible codecs",
    ),
    _rule(
        rule_id="R-VID-007",
        category="video",
        action="transcode_to_hevc_mp4",
        extensions=[".mkv", ".webm"],
        libmagic=["video/x-matroska", "video/webm"],
        puremagic=["webm", "video/webm"],
        pyfsig=["matroska data", "webm"],
        binwalk=["webm"],
        ffprobe=["video:vp9", "audio:opus"],
        notes="VP9/Opus containers",
    ),
    _rule(
        rule_id="R-VID-008",
        category="video",
        action="transcode_to_hevc_mp4",
        extensions=[".avi"],
        libmagic=["video/x-msvideo"],
        puremagic=["avi", "video/x-msvideo"],
        pyfsig=["riff avi"],
        binwalk=["avi"],
        notes="AVI container",
    ),
    _rule(
        rule_id="R-VID-009",
        category="video",
        action="transcode_to_hevc_mp4",
        extensions=[".wmv"],
        libmagic=["video/x-ms-wmv"],
        puremagic=["wmv", "video/x-ms-wmv"],
        pyfsig=["asf/wmv"],
        binwalk=["microsoft asf"],
        notes="Windows Media",
    ),
    _rule(
        rule_id="R-VID-010",
        category="video",
        action="transcode_to_hevc_mp4",
        extensions=[".flv"],
        libmagic=["video/x-flv"],
        puremagic=["flv", "video/x-flv"],
        pyfsig=["flash video"],
        binwalk=["flv"],
        notes="Flash Video",
    ),
    _rule(
        rule_id="R-VID-011",
        category="video",
        action="rewrap_or_transcode_to_mp4",
        extensions=[".3gp", ".3g2"],
        libmagic=["video/3gpp", "video/3gpp2"],
        puremagic=["3gp", "3g2"],
        pyfsig=["3gpp multimedia"],
        binwalk=["3gp"],
        notes="3GPP container",
    ),
    _rule(
        rule_id="R-VID-012",
        category="video",
        action="skip_unknown_video",
        extensions=[".unknown"],
        notes="Unhandled/legacy video",
    ),
)


EXTENSION_INDEX: dict[str, list[FormatRule]] = {}
for rule in FORMAT_RULES:
    for ext in rule.extensions:
        EXTENSION_INDEX.setdefault(ext, []).append(rule)


def find_rules_by_extension(extension: Optional[str]) -> list[FormatRule]:
    if not extension:
        return []
    ext = extension.lower()
    if not ext.startswith("."):
        ext = f".{ext}"
    return EXTENSION_INDEX.get(ext, [])


def match_rule(
    *,
    extension: Optional[str] = None,
    libmagic: Optional[Iterable[str] | str] = None,
    puremagic: Optional[Iterable[str] | str] = None,
    pyfsig: Optional[Iterable[str] | str] = None,
    binwalk: Optional[Iterable[str] | str] = None,
    rawpy: Optional[Iterable[str] | str] = None,
    ffprobe_streams: Optional[Iterable[str]] = None,
    animated: Optional[bool] = None,
    size_bytes: Optional[int] = None,
    psd_color_mode: Optional[str] = None,
) -> Optional[FormatRule]:
    """Return the first rule that matches the supplied identifiers."""

    candidates = list(FORMAT_RULES)
    if extension:
        candidates = find_rules_by_extension(extension) or candidates

    def normalise_iter(value: Optional[Iterable[str] | str]) -> set[str]:
        if value is None:
            return set()
        if isinstance(value, str):
            value_lower = value.lower()
            str_result = {value_lower}
            if value_lower.startswith(".") and "/" not in value_lower:
                stripped = value_lower.lstrip(".")
                if stripped:
                    str_result.add(stripped)
            return str_result
        iter_result: set[str] = set()
        for entry in value:
            if entry:
                lowered = entry.lower()
                iter_result.add(lowered)
                if lowered.startswith(".") and "/" not in lowered:
                    stripped = lowered.lstrip(".")
                    if stripped:
                        iter_result.add(stripped)
        return iter_result

    libmagic_set = normalise_iter(libmagic)
    puremagic_set = normalise_iter(puremagic)
    pyfsig_set = normalise_iter(pyfsig)
    binwalk_set = normalise_iter(binwalk)
    rawpy_set = normalise_iter(rawpy)
    ffprobe_set = normalise_iter(ffprobe_streams)

    for rule in candidates:
        if rule.libmagic and libmagic_set and not libmagic_set & set(rule.libmagic):
            continue
        if rule.puremagic and puremagic_set and not puremagic_set & set(rule.puremagic):
            continue
        if rule.pyfsig and pyfsig_set and not pyfsig_set & set(rule.pyfsig):
            pass
        if rule.binwalk and binwalk_set and not binwalk_set & set(rule.binwalk):
            continue
        if rule.rawpy and rawpy_set and not rawpy_set & set(rule.rawpy):
            continue
        if rule.ffprobe and ffprobe_set and not ffprobe_set & set(rule.ffprobe):
            continue

        conditions = rule.conditions
        if "animated" in conditions and animated is not None:
            if bool(conditions["animated"]) != animated:
                continue
        if "max_size_mb" in conditions and size_bytes is not None:
            max_size_mb = conditions["max_size_mb"]
            if isinstance(max_size_mb, (int, float)) and size_bytes / (1024 * 1024) > float(max_size_mb):
                continue
        if "min_size_mb" in conditions and size_bytes is not None:
            min_size_mb = conditions["min_size_mb"]
            if isinstance(min_size_mb, (int, float)) and size_bytes / (1024 * 1024) < float(min_size_mb):
                continue
        if "psd_color_mode" in conditions and psd_color_mode is not None:
            required_mode = conditions["psd_color_mode"]
            if isinstance(required_mode, str) and required_mode == "rgb" and psd_color_mode.lower() != "rgb":
                continue
            if isinstance(required_mode, str) and required_mode == "non-rgb" and psd_color_mode.lower() == "rgb":
                continue

        return rule

    return None


__all__ = [
    "FormatRule",
    "FORMAT_RULES",
    "find_rules_by_extension",
    "match_rule",
]
