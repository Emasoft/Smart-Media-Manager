"""
Format Registry Module for Smart Media Manager.

Provides UUID-based format identification and compatibility checking
using the unified format registry system.
"""

import importlib.resources as resources
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

LOG = logging.getLogger(__name__)

# Global registry cache
_REGISTRY: Optional[Dict[str, Any]] = None
_COMPATIBILITY: Optional[Dict[str, Any]] = None


def _merge_unique_list(target: list, additions: list) -> None:
    existing = set(target)
    for item in additions:
        if item not in existing:
            target.append(item)
            existing.add(item)


def _merge_updates(base: Dict[str, Any], updates: Dict[str, Any]) -> None:
    """Merge a compatibility/registry updates overlay into the base data.

    The overlay format matches the auto-generated format_registry_updates_*.json
    files produced during runs when unknown mappings are encountered.
    """

    # tool_mappings
    for tool, mapping in updates.get("tool_mappings", {}).items():
        base.setdefault("tool_mappings", {}).setdefault(tool, {}).update(mapping)

    # format_names
    for fmt_uuid, info in updates.get("format_names", {}).items():
        base.setdefault("format_names", {}).setdefault(fmt_uuid, info)

    # apple_photos_compatible
    compat_updates = updates.get("apple_photos_compatible", {})
    if compat_updates:
        base_apc = base.setdefault("apple_photos_compatible", {})
        for section, values in compat_updates.items():  # images/videos
            base_section = base_apc.setdefault(section, {})
            for key, val in values.items():
                base_list = base_section.setdefault(key, [])
                if isinstance(val, list):
                    _merge_unique_list(base_list, val)


def _load_update_files() -> list[Path]:
    """Locate format_registry_updates_*.json overlays in likely locations."""
    candidates: list[Path] = []
    cwd = Path.cwd()
    candidates.extend(sorted(cwd.glob("format_registry_updates_*.json")))

    repo_root = Path(__file__).parent.parent
    if repo_root != cwd:
        candidates.extend(sorted(repo_root.glob("format_registry_updates_*.json")))

    return [path for path in candidates if path.is_file()]


def load_format_registry() -> Dict[str, Any]:
    """Load the complete format registry from the packaged format_registry.json."""
    global _REGISTRY
    if _REGISTRY is not None:
        return _REGISTRY

    try:
        resource_path = resources.files("smart_media_manager").joinpath("format_registry.json")
        with resource_path.open("r", encoding="utf-8") as handle:
            _REGISTRY = json.load(handle)
            LOG.info(
                "Loaded format registry with %d format definitions (packaged resource)",
                len(_REGISTRY.get("format_names", {})),
            )
            return _REGISTRY
    except FileNotFoundError:
        LOG.error("Packaged format registry not found.")
    except Exception as exc:  # pragma: no cover - corrupted install
        LOG.error(f"Failed to load packaged format registry: {exc}")
    _REGISTRY = {}
    return _REGISTRY


def load_compatibility_data() -> Dict[str, Any]:
    """Load Apple Photos compatibility data from format_compatibility.json.

    Returns:
        Dictionary containing compatibility rules
    """
    global _COMPATIBILITY
    if _COMPATIBILITY is not None:
        return _COMPATIBILITY

    compat_path = Path(__file__).parent / "format_compatibility.json"
    if not compat_path.exists():
        LOG.error(f"FATAL: Compatibility data not found at {compat_path}")
        LOG.error("This file must be included in the package. The installation is corrupted.")
        LOG.error("Please reinstall: uv tool uninstall smart-media-manager && uv tool install smart-media-manager")
        raise FileNotFoundError(f"Critical file missing: {compat_path}")

    try:
        with open(compat_path) as f:
            _COMPATIBILITY = json.load(f)
            LOG.info("Loaded Apple Photos compatibility rules")

        # Merge any local update overlays (format_registry_updates_*.json)
        for update_file in _load_update_files():
            try:
                with update_file.open("r", encoding="utf-8") as handle:
                    updates = json.load(handle)
                _merge_updates(_COMPATIBILITY, updates)
                LOG.info("Applied compatibility updates from %s", update_file)
            except Exception as exc:  # noqa: BLE001
                LOG.warning("Failed to apply updates from %s: %s", update_file, exc)

        return _COMPATIBILITY
    except Exception as exc:
        LOG.error(f"FATAL: Failed to load compatibility data: {exc}")
        raise RuntimeError(f"Failed to load critical compatibility data from {compat_path}") from exc


