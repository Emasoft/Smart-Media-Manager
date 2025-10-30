#!/usr/bin/env python3
"""
Test that the script NEVER touches non-media files (HTML, text, code, config files, etc.).
This is a CRITICAL safety test to ensure project files are never moved or modified.
"""

import sys
import tempfile
from pathlib import Path

# Add the module to path
sys.path.insert(0, str(Path(__file__).parent))

from smart_media_manager.cli import (
    gather_media_files,
    move_to_staging,
    SkipLogger,
    RunStatistics,
    timestamp,
)


def test_html_files_never_moved():
    """Test that HTML files are NEVER moved to staging directory."""
    print("\n" + "=" * 70)
    print("Testing HTML Files Safety - NEVER Moved to Staging")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create HTML files that might be part of a web project
        (tmppath / "index.html").write_text("<!DOCTYPE html><html><body><h1>My Project</h1></body></html>")
        (tmppath / "styles.htm").write_text("<style>body { color: red; }</style>")

        # Create a media file
        jpeg_file = tmppath / "photo.jpg"
        jpeg_file.write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")

        skip_logger = SkipLogger(tmppath / "skip.log")
        stats = RunStatistics()

        # Scan for media files
        media_files = gather_media_files(
            root=tmppath,
            recursive=False,
            follow_symlinks=False,
            skip_logger=skip_logger,
            stats=stats,
            skip_compatibility_check=True,
        )

        # CRITICAL: Only photo.jpg should be detected, HTML files should be ignored
        assert len(media_files) == 1, f"Expected 1 media file, got {len(media_files)}"
        assert media_files[0].source.name == "photo.jpg", f"Expected photo.jpg, got {media_files[0].source.name}"

        # Move to staging
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_dir.mkdir()

        move_to_staging(media_files, staging_dir)

        # CRITICAL: Verify HTML files are still in original location, NOT moved
        assert (tmppath / "index.html").exists(), "index.html should NOT be moved!"
        assert (tmppath / "styles.htm").exists(), "styles.htm should NOT be moved!"

        # CRITICAL: Verify HTML files are NOT in staging directory
        assert not (staging_dir / "index.html").exists(), "index.html should NOT be in staging!"
        assert not (staging_dir / "styles.htm").exists(), "styles.htm should NOT be in staging!"

        # Verify only the JPEG was staged
        staged_files = list(staging_dir.glob("*"))
        staged_files = [f for f in staged_files if f.name != "ORIGINALS"]  # Exclude ORIGINALS dir
        assert len(staged_files) == 1, f"Expected 1 staged file, got {len(staged_files)}"
        assert staged_files[0].name == "photo.jpg", f"Expected photo.jpg, got {staged_files[0].name}"

        print("✓ HTML files NOT detected as media")
        print("✓ HTML files remain in original location")
        print("✓ HTML files NOT moved to staging")
        print("✓ Only media file (photo.jpg) was staged")

        return True


def test_code_files_never_moved():
    """Test that source code files are NEVER moved to staging directory."""
    print("\n" + "=" * 70)
    print("Testing Code Files Safety - NEVER Moved to Staging")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create code files that might be part of a project
        (tmppath / "app.py").write_text('print("Hello, world!")')
        (tmppath / "script.js").write_text('console.log("Hello!");')
        (tmppath / "main.cpp").write_text("#include <iostream>\nint main() {}")
        (tmppath / "README.md").write_text("# My Project\n\nThis is my project.")
        (tmppath / "config.json").write_text('{"key": "value"}')

        # Create a media file
        png_file = tmppath / "logo.png"
        png_file.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde")

        skip_logger = SkipLogger(tmppath / "skip.log")
        stats = RunStatistics()

        # Scan for media files
        media_files = gather_media_files(
            root=tmppath,
            recursive=False,
            follow_symlinks=False,
            skip_logger=skip_logger,
            stats=stats,
            skip_compatibility_check=True,
        )

        # CRITICAL: Only logo.png should be detected
        assert len(media_files) == 1, f"Expected 1 media file, got {len(media_files)}"
        assert media_files[0].source.name == "logo.png", f"Expected logo.png, got {media_files[0].source.name}"

        # Move to staging
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_dir.mkdir()

        move_to_staging(media_files, staging_dir)

        # CRITICAL: Verify all code files are still in original location
        code_files = ["app.py", "script.js", "main.cpp", "README.md", "config.json"]
        for filename in code_files:
            assert (tmppath / filename).exists(), f"{filename} should NOT be moved!"
            assert not (staging_dir / filename).exists(), f"{filename} should NOT be in staging!"

        # Verify only the PNG was staged
        staged_files = list(staging_dir.glob("*"))
        staged_files = [f for f in staged_files if f.name != "ORIGINALS"]
        assert len(staged_files) == 1, f"Expected 1 staged file, got {len(staged_files)}"

        print("✓ Code files NOT detected as media")
        print("✓ Code files remain in original location")
        print("✓ Code files NOT moved to staging")
        print("✓ Only media file (logo.png) was staged")

        return True


