"""
Metadata Field Registry Module for Smart Media Manager.

Provides UUID-based metadata field identification for unified field recognition
across different tools and formats (ExifTool, FFmpeg, libmagic, etc.).

This complements the format UUID system by providing a translation layer for
metadata field names, enabling programmatic metadata operations across tools.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

LOG = logging.getLogger(__name__)

# Global registry cache
_METADATA_REGISTRY: Optional[Dict[str, Any]] = None


def load_metadata_registry() -> Dict[str, Any]:
    """Load the metadata field registry from metadata_registry.json.

    Returns:
        Dictionary containing all metadata field mappings with UUIDs
    """
    global _METADATA_REGISTRY
    if _METADATA_REGISTRY is not None:
        return _METADATA_REGISTRY

    registry_path = Path(__file__).parent / "metadata_registry.json"
    if not registry_path.exists():
        LOG.warning(f"Metadata registry not found at {registry_path}, using empty registry")
        _METADATA_REGISTRY = {}
        return _METADATA_REGISTRY

    try:
        with open(registry_path) as f:
            _METADATA_REGISTRY = json.load(f)
            field_count = sum(len(fields) for fields in _METADATA_REGISTRY.get("metadata_fields", {}).values())
            LOG.info(f"Loaded metadata registry with {field_count} field definitions")
            return _METADATA_REGISTRY
    except Exception as exc:
        LOG.error(f"Failed to load metadata registry: {exc}")
        _METADATA_REGISTRY = {}
        return _METADATA_REGISTRY


def lookup_metadata_field_uuid(tool_name: str, field_name: str) -> Optional[str]:
    """Look up metadata field UUID from tool-specific field name.

    Args:
        tool_name: Name of the tool (exiftool, ffprobe, ffmpeg, etc.)
        field_name: The field name as reported by the tool

    Returns:
        Metadata field UUID with -M suffix, or None if not found

    Example:
        >>> lookup_metadata_field_uuid("exiftool", "EXIF:DateTimeOriginal")
        '3d4f8a9c-1e7b-5c3d-9a2f-4e8c1b7d3a9f-M'
        >>> lookup_metadata_field_uuid("ffprobe", "creation_time")
        '3d4f8a9c-1e7b-5c3d-9a2f-4e8c1b7d3a9f-M'
    """
    registry = load_metadata_registry()
    metadata_fields = registry.get("metadata_fields", {})

    # Search through all categories and fields
    for category in metadata_fields.values():
        for field_info in category.values():
            tool_mappings = field_info.get("tool_mappings", {})
            if tool_name in tool_mappings:
                if field_name in tool_mappings[tool_name]:
                    uuid_value = field_info.get("uuid")
                    # Ensure we return str or None, not Any
                    return str(uuid_value) if uuid_value is not None else None

    return None


def get_canonical_field_name(field_uuid: str) -> Optional[str]:
    """Get canonical field name from UUID.

    Args:
        field_uuid: Metadata field UUID with -M suffix

    Returns:
        Canonical field name, or None if not found

    Example:
        >>> get_canonical_field_name("3d4f8a9c-1e7b-5c3d-9a2f-4e8c1b7d3a9f-M")
        'creation_datetime'
    """
    registry = load_metadata_registry()
    metadata_fields = registry.get("metadata_fields", {})

    for category in metadata_fields.values():
        for field_info in category.values():
            if field_info.get("uuid") == field_uuid:
                canonical_value = field_info.get("canonical")
                # Ensure we return str or None, not Any
                return str(canonical_value) if canonical_value is not None else None

    return None


def get_tool_field_names(field_uuid: str, tool_name: str) -> List[str]:
    """Get all tool-specific field names for a UUID.

    Args:
        field_uuid: Metadata field UUID with -M suffix
        tool_name: Tool to get field names for (exiftool, ffprobe, etc.)

    Returns:
        List of field names used by the tool

    Example:
        >>> get_tool_field_names("3d4f8a9c-...-M", "exiftool")
        ['EXIF:DateTimeOriginal', 'EXIF:CreateDate', 'XMP:CreateDate']
    """
    registry = load_metadata_registry()
    metadata_fields = registry.get("metadata_fields", {})

    for category in metadata_fields.values():
        for field_info in category.values():
            if field_info.get("uuid") == field_uuid:
                tool_mappings = field_info.get("tool_mappings", {})
                field_names = tool_mappings.get(tool_name, [])
                # Ensure we return List[str], not Any - validate each item is a string
                return [str(name) for name in field_names] if isinstance(field_names, list) else []

    return []


def translate_field_name(source_tool: str, source_field: str, target_tool: str) -> Optional[str]:
    """Translate a field name from one tool to another using UUID mapping.

    Args:
        source_tool: Tool that reported the field (exiftool, ffprobe, etc.)
        source_field: Field name as reported by source tool
        target_tool: Tool to translate field name for

    Returns:
        First matching field name for target tool, or None if not found

    Example:
        >>> translate_field_name("exiftool", "EXIF:DateTimeOriginal", "ffprobe")
        'creation_time'
        >>> translate_field_name("ffprobe", "creation_time", "exiftool")
        'EXIF:DateTimeOriginal'
    """
    # Look up UUID from source tool's field name
    field_uuid = lookup_metadata_field_uuid(source_tool, source_field)
    if not field_uuid:
        return None

    # Get target tool's field names for this UUID
    target_fields = get_tool_field_names(field_uuid, target_tool)
    return target_fields[0] if target_fields else None


def normalize_metadata_dict(tool_name: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a metadata dictionary to use canonical field names (UUIDs).

    Converts tool-specific field names to UUIDs for tool-agnostic metadata handling.

    Args:
        tool_name: Tool that produced the metadata (exiftool, ffprobe, etc.)
        metadata: Dictionary with tool-specific field names

    Returns:
        Dictionary with UUID keys and original values

    Example:
        >>> normalize_metadata_dict("ffprobe", {"creation_time": "2024-01-15"})
        {'3d4f8a9c-1e7b-5c3d-9a2f-4e8c1b7d3a9f-M': '2024-01-15'}
    """
    normalized = {}
    for field_name, value in metadata.items():
        field_uuid = lookup_metadata_field_uuid(tool_name, field_name)
        if field_uuid:
            normalized[field_uuid] = value
        else:
            # Preserve unmapped fields with original name
            LOG.debug(f"No UUID mapping for {tool_name} field: {field_name}")
            normalized[f"unmapped:{tool_name}:{field_name}"] = value

    return normalized


def get_field_description(field_uuid: str) -> Optional[str]:
    """Get human-readable description of a metadata field.

    Args:
        field_uuid: Metadata field UUID with -M suffix

    Returns:
        Field description, or None if not found
    """
    registry = load_metadata_registry()
    metadata_fields = registry.get("metadata_fields", {})

    for category in metadata_fields.values():
        for field_info in category.values():
            if field_info.get("uuid") == field_uuid:
                description_value = field_info.get("description")
                # Ensure we return str or None, not Any
                return str(description_value) if description_value is not None else None

    return None


def get_all_field_uuids() -> List[str]:
    """Get list of all metadata field UUIDs in the registry.

    Returns:
        List of all field UUIDs
    """
    registry = load_metadata_registry()
    metadata_fields = registry.get("metadata_fields", {})

    uuids = []
    for category in metadata_fields.values():
        for field_info in category.values():
            if "uuid" in field_info:
                uuids.append(field_info["uuid"])

    return uuids
