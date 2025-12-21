#!/usr/bin/env python3
"""
Quick test to verify format_registry UUID detection works with sample files.
"""

import sys
from pathlib import Path

# Add the module to path
sys.path.insert(0, str(Path(__file__).parent))

from smart_media_manager import format_registry


def test_file(filepath: Path):
    """Test UUID-based detection on a file."""
    print(f"\nTesting: {filepath.name}")
    print("-" * 60)

    # Simulate tool outputs (simplified - in real code these come from actual tool calls)
    # For now, just test the UUID lookup functions

    # Test with JPEG
    if filepath.suffix.lower() in {".jpg", ".jpeg"}:
        uuid = format_registry.lookup_format_uuid("ffprobe", "mjpeg")
        if uuid:
            print(f"  UUID: {uuid}")
            print(f"  Canonical name: {format_registry.get_canonical_name(uuid)}")
            print(f"  Extensions: {format_registry.get_format_extensions(uuid)}")
            print(f"  Compatible: {format_registry.is_apple_photos_compatible(uuid)}")
            print(f"  Needs conversion: {format_registry.needs_conversion(uuid)}")

    # Test with PNG
    elif filepath.suffix.lower() == ".png":
        uuid = format_registry.lookup_format_uuid("puremagic", "image/png")
        if uuid:
            print(f"  UUID: {uuid}")
            print(f"  Canonical name: {format_registry.get_canonical_name(uuid)}")
            print(f"  Compatible: {format_registry.is_apple_photos_compatible(uuid)}")

    # Test with WebP
    elif filepath.suffix.lower() == ".webp":
        uuid = format_registry.lookup_format_uuid("libmagic", "Web/P image")
        if uuid:
            print(f"  UUID: {uuid}")
            print(f"  Canonical name: {format_registry.get_canonical_name(uuid)}")
            print(f"  Compatible: {format_registry.is_apple_photos_compatible(uuid)}")

    # Test with MP4
    elif filepath.suffix.lower() == ".mp4":
        uuid = format_registry.lookup_format_uuid("ffprobe", "mp4")
        if uuid:
            print(f"  UUID: {uuid}")
            print(f"  Canonical name: {format_registry.get_canonical_name(uuid)}")
            print(f"  Compatible: {format_registry.is_apple_photos_compatible(uuid)}")

    # Test with MKV
    elif filepath.suffix.lower() == ".mkv":
        uuid = format_registry.lookup_format_uuid("ffprobe", "matroska")
        if uuid:
            print(f"  UUID: {uuid}")
            print(f"  Canonical name: {format_registry.get_canonical_name(uuid)}")
            print(f"  Compatible: {format_registry.is_apple_photos_compatible(uuid)}")
            print(f"  Needs conversion: {format_registry.needs_conversion(uuid)}")


def main():
    samples_dir = Path("tests/samples/media")

    if not samples_dir.exists():
        print(f"Error: {samples_dir} does not exist")
        return 1

    print("=" * 60)
    print("UUID Format Registry Integration Test")
    print("=" * 60)

    # Test a few sample files
    test_files = [
        "463108291_3854235968172130_2760581135168458128_n.jpg",
        "image.webp",
        "5_00026_.png",
        "2f84d671-952f-485f-9825-ae26d469b2c2.mp4",
        "Avengers - Endgame - 4K Trailer copy.mkv",
    ]

    for filename in test_files:
        filepath = samples_dir / filename
        if filepath.exists():
            test_file(filepath)
        else:
            print(f"\nSkipping {filename} (not found)")

    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