def lookup_format_uuid(tool_name: str, tool_output: str) -> Optional[str]:
    """Look up format UUID from tool-specific output.

    Args:
        tool_name: Name of the detection tool (libmagic, puremagic, ffprobe, etc.)
        tool_output: The format string returned by the tool

    Returns:
        Format UUID with type suffix, or None if not found
    """
    compat = load_compatibility_data()
    mappings = compat.get("tool_mappings", {}).get(tool_name, {})

    # Direct lookup
    if tool_output in mappings:
        result = mappings[tool_output]
        # Handle both single UUID and list of UUIDs
        if isinstance(result, list):
            return result[0] if result else None
        return result

    # Partial match for complex strings (e.g., "JPEG image data, JFIF standard...")
    for key, uuid in mappings.items():
        if key in tool_output or tool_output in key:
            if isinstance(uuid, list):
                return uuid[0] if uuid else None
            return uuid

    return None


def get_canonical_name(format_uuid: str) -> Optional[str]:
    """Get canonical format name from UUID.

    Args:
        format_uuid: Format UUID with type suffix

    Returns:
        Canonical format name, or None if not found
    """
    compat = load_compatibility_data()
    format_info = compat.get("format_names", {}).get(format_uuid)
    if format_info:
        return format_info.get("canonical")
    return None


def get_format_extensions(format_uuid: str) -> List[str]:
    """Get file extensions for a format UUID.

    Args:
        format_uuid: Format UUID with type suffix

    Returns:
        List of file extensions (with dots)
    """
    compat = load_compatibility_data()
    format_info = compat.get("format_names", {}).get(format_uuid)
    if format_info:
        return format_info.get("extensions", [])
    return []


def is_apple_photos_compatible(format_uuid: str) -> bool:
    """Check if format is directly compatible with Apple Photos.

    Args:
        format_uuid: Format UUID with type suffix

    Returns:
        True if format can be directly imported to Apple Photos
    """
    compat = load_compatibility_data()
    apple_compat = compat.get("apple_photos_compatible", {})

    # Check image formats
    if format_uuid in apple_compat.get("images", {}).get("direct_import", []):
        return True

    # Check RAW formats
    if format_uuid in apple_compat.get("images", {}).get("raw_formats", []):
        return True

    # Check video containers
    if format_uuid in apple_compat.get("videos", {}).get("compatible_containers", []):
        return True

    # Check video codecs
    if format_uuid in apple_compat.get("videos", {}).get("compatible_video_codecs", []):
        return True

    return False


def needs_conversion(format_uuid: str) -> bool:
    """Check if format needs conversion before Apple Photos import.

    Args:
        format_uuid: Format UUID with type suffix

    Returns:
        True if format needs conversion
    """
    compat = load_compatibility_data()
    apple_compat = compat.get("apple_photos_compatible", {})

    # Check if in needs_conversion lists
    if format_uuid in apple_compat.get("images", {}).get("needs_conversion", []):
        return True

    if format_uuid in apple_compat.get("videos", {}).get("needs_rewrap", []):
        return True

    if format_uuid in apple_compat.get("videos", {}).get("needs_transcode_video", []):
        return True

    return False


