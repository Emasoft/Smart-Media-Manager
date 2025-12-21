#!/usr/bin/env python3
"""
Comprehensive format compatibility testing for Apple Photos.

This script:
1. Generates test samples for uncertain formats
2. Validates each sample is correct
3. Attempts import via smart-media-manager
4. Analyzes logs with log-auditor agents
5. Compiles compatibility sheet

Usage:
    uv run scripts/test_format_compatibility.py
"""

import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

# Test configuration
SAMPLES_DIR = Path("tests/samples/format_tests")
LOGS_DIR = Path("format_tests_results")
BASE_IMAGE = Path("tests/samples/media/_2ca686b5-aaaa-4f56-8837-13081195f721.jpeg")
BASE_VIDEO = Path("tests/samples/media/001.mp4")


@dataclass
class FormatTest:
    """Format test specification."""
    name: str
    extension: str
    category: str  # image, video, audio
    codec: Optional[str] = None
    container: Optional[str] = None
    sample_rate: Optional[int] = None
    bit_depth: Optional[int] = None
    color_format: Optional[str] = None
    frame_rate: Optional[str] = None
    profile: Optional[str] = None
    # Test result (filled after testing)
    compatible: Optional[bool] = None
    import_result: Optional[str] = None
    error_message: Optional[str] = None
    notes: Optional[str] = None


# Define all formats to test
FORMAT_TESTS = [
    # === PRIORITY 1: High Usage ===

    # Image formats
    FormatTest(
        name="JPEG 2000",
        extension="jp2",
        category="image",
        codec="jpeg2000",
    ),
    FormatTest(
        name="APNG Animated",
        extension="png",
        category="image",
        codec="apng",
        notes="Animated PNG",
    ),
    FormatTest(
        name="HEIF Sequence",
        extension="heics",
        category="image",
        codec="hevc",
        notes="Animated HEIC",
    ),
    FormatTest(
        name="JPEG XL",
        extension="jxl",
        category="image",
        codec="mjpeg",  # ffmpeg doesn't support jxl encode yet
        notes="May need external tool",
    ),
    FormatTest(
        name="AVIF",
        extension="avif",
        category="image",
        codec="av1",
        notes="Modern format",
    ),

    # Video containers
    FormatTest(
        name="Transport Stream H.264",
        extension="ts",
        category="video",
        container="mpegts",
        codec="h264",
    ),
    FormatTest(
        name="M2TS H.264",
        extension="m2ts",
        category="video",
        container="mpegts",
        codec="h264",
    ),

    # Video codecs
    FormatTest(
        name="Motion JPEG in MOV",
        extension="mov",
        category="video",
        container="mov",
        codec="mjpeg",
    ),
    FormatTest(
        name="MPEG-2 in MOV",
        extension="mov",
        category="video",
        container="mov",
        codec="mpeg2video",
    ),
    FormatTest(
        name="MPEG-4 ASP in MP4",
        extension="mp4",
        category="video",
        container="mp4",
        codec="mpeg4",
        profile="simple",
    ),

    # Video frame rates
    FormatTest(
        name="H.264 60fps",
        extension="mp4",
        category="video",
        codec="h264",
        frame_rate="60",
    ),
    FormatTest(
        name="H.264 120fps",
        extension="mp4",
        category="video",
        codec="h264",
        frame_rate="120",
    ),
    FormatTest(
        name="HEVC 60fps",
        extension="mp4",
        category="video",
        codec="hevc",
        frame_rate="60",
    ),

    # Video color formats
    FormatTest(
        name="H.264 4:2:2",
        extension="mp4",
        category="video",
        codec="h264",
        color_format="yuv422p",
    ),
    FormatTest(
        name="H.264 4:4:4",
        extension="mp4",
        category="video",
        codec="h264",
        color_format="yuv444p",
    ),
    FormatTest(
        name="HEVC 10-bit",
        extension="mp4",
        category="video",
        codec="hevc",
        bit_depth=10,
        color_format="yuv420p10le",
        notes="Known incompatible, testing to confirm",
    ),
    FormatTest(
        name="HEVC 12-bit",
        extension="mp4",
        category="video",
        codec="hevc",
        bit_depth=12,
        color_format="yuv420p12le",
    ),

    # Audio codecs in video
    FormatTest(
        name="AMR-NB in 3GP",
        extension="3gp",
        category="video",
        codec="amr_nb",
        notes="3GP audio codec",
    ),
    FormatTest(
        name="AMR-WB in 3GP",
        extension="3gp",
        category="video",
        codec="amr_wb",
    ),
    FormatTest(
        name="IMA ADPCM in MOV",
        extension="mov",
        category="video",
        codec="adpcm_ima_qt",
    ),

    # Audio sample rates
    FormatTest(
        name="AAC 6000 Hz",
        extension="mp4",
        category="video",
        codec="aac",
        sample_rate=6000,
        notes="Non-standard rate",
    ),
    FormatTest(
        name="AAC 64000 Hz",
        extension="mp4",
        category="video",
        codec="aac",
        sample_rate=64000,
    ),
    FormatTest(
        name="AAC 4000 Hz",
        extension="mp4",
        category="video",
        codec="aac",
        sample_rate=4000,
        notes="Very low",
    ),
]


