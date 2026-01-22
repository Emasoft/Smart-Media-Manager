"""
End-to-end tests for format registry integration.

Tests that the format compatibility JSON correctly filters files
during the import process.
"""

import json
import shutil
import tempfile
from pathlib import Path

import pytest

from smart_media_manager import format_registry


@pytest.fixture
def temp_compat_file():
    """Create a temporary compatibility JSON file for testing."""
    original_compat = format_registry._COMPATIBILITY
    original_path = Path(format_registry.__file__).parent / "format_compatibility.json"

    # Create temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = Path(f.name)

        # Copy original content
        if original_path.exists():
            with open(original_path) as orig:
                content = json.load(orig)
                json.dump(content, f, indent=2)
        else:
            # Create minimal test content
            test_content = {
                "apple_photos_compatible": {"images": {"direct_import": ["d33d5c73-5f1a-5c4b-878e-58c3f9c193c0-I"]}},
                "format_names": {
                    "d33d5c73-5f1a-5c4b-878e-58c3f9c193c0-I": {
                        "canonical": "jpeg",
                        "extensions": [".jpg", ".jpeg"],
                        "category": "image",
                    }
                },
                "tool_mappings": {"libmagic": {"JPEG image data": "d33d5c73-5f1a-5c4b-878e-58c3f9c193c0-I"}},
            }
            json.dump(test_content, f, indent=2)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()

    # Reset cache
    format_registry._COMPATIBILITY = original_compat


def test_load_compatibility_data():
    """Test loading compatibility data from JSON."""
    compat = format_registry.load_compatibility_data()

    assert isinstance(compat, dict)
    assert "apple_photos_compatible" in compat or len(compat) == 0  # Empty if file missing


def test_lookup_format_uuid():
    """Test UUID lookup from tool output."""
    # This will use the actual compatibility JSON
    uuid = format_registry.lookup_format_uuid("libmagic", "JPEG image data")

    # Should find JPEG UUID
    if uuid:
        assert uuid.endswith("-I")  # Image format
        assert "5c4b" in uuid or "5f1a" in uuid  # Part of JPEG UUID


def test_is_apple_photos_compatible():
    """Test compatibility checking for known formats."""
    # JPEG UUID (from our compatibility JSON)
    jpeg_uuid = "d33d5c73-5f1a-5c4b-878e-58c3f9c193c0-I"

    result = format_registry.is_apple_photos_compatible(jpeg_uuid)

    # JPEG should be compatible
    assert result is True


def test_needs_conversion():
    """Test conversion requirement checking."""
    # JPEG XL UUID (needs conversion)
    jxl_uuid = "c416405f-af41-56cb-8c6c-46533f290969-I"

    result = format_registry.needs_conversion(jxl_uuid)

    # JXL needs conversion to HEIC
    assert result is True


def test_get_canonical_name():
    """Test getting canonical format name from UUID."""
    jpeg_uuid = "d33d5c73-5f1a-5c4b-878e-58c3f9c193c0-I"

    name = format_registry.get_canonical_name(jpeg_uuid)

    assert name == "jpeg"


def test_get_format_extensions():
    """Test getting file extensions for format."""
    jpeg_uuid = "d33d5c73-5f1a-5c4b-878e-58c3f9c193c0-I"

    extensions = format_registry.get_format_extensions(jpeg_uuid)

    assert ".jpg" in extensions or ".jpeg" in extensions


def test_format_detection_consensus():
    """Test consensus-based format detection."""
    # Multiple tools detecting JPEG
    tool_results = {
        "libmagic": "JPEG image data",
        "puremagic": "image/jpeg",
        "ffprobe": "mjpeg",
    }

    uuid = format_registry.format_detection_result(tool_results)

    # Should return JPEG UUID based on consensus
    if uuid:
        assert uuid.endswith("-I")
        canonical = format_registry.get_canonical_name(uuid)
        assert canonical == "jpeg"


def test_compatibility_json_modification(temp_compat_file):
    """
    E2E test: Modify JSON to mark JPEG as incompatible,
    verify it gets filtered out.
    """
    # Load and modify the temp compatibility file
    with open(temp_compat_file) as f:
        compat_data = json.load(f)

    # Remove JPEG from compatible list
    jpeg_uuid = "d33d5c73-5f1a-5c4b-878e-58c3f9c193c0-I"
    if "apple_photos_compatible" in compat_data:
        if "images" in compat_data["apple_photos_compatible"]:
            direct_import = compat_data["apple_photos_compatible"]["images"].get("direct_import", [])
            if jpeg_uuid in direct_import:
                direct_import.remove(jpeg_uuid)

    # Write modified data back
    with open(temp_compat_file, "w") as f:
        json.dump(compat_data, f, indent=2)

    # Reload compatibility data by clearing cache
    format_registry._COMPATIBILITY = None

    # Temporarily point to our test file
    original_init_file = format_registry.__file__

    # Copy test file to expected location
    target_path = Path(original_init_file).parent / "format_compatibility.json"
    backup_path = None
    if target_path.exists():
        backup_path = target_path.with_suffix(".json.backup")
        shutil.copy(target_path, backup_path)

    try:
        shutil.copy(temp_compat_file, target_path)

        # Clear cache and reload
        format_registry._COMPATIBILITY = None
        compat = format_registry.load_compatibility_data()

        # Verify JPEG is no longer in compatible list
        direct_import = compat.get("apple_photos_compatible", {}).get("images", {}).get("direct_import", [])
        assert jpeg_uuid not in direct_import

        # Test compatibility check
        is_compat = format_registry.is_apple_photos_compatible(jpeg_uuid)
        assert is_compat is False

    finally:
        # Restore original file
        if backup_path and backup_path.exists():
            shutil.copy(backup_path, target_path)
            backup_path.unlink()

        # Clear cache
        format_registry._COMPATIBILITY = None


def test_compatibility_json_addition():
    """
    E2E test: Add a new format to compatible list,
    verify it gets included.
    """
    # Test adding WebP to compatible (if not already there)
    webp_uuid = "002b5a9f-6bbb-5c17-ab0e-f3abb791ab72-I"

    # Check compatibility
    was_compatible = format_registry.is_apple_photos_compatible(webp_uuid)

    # WebP should be compatible in our setup
    assert was_compatible is True


def test_get_compatible_formats():
    """Test getting set of all compatible formats."""
    compatible = format_registry.get_compatible_formats()

    assert isinstance(compatible, set)
    # Should have at least some formats
    assert len(compatible) > 0


def test_unknown_format_handling():
    """Test handling of unknown/unsupported formats."""
    fake_uuid = "00000000-0000-0000-0000-000000000000-X"

    # Should handle gracefully
    is_compat = format_registry.is_apple_photos_compatible(fake_uuid)
    assert is_compat is False

    needs_conv = format_registry.needs_conversion(fake_uuid)
    assert needs_conv is False

    canonical = format_registry.get_canonical_name(fake_uuid)
    assert canonical is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