def test_text_files_never_moved():
    """Test that plain text files are NEVER moved to staging directory."""
    print("\n" + "=" * 70)
    print("Testing Text Files Safety - NEVER Moved to Staging")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create text files
        (tmppath / "notes.txt").write_text("These are my notes.")
        (tmppath / "LICENSE").write_text("MIT License\n\nCopyright...")
        (tmppath / "TODO.txt").write_text("1. Task one\n2. Task two")

        # Create a media file
        gif_file = tmppath / "animation.gif"
        gif_file.write_bytes(b"GIF89a\x01\x00\x01\x00\x00\x00\x00,")

        skip_logger = SkipLogger(tmppath / "skip.log")
        stats = RunStatistics()

        # Scan for media files
        media_files = gather_media_files(
            root=tmppath,
            recursive=False,
            follow_symlinks=False,
            skip_logger=skip_logger,
            stats=stats,
            skip_compatibility_check=True,
        )

        # CRITICAL: Only animation.gif should be detected
        assert len(media_files) == 1, f"Expected 1 media file, got {len(media_files)}"
        assert media_files[0].source.name == "animation.gif", f"Expected animation.gif, got {media_files[0].source.name}"

        # Move to staging
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_dir.mkdir()

        move_to_staging(media_files, staging_dir)

        # CRITICAL: Verify text files are still in original location
        text_files = ["notes.txt", "LICENSE", "TODO.txt"]
        for filename in text_files:
            assert (tmppath / filename).exists(), f"{filename} should NOT be moved!"
            assert not (staging_dir / filename).exists(), f"{filename} should NOT be in staging!"

        print("✓ Text files NOT detected as media")
        print("✓ Text files remain in original location")
        print("✓ Text files NOT moved to staging")
        print("✓ Only media file (animation.gif) was staged")

        return True


def test_config_files_never_moved():
    """Test that configuration files are NEVER moved to staging directory."""
    print("\n" + "=" * 70)
    print("Testing Config Files Safety - NEVER Moved to Staging")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create config files
        (tmppath / "config.yml").write_text("version: 1.0\nname: myproject")
        (tmppath / "settings.toml").write_text("[server]\nport = 8080")
        (tmppath / "package.json").write_text('{"name": "myproject", "version": "1.0.0"}')
        (tmppath / ".env").write_text("API_KEY=secret123")

        # Create a media file
        webp_file = tmppath / "image.webp"
        webp_file.write_bytes(b"RIFF\x1a\x00\x00\x00WEBPVP8 \x0e\x00\x00\x000\x01\x00\x9d\x01\x2a\x01\x00\x01\x00\x01\x00")

        skip_logger = SkipLogger(tmppath / "skip.log")
        stats = RunStatistics()

        # Scan for media files
        media_files = gather_media_files(
            root=tmppath,
            recursive=False,
            follow_symlinks=False,
            skip_logger=skip_logger,
            stats=stats,
            skip_compatibility_check=True,
        )

        # CRITICAL: Only image.webp should be detected
        assert len(media_files) == 1, f"Expected 1 media file, got {len(media_files)}"
        assert media_files[0].source.name == "image.webp", f"Expected image.webp, got {media_files[0].source.name}"

        # Move to staging
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_dir.mkdir()

        move_to_staging(media_files, staging_dir)

        # CRITICAL: Verify config files are still in original location
        config_files = ["config.yml", "settings.toml", "package.json", ".env"]
        for filename in config_files:
            assert (tmppath / filename).exists(), f"{filename} should NOT be moved!"
            assert not (staging_dir / filename).exists(), f"{filename} should NOT be in staging!"

        print("✓ Config files NOT detected as media")
        print("✓ Config files remain in original location")
        print("✓ Config files NOT moved to staging")
        print("✓ Only media file (image.webp) was staged")

        return True


