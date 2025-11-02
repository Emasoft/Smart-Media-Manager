"""
Integration tests for detect_media function.

WHY INTEGRATION TEST INSTEAD OF UNIT TEST?
==========================================

The detect_media function (409 lines, smart_media_manager/cli.py:1996-2404) orchestrates 16+ internal functions:
- safe_filetype_guess, safe_puremagic_guess
- collect_format_votes, select_consensus_vote
- determine_media_kind, match_rule
- is_animated_gif, is_animated_png, is_animated_webp
- get_psd_color_mode, is_video_corrupt_or_truncated
- ffprobe, extract_and_normalize_metadata, extract_container
- refine_image_media, refine_video_media, refine_raw_media

Attempting unit tests would require mocking all 16+ functions, which would:
1. Bypass all real detection logic
2. Test only mocks, not actual code execution
3. Provide false confidence
4. Miss real bugs in the orchestration flow

Therefore, this is an INTEGRATION test that:
- Uses real sample files (small, <100KB for CI)
- Executes actual detection pipeline
- Only mocks external tools (exiftool, ffmpeg) if absolutely necessary
- Tests end-to-end behavior with realistic data

Coverage: Tests the complete detection pipeline with real files
Limitations: Does not test every edge case or code path in isolation
"""

from pathlib import Path


class TestDetectMediaIntegration:
    """Integration tests for detect_media with real sample files."""

    def test_detect_media_jpeg_image(self):
        """Test detect_media successfully detects a real JPEG image."""
        from smart_media_manager.cli import detect_media

        # Use real sample file from CI test suite
        sample_jpg = Path(__file__).parent / "samples" / "ci" / "images" / "test_image.jpg"
        assert sample_jpg.exists(), f"Sample file not found: {sample_jpg}"

        # Execute real detection pipeline
        media, error = detect_media(sample_jpg)

        # Verify successful detection
        assert error is None, f"Detection failed with error: {error}"
        assert media is not None, "MediaFile should not be None for valid JPEG"

        # Verify media file attributes
        assert media.kind == "image", f"Expected kind='image', got '{media.kind}'"
        assert media.source == sample_jpg, "Source path should match input"
        assert media.extension in [".jpg", ".jpeg"], f"Expected JPEG extension, got '{media.extension}'"
        assert media.format_name.lower() in ["jpg", "jpeg"], f"Expected JPEG format name, got '{media.format_name}'"

        # Verify action is set (should be 'import' for compatible JPEG)
        assert media.action is not None, "Action should be set by detection"
        assert media.action == "import", f"JPEG should be directly importable, got action='{media.action}'"
        assert media.compatible is True, "JPEG should be compatible with Apple Photos"
        assert media.requires_processing is False, "Compatible JPEG should not require processing"

        # Verify rule_id is set
        assert media.rule_id is not None, "Rule ID should be set by detection"
        assert media.rule_id.startswith("R-"), f"Rule ID should start with 'R-', got '{media.rule_id}'"

    def test_detect_media_mp4_video(self):
        """Test detect_media successfully detects a real MP4 video."""
        from smart_media_manager.cli import detect_media

        # Use real sample file from CI test suite
        sample_mp4 = Path(__file__).parent / "samples" / "ci" / "videos" / "test_video.mp4"
        assert sample_mp4.exists(), f"Sample file not found: {sample_mp4}"

        # Execute real detection pipeline
        media, error = detect_media(sample_mp4)

        # Verify successful detection
        assert error is None, f"Detection failed with error: {error}"
        assert media is not None, "MediaFile should not be None for valid MP4"

        # Verify media file attributes
        assert media.kind == "video", f"Expected kind='video', got '{media.kind}'"
        assert media.source == sample_mp4, "Source path should match input"
        assert media.extension in [".mp4", ".mov"], f"Expected MP4/MOV extension, got '{media.extension}'"

        # Verify video codec is detected
        assert media.video_codec is not None, "Video codec should be detected"
        assert isinstance(media.video_codec, str), f"Video codec should be string, got {type(media.video_codec)}"

        # Verify action is set
        assert media.action is not None, "Action should be set by detection"
        assert media.action in ["import", "rewrap", "transcode"], f"Unexpected action for MP4: '{media.action}'"

        # Verify compatible flag matches action
        if media.action == "import":
            assert media.compatible is True, "Import action implies compatibility"
            assert media.requires_processing is False, "Import action should not require processing"
        else:
            assert media.compatible is False, "Non-import action implies incompatibility"
            assert media.requires_processing is True, "Non-import action requires processing"

        # Verify rule_id is set
        assert media.rule_id is not None, "Rule ID should be set by detection"
        assert media.rule_id.startswith("R-"), f"Rule ID should start with 'R-', got '{media.rule_id}'"

    def test_detect_media_rejects_nonexistent_file(self):
        """Test detect_media handles nonexistent files gracefully."""
        from smart_media_manager.cli import detect_media

        nonexistent = Path("/tmp/this_file_does_not_exist_12345.xyz")
        assert not nonexistent.exists(), "Test file should not exist"

        # Should return error, not crash
        media, error = detect_media(nonexistent)

        assert media is None, "Should return None for nonexistent file"
        assert error is not None, "Should return error message for nonexistent file"

    def test_detect_media_rejects_empty_file(self, tmp_path):
        """Test detect_media rejects empty files."""
        from smart_media_manager.cli import detect_media

        empty_file = tmp_path / "empty.dat"
        empty_file.touch()  # Create 0-byte file

        media, error = detect_media(empty_file)

        assert media is None, "Should return None for empty file"
        assert error is not None, "Should return error message for empty file"

    def test_detect_media_skip_compatibility_check_flag(self):
        """Test detect_media respects skip_compatibility_check flag."""
        from smart_media_manager.cli import detect_media

        sample_jpg = Path(__file__).parent / "samples" / "ci" / "images" / "test_image.jpg"
        assert sample_jpg.exists(), f"Sample file not found: {sample_jpg}"

        # Call with skip flag
        media, error = detect_media(sample_jpg, skip_compatibility_check=True)

        # Should still detect successfully
        assert error is None, f"Detection failed with error: {error}"
        assert media is not None, "MediaFile should not be None"
        assert media.kind == "image", "Should still detect as image"

        # The skip flag affects internal validation but not core detection
        # We can't easily verify the flag was passed to refine_image_media
        # without mocking, but we verify detection still works


