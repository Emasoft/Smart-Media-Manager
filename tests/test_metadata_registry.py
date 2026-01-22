"""
Unit tests for metadata_registry module.

Tests UUID-based metadata field translation across different tools (ExifTool, FFprobe, etc.).
"""

from typing import Any, Dict

import pytest

from smart_media_manager import metadata_registry


@pytest.fixture
def sample_registry() -> Dict[str, Any]:
    """Load the actual metadata registry for testing."""
    return metadata_registry.load_metadata_registry()


def test_load_metadata_registry(sample_registry: Dict[str, Any]) -> None:
    """Test that metadata registry loads successfully and has expected structure."""
    assert sample_registry is not None
    assert "metadata_fields" in sample_registry
    assert isinstance(sample_registry["metadata_fields"], dict)

    # Verify expected categories exist
    expected_categories = [
        "temporal",
        "spatial",
        "authorship",
        "descriptive",
        "technical",
        "apple_specific",
    ]
    for category in expected_categories:
        assert category in sample_registry["metadata_fields"], f"Missing category: {category}"


def test_lookup_metadata_field_uuid_exiftool_temporal(
    sample_registry: Dict[str, Any],
) -> None:
    """Test looking up UUID for ExifTool temporal metadata field."""
    # ExifTool's DateTimeOriginal should map to creation_datetime UUID
    uuid = metadata_registry.lookup_metadata_field_uuid("exiftool", "EXIF:DateTimeOriginal")
    assert uuid is not None
    assert uuid.endswith("-M")
    assert uuid == "3d4f8a9c-1e7b-5c3d-9a2f-4e8c1b7d3a9f-M"


def test_lookup_metadata_field_uuid_ffprobe_temporal(
    sample_registry: Dict[str, Any],
) -> None:
    """Test looking up UUID for FFprobe temporal metadata field."""
    # FFprobe's creation_time should map to same UUID as ExifTool's DateTimeOriginal
    uuid = metadata_registry.lookup_metadata_field_uuid("ffprobe", "creation_time")
    assert uuid is not None
    assert uuid.endswith("-M")
    assert uuid == "3d4f8a9c-1e7b-5c3d-9a2f-4e8c1b7d3a9f-M"


def test_lookup_metadata_field_uuid_cross_tool_consistency(
    sample_registry: Dict[str, Any],
) -> None:
    """Test that different tools' field names map to same UUID for same semantic field."""
    exiftool_uuid = metadata_registry.lookup_metadata_field_uuid("exiftool", "EXIF:DateTimeOriginal")
    ffprobe_uuid = metadata_registry.lookup_metadata_field_uuid("ffprobe", "creation_time")

    assert exiftool_uuid == ffprobe_uuid, "Different tools should map to same UUID for creation datetime"


def test_lookup_metadata_field_uuid_not_found(sample_registry: Dict[str, Any]) -> None:
    """Test that non-existent field returns None."""
    uuid = metadata_registry.lookup_metadata_field_uuid("exiftool", "NonExistentField")
    assert uuid is None


def test_lookup_metadata_field_uuid_spatial_gps(
    sample_registry: Dict[str, Any],
) -> None:
    """Test looking up UUID for GPS spatial metadata fields."""
    lat_uuid = metadata_registry.lookup_metadata_field_uuid("exiftool", "GPS:GPSLatitude")
    lon_uuid = metadata_registry.lookup_metadata_field_uuid("exiftool", "GPS:GPSLongitude")

    assert lat_uuid is not None
    assert lon_uuid is not None
    assert lat_uuid != lon_uuid, "Latitude and longitude should have different UUIDs"
    assert lat_uuid.endswith("-M")
    assert lon_uuid.endswith("-M")


def test_get_canonical_field_name_temporal(sample_registry: Dict[str, Any]) -> None:
    """Test getting canonical field name from UUID."""
    uuid = "3d4f8a9c-1e7b-5c3d-9a2f-4e8c1b7d3a9f-M"
    canonical = metadata_registry.get_canonical_field_name(uuid)
    assert canonical == "creation_datetime"


def test_get_canonical_field_name_spatial(sample_registry: Dict[str, Any]) -> None:
    """Test getting canonical field name for spatial metadata."""
    lat_uuid = "9e1f3b7d-6c4a-5e8d-7f2b-1a9c4e3d8b5f-M"
    canonical = metadata_registry.get_canonical_field_name(lat_uuid)
    assert canonical == "gps_latitude"


def test_get_canonical_field_name_not_found(sample_registry: Dict[str, Any]) -> None:
    """Test that non-existent UUID returns None."""
    canonical = metadata_registry.get_canonical_field_name("00000000-0000-0000-0000-000000000000-M")
    assert canonical is None


