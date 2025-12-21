#!/usr/bin/env python3
"""
Test what extensions detection tools actually return for various formats.
This helps identify which formats need canonicalization mappings.
"""

import sys
import tempfile
from pathlib import Path

# Add the module to path
sys.path.insert(0, str(Path(__file__).parent))

from smart_media_manager.cli import (
    gather_media_files,
    SkipLogger,
    RunStatistics,
)


def create_sample_files(tmpdir: Path) -> dict[str, tuple[bytes, str]]:
    """
    Create sample files for various formats.
    Returns: dict mapping format_name -> (content_bytes, expected_canonical_extension)
    """
    samples = {
        # JPEG variants
        "JPEG with JFIF header": (b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00", ".jpg"),
        # PNG
        "PNG": (b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde", ".png"),
        # GIF
        "GIF89a": (b"GIF89a\x01\x00\x01\x00\x00\x00\x00,", ".gif"),
        # WebP
        "WebP": (b"RIFF\x1a\x00\x00\x00WEBPVP8 \x0e\x00\x00\x000\x01\x00\x9d\x01\x2a\x01\x00\x01\x00\x01\x00", ".webp"),
        # TIFF (little-endian)
        "TIFF little-endian": (b"II*\x00\x08\x00\x00\x00", ".tiff"),
        # TIFF (big-endian)
        "TIFF big-endian": (b"MM\x00*\x00\x00\x00\x08", ".tiff"),
        # BMP
        "BMP": (b"BM6\x00\x00\x00\x00\x00\x00\x006\x00\x00\x00(\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x18\x00", ".bmp"),
    }

    return samples


def test_extension_detection():
    """Test what extensions are actually detected for various formats."""
    print("=" * 80)
    print("Extension Detection Test - What extensions do detection tools return?")
    print("=" * 80)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        samples = create_sample_files(tmppath)

        results = {}

        for format_name, (content, expected_ext) in samples.items():
            # Create file without extension
            test_file = tmppath / f"test_{format_name.replace(' ', '_').replace('/', '_')}"
            test_file.write_bytes(content)

            skip_logger = SkipLogger(tmppath / "skip.log")
            stats = RunStatistics()

            # Detect the file
            media_files = gather_media_files(
                root=tmppath,
                recursive=False,
                follow_symlinks=False,
                skip_logger=skip_logger,
                stats=stats,
                skip_compatibility_check=True,
            )

            if media_files:
                detected_ext = media_files[0].extension
                results[format_name] = {
                    "detected": detected_ext,
                    "expected": expected_ext,
                    "match": detected_ext == expected_ext,
                }
            else:
                results[format_name] = {
                    "detected": None,
                    "expected": expected_ext,
                    "match": False,
                }

            # Clean up
            test_file.unlink()
            if skip_logger.path.exists():
                skip_logger.path.unlink()

    # Report results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)

    issues = []
    ok = []

    for format_name, result in results.items():
        detected = result["detected"]
        expected = result["expected"]
        match = result["match"]

        if match:
            ok.append(format_name)
            print(f"✓ {format_name:30s} → {detected:10s} (correct)")
        else:
            issues.append(format_name)
            print(f"✗ {format_name:30s} → {detected:10s} (expected {expected}, MISMATCH!)")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✓ Correct: {len(ok)}/{len(results)}")
    print(f"✗ Issues:  {len(issues)}/{len(results)}")

    if issues:
        print("\n⚠️  FORMATS NEEDING CANONICALIZATION:")
        for format_name in issues:
            result = results[format_name]
            print(f"   - {format_name}: {result['detected']} → {result['expected']}")
        return 1
    else:
        print("\n✓ All formats detected with correct canonical extensions!")
        return 0


if __name__ == "__main__":
    sys.exit(test_extension_detection())