def get_format_action(
    format_uuid: str,
    video_codec: Optional[str] = None,
    audio_codec: Optional[str] = None,
    container_uuid: Optional[str] = None,
) -> Optional[str]:
    """Determine the required action for a format based on Apple Photos compatibility.

    Supports both exact UUID matching and pattern-based matching for expanded UUIDs.
    For video codecs, checks format parameters (bit depth, pixel format, profile).
    For videos, checks BOTH container and video codec compatibility.

    Args:
        format_uuid: Format UUID with type suffix (may include parameters like "8bit-yuv420p-high")
        video_codec: Video codec name (for videos)
        audio_codec: Audio codec name (for videos)
        container_uuid: Container UUID (for videos, to check container compatibility separately)

    Returns:
        Action string: "import", "rewrap_to_mp4", "transcode_to_hevc_mp4", "transcode_audio_to_supported", "convert_to_png", or None if unsupported
    """
    compat = load_compatibility_data()
    apple_compat = compat.get("apple_photos_compatible", {})

    # Check if directly compatible (exact match)
    if format_uuid in apple_compat.get("images", {}).get("direct_import", []):
        return "import"

    if format_uuid in apple_compat.get("images", {}).get("raw_formats", []):
        return "import"

    # For videos, check container AND codecs
    # If container_uuid is provided, check container compatibility first
    if container_uuid:
        container_compatible = container_uuid in apple_compat.get("videos", {}).get("compatible_containers", [])
        container_needs_rewrap = container_uuid in apple_compat.get("videos", {}).get("needs_rewrap", [])

        # Check video codec compatibility
        video_codec_compatible = format_uuid in apple_compat.get("videos", {}).get("compatible_video_codecs", [])

        # Pattern-based matching for video codecs
        video_needs_transcode = False
        for transcode_pattern in apple_compat.get("videos", {}).get("needs_transcode_video", []):
            if _uuid_matches_pattern(format_uuid, transcode_pattern):
                video_needs_transcode = True
                break

        # Decision logic for videos with both container and codec info
        if not container_compatible and container_needs_rewrap:
            # Container needs rewrap
            if video_codec_compatible and not video_needs_transcode:
                return "rewrap_to_mp4"  # Container incompatible, but codec compatible
            else:
                return "transcode_to_hevc_mp4"  # Both container and codec incompatible
        elif container_compatible:
            # Container is compatible, check codecs
            if video_needs_transcode:
                return "transcode_to_hevc_mp4"  # Video codec needs transcode
            # Check audio codec compatibility using UUID matching
            if audio_codec:
                # Extract base UUID from expanded audio codec UUID
                audio_needs_transcode = False
                for transcode_pattern in apple_compat.get("videos", {}).get("needs_transcode_audio", []):
                    if _uuid_matches_pattern(audio_codec, transcode_pattern):
                        audio_needs_transcode = True
                        break
                if audio_needs_transcode:
                    return "transcode_audio_to_supported"  # Audio codec needs transcode
            return "import"  # Container and codecs are compatible
        else:
            # Container is neither compatible nor needs rewrap (unknown container)
            if video_codec_compatible:
                return "rewrap_to_mp4"  # Assume container needs rewrap if codec is compatible
            else:
                return "transcode_to_hevc_mp4"  # Full transcode needed

    # Legacy path for non-video or when container_uuid not provided
    if format_uuid in apple_compat.get("videos", {}).get("compatible_containers", []):
        # Container is compatible, check codecs
        if video_codec and video_codec not in ["h264", "hevc", "av1"]:
            return "transcode_to_hevc_mp4"  # Need to transcode video codec
        # Check audio codec compatibility using UUID matching
        if audio_codec:
            audio_needs_transcode = False
            for transcode_pattern in apple_compat.get("videos", {}).get("needs_transcode_audio", []):
                if _uuid_matches_pattern(audio_codec, transcode_pattern):
                    audio_needs_transcode = True
                    break
            if audio_needs_transcode:
                return "transcode_audio_to_supported"  # Need to transcode audio codec
        return "import"  # Container and codecs are compatible

    # Check video codec UUID (exact match first)
    if format_uuid in apple_compat.get("videos", {}).get("compatible_video_codecs", []):
        return "import"  # Video codec is compatible

    # Pattern-based matching for video codecs with parameters
    # Check if UUID matches any transcode patterns (10-bit H.264, 4:2:2, 4:4:4)
    for transcode_pattern in apple_compat.get("videos", {}).get("needs_transcode_video", []):
        if _uuid_matches_pattern(format_uuid, transcode_pattern):
            return "transcode_to_hevc_mp4"

    # Check if conversion needed
    if format_uuid in apple_compat.get("images", {}).get("needs_conversion", []):
        return "convert_to_png"  # Convert incompatible image formats

    if format_uuid in apple_compat.get("videos", {}).get("needs_rewrap", []):
        return "rewrap_to_mp4"  # Container incompatible, but codecs compatible

    if format_uuid in apple_compat.get("videos", {}).get("needs_transcode_container", []):
        return "transcode_to_hevc_mp4"  # Container always needs full transcode (e.g., AVI)

    # Check audio codec separately using UUID matching
    if audio_codec:
        audio_needs_transcode = False
        for transcode_pattern in apple_compat.get("videos", {}).get("needs_transcode_audio", []):
            if _uuid_matches_pattern(audio_codec, transcode_pattern):
                audio_needs_transcode = True
                break
        if audio_needs_transcode:
            return "transcode_audio_to_supported"

    return None  # Unsupported format