def test_get_tool_field_names_exiftool(sample_registry: Dict[str, Any]) -> None:
    """Test getting all ExifTool field names for a UUID."""
    uuid = "3d4f8a9c-1e7b-5c3d-9a2f-4e8c1b7d3a9f-M"
    field_names = metadata_registry.get_tool_field_names(uuid, "exiftool")

    assert isinstance(field_names, list)
    assert len(field_names) > 0
    assert "EXIF:DateTimeOriginal" in field_names
    assert "EXIF:CreateDate" in field_names
    assert "XMP:CreateDate" in field_names


def test_get_tool_field_names_ffprobe(sample_registry: Dict[str, Any]) -> None:
    """Test getting all FFprobe field names for a UUID."""
    uuid = "3d4f8a9c-1e7b-5c3d-9a2f-4e8c1b7d3a9f-M"
    field_names = metadata_registry.get_tool_field_names(uuid, "ffprobe")

    assert isinstance(field_names, list)
    assert len(field_names) > 0
    assert "creation_time" in field_names


def test_get_tool_field_names_not_found(sample_registry: Dict[str, Any]) -> None:
    """Test that non-existent UUID returns empty list."""
    field_names = metadata_registry.get_tool_field_names("00000000-0000-0000-0000-000000000000-M", "exiftool")
    assert field_names == []


def test_translate_field_name_exiftool_to_ffprobe(
    sample_registry: Dict[str, Any],
) -> None:
    """Test translating field name from ExifTool to FFprobe."""
    ffprobe_field = metadata_registry.translate_field_name("exiftool", "EXIF:DateTimeOriginal", "ffprobe")
    assert ffprobe_field is not None
    assert ffprobe_field == "creation_time"


def test_translate_field_name_ffprobe_to_exiftool(
    sample_registry: Dict[str, Any],
) -> None:
    """Test translating field name from FFprobe to ExifTool."""
    exiftool_field = metadata_registry.translate_field_name("ffprobe", "creation_time", "exiftool")
    assert exiftool_field is not None
    assert exiftool_field in [
        "EXIF:DateTimeOriginal",
        "EXIF:CreateDate",
        "XMP:CreateDate",
    ]


def test_translate_field_name_not_found(sample_registry: Dict[str, Any]) -> None:
    """Test that translation returns None for non-existent field."""
    result = metadata_registry.translate_field_name("exiftool", "NonExistentField", "ffprobe")
    assert result is None


def test_normalize_metadata_dict_ffprobe(sample_registry: Dict[str, Any]) -> None:
    """Test normalizing FFprobe metadata dictionary to use UUIDs."""
    metadata = {
        "creation_time": "2024-01-15T10:30:00.000000Z",
        "artist": "John Doe",
        "title": "Test Video",
    }

    normalized = metadata_registry.normalize_metadata_dict("ffprobe", metadata)

    assert isinstance(normalized, dict)
    # creation_time should be mapped to UUID
    assert "3d4f8a9c-1e7b-5c3d-9a2f-4e8c1b7d3a9f-M" in normalized
    assert normalized["3d4f8a9c-1e7b-5c3d-9a2f-4e8c1b7d3a9f-M"] == "2024-01-15T10:30:00.000000Z"


def test_normalize_metadata_dict_exiftool(sample_registry: Dict[str, Any]) -> None:
    """Test normalizing ExifTool metadata dictionary to use UUIDs."""
    metadata = {
        "EXIF:DateTimeOriginal": "2024:01:15 10:30:00",
        "EXIF:Artist": "Jane Smith",
        "GPS:GPSLatitude": "37.7749",
    }

    normalized = metadata_registry.normalize_metadata_dict("exiftool", metadata)

    assert isinstance(normalized, dict)
    # DateTimeOriginal should be mapped to UUID
    assert "3d4f8a9c-1e7b-5c3d-9a2f-4e8c1b7d3a9f-M" in normalized
    # GPSLatitude should be mapped to UUID
    assert "9e1f3b7d-6c4a-5e8d-7f2b-1a9c4e3d8b5f-M" in normalized


def test_normalize_metadata_dict_preserves_unmapped(
    sample_registry: Dict[str, Any],
) -> None:
    """Test that unmapped fields are preserved with special prefix."""
    metadata = {
        "creation_time": "2024-01-15T10:30:00.000000Z",
        "custom_field": "custom_value",
    }

    normalized = metadata_registry.normalize_metadata_dict("ffprobe", metadata)

    # Unmapped field should be preserved with prefix
    assert "unmapped:ffprobe:custom_field" in normalized
    assert normalized["unmapped:ffprobe:custom_field"] == "custom_value"


def test_get_field_description_temporal(sample_registry: Dict[str, Any]) -> None:
    """Test getting field description for temporal metadata."""
    uuid = "3d4f8a9c-1e7b-5c3d-9a2f-4e8c1b7d3a9f-M"
    description = metadata_registry.get_field_description(uuid)

    assert description is not None
    assert "created" in description.lower() or "captured" in description.lower()


