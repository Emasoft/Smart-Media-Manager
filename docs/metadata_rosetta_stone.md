# Metadata Registry: The Rosetta Stone Architecture

## Purpose

The `metadata_registry.json` file is our **Rosetta Stone** for translating metadata field names across different tools. It enables:

1. **Reading metadata** from any tool → Translate to internal UUIDs
2. **Writing metadata** with any tool → Translate from UUIDs to tool-specific names
3. **Cross-tool metadata preservation** → Read with Tool A, write with Tool B

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    metadata_registry.json                        │
│                     (The Rosetta Stone)                          │
│                                                                  │
│  UUID: "3d4f8a9c-1e7b-5c3d-9a2f-4e8c1b7d3a9f-M"                 │
│  Canonical: "creation_datetime"                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ ExifTool         FFprobe           FFmpeg                   │ │
│  │ ─────────        ────────          ──────                   │ │
│  │ EXIF:DateTimeOriginal  creation_time    creation_time       │ │
│  │ EXIF:CreateDate        date             date                │ │
│  │ XMP:CreateDate                                              │ │
│  │ IPTC:DateCreated                                            │ │
│  │ QuickTime:CreateDate                                        │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow: Metadata Preservation During Conversion

### Example: Convert JPEG → MP4 with FFmpeg

```python
# Step 1: Read original file metadata with ExifTool
exiftool_output = {
    "EXIF:DateTimeOriginal": "2024:01:15 10:30:00",
    "EXIF:Artist": "John Doe",
    "XMP:Title": "Sunset Photo",
    "XMP:Description": "Beautiful sunset over the ocean"
}

# Step 2: Normalize to UUIDs using metadata_registry
from smart_media_manager import metadata_registry

uuid_metadata = metadata_registry.normalize_metadata_dict("exiftool", exiftool_output)
# Result:
# {
#   "3d4f8a9c-1e7b-5c3d-9a2f-4e8c1b7d3a9f-M": "2024:01:15 10:30:00",  # creation_datetime
#   "8a3d9f2c-5e7b-5c1d-9f4a-3e8b2c7d1f9a-M": "John Doe",            # creator
#   "1c7d9f3a-8e2b-5d4c-9a7f-2e8b3c1d9f5a-M": "Sunset Photo",        # title
#   "6e8b4c2d-9f1a-5c7d-8e3b-4f9a2c7d1e5b-M": "Beautiful sunset..."  # description
# }

# Step 3: Convert file with FFmpeg
subprocess.run(["ffmpeg", "-i", "input.jpg", "output.mp4"])

# Step 4: Translate UUIDs to FFmpeg field names
ffmpeg_metadata = {}
for uuid, value in uuid_metadata.items():
    # Get FFmpeg field name for this UUID
    ffmpeg_fields = metadata_registry.get_tool_field_names(uuid, "ffmpeg")
    if ffmpeg_fields:
        # Use first FFmpeg field name
        ffmpeg_metadata[ffmpeg_fields[0]] = value

# Result:
# {
#   "creation_time": "2024:01:15 10:30:00",
#   "artist": "John Doe",
#   "title": "Sunset Photo",
#   "description": "Beautiful sunset over the ocean"
# }

# Step 5: Write metadata to converted file with FFmpeg
for key, value in ffmpeg_metadata.items():
    subprocess.run(["ffmpeg", "-i", "output.mp4", "-metadata", f"{key}={value}", ...])
```

## Why This Matters

### Problem Without UUID Translation:
```python
# Reading from ExifTool
original_metadata = {"EXIF:Artist": "John Doe"}

# Converting with FFmpeg
# ❌ WRONG: "EXIF:Artist" is not a valid FFmpeg field name!
subprocess.run(["ffmpeg", "-metadata", "EXIF:Artist=John Doe", ...])
# FFmpeg ignores this - metadata lost!
```

### Solution With UUID Translation:
```python
# Reading from ExifTool
original_metadata = {"EXIF:Artist": "John Doe"}

# Translate to UUID
uuid = metadata_registry.lookup_metadata_field_uuid("exiftool", "EXIF:Artist")
# → "8a3d9f2c-5e7b-5c1d-9f4a-3e8b2c7d1f9a-M" (creator)

# Translate to FFmpeg
ffmpeg_field = metadata_registry.translate_field_name("exiftool", "EXIF:Artist", "ffmpeg")
# → "artist"

# ✅ CORRECT: Use FFmpeg's field name
subprocess.run(["ffmpeg", "-metadata", "artist=John Doe", ...])
# Metadata preserved!
```

## Registry Structure

Each metadata field has:

```json
{
  "creation_datetime": {
    "uuid": "3d4f8a9c-1e7b-5c3d-9a2f-4e8c1b7d3a9f-M",
    "canonical": "creation_datetime",
    "description": "Date and time when the media was originally created/captured",
    "tool_mappings": {
      "exiftool": ["EXIF:DateTimeOriginal", "EXIF:CreateDate", ...],
      "ffprobe": ["creation_time", "date"],
      "ffmpeg": ["creation_time", "date"]
    }
  }
}
```