def generate_sample(test: FormatTest, output_path: Path) -> bool:
    """Generate a test sample file using ffmpeg."""
    print(f"  Generating: {output_path.name}")

    try:
        # Choose base file
        if test.category == "image":
            input_file = BASE_IMAGE
        else:
            input_file = BASE_VIDEO

        # Build ffmpeg command based on test parameters
        cmd = ["ffmpeg", "-y", "-i", str(input_file)]

        # Video codec
        if test.codec and test.category == "video":
            if test.codec == "mjpeg":
                cmd.extend(["-c:v", "mjpeg", "-q:v", "2"])
            elif test.codec == "mpeg2video":
                cmd.extend(["-c:v", "mpeg2video", "-b:v", "5M"])
            elif test.codec == "mpeg4":
                cmd.extend(["-c:v", "mpeg4", "-b:v", "2M"])
            elif test.codec == "h264":
                cmd.extend(["-c:v", "libx264"])
            elif test.codec == "hevc":
                cmd.extend(["-c:v", "libx265"])

        # Pixel format / color depth
        if test.color_format:
            cmd.extend(["-pix_fmt", test.color_format])

        # Frame rate
        if test.frame_rate:
            cmd.extend(["-r", test.frame_rate])

        # Audio codec
        if test.codec and test.category == "video" and test.codec.startswith("a"):
            # Audio-specific codec
            if test.codec == "amr_nb":
                cmd.extend(["-c:a", "libopencore_amrnb", "-ar", "8000", "-ac", "1"])
            elif test.codec == "amr_wb":
                cmd.extend(["-c:a", "amr_wb", "-ar", "16000", "-ac", "1"])
            elif test.codec == "adpcm_ima_qt":
                cmd.extend(["-c:a", "adpcm_ima_qt"])
            elif test.codec == "aac":
                cmd.extend(["-c:a", "aac"])
                if test.sample_rate:
                    cmd.extend(["-ar", str(test.sample_rate)])
        else:
            # Keep audio codec from source
            cmd.extend(["-c:a", "copy"])

        # Container format
        if test.container:
            cmd.extend(["-f", test.container])

        # Limit duration to 3 seconds
        cmd.extend(["-t", "3"])

        # Output
        cmd.append(str(output_path))

        # Run ffmpeg
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"    ❌ ffmpeg failed: {result.stderr[:200]}")
            return False

        # Verify file was created
        if not output_path.exists() or output_path.stat().st_size == 0:
            print(f"    ❌ Output file is empty or missing")
            return False

        print(f"    ✅ Generated ({output_path.stat().st_size} bytes)")
        return True

    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False


def validate_sample(test: FormatTest, file_path: Path) -> bool:
    """Validate the generated sample is correct format."""
    print(f"  Validating: {file_path.name}")

    try:
        # Use ffprobe for video files
        if test.category == "video":
            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "stream=codec_name,codec_type,sample_rate,pix_fmt,r_frame_rate",
                "-of", "json",
                str(file_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"    ❌ ffprobe failed")
                return False

            data = json.loads(result.stdout)
            streams = data.get("streams", [])

            if not streams:
                print(f"    ❌ No streams found")
                return False

            print(f"    ✅ Valid ({len(streams)} stream(s))")
            return True

        # Use PIL for images
        else:
            from PIL import Image

            with Image.open(file_path) as img:
                img.load()
                print(f"    ✅ Valid image ({img.size[0]}x{img.size[1]})")
                return True

    except Exception as e:
        print(f"    ❌ Validation failed: {e}")
        return False


