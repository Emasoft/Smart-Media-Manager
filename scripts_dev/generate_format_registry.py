#!/usr/bin/env python3
"""
Generate FORMAT_REGISTRY.md with UUID-based unified naming system.
Maps format names across different detection tools to create a single source of truth.
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Tuple


def generate_uuid(seed: str, suffix: str) -> str:
    """Generate deterministic UUID from seed string with type suffix.

    Suffix letters for easy identification:
    - C: Container format
    - V: Video codec
    - A: Audio codec
    - I: Image format
    - R: RAW camera format
    - P: Pixel format
    - S: Sample format (audio)
    - L: Channel layout
    """
    # Use UUID5 with a custom namespace for reproducibility
    namespace = uuid.UUID("12345678-1234-5678-1234-567812345678")
    base_uuid = str(uuid.uuid5(namespace, seed))
    # Append suffix letter for type identification
    return f"{base_uuid}-{suffix}"


def run_ffprobe_queries() -> Dict[str, str]:
    """Run all ffprobe discovery commands."""
    import subprocess

    commands = {
        "formats": ["ffprobe", "-hide_banner", "-formats"],
        "codecs": ["ffprobe", "-hide_banner", "-codecs"],
        "pix_fmts": ["ffprobe", "-hide_banner", "-pix_fmts"],
        "sample_fmts": ["ffprobe", "-hide_banner", "-sample_fmts"],
        "layouts": ["ffprobe", "-hide_banner", "-layouts"],
    }

    outputs = {}
    for key, cmd in commands.items():
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            outputs[key] = result.stdout
        except Exception as e:
            print(f"Warning: Failed to run {' '.join(cmd)}: {e}")
            outputs[key] = ""

    return outputs


def parse_formats_from_ffprobe(text: str) -> List[Dict]:
    """Parse container formats from ffprobe -formats output."""
    import re

    formats = []
    started = False

    for line in text.split("\n"):
        if line.strip().startswith("--"):
            started = True
            continue

        if not started:
            continue

        # Format: " D  ext            Description"
        match = re.match(r"\s*([D ][E ])\s+(\S+)\s+(.+)?", line)
        if match:
            flags, name, description = match.groups()
            formats.append(
                {
                    "name": name,
                    "description": description.strip() if description else "",
                    "demux": "D" in flags,
                    "mux": "E" in flags,
                }
            )

    return formats


def parse_codecs_from_ffprobe(text: str, codec_type: str) -> List[Dict]:
    """Parse codecs from ffprobe -codecs output."""
    import re

    codecs = []
    started = False

    for line in text.split("\n"):
        if line.strip().startswith("------"):
            started = True
            continue

        if not started:
            continue

        # Format: " DEV... codec_name        Description"
        match = re.match(r"\s*([D ][E ])([VAS\.\!])([I \.])([L \.])([S \.])\s+(\S+)\s+(.+)?", line)
        if match:
            d_flag, type_flag, intra, lossy, lossless, name, description = match.groups()

            # Filter by requested type
            if codec_type == "video" and type_flag != "V":
                continue
            if codec_type == "audio" and type_flag != "A":
                continue

            codecs.append(
                {
                    "name": name,
                    "description": description.strip() if description else "",
                    "decode": "D" in d_flag,
                    "encode": "E" in d_flag,
                    "type": type_flag,
                }
            )

    return codecs


def parse_pix_fmts_from_ffprobe(text: str) -> List[str]:
    """Parse pixel formats from ffprobe -pix_fmts output."""
    import re

    pix_fmts = []
    started = False

    for line in text.split("\n"):
        if line.strip().startswith("-----"):
            started = True
            continue

        if not started:
            continue

        # Format: "IO... format_name        nb_components nb_bits"
        # Flags are I, O, H, P, B (5 chars) followed by space and name
        match = re.match(r"\s*[IOHPBhpb\.]{5}\s+(\S+)", line)
        if match:
            pix_fmts.append(match.group(1))

    return pix_fmts


def parse_sample_fmts_from_ffprobe(text: str) -> List[str]:
    """Parse sample formats from ffprobe -sample_fmts output."""
    sample_fmts = []
    started = False

    for line in text.split("\n"):
        line = line.strip()
        if not line or line.startswith("name"):
            started = True
            continue

        if started and line:
            # Format: "name   depth"
            parts = line.split()
            if parts:
                sample_fmts.append(parts[0])

    return sample_fmts


def parse_layouts_from_ffprobe(text: str) -> List[str]:
    """Parse channel layouts from ffprobe -layouts output."""
    import re

    layouts = []
    in_standard_section = False

    for line in text.split("\n"):
        if "Standard channel layouts:" in line:
            in_standard_section = True
            continue

        if not in_standard_section:
            continue

        # Stop when we hit Individual channels section (comes after Standard in output)
        if "Individual channels:" in line:
            break

        line = line.strip()
        if not line or line.startswith("NAME"):
            continue

        # Format: "NAME            decomposition"
        # Extract first word before whitespace
        match = re.match(r"^(\S+)\s+", line)
        if match:
            layouts.append(match.group(1))

    return layouts


def load_ffprobe_formats() -> Tuple[List[Dict], List[Dict], List[Dict], List[str], List[str], List[str]]:
    """Load formats discovered by ffprobe."""
    print("Running ffprobe queries...")
    outputs = run_ffprobe_queries()

    containers = parse_formats_from_ffprobe(outputs["formats"])
    video_codecs = parse_codecs_from_ffprobe(outputs["codecs"], "video")
    audio_codecs = parse_codecs_from_ffprobe(outputs["codecs"], "audio")
    pixel_fmts = parse_pix_fmts_from_ffprobe(outputs["pix_fmts"])
    sample_fmts = parse_sample_fmts_from_ffprobe(outputs["sample_fmts"])
    layouts = parse_layouts_from_ffprobe(outputs["layouts"])

    print(f"  Parsed {len(containers)} containers")
    print(f"  Parsed {len(video_codecs)} video codecs")
    print(f"  Parsed {len(audio_codecs)} audio codecs")
    print(f"  Parsed {len(pixel_fmts)} pixel formats")
    print(f"  Parsed {len(sample_fmts)} sample formats")
    print(f"  Parsed {len(layouts)} channel layouts")

    return containers, video_codecs, audio_codecs, pixel_fmts, sample_fmts, layouts


def create_format_mapping(name: str, category: str) -> Dict:
    """Create format mapping entry with UUID and tool-specific names."""
    # Map category to suffix letter
    suffix_map = {
        "container": "C",
        "video_codec": "V",
        "audio_codec": "A",
        "image_format": "I",
        "raw_format": "R",
        "pixel_format": "P",
        "sample_format": "S",
        "channel_layout": "L",
    }
    suffix = suffix_map.get(category, "X")
    uid = generate_uuid(f"{category}:{name}", suffix)

    mapping = {
        "uuid": uid,
        "category": category,
        "canonical_name": name,
        "ffprobe": name,
        "libmagic": "",
        "puremagic": "",
        "pyfsig": "",
        "binwalk": "",
        "rawpy": "",
        "pillow": "",
        "exiftool": "",
    }

    return mapping


def add_known_mappings(registry: Dict[str, Dict]):
    """Add known mappings between tool names for common formats."""
    # Common video codecs
    codec_mappings = {
        "h264": {
            "ffprobe": "h264",
            "libmagic": "MPEG v4 system",
            "puremagic": "video/mp4",
            "pillow": "N/A",
            "exiftool": "AVC",
        },
        "hevc": {
            "ffprobe": "hevc",
            "libmagic": "ISO Media",
            "puremagic": "video/mp4",
            "pillow": "N/A",
            "exiftool": "HEVC",
        },
        "vp9": {
            "ffprobe": "vp9",
            "libmagic": "WebM",
            "puremagic": "video/webm",
            "pillow": "N/A",
            "exiftool": "VP9",
        },
        "av1": {
            "ffprobe": "av1",
            "libmagic": "ISO Media",
            "puremagic": "video/mp4",
            "pillow": "N/A",
            "exiftool": "AV1",
        },
    }

    # Common image formats
    image_mappings = {
        "jpeg": {
            "ffprobe": "mjpeg",
            "libmagic": "JPEG image data",
            "puremagic": "image/jpeg",
            "pillow": "JPEG",
            "exiftool": "JPEG",
        },
        "png": {
            "ffprobe": "png",
            "libmagic": "PNG image data",
            "puremagic": "image/png",
            "pillow": "PNG",
            "exiftool": "PNG",
        },
        "gif": {
            "ffprobe": "gif",
            "libmagic": "GIF image data",
            "puremagic": "image/gif",
            "pillow": "GIF",
            "exiftool": "GIF",
        },
        "webp": {
            "ffprobe": "webp",
            "libmagic": "Web/P image",
            "puremagic": "image/webp",
            "pillow": "WEBP",
            "exiftool": "WebP",
        },
        "heif": {
            "ffprobe": "heif",
            "libmagic": "ISO Media",
            "puremagic": "image/heif",
            "pillow": "HEIF",
            "exiftool": "HEIF",
        },
        "avif": {
            "ffprobe": "avif",
            "libmagic": "ISO Media",
            "puremagic": "image/avif",
            "pillow": "AVIF",
            "exiftool": "AVIF",
        },
        "jxl": {
            "ffprobe": "jxl",
            "libmagic": "JPEG XL codestream",
            "puremagic": "image/jxl",
            "pillow": "N/A",
            "exiftool": "JXL",
        },
        "tiff": {
            "ffprobe": "tiff",
            "libmagic": "TIFF image data",
            "puremagic": "image/tiff",
            "pillow": "TIFF",
            "exiftool": "TIFF",
        },
    }

    # RAW formats
    raw_mappings = {
        "cr2": {
            "ffprobe": "N/A",
            "libmagic": "Canon CR2 RAW",
            "puremagic": "image/x-canon-cr2",
            "pillow": "N/A",
            "rawpy": "CR2",
            "exiftool": "CR2",
        },
        "cr3": {
            "ffprobe": "N/A",
            "libmagic": "Canon CR3",
            "puremagic": "image/x-canon-cr3",
            "pillow": "N/A",
            "rawpy": "CR3",
            "exiftool": "CR3",
        },
        "nef": {
            "ffprobe": "N/A",
            "libmagic": "Nikon NEF RAW",
            "puremagic": "image/x-nikon-nef",
            "pillow": "N/A",
            "rawpy": "NEF",
            "exiftool": "NEF",
        },
        "arw": {
            "ffprobe": "N/A",
            "libmagic": "Sony ARW RAW",
            "puremagic": "image/x-sony-arw",
            "pillow": "N/A",
            "rawpy": "ARW",
            "exiftool": "ARW",
        },
        "raf": {
            "ffprobe": "N/A",
            "libmagic": "Fujifilm RAF",
            "puremagic": "image/x-fuji-raf",
            "pillow": "N/A",
            "rawpy": "RAF",
            "exiftool": "RAF",
        },
        "orf": {
            "ffprobe": "N/A",
            "libmagic": "Olympus ORF RAW",
            "puremagic": "image/x-olympus-orf",
            "pillow": "N/A",
            "rawpy": "ORF",
            "exiftool": "ORF",
        },
        "rw2": {
            "ffprobe": "N/A",
            "libmagic": "Panasonic RW2 RAW",
            "puremagic": "image/x-panasonic-rw2",
            "pillow": "N/A",
            "rawpy": "RW2",
            "exiftool": "RW2",
        },
        "dng": {
            "ffprobe": "N/A",
            "libmagic": "Adobe DNG",
            "puremagic": "image/x-adobe-dng",
            "pillow": "N/A",
            "rawpy": "DNG",
            "exiftool": "DNG",
        },
    }

    # Containers
    container_mappings = {
        "mp4": {
            "ffprobe": "mp4",
            "libmagic": "ISO Media, MP4",
            "puremagic": "video/mp4",
            "pillow": "N/A",
            "exiftool": "MP4",
        },
        "mov": {
            "ffprobe": "mov",
            "libmagic": "ISO Media, Apple QuickTime",
            "puremagic": "video/quicktime",
            "pillow": "N/A",
            "exiftool": "QuickTime",
        },
        "mkv": {
            "ffprobe": "matroska",
            "libmagic": "Matroska data",
            "puremagic": "video/x-matroska",
            "pillow": "N/A",
            "exiftool": "Matroska",
        },
        "webm": {
            "ffprobe": "webm",
            "libmagic": "WebM",
            "puremagic": "video/webm",
            "pillow": "N/A",
            "exiftool": "WebM",
        },
        "avi": {
            "ffprobe": "avi",
            "libmagic": "RIFF (little-endian) data, AVI",
            "puremagic": "video/x-msvideo",
            "pillow": "N/A",
            "exiftool": "AVI",
        },
    }

    # Merge all mappings into registry
    all_mappings = {
        **codec_mappings,
        **image_mappings,
        **raw_mappings,
        **container_mappings,
    }

    for name, tools in all_mappings.items():
        if name in registry:
            # Update existing entry with tool-specific names
            registry[name].update(tools)


def generate_markdown_table(entries: List[Dict], category: str) -> str:
    """Generate markdown table for format category."""
    if not entries:
        return f"### {category}\n\n*No formats discovered*\n\n"

    # Build table header
    table = f"### {category}\n\n"
    table += "| UUID (Type-Suffixed) | Canonical Name | ffprobe | libmagic | puremagic | pyfsig | binwalk | rawpy | Pillow | exiftool |\n"
    table += "|---------------------|---------------|---------|----------|-----------|--------|---------|-------|--------|----------|\n"

    # Sort entries by canonical name
    sorted_entries = sorted(entries, key=lambda x: x["canonical_name"])

    for entry in sorted_entries:
        # Show first 8 chars + suffix for compact display
        uuid_parts = entry["uuid"].rsplit("-", 1)
        if len(uuid_parts) == 2:
            uuid_short = uuid_parts[0][:8] + "...-" + uuid_parts[1]
        else:
            uuid_short = entry["uuid"][:8] + "..."

        table += f"| `{uuid_short}` | **{entry['canonical_name']}** "
        table += f"| {entry['ffprobe'] or '—'} "
        table += f"| {entry['libmagic'] or '—'} "
        table += f"| {entry['puremagic'] or '—'} "
        table += f"| {entry['pyfsig'] or '—'} "
        table += f"| {entry['binwalk'] or '—'} "
        table += f"| {entry['rawpy'] or '—'} "
        table += f"| {entry['pillow'] or '—'} "
        table += f"| {entry['exiftool'] or '—'} |\n"

    table += "\n"
    return table


def generate_full_uuid_reference(all_entries: Dict[str, List[Dict]]) -> str:
    """Generate full UUID reference section."""
    table = "## Full UUID Reference\n\n"
    table += "Complete UUIDs for all formats (expandable for copy-paste):\n\n"
    table += "```\n"

    for category, entries in all_entries.items():
        if entries:
            table += f"\n# {category}\n"
            for entry in sorted(entries, key=lambda x: x["canonical_name"]):
                table += f"{entry['uuid']}  # {entry['canonical_name']}\n"

    table += "```\n\n"
    return table


def main():
    """Generate FORMAT_REGISTRY.md file."""
    print("🔧 Generating FORMAT_REGISTRY.md...")

    # Initialize registry by category
    registry = {
        "containers": {},
        "video_codecs": {},
        "audio_codecs": {},
        "pixel_formats": {},
        "sample_formats": {},
        "channel_layouts": {},
        "image_formats": {},
        "raw_formats": {},
    }

    # Load formats from ffprobe
    containers, video_codecs, audio_codecs, pixel_fmts, sample_fmts, layouts = load_ffprobe_formats()

    # Add all ffprobe formats to registry
    print("\nBuilding format registry...")

    # Separate image formats from containers
    image_extensions = ["jpeg", "jpg", "png", "gif", "bmp", "tiff", "tif", "webp", "heif", "heic", "avif", "jxl", "psd"]
    raw_extensions = ["cr2", "cr3", "nef", "arw", "raf", "orf", "rw2", "pef", "srw", "dng", "3fr", "ari", "bay", "crw", "dcr", "dcs", "erf", "fff", "iiq", "k25", "kdc", "mef", "mos", "mrw", "nrw", "ptx", "r3d", "raw", "rdc", "rwl", "rwz", "sr2", "srf", "x3f"]

    for fmt in containers:
        name = fmt["name"]
        if name.lower() in raw_extensions:
            registry["raw_formats"][name] = create_format_mapping(name, "raw_format")
        elif name.lower() in image_extensions:
            registry["image_formats"][name] = create_format_mapping(name, "image_format")
        else:
            registry["containers"][name] = create_format_mapping(name, "container")

    for codec in video_codecs:
        name = codec["name"]
        registry["video_codecs"][name] = create_format_mapping(name, "video_codec")

    for codec in audio_codecs:
        name = codec["name"]
        registry["audio_codecs"][name] = create_format_mapping(name, "audio_codec")

    for pix_fmt in pixel_fmts:
        registry["pixel_formats"][pix_fmt] = create_format_mapping(pix_fmt, "pixel_format")

    for sample_fmt in sample_fmts:
        registry["sample_formats"][sample_fmt] = create_format_mapping(sample_fmt, "sample_format")

    for layout in layouts:
        registry["channel_layouts"][layout] = create_format_mapping(layout, "channel_layout")

    # Read extra_formats.txt to add missing formats
    extra_formats_path = Path(__file__).parent / "extra_formats.txt"
    if extra_formats_path.exists():
        print("Loading extra formats from extra_formats.txt...")
        with open(extra_formats_path) as f:
            content = f.read()

            # Parse formats
            in_formats = False
            in_codecs = False
            for line in content.split("\n"):
                if "===== FORMATS/MUXERS =====" in line:
                    in_formats = True
                    in_codecs = False
                elif "===== CODECS =====" in line:
                    in_formats = False
                    in_codecs = True
                elif line.strip().startswith("DE ") or line.strip().startswith("D ") or line.strip().startswith(" E"):
                    parts = line.strip().split(maxsplit=2)
                    if len(parts) >= 3:
                        name = parts[1]
                        if in_formats:
                            # Check if it's a RAW format
                            if name.lower() in raw_extensions and name not in registry["raw_formats"]:
                                registry["raw_formats"][name] = create_format_mapping(name, "raw_format")
                            elif name.lower() in image_extensions and name not in registry["image_formats"]:
                                registry["image_formats"][name] = create_format_mapping(name, "image_format")
                            elif name not in registry["containers"]:
                                registry["containers"][name] = create_format_mapping(name, "container")
                        elif in_codecs:
                            codec_type = parts[0]
                            if "V" in codec_type and name not in registry["video_codecs"]:
                                registry["video_codecs"][name] = create_format_mapping(name, "video_codec")
                            elif "A" in codec_type and name not in registry["audio_codecs"]:
                                registry["audio_codecs"][name] = create_format_mapping(name, "audio_codec")

    # Apply known mappings for common formats
    print("Applying known tool mappings...")
    for category_dict in registry.values():
        add_known_mappings(category_dict)

    # Generate markdown content
    markdown = "# Format Registry - Unified Naming System\n\n"
    markdown += "**Universal format identifier mapping across all detection tools**\n\n"
    markdown += "This registry provides a unified naming system for media formats, codecs, and related attributes. "
    markdown += "Each format is assigned a unique UUID that maps to tool-specific names used by different detection libraries.\n\n"
    markdown += "## Purpose\n\n"
    markdown += "Different detection tools use different names for the same formats:\n"
    markdown += "- `ffprobe` might call it `h264`\n"
    markdown += "- `libmagic` might detect it as `MPEG v4 system`\n"
    markdown += "- `puremagic` returns `video/mp4` (MIME type)\n"
    markdown += "- `exiftool` reports it as `AVC`\n\n"
    markdown += "This registry resolves these naming conflicts by providing:\n"
    markdown += "1. **UUID**: Globally unique identifier (deterministic, reproducible)\n"
    markdown += "2. **Canonical Name**: Standard internal name for Smart Media Manager\n"
    markdown += "3. **Tool-specific mappings**: What each tool calls this format\n\n"
    markdown += "## Detection Tools\n\n"
    markdown += "| Tool | Description | Used For |\n"
    markdown += "|------|-------------|----------|\n"
    markdown += "| **ffprobe** | FFmpeg's format probe | Containers, codecs, pixel/sample formats, layouts |\n"
    markdown += "| **libmagic** | File type identification (via python-magic) | File signatures, MIME types |\n"
    markdown += "| **puremagic** | Pure Python magic number detection | File signatures without libmagic |\n"
    markdown += "| **pyfsig** | Python file signature library | Additional format signatures |\n"
    markdown += "| **binwalk** | Firmware analysis tool | Binary signature scanning |\n"
    markdown += "| **rawpy** | RAW image processing (libraw wrapper) | Camera RAW formats |\n"
    markdown += "| **Pillow** | Python Imaging Library | Image format processing |\n"
    markdown += "| **exiftool** | Metadata extraction | Format identification from metadata |\n\n"
    markdown += "## Format Categories\n\n"

    # Generate tables for each category
    all_entries = {}
    categories_order = [
        ("containers", "Container Formats"),
        ("video_codecs", "Video Codecs"),
        ("audio_codecs", "Audio Codecs"),
        ("image_formats", "Image Formats"),
        ("raw_formats", "Camera RAW Formats"),
        ("pixel_formats", "Pixel Formats"),
        ("sample_formats", "Audio Sample Formats"),
        ("channel_layouts", "Audio Channel Layouts"),
    ]

    for key, title in categories_order:
        entries = list(registry.get(key, {}).values())
        all_entries[title] = entries
        markdown += generate_markdown_table(entries, title)

    # Add full UUID reference
    markdown += generate_full_uuid_reference(all_entries)

    # Add usage notes
    markdown += "## Usage Notes\n\n"
    markdown += "### For Developers\n\n"
    markdown += "When implementing format detection:\n\n"
    markdown += "1. **Query multiple tools** to get different names for the same format\n"
    markdown += "2. **Look up the UUID** using any tool's output name\n"
    markdown += "3. **Use the canonical name** internally for consistency\n"
    markdown += "4. **Map back to tool-specific names** when needed for external commands\n\n"
    markdown += "### Empty Fields\n\n"
    markdown += "- **N/A**: Tool does not support this format category (e.g., Pillow doesn't process video codecs)\n"
    markdown += "- **Empty**: Mapping not yet discovered (needs investigation)\n\n"
    markdown += "### Extending the Registry\n\n"
    markdown += "To add new formats:\n\n"
    markdown += "1. Run format discovery: `python3 scripts/ultimate_format_test.py --skip-install`\n"
    markdown += "2. Update `scripts/extra_formats.txt` with missing formats\n"
    markdown += "3. Regenerate registry: `python3 scripts/generate_format_registry.py`\n"
    markdown += "4. Manually verify tool-specific mappings\n"
    markdown += "5. Test with actual media files\n\n"
    markdown += "### UUID Generation\n\n"
    markdown += "UUIDs are generated using UUID5 (SHA-1 hash) with:\n"
    markdown += "- Namespace: `12345678-1234-5678-1234-567812345678`\n"
    markdown += "- Name: `{category}:{canonical_name}` (e.g., `video_codec:h264`)\n\n"
    markdown += "This ensures UUIDs are:\n"
    markdown += "- **Deterministic**: Same input always produces same UUID\n"
    markdown += "- **Unique**: Different formats have different UUIDs\n"
    markdown += "- **Reproducible**: Can regenerate identical UUIDs across systems\n\n"
    markdown += "---\n\n"
    markdown += "*Generated by `scripts/generate_format_registry.py`*\n"
    markdown += f"*Last updated: {Path(__file__).stat().st_mtime}*\n"

    # Write to file
    output_path = Path(__file__).parent.parent / "FORMAT_REGISTRY.md"
    with open(output_path, "w") as f:
        f.write(markdown)

    print(f"✅ Generated {output_path}")
    print("   Total formats registered:")
    for key, title in categories_order:
        count = len(registry.get(key, {}))
        if count > 0:
            print(f"   - {title}: {count}")

    # Also generate JSON version for programmatic access
    json_output = {}
    for category_key, entries_dict in registry.items():
        json_output[category_key] = {name: entry for name, entry in entries_dict.items()}

    repo_root = Path(__file__).resolve().parents[1]
    json_path = repo_root / "smart_media_manager" / "format_registry.json"
    with open(json_path, "w") as f:
        json.dump(json_output, f, indent=2)

    print(f"✅ Generated {json_path} (machine-readable version)")


if __name__ == "__main__":
    main()