### Key Components:

- **uuid**: Globally unique identifier with `-M` suffix (M = Metadata)
- **canonical**: Human-readable standardized name
- **description**: What this field represents
- **tool_mappings**: Field names used by each tool

## API Functions

### 1. Reading Metadata (Tool → UUID)

```python
# Look up UUID from tool-specific field name
uuid = metadata_registry.lookup_metadata_field_uuid("exiftool", "EXIF:Artist")
# → "8a3d9f2c-5e7b-5c1d-9f4a-3e8b2c7d1f9a-M"

# Normalize entire metadata dict
normalized = metadata_registry.normalize_metadata_dict("exiftool", metadata_dict)
# → {"uuid1": "value1", "uuid2": "value2", ...}
```

### 2. Writing Metadata (UUID → Tool)

```python
# Get tool-specific field names for a UUID
field_names = metadata_registry.get_tool_field_names(uuid, "ffmpeg")
# → ["artist", "author"]

# Translate field name between tools
ffmpeg_field = metadata_registry.translate_field_name("exiftool", "EXIF:Artist", "ffmpeg")
# → "artist"
```

### 3. Getting Information

```python
# Get canonical name
canonical = metadata_registry.get_canonical_field_name(uuid)
# → "creator"

# Get description
description = metadata_registry.get_field_description(uuid)
# → "Person or entity that created the media"
```

## Cross-Tool Coverage

Current registry status (v3.1.0):

- **Total fields**: 70
- **Cross-tool fields**: 49 (70%)
- **Single-tool fields**: 21 (30%, mostly photography-specific)

### Common Transferable Fields (All Cross-Mapped):
- creation_datetime, creator, title, description, copyright
- camera_make, camera_model, software, orientation
- audio/music: album, artist, composer, genre, track, disc
- broadcast: show, episode_id, season, network
- technical: duration, bitrate, frame_rate, codecs

### Photography-Specific (ExifTool Only):
- Camera exposure: ISO, aperture, shutter speed, white balance, flash
- Lens info: focal length, lens model/make
- GPS: Individual lat/lon fields (FFmpeg uses composite ISO6709)
- IPTC: keywords, rating, credit, source

**Note**: Photography-specific fields have no FFmpeg equivalent because FFmpeg has limited EXIF support. These are unavoidably lost during image→video conversion.

## Future Extensibility

When adding new conversion tools:

1. Add tool name to `tool_mappings` for each field
2. Map tool-specific field names to existing UUIDs
3. Same UUID = same semantic meaning across all tools

Example: Adding ImageMagick support:
```json
{
  "creation_datetime": {
    "uuid": "3d4f8a9c-1e7b-5c3d-9a2f-4e8c1b7d3a9f-M",
    "tool_mappings": {
      "exiftool": ["EXIF:DateTimeOriginal", ...],
      "ffprobe": ["creation_time", "date"],
      "ffmpeg": ["creation_time", "date"],
      "imagemagick": ["exif:DateTimeOriginal"]  ← New tool added
    }
  }
}
```

## Best Practices

1. **Always use UUID as internal representation**
   - Never store tool-specific field names internally
   - Always translate to/from UUIDs at boundaries

2. **Preserve unmapped fields**
   - Fields without UUID mapping stored as "unmapped:tool:fieldname"
   - Allows round-trip preservation of tool-specific metadata

3. **Handle context-dependent fields**
   - Some tool fields map to different UUIDs based on context
   - Example: `codec_name` → `video_codec` or `audio_codec` (stream type dependent)

4. **Maintain backward compatibility**
   - Never change existing UUIDs
   - Only add new fields or extend tool_mappings

## Testing

```python
# Test cross-tool translation
def test_cross_tool_consistency():
    # ExifTool → UUID → FFmpeg
    exiftool_uuid = metadata_registry.lookup_metadata_field_uuid(
        "exiftool", "EXIF:DateTimeOriginal"
    )
    ffprobe_uuid = metadata_registry.lookup_metadata_field_uuid(
        "ffprobe", "creation_time"
    )

    # Should be same UUID
    assert exiftool_uuid == ffprobe_uuid

    # Translate between tools
    ffmpeg_field = metadata_registry.translate_field_name(
        "exiftool", "EXIF:DateTimeOriginal", "ffmpeg"
    )
    assert ffmpeg_field == "creation_time"
```

## Conclusion

The metadata registry is the **foundation of tool-agnostic metadata handling**. By translating all tool-specific field names to canonical UUIDs, we enable:

- **Seamless metadata preservation** during conversions
- **Tool independence** (add new tools without changing application code)
- **Semantic consistency** (same meaning = same UUID, regardless of tool)

This "Rosetta Stone" architecture ensures that metadata survives format conversions and tool changes, preserving the user's valuable information across their entire media library.
