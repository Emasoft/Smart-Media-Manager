"""
Format Registry Module for Smart Media Manager.

Provides UUID-based format identification and compatibility checking
using the unified format registry system.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

LOG = logging.getLogger(__name__)

# Global registry cache
_REGISTRY: Optional[Dict[str, Any]] = None
_COMPATIBILITY: Optional[Dict[str, Any]] = None


def load_format_registry() -> Dict[str, Any]:
    """Load the complete format registry from format_registry.json.

    Returns:
        Dictionary containing all format mappings with UUIDs
    """
    global _REGISTRY
    if _REGISTRY is not None:
        return _REGISTRY

    registry_path = Path(__file__).parent / "format_registry.json"
    if not registry_path.exists():
        # Fall back to parent directory
        registry_path = Path(__file__).parent.parent / "format_registry.json"

    if not registry_path.exists():
        LOG.warning(f"Format registry not found at {registry_path}, using empty registry")
        _REGISTRY = {}
        return _REGISTRY

    try:
        with open(registry_path) as f:
            _REGISTRY = json.load(f)
            LOG.info(f"Loaded format registry with {len(_REGISTRY.get('format_names', {}))} format definitions")
            return _REGISTRY
    except Exception as exc:
        LOG.error(f"Failed to load format registry: {exc}")
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


def get_format_action(format_uuid: str, video_codec: Optional[str] = None, audio_codec: Optional[str] = None) -> Optional[str]:
    """Determine the required action for a format based on Apple Photos compatibility.
    
    Args:
        format_uuid: Format UUID with type suffix
        video_codec: Video codec name (for videos)
        audio_codec: Audio codec name (for videos)
        
    Returns:
        Action string: "import", "rewrap_to_mp4", "transcode_to_hevc_mp4", "transcode_audio_to_supported", "convert_to_png", or None if unsupported
    """
    compat = load_compatibility_data()
    apple_compat = compat.get("apple_photos_compatible", {})
    
    # Check if directly compatible
    if format_uuid in apple_compat.get("images", {}).get("direct_import", []):
        return "import"
    
    if format_uuid in apple_compat.get("images", {}).get("raw_formats", []):
        return "import"
    
    # For videos, check container AND codecs
    if format_uuid in apple_compat.get("videos", {}).get("compatible_containers", []):
        # Container is compatible, check codecs
        if video_codec and video_codec not in ["h264", "hevc", "av1"]:
            return "transcode_to_hevc_mp4"  # Need to transcode video codec
        if audio_codec and audio_codec in ["opus", "vorbis", "dts"]:
            return "transcode_audio_to_supported"  # Need to transcode audio codec
        return "import"  # Container and codecs are compatible
    
    if format_uuid in apple_compat.get("videos", {}).get("compatible_video_codecs", []):
        return "import"  # Video codec is compatible
    
    # Check if conversion needed
    if format_uuid in apple_compat.get("images", {}).get("needs_conversion", []):
        return "convert_to_png"  # Convert incompatible image formats
    
    if format_uuid in apple_compat.get("videos", {}).get("needs_rewrap", []):
        return "rewrap_to_mp4"  # Container incompatible, but codecs compatible
    
    if format_uuid in apple_compat.get("videos", {}).get("needs_transcode_video", []):
        return "transcode_to_hevc_mp4"  # Video codec incompatible
    
    if format_uuid in apple_compat.get("videos", {}).get("needs_transcode_container", []):
        return "transcode_to_hevc_mp4"  # Container always needs full transcode (e.g., AVI)
    
    # Check audio codec separately
    if audio_codec and audio_codec in apple_compat.get("videos", {}).get("needs_transcode_audio", []):
        return "transcode_audio_to_supported"
    
    return None  # Unsupported format  # Unsupported format


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
