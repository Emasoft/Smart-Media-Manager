"""
Audit cross-tool metadata field mappings.

Verifies that semantically equivalent fields across ExifTool, FFmpeg, and FFprobe
all map to the SAME UUID (critical for metadata preservation during conversions).
"""
import json
from pathlib import Path
from collections import defaultdict

# Load registry
repo_root = Path(__file__).resolve().parents[1]
registry_path = repo_root / "smart_media_manager" / "metadata_registry.json"
with open(registry_path) as f:
    registry = json.load(f)

metadata_fields = registry["metadata_fields"]

print("=" * 80)
print("CROSS-TOOL METADATA MAPPING AUDIT")
print("=" * 80)
print()
print("Checking that equivalent fields map to SAME UUID across tools...")
print()

# Analyze each field
issues_found = []
good_mappings = []

for category, fields in metadata_fields.items():
    for field_name, field_info in fields.items():
        canonical = field_info["canonical"]
        uuid = field_info["uuid"]
        mappings = field_info["tool_mappings"]

        has_exiftool = len(mappings.get("exiftool", [])) > 0
        has_ffprobe = len(mappings.get("ffprobe", [])) > 0
        has_ffmpeg = len(mappings.get("ffmpeg", [])) > 0

        # Check if field has mappings for multiple tools
        tool_count = sum([has_exiftool, has_ffprobe, has_ffmpeg])

        if tool_count >= 2:
            # Good - this field maps across multiple tools
            tools = []
            if has_exiftool:
                tools.append(f"ExifTool({len(mappings['exiftool'])} fields)")
            if has_ffprobe:
                tools.append(f"FFprobe({len(mappings['ffprobe'])} fields)")
            if has_ffmpeg:
                tools.append(f"FFmpeg({len(mappings['ffmpeg'])} fields)")

            good_mappings.append({
                "canonical": canonical,
                "category": category,
                "tools": " + ".join(tools),
                "uuid": uuid
            })
        elif tool_count == 1:
            # Potential issue - field only mapped in one tool
            tool = "ExifTool" if has_exiftool else ("FFprobe" if has_ffprobe else "FFmpeg")
            issues_found.append({
                "canonical": canonical,
                "category": category,
                "tool": tool,
                "uuid": uuid,
                "description": field_info.get("description", "")
            })

print("✓ GOOD CROSS-TOOL MAPPINGS (same UUID across multiple tools):")
print("=" * 80)
for mapping in good_mappings:
    print(f"  {mapping['canonical']:30} → {mapping['tools']}")
print()
print(f"Total: {len(good_mappings)} fields properly mapped across tools")
print()

if issues_found:
    print("⚠️  FIELDS MAPPED IN ONLY ONE TOOL:")
    print("=" * 80)
    print("These may be tool-specific, OR they may need FFmpeg/FFprobe equivalents:")
    print()
    for issue in issues_found:
        print(f"  {issue['canonical']:30} ({issue['category']})")
        print(f"    Only in: {issue['tool']}")
        print(f"    Description: {issue['description'][:60]}...")
        print()
    print(f"Total: {len(issues_found)} single-tool fields")
    print()

# Check for common metadata that SHOULD be mapped across tools
print("=" * 80)
print("CHECKING COMMON METADATA FIELDS FOR PROPER CROSS-TOOL MAPPING")
print("=" * 80)
print()

# Common fields that should exist across ExifTool + FFmpeg/FFprobe
common_fields = {
    "creation_datetime": {
        "exiftool": ["EXIF:DateTimeOriginal", "EXIF:CreateDate"],
        "ffprobe": ["creation_time"],
        "ffmpeg": ["creation_time"]
    },
    "creator": {
        "exiftool": ["EXIF:Artist"],
        "ffprobe": ["artist"],
        "ffmpeg": ["artist"]
    },
    "title": {
        "exiftool": ["XMP:Title"],
        "ffprobe": ["title"],
        "ffmpeg": ["title"]
    },
    "description": {
        "exiftool": ["XMP:Description", "IPTC:Caption-Abstract"],
        "ffprobe": ["comment", "description"],
        "ffmpeg": ["comment", "description"]
    },
    "copyright": {
        "exiftool": ["EXIF:Copyright"],
        "ffprobe": ["copyright"],
        "ffmpeg": ["copyright"]
    }
}

all_ok = True
for canonical, expected_mappings in common_fields.items():
    # Find this field in registry
    found = False
    for category, fields in metadata_fields.items():
        for field_name, field_info in fields.items():
            if field_info["canonical"] == canonical:
                found = True
                actual_mappings = field_info["tool_mappings"]

                print(f"✓ {canonical}:")

                # Check each tool
                for tool, expected_fields in expected_mappings.items():
                    actual_fields = actual_mappings.get(tool, [])

                    if len(actual_fields) > 0:
                        print(f"    {tool:12} → {actual_fields}")
                    else:
                        print(f"    {tool:12} → ⚠️  MISSING! Expected: {expected_fields}")
                        all_ok = False
                print()
                break
        if found:
            break

    if not found:
        print(f"⚠️  {canonical}: NOT FOUND IN REGISTRY!")
        all_ok = False
        print()

if all_ok:
    print("✓ All common metadata fields properly mapped across tools!")
else:
    print("⚠️  Some common fields missing FFmpeg/FFprobe mappings!")

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total fields: {sum(len(fields) for fields in metadata_fields.values())}")
print(f"Multi-tool fields: {len(good_mappings)}")
print(f"Single-tool fields: {len(issues_found)}")
print()
print("RECOMMENDATION:")
print("  For metadata preservation during FFmpeg conversions, ensure all")
print("  ExifTool fields have equivalent FFmpeg/FFprobe mappings to same UUID.")