def test_import(test: FormatTest, file_path: Path, log_dir: Path) -> dict:
    """Test importing file via smart-media-manager."""
    print(f"  Testing import: {file_path.name}")

    log_file = log_dir / f"{file_path.stem}_import.log"

    try:
        cmd = [
            "uv", "run", "smart-media-manager",
            str(file_path),
            "--file",
            "--skip-renaming",
            "--skip-convert",
            "--skip-compatibility-check",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )

        # Save log
        with open(log_file, "w") as f:
            f.write(f"=== COMMAND ===\n")
            f.write(" ".join(cmd) + "\n\n")
            f.write(f"=== STDOUT ===\n")
            f.write(result.stdout + "\n\n")
            f.write(f"=== STDERR ===\n")
            f.write(result.stderr + "\n\n")
            f.write(f"=== EXIT CODE ===\n")
            f.write(str(result.returncode) + "\n")

        return {
            "success": result.returncode == 0,
            "log_file": str(log_file),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
        }

    except subprocess.TimeoutExpired:
        print(f"    ⏱️  Timeout!")
        return {
            "success": False,
            "log_file": str(log_file),
            "error": "Import timeout after 120 seconds",
        }
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return {
            "success": False,
            "log_file": str(log_file),
            "error": str(e),
        }


def main():
    """Main test orchestration."""
    print("=" * 80)
    print("FORMAT COMPATIBILITY TESTING")
    print("=" * 80)
    print()

    # Create directories
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Check base files exist
    if not BASE_IMAGE.exists():
        print(f"❌ Base image not found: {BASE_IMAGE}")
        return 1
    if not BASE_VIDEO.exists():
        print(f"❌ Base video not found: {BASE_VIDEO}")
        return 1

    print(f"✅ Base image: {BASE_IMAGE}")
    print(f"✅ Base video: {BASE_VIDEO}")
    print(f"✅ Output directory: {SAMPLES_DIR}")
    print(f"✅ Logs directory: {LOGS_DIR}")
    print()

    print(f"Testing {len(FORMAT_TESTS)} format combinations...")
    print()

    results = []

    for i, test in enumerate(FORMAT_TESTS, 1):
        print(f"[{i}/{len(FORMAT_TESTS)}] {test.name}")

        # Generate filename
        parts = [f"test_{test.category}"]
        if test.codec:
            parts.append(test.codec)
        if test.sample_rate:
            parts.append(f"{test.sample_rate}hz")
        if test.frame_rate:
            parts.append(f"{test.frame_rate}fps")
        if test.color_format:
            parts.append(test.color_format.replace("yuv", "").replace("p", ""))
        if test.bit_depth:
            parts.append(f"{test.bit_depth}bit")

        filename = "_".join(parts) + f".{test.extension}"
        output_path = SAMPLES_DIR / filename

        # Step 1: Generate sample
        if not generate_sample(test, output_path):
            test.compatible = None
            test.import_result = "generation_failed"
            results.append(test)
            print()
            continue

        # Step 2: Validate sample
        if not validate_sample(test, output_path):
            test.compatible = None
            test.import_result = "validation_failed"
            results.append(test)
            print()
            continue

        # Step 3: Test import
        import_result = test_import(test, output_path, LOGS_DIR)

        if import_result["success"]:
            test.compatible = True
            test.import_result = "success"
            print(f"  ✅ COMPATIBLE")
        else:
            test.compatible = False
            test.import_result = "failed"
            test.error_message = import_result.get("error", "Import failed")
            print(f"  ❌ INCOMPATIBLE")

        results.append(test)
        print()

    # Save results to JSON
    results_file = LOGS_DIR / "test_results.json"
    with open(results_file, "w") as f:
        json.dump([asdict(r) for r in results], f, indent=2)

    print("=" * 80)
    print(f"✅ Testing complete! Results saved to {results_file}")
    print("=" * 80)
    print()
    print("Summary:")
    compatible = sum(1 for r in results if r.compatible is True)
    incompatible = sum(1 for r in results if r.compatible is False)
    failed = sum(1 for r in results if r.compatible is None)
    print(f"  ✅ Compatible: {compatible}")
    print(f"  ❌ Incompatible: {incompatible}")
    print(f"  ⚠️  Failed to generate/validate: {failed}")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