def test_get_field_description_spatial(sample_registry: Dict[str, Any]) -> None:
    """Test getting field description for spatial metadata."""
    lat_uuid = "9e1f3b7d-6c4a-5e8d-7f2b-1a9c4e3d8b5f-M"
    description = metadata_registry.get_field_description(lat_uuid)

    assert description is not None
    assert "latitude" in description.lower()


def test_get_field_description_not_found(sample_registry: Dict[str, Any]) -> None:
    """Test that non-existent UUID returns None for description."""
    description = metadata_registry.get_field_description("00000000-0000-0000-0000-000000000000-M")
    assert description is None


def test_get_all_field_uuids(sample_registry: Dict[str, Any]) -> None:
    """Test getting all metadata field UUIDs."""
    uuids = metadata_registry.get_all_field_uuids()

    assert isinstance(uuids, list)
    assert len(uuids) > 0

    # All UUIDs should end with -M
    for uuid in uuids:
        assert uuid.endswith("-M"), f"UUID {uuid} should end with -M suffix"

    # Should include known UUIDs
    assert "3d4f8a9c-1e7b-5c3d-9a2f-4e8c1b7d3a9f-M" in uuids  # creation_datetime
    assert "9e1f3b7d-6c4a-5e8d-7f2b-1a9c4e3d8b5f-M" in uuids  # gps_latitude


def test_metadata_registry_caching(sample_registry: Dict[str, Any]) -> None:
    """Test that registry is cached after first load."""
    # Load registry twice
    registry1 = metadata_registry.load_metadata_registry()
    registry2 = metadata_registry.load_metadata_registry()

    # Should return same object (cached)
    assert registry1 is registry2


def test_metadata_registry_all_fields_have_uuids(
    sample_registry: Dict[str, Any],
) -> None:
    """Test that all fields in registry have valid UUIDs."""
    metadata_fields = sample_registry.get("metadata_fields", {})

    for category_name, category_fields in metadata_fields.items():
        for field_name, field_info in category_fields.items():
            assert "uuid" in field_info, f"Field {category_name}.{field_name} missing UUID"
            assert field_info["uuid"].endswith("-M"), f"Field {category_name}.{field_name} UUID should end with -M"


def test_metadata_registry_all_fields_have_tool_mappings(
    sample_registry: Dict[str, Any],
) -> None:
    """Test that all fields have at least one tool mapping."""
    metadata_fields = sample_registry.get("metadata_fields", {})

    for category_name, category_fields in metadata_fields.items():
        for field_name, field_info in category_fields.items():
            assert "tool_mappings" in field_info, f"Field {category_name}.{field_name} missing tool_mappings"
            assert len(field_info["tool_mappings"]) > 0, f"Field {category_name}.{field_name} has empty tool_mappings"


def test_apple_specific_live_photo_content_id(sample_registry: Dict[str, Any]) -> None:
    """Test Apple-specific Live Photo content identifier field."""
    uuid = metadata_registry.lookup_metadata_field_uuid("exiftool", "QuickTime:ContentIdentifier")
    assert uuid is not None
    assert uuid.endswith("-M")

    canonical = metadata_registry.get_canonical_field_name(uuid)
    assert canonical == "live_photo_content_id"


def test_technical_camera_fields(sample_registry: Dict[str, Any]) -> None:
    """Test technical camera metadata fields."""
    make_uuid = metadata_registry.lookup_metadata_field_uuid("exiftool", "EXIF:Make")
    model_uuid = metadata_registry.lookup_metadata_field_uuid("exiftool", "EXIF:Model")

    assert make_uuid is not None
    assert model_uuid is not None
    assert make_uuid != model_uuid

    make_canonical = metadata_registry.get_canonical_field_name(make_uuid)
    model_canonical = metadata_registry.get_canonical_field_name(model_uuid)

    assert make_canonical == "camera_make"
    assert model_canonical == "camera_model"


def test_authorship_fields(sample_registry: Dict[str, Any]) -> None:
    """Test authorship metadata fields (creator, copyright)."""
    creator_uuid = metadata_registry.lookup_metadata_field_uuid("exiftool", "EXIF:Artist")
    copyright_uuid = metadata_registry.lookup_metadata_field_uuid("exiftool", "EXIF:Copyright")

    assert creator_uuid is not None
    assert copyright_uuid is not None
    assert creator_uuid != copyright_uuid

    # FFprobe should map to same UUIDs
    ffprobe_creator = metadata_registry.lookup_metadata_field_uuid("ffprobe", "artist")
    ffprobe_copyright = metadata_registry.lookup_metadata_field_uuid("ffprobe", "copyright")

    assert ffprobe_creator == creator_uuid
    assert ffprobe_copyright == copyright_uuid