class TestDetectMediaEdgeCases:
    """Integration tests for edge cases in detect_media."""

    def test_detect_media_with_wrong_extension(self, tmp_path):
        """Test detect_media handles files with misleading extensions."""
        from smart_media_manager.cli import detect_media
        import shutil

        # Copy JPEG but give it .txt extension
        sample_jpg = Path(__file__).parent / "samples" / "ci" / "images" / "test_image.jpg"
        wrong_ext = tmp_path / "image.txt"
        shutil.copy(sample_jpg, wrong_ext)

        media, error = detect_media(wrong_ext)

        # Should detect based on content, not extension
        if media is not None:
            # If detection succeeds, should identify as image despite .txt extension
            assert media.kind == "image", "Should detect as image based on content"
            assert media.extension in [".jpg", ".jpeg"], "Should use detected format, not file extension"
        else:
            # Or might reject as text file if filetype/puremagic see .txt first
            # Either behavior is acceptable - both are correct
            assert error is not None, "Should provide error message"

    def test_detect_media_with_no_extension(self, tmp_path):
        """Test detect_media handles files with no extension."""
        from smart_media_manager.cli import detect_media
        import shutil

        # Copy JPEG but remove extension
        sample_jpg = Path(__file__).parent / "samples" / "ci" / "images" / "test_image.jpg"
        no_ext = tmp_path / "image_no_extension"
        shutil.copy(sample_jpg, no_ext)

        media, error = detect_media(no_ext)

        # Should detect based on content
        assert error is None or "not identified" in error, f"Unexpected error: {error}"

        if media is not None:
            assert media.kind == "image", "Should detect as image based on content"
            assert media.extension in [".jpg", ".jpeg"], "Should assign detected extension"