def test_mixed_directory_only_media_moved():
    """Test that in a mixed directory with code/config/media, ONLY media files are moved."""
    print("\n" + "=" * 70)
    print("Testing Mixed Directory - ONLY Media Files Moved")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create a realistic project directory with mixed content
        # Code files
        (tmppath / "app.py").write_text('print("Hello")')
        (tmppath / "test.js").write_text('console.log("test");')

        # Config files
        (tmppath / "config.yml").write_text("version: 1.0")
        (tmppath / "package.json").write_text('{"name": "app"}')

        # Documentation
        (tmppath / "README.md").write_text("# Project")
        (tmppath / "LICENSE").write_text("MIT License")

        # HTML/web files
        (tmppath / "index.html").write_text("<html><body>Hello</body></html>")

        # Media files (should be moved)
        (tmppath / "photo1.jpg").write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")
        (tmppath / "photo2.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde")
        (tmppath / "animation.gif").write_bytes(b"GIF89a\x01\x00\x01\x00\x00\x00\x00,")

        skip_logger = SkipLogger(tmppath / "skip.log")
        stats = RunStatistics()

        # Record original non-media files
        non_media_files = ["app.py", "test.js", "config.yml", "package.json", "README.md", "LICENSE", "index.html"]

        # Scan for media files
        media_files = gather_media_files(
            root=tmppath,
            recursive=False,
            follow_symlinks=False,
            skip_logger=skip_logger,
            stats=stats,
            skip_compatibility_check=True,
        )

        # CRITICAL: Only 3 media files should be detected
        assert len(media_files) == 3, f"Expected 3 media files, got {len(media_files)}"

        media_names = sorted([m.source.name for m in media_files])
        expected_names = sorted(["photo1.jpg", "photo2.png", "animation.gif"])
        assert media_names == expected_names, f"Expected {expected_names}, got {media_names}"

        # Move to staging
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_dir.mkdir()

        move_to_staging(media_files, staging_dir)

        # CRITICAL: Verify ALL non-media files are still in original location
        for filename in non_media_files:
            assert (tmppath / filename).exists(), f"{filename} should NOT be moved!"
            assert not (staging_dir / filename).exists(), f"{filename} should NOT be in staging!"

        # CRITICAL: Verify ONLY media files are in staging
        staged_files = list(staging_dir.glob("*"))
        staged_files = [f for f in staged_files if f.name != "ORIGINALS"]
        staged_names = sorted([f.name for f in staged_files])

        assert staged_names == expected_names, f"Expected {expected_names} in staging, got {staged_names}"

        # CRITICAL: Verify media files were MOVED (not in original location)
        assert not (tmppath / "photo1.jpg").exists(), "photo1.jpg should be moved"
        assert not (tmppath / "photo2.png").exists(), "photo2.png should be moved"
        assert not (tmppath / "animation.gif").exists(), "animation.gif should be moved"

        print("✓ Only 3 media files detected (out of 10 total files)")
        print("✓ All 7 non-media files remain in original location")
        print("✓ ONLY media files moved to staging")
        print(f"✓ Non-media files: {', '.join(non_media_files)}")
        print(f"✓ Media files: {', '.join(expected_names)}")

        return True


def main():
    print("=" * 70)
    print("Non-Media Files Safety Tests")
    print("CRITICAL: Verify script NEVER touches HTML, text, code, or config files")
    print("=" * 70)

    results = []

    # Run all tests
    try:
        results.append(("HTML files never moved", test_html_files_never_moved()))
    except Exception as e:
        print(f"\n✗ HTML files test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("HTML files never moved", False))

    try:
        results.append(("Code files never moved", test_code_files_never_moved()))
    except Exception as e:
        print(f"\n✗ Code files test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("Code files never moved", False))

    try:
        results.append(("Text files never moved", test_text_files_never_moved()))
    except Exception as e:
        print(f"\n✗ Text files test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("Text files never moved", False))

    try:
        results.append(("Config files never moved", test_config_files_never_moved()))
    except Exception as e:
        print(f"\n✗ Config files test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("Config files never moved", False))

    try:
        results.append(("Mixed directory - only media moved", test_mixed_directory_only_media_moved()))
    except Exception as e:
        print(f"\n✗ Mixed directory test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("Mixed directory - only media moved", False))

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False

    print("=" * 70)

    if all_passed:
        print("✓ All safety tests passed!")
        print("✓ CONFIRMED: Script NEVER touches non-media files")
        print("✓ HTML, text, code, and config files are SAFE")
        return 0
    else:
        print("✗ Some safety tests failed!")
        print("⚠️  WARNING: Script may be touching non-media files!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