def _uuid_matches_pattern(uuid: str, pattern: str) -> bool:
    """Check if a UUID matches a pattern (for expanded UUIDs with wildcards).

    Supports wildcard patterns like:
    - "b2e62c4a-6122-548c-9bfa-0fcf3613942a-10bit-V" (matches any 10-bit H.264)
    - "b2e62c4a-6122-548c-9bfa-0fcf3613942a-yuv422p-V" (matches any 4:2:2 H.264)

    Args:
        uuid: The UUID to check
        pattern: The pattern to match against

    Returns:
        True if UUID matches the pattern
    """
    # Exact match
    if uuid == pattern:
        return True

    # Extract base UUID (first 5 parts: xxxx-xxxx-xxxx-xxxx-xxxx)
    uuid_parts = uuid.split("-")
    pattern_parts = pattern.split("-")

    if len(uuid_parts) < 5 or len(pattern_parts) < 5:
        return False

    # Base UUIDs must match
    uuid_base = "-".join(uuid_parts[:5])
    pattern_base = "-".join(pattern_parts[:5])

    if uuid_base != pattern_base:
        return False

    # If pattern has no parameters, match any UUID with same base
    if len(pattern_parts) == 6 and pattern_parts[5] in ["V", "A", "I", "C", "R"]:
        return True

    # Check if UUID contains the pattern's key parameters
    uuid_params = set(uuid_parts[5:])
    pattern_params = set(pattern_parts[5:])

    # Pattern parameters must be present in UUID
    return pattern_params.issubset(uuid_params)


def get_compatible_formats() -> Set[str]:
    """Get set of all Apple Photos compatible format UUIDs.

    Returns:
        Set of format UUIDs that are compatible
    """
    compat = load_compatibility_data()
    apple_compat = compat.get("apple_photos_compatible", {})

    compatible = set()

    # Add image formats
    compatible.update(apple_compat.get("images", {}).get("direct_import", []))
    compatible.update(apple_compat.get("images", {}).get("raw_formats", []))

    # Add video formats
    compatible.update(apple_compat.get("videos", {}).get("compatible_containers", []))
    compatible.update(apple_compat.get("videos", {}).get("compatible_video_codecs", []))

    return compatible


def get_incompatible_formats() -> Set[str]:
    """Get set of known incompatible format UUIDs.

    Returns:
        Set of format UUIDs that cannot be imported
    """
    # For now, we'll consider anything not in the compatible set as potentially incompatible
    # This could be expanded with explicit incompatible lists in the JSON
    compat = load_compatibility_data()
    all_formats = set(compat.get("format_names", {}).keys())
    compatible = get_compatible_formats()

    # Also include formats that need conversion as "compatible"
    # since we can process them
    needs_conv = set()
    apple_compat = compat.get("apple_photos_compatible", {})
    needs_conv.update(apple_compat.get("images", {}).get("needs_conversion", []))
    needs_conv.update(apple_compat.get("videos", {}).get("needs_rewrap", []))
    needs_conv.update(apple_compat.get("videos", {}).get("needs_transcode_video", []))

    return all_formats - compatible - needs_conv


def format_detection_result(tool_results: Dict[str, str]) -> Optional[str]:
    """Perform consensus-based format detection from multiple tools.

    Args:
        tool_results: Dictionary mapping tool names to their output strings

    Returns:
        Consensus format UUID, or None if no consensus
    """
    # Weight different tools
    weights = {
        "libmagic": 1.4,
        "puremagic": 1.1,
        "pyfsig": 1.0,
        "binwalk": 1.2,
        "ffprobe": 1.3,
    }

    # Collect votes
    votes: Dict[str, float] = {}
    for tool_name, tool_output in tool_results.items():
        if not tool_output:
            continue

        uuid = lookup_format_uuid(tool_name, tool_output)
        if uuid:
            weight = weights.get(tool_name, 1.0)
            votes[uuid] = votes.get(uuid, 0.0) + weight

    if not votes:
        return None

    # Return highest-weighted UUID
    return max(votes.items(), key=lambda x: x[1])[0]
