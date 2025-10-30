#!/usr/bin/env python3
"""
Test that audio files are NEVER moved to staging directory.
Apple Photos does NOT support audio-only files, so they must be left alone.
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


def test_mp3_files_never_moved():
    """Test that MP3 audio files are NEVER moved to staging directory."""
    print("\n" + "=" * 70)
    print("Testing MP3 Audio Files Safety - NEVER Moved to Staging")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create MP3 audio file (ID3v2.3 header)
        mp3_file = tmppath / "song.mp3"
        mp3_file.write_bytes(
            b"ID3\x03\x00\x00\x00\x00\x00\x00"  # ID3v2.3 header
            b"\xff\xfb\x90\x00"  # MP3 frame sync
        )

        # Create a media file (should be moved)
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

        # CRITICAL: Only photo.jpg should be detected, NOT song.mp3
        assert len(media_files) == 1, f"Expected 1 media file, got {len(media_files)}"
        assert media_files[0].source.name == "photo.jpg", f"Expected photo.jpg, got {media_files[0].source.name}"

        # Move to staging
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_dir.mkdir()

        move_to_staging(media_files, staging_dir)

        # CRITICAL: Verify MP3 file is still in original location, NOT moved
        assert (tmppath / "song.mp3").exists(), "song.mp3 should NOT be moved!"

        # CRITICAL: Verify MP3 file is NOT in staging directory
        assert not (staging_dir / "song.mp3").exists(), "song.mp3 should NOT be in staging!"

        # Verify only the JPEG was staged
        staged_files = list(staging_dir.glob("*"))
        staged_files = [f for f in staged_files if f.name != "ORIGINALS"]
        assert len(staged_files) == 1, f"Expected 1 staged file, got {len(staged_files)}"
        assert staged_files[0].name == "photo.jpg", f"Expected photo.jpg, got {staged_files[0].name}"

        print("✓ MP3 audio file NOT detected as media")
        print("✓ MP3 audio file remains in original location")
        print("✓ MP3 audio file NOT moved to staging")
        print("✓ Only media file (photo.jpg) was staged")

        return True


def test_wav_files_never_moved():
    """Test that WAV audio files are NEVER moved to staging directory."""
    print("\n" + "=" * 70)
    print("Testing WAV Audio Files Safety - NEVER Moved to Staging")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create WAV audio file (RIFF WAVE header)
        wav_file = tmppath / "audio.wav"
        wav_file.write_bytes(
            b"RIFF\x24\x00\x00\x00WAVE"  # RIFF WAVE header
            b"fmt \x10\x00\x00\x00"  # Format chunk
        )

        # Create a media file (should be moved)
        png_file = tmppath / "image.png"
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

        # CRITICAL: Only image.png should be detected, NOT audio.wav
        assert len(media_files) == 1, f"Expected 1 media file, got {len(media_files)}"
        assert media_files[0].source.name == "image.png", f"Expected image.png, got {media_files[0].source.name}"

        # Move to staging
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_dir.mkdir()

        move_to_staging(media_files, staging_dir)

        # CRITICAL: Verify WAV file is still in original location, NOT moved
        assert (tmppath / "audio.wav").exists(), "audio.wav should NOT be moved!"

        # CRITICAL: Verify WAV file is NOT in staging directory
        assert not (staging_dir / "audio.wav").exists(), "audio.wav should NOT be in staging!"

        print("✓ WAV audio file NOT detected as media")
        print("✓ WAV audio file remains in original location")
        print("✓ WAV audio file NOT moved to staging")
        print("✓ Only media file (image.png) was staged")

        return True


def test_flac_files_never_moved():
    """Test that FLAC audio files are NEVER moved to staging directory."""
    print("\n" + "=" * 70)
    print("Testing FLAC Audio Files Safety - NEVER Moved to Staging")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create FLAC audio file (fLaC header)
        flac_file = tmppath / "music.flac"
        flac_file.write_bytes(b"fLaC\x00\x00\x00\x22")  # FLAC header

        # Create a media file (should be moved)
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

        # CRITICAL: Only animation.gif should be detected, NOT music.flac
        assert len(media_files) == 1, f"Expected 1 media file, got {len(media_files)}"
        assert media_files[0].source.name == "animation.gif", f"Expected animation.gif, got {media_files[0].source.name}"

        # Move to staging
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_dir.mkdir()

        move_to_staging(media_files, staging_dir)

        # CRITICAL: Verify FLAC file is still in original location, NOT moved
        assert (tmppath / "music.flac").exists(), "music.flac should NOT be moved!"

        # CRITICAL: Verify FLAC file is NOT in staging directory
        assert not (staging_dir / "music.flac").exists(), "music.flac should NOT be in staging!"

        print("✓ FLAC audio file NOT detected as media")
        print("✓ FLAC audio file remains in original location")
        print("✓ FLAC audio file NOT moved to staging")
        print("✓ Only media file (animation.gif) was staged")

        return True


def test_ogg_files_never_moved():
    """Test that OGG audio files are NEVER moved to staging directory."""
    print("\n" + "=" * 70)
    print("Testing OGG Audio Files Safety - NEVER Moved to Staging")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create OGG audio file (OggS header)
        ogg_file = tmppath / "podcast.ogg"
        ogg_file.write_bytes(b"OggS\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00")  # OGG header

        # Create a media file (should be moved)
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

        # CRITICAL: Only image.webp should be detected, NOT podcast.ogg
        assert len(media_files) == 1, f"Expected 1 media file, got {len(media_files)}"
        assert media_files[0].source.name == "image.webp", f"Expected image.webp, got {media_files[0].source.name}"

        # Move to staging
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_dir.mkdir()

        move_to_staging(media_files, staging_dir)

        # CRITICAL: Verify OGG file is still in original location, NOT moved
        assert (tmppath / "podcast.ogg").exists(), "podcast.ogg should NOT be moved!"

        # CRITICAL: Verify OGG file is NOT in staging directory
        assert not (staging_dir / "podcast.ogg").exists(), "podcast.ogg should NOT be in staging!"

        print("✓ OGG audio file NOT detected as media")
        print("✓ OGG audio file remains in original location")
        print("✓ OGG audio file NOT moved to staging")
        print("✓ Only media file (image.webp) was staged")

        return True


def test_mixed_audio_and_video():
    """Test that in a directory with audio and video, ONLY video is moved."""
    print("\n" + "=" * 70)
    print("Testing Mixed Audio/Video - ONLY Video Moved")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create audio files (should NOT be moved)
        (tmppath / "song.mp3").write_bytes(b"ID3\x03\x00\x00\x00\x00\x00\x00\xff\xfb\x90\x00")
        (tmppath / "audio.wav").write_bytes(b"RIFF\x24\x00\x00\x00WAVE")
        (tmppath / "music.flac").write_bytes(b"fLaC\x00\x00\x00\x22")

        # Create media files (should be moved)
        (tmppath / "photo.jpg").write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")
        (tmppath / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde")

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

        # CRITICAL: Only 2 image files should be detected (NOT 3 audio files)
        assert len(media_files) == 2, f"Expected 2 media files, got {len(media_files)}"

        media_names = sorted([m.source.name for m in media_files])
        expected_names = sorted(["photo.jpg", "image.png"])
        assert media_names == expected_names, f"Expected {expected_names}, got {media_names}"

        # Move to staging
        run_ts = timestamp()
        staging_dir = tmppath / f"FOUND_MEDIA_FILES_{run_ts}"
        staging_dir.mkdir()

        move_to_staging(media_files, staging_dir)

        # CRITICAL: Verify ALL audio files are still in original location
        audio_files = ["song.mp3", "audio.wav", "music.flac"]
        for filename in audio_files:
            assert (tmppath / filename).exists(), f"{filename} should NOT be moved!"
            assert not (staging_dir / filename).exists(), f"{filename} should NOT be in staging!"

        # CRITICAL: Verify ONLY media files are in staging
        staged_files = list(staging_dir.glob("*"))
        staged_files = [f for f in staged_files if f.name != "ORIGINALS"]
        staged_names = sorted([f.name for f in staged_files])

        assert staged_names == expected_names, f"Expected {expected_names} in staging, got {staged_names}"

        print("✓ Only 2 image files detected (out of 5 total files)")
        print("✓ All 3 audio files remain in original location")
        print("✓ ONLY image files moved to staging")
        print(f"✓ Audio files: {', '.join(audio_files)}")
        print(f"✓ Image files: {', '.join(expected_names)}")

        return True


def main():
    print("=" * 70)
    print("Audio Files Safety Tests")
    print("CRITICAL: Verify script NEVER touches audio-only files")
    print("Apple Photos does NOT support audio-only files")
    print("=" * 70)

    results = []

    # Run all tests
    try:
        results.append(("MP3 files never moved", test_mp3_files_never_moved()))
    except Exception as e:
        print(f"\n✗ MP3 files test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("MP3 files never moved", False))

    try:
        results.append(("WAV files never moved", test_wav_files_never_moved()))
    except Exception as e:
        print(f"\n✗ WAV files test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("WAV files never moved", False))

    try:
        results.append(("FLAC files never moved", test_flac_files_never_moved()))
    except Exception as e:
        print(f"\n✗ FLAC files test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("FLAC files never moved", False))

    try:
        results.append(("OGG files never moved", test_ogg_files_never_moved()))
    except Exception as e:
        print(f"\n✗ OGG files test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("OGG files never moved", False))

    try:
        results.append(("Mixed audio/video - only video moved", test_mixed_audio_and_video()))
    except Exception as e:
        print(f"\n✗ Mixed audio/video test FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("Mixed audio/video - only video moved", False))

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
        print("✓ All audio safety tests passed!")
        print("✓ CONFIRMED: Script NEVER touches audio-only files")
        print("✓ MP3, WAV, FLAC, OGG files are SAFE")
        return 0
    else:
        print("✗ Some audio safety tests failed!")
        print("⚠️  WARNING: Script may be touching audio files!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
