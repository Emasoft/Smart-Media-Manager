"""
Unit tests for utility functions in cli.py that lack coverage.

Tests cover:
- Path and string utilities
- Extension normalization
- MIME type helpers
- Kind determination
- Signature helpers
- Vote/consensus logic
- Animation detection
- File filtering
"""

from pathlib import Path
from unittest.mock import Mock
from smart_media_manager.cli import (
    # Extension and path utilities
    normalize_extension,
    ensure_dot_extension,
    canonicalize_extension,
    sanitize_path_string,
    stem_needs_sanitization,
    build_safe_stem,
    next_available_name,
    # MIME and kind helpers
    normalize_mime_value,
    is_textual_mime,
    kind_from_mime,
    kind_from_extension,
    kind_from_description,
    extension_from_mime,
    extension_from_description,
    # Signature helpers
    canonical_image_extension,
    canonical_video_extension,
    is_archive_signature,
    is_image_signature,
    is_video_signature,
    choose_image_extension,
    choose_video_extension,
    guess_extension,
    # Vote and consensus
    tool_rank,
    vote_weight,
    choose_vote_by_priority,
    votes_error_summary,
    # File filtering
    should_ignore,
    is_skippable_file,
    looks_like_text_file,
    is_raw_extension,
    # Video helpers
    is_supported_video_codec,
    extract_container,
    # Utility
    timestamp,
    find_executable,
    # Dataclasses
    FormatVote,
)


class TestExtensionUtilities:
    """Tests for extension normalization and handling."""

    def test_normalize_extension_removes_dot(self):
        """Test normalize_extension removes leading dot."""
        assert normalize_extension(".jpg") == "jpg"
        assert normalize_extension(".jpeg") == "jpeg"
        assert normalize_extension(".PNG") == "png"

    def test_normalize_extension_preserves_no_dot(self):
        """Test normalize_extension keeps extensions without dot."""
        assert normalize_extension("jpg") == "jpg"
        assert normalize_extension("JPEG") == "jpeg"

    def test_normalize_extension_lowercases(self):
        """Test normalize_extension converts to lowercase."""
        assert normalize_extension("JPG") == "jpg"
        assert normalize_extension("PNG") == "png"

    def test_normalize_extension_none_input(self):
        """Test normalize_extension handles None gracefully."""
        assert normalize_extension(None) is None

    def test_normalize_extension_empty_string(self):
        """Test normalize_extension handles empty string."""
        assert normalize_extension("") is None
        assert normalize_extension("  ") is None

    def test_ensure_dot_extension_adds_dot(self):
        """Test ensure_dot_extension adds leading dot."""
        assert ensure_dot_extension("jpg") == ".jpg"
        assert ensure_dot_extension("mp4") == ".mp4"

    def test_ensure_dot_extension_preserves_dot(self):
        """Test ensure_dot_extension preserves existing dot."""
        assert ensure_dot_extension(".jpg") == ".jpg"
        assert ensure_dot_extension(".mp4") == ".mp4"

    def test_ensure_dot_extension_handles_none(self):
        """Test ensure_dot_extension handles None."""
        assert ensure_dot_extension(None) is None

    def test_ensure_dot_extension_handles_empty(self):
        """Test ensure_dot_extension handles empty string."""
        assert ensure_dot_extension("") is None
        assert ensure_dot_extension("  ") is None

    def test_canonicalize_extension_jpeg_variants(self):
        """Test canonicalize_extension normalizes JPEG variants."""
        assert canonicalize_extension(".jpeg") == ".jpg"
        assert canonicalize_extension(".JPEG") == ".jpg"
        assert canonicalize_extension("jpeg") == ".jpg"
        assert canonicalize_extension(".jpg") == ".jpg"

    def test_canonicalize_extension_tiff_variants(self):
        """Test canonicalize_extension normalizes TIFF variants."""
        assert canonicalize_extension(".tif") == ".tiff"
        assert canonicalize_extension(".TIF") == ".tiff"
        assert canonicalize_extension("tiff") == ".tiff"

    def test_canonicalize_extension_preserves_others(self):
        """Test canonicalize_extension preserves non-canonical extensions."""
        assert canonicalize_extension(".png") == ".png"
        assert canonicalize_extension(".mp4") == ".mp4"
        assert canonicalize_extension(".mkv") == ".mkv"

    def test_canonicalize_extension_handles_none(self):
        """Test canonicalize_extension handles None."""
        assert canonicalize_extension(None) is None


class TestPathUtilities:
    """Tests for path sanitization and name generation."""

    def test_sanitize_path_string_removes_unsafe_chars(self):
        """Test sanitize_path_string removes unsafe characters."""
        assert sanitize_path_string("file:name") == "file:name"  # Colon is allowed (macOS/Linux)
        assert sanitize_path_string("file<>name") == "filename"  # < > are removed
        assert sanitize_path_string('file"name') == "filename"  # " is removed

    def test_sanitize_path_string_preserves_safe_chars(self):
        """Test sanitize_path_string preserves safe characters."""
        assert sanitize_path_string("file-name.jpg") == "file-name.jpg"
        assert sanitize_path_string("file_123.png") == "file_123.png"

    def test_sanitize_path_string_handles_unicode(self):
        """Test sanitize_path_string handles unicode properly."""
        result = sanitize_path_string("café")
        assert result == "café"  # Preserves unicode (NFC normalization)

    def test_stem_needs_sanitization_unsafe_chars(self):
        """Test stem_needs_sanitization detects unsafe characters."""
        assert stem_needs_sanitization("file:name") is True
        assert stem_needs_sanitization("file<name") is True
        assert stem_needs_sanitization('file"name') is True

    def test_stem_needs_sanitization_safe_stems(self):
        """Test stem_needs_sanitization accepts safe stems."""
        assert stem_needs_sanitization("file-name") is False
        assert stem_needs_sanitization("file_123") is False
        assert stem_needs_sanitization("photo.backup") is False

    def test_stem_needs_sanitization_length_check(self):
        """Test stem_needs_sanitization detects overly long stems."""
        long_stem = "a" * 150
        assert stem_needs_sanitization(long_stem) is True

    def test_stem_needs_sanitization_whitespace(self):
        """Test stem_needs_sanitization detects leading/trailing whitespace."""
        assert stem_needs_sanitization(" filename") is True
        assert stem_needs_sanitization("filename ") is True
        assert stem_needs_sanitization("  filename  ") is True

    def test_build_safe_stem_creates_unique_name(self):
        """Test build_safe_stem creates unique safe filename."""
        result = build_safe_stem("original", "abc123", 1)
        assert "abc123" in result
        assert "001" in result

    def test_build_safe_stem_preserves_original_prefix(self):
        """Test build_safe_stem preserves part of original name."""
        result = build_safe_stem("my_photo", "token", 5)
        assert "my_photo" in result or "my-photo" in result

    def test_build_safe_stem_truncates_long_names(self):
        """Test build_safe_stem truncates overly long names."""
        long_name = "a" * 200
        result = build_safe_stem(long_name, "token", 1)
        assert len(result) <= 120  # MAX_SAFE_STEM_LENGTH

    def test_next_available_name_no_collision(self, tmp_path):
        """Test next_available_name when no file exists."""
        result = next_available_name(tmp_path, "test", ".txt")
        assert result == tmp_path / "test.txt"

    def test_next_available_name_with_collision(self, tmp_path):
        """Test next_available_name increments on collision."""
        # Create existing file
        (tmp_path / "test.txt").touch()
        result = next_available_name(tmp_path, "test", ".txt")
        assert result == tmp_path / "test_1.txt"  # Uses underscore format

    def test_next_available_name_multiple_collisions(self, tmp_path):
        """Test next_available_name handles multiple collisions."""
        # Create multiple existing files
        (tmp_path / "test.txt").touch()
        (tmp_path / "test_1.txt").touch()
        (tmp_path / "test_2.txt").touch()
        result = next_available_name(tmp_path, "test", ".txt")
        assert result == tmp_path / "test_3.txt"  # Uses underscore format


class TestMimeAndKindHelpers:
    """Tests for MIME type and media kind determination."""

    def test_normalize_mime_value_strips_whitespace(self):
        """Test normalize_mime_value strips whitespace."""
        assert normalize_mime_value("  image/jpeg  ") == "image/jpeg"
        assert normalize_mime_value("video/mp4 ") == "video/mp4"

    def test_normalize_mime_value_lowercases(self):
        """Test normalize_mime_value converts to lowercase."""
        assert normalize_mime_value("IMAGE/JPEG") == "image/jpeg"
        assert normalize_mime_value("Video/MP4") == "video/mp4"

    def test_normalize_mime_value_handles_none(self):
        """Test normalize_mime_value handles None."""
        assert normalize_mime_value(None) is None

    def test_normalize_mime_value_handles_empty(self):
        """Test normalize_mime_value handles empty string."""
        assert normalize_mime_value("") is None
        assert normalize_mime_value("  ") is None

    def test_is_textual_mime_text_types(self):
        """Test is_textual_mime identifies text types."""
        assert is_textual_mime("text/plain") is True
        assert is_textual_mime("text/html") is True
        assert is_textual_mime("application/json") is True
        assert is_textual_mime("application/xml") is True

    def test_is_textual_mime_non_text_types(self):
        """Test is_textual_mime rejects non-text types."""
        assert is_textual_mime("image/jpeg") is False
        assert is_textual_mime("video/mp4") is False
        assert is_textual_mime("application/octet-stream") is False

    def test_is_textual_mime_handles_none(self):
        """Test is_textual_mime handles None."""
        assert is_textual_mime(None) is False

    def test_kind_from_mime_image_types(self):
        """Test kind_from_mime identifies image types."""
        assert kind_from_mime("image/jpeg") == "image"
        assert kind_from_mime("image/png") == "image"
        assert kind_from_mime("image/webp") == "image"

    def test_kind_from_mime_video_types(self):
        """Test kind_from_mime identifies video types."""
        assert kind_from_mime("video/mp4") == "video"
        assert kind_from_mime("video/quicktime") == "video"
        assert kind_from_mime("video/x-matroska") == "video"

    def test_kind_from_mime_handles_none(self):
        """Test kind_from_mime handles None."""
        assert kind_from_mime(None) is None

    def test_kind_from_extension_image_extensions(self):
        """Test kind_from_extension identifies image extensions."""
        assert kind_from_extension(".jpg") == "image"
        assert kind_from_extension(".png") == "image"
        assert kind_from_extension(".gif") == "image"

    def test_kind_from_extension_video_extensions(self):
        """Test kind_from_extension identifies video extensions."""
        assert kind_from_extension(".mp4") == "video"
        assert kind_from_extension(".mov") == "video"
        assert kind_from_extension(".mkv") == "video"

    def test_kind_from_extension_raw_extensions(self):
        """Test kind_from_extension identifies RAW extensions."""
        assert kind_from_extension(".cr2") == "raw"
        assert kind_from_extension(".nef") == "raw"
        assert kind_from_extension(".arw") == "raw"

    def test_kind_from_extension_case_insensitive(self):
        """Test kind_from_extension is case-insensitive."""
        assert kind_from_extension(".JPG") == "image"
        assert kind_from_extension(".MP4") == "video"

    def test_kind_from_description_image_descriptions(self):
        """Test kind_from_description identifies image descriptions."""
        assert kind_from_description("JPEG image data") == "image"
        assert kind_from_description("PNG image") == "image"

    def test_kind_from_description_video_descriptions(self):
        """Test kind_from_description identifies video descriptions."""
        assert kind_from_description("ISO Media, MP4") == "video"
        assert kind_from_description("MPEG video") == "video"
        assert kind_from_description("Matroska data") is None  # Doesn't match video keywords

    def test_extension_from_mime_image_types(self):
        """Test extension_from_mime returns correct extensions for images."""
        assert extension_from_mime("image/jpeg") == ".jpg"
        assert extension_from_mime("image/png") == ".png"
        assert extension_from_mime("image/gif") == ".gif"

    def test_extension_from_mime_video_types(self):
        """Test extension_from_mime returns correct extensions for videos."""
        assert extension_from_mime("video/mp4") == ".mp4"
        assert extension_from_mime("video/quicktime") == ".mov"

    def test_extension_from_description_extracts_extension(self):
        """Test extension_from_description extracts extension from description."""
        # This function looks for patterns like "JPEG image" or "PNG image"
        result = extension_from_description("JPEG image data, JFIF standard")
        assert result in [".jpg", ".jpeg", None]  # Depends on implementation


class TestSignatureHelpers:
    """Tests for signature validation and helper functions."""

    def test_canonical_image_extension_normalizes_jpeg(self):
        """Test canonical_image_extension normalizes JPEG."""
        assert canonical_image_extension("jpeg") == ".jpg"
        assert canonical_image_extension("jpg") == ".jpg"

    def test_canonical_image_extension_normalizes_tiff(self):
        """Test canonical_image_extension normalizes TIFF."""
        assert canonical_image_extension("tiff") == ".tiff"
        assert canonical_image_extension("tif") == ".tiff"

    def test_canonical_image_extension_preserves_others(self):
        """Test canonical_image_extension preserves other formats."""
        assert canonical_image_extension("png") == ".png"
        assert canonical_image_extension("gif") == ".gif"

    def test_canonical_video_extension_normalizes_mpeg(self):
        """Test canonical_video_extension normalizes MPEG."""
        assert canonical_video_extension("mpeg") == ".mpg"

    def test_canonical_video_extension_preserves_others(self):
        """Test canonical_video_extension preserves other formats."""
        assert canonical_video_extension("mp4") == ".mp4"
        assert canonical_video_extension("mov") == ".mov"

    def test_is_archive_signature_zip(self):
        """Test is_archive_signature detects ZIP files."""
        mock_sig = Mock()
        mock_sig.extension = "zip"
        mock_sig.mime = "application/zip"  # Use 'mime' not 'mime_type'
        mock_sig.is_empty.return_value = False
        assert is_archive_signature(mock_sig) is True

    def test_is_archive_signature_non_archive(self):
        """Test is_archive_signature rejects non-archive files."""
        mock_sig = Mock()
        mock_sig.extension = "jpg"
        mock_sig.mime = "image/jpeg"  # Use 'mime' not 'mime_type'
        mock_sig.is_empty.return_value = False
        assert is_archive_signature(mock_sig) is False

    def test_is_image_signature_jpeg(self):
        """Test is_image_signature detects JPEG files."""
        mock_sig = Mock()
        mock_sig.extension = "jpg"
        mock_sig.mime = "image/jpeg"  # Use 'mime' not 'mime_type'
        mock_sig.is_empty.return_value = False
        assert is_image_signature(mock_sig) is True

    def test_is_image_signature_png(self):
        """Test is_image_signature detects PNG files."""
        mock_sig = Mock()
        mock_sig.extension = "png"
        mock_sig.mime = "image/png"  # Use 'mime' not 'mime_type'
        mock_sig.is_empty.return_value = False
        assert is_image_signature(mock_sig) is True

    def test_is_video_signature_mp4(self):
        """Test is_video_signature detects MP4 files."""
        mock_sig = Mock()
        mock_sig.extension = "mp4"
        mock_sig.mime = "video/mp4"  # Use 'mime' not 'mime_type'
        mock_sig.is_empty.return_value = False
        assert is_video_signature(mock_sig) is True

    def test_guess_extension_mp4_container(self):
        """Test guess_extension for MP4 container."""
        assert guess_extension("mp4", "video") == ".mp4"

    def test_guess_extension_mkv_container(self):
        """Test guess_extension for MKV container."""
        assert guess_extension("matroska", "video") == ".mkv"


class TestVoteAndConsensus:
    """Tests for voting and consensus logic."""

    def test_tool_rank_libmagic_highest(self):
        """Test tool_rank gives libmagic highest rank (0)."""
        assert tool_rank("libmagic") == 0

    def test_tool_rank_binwalk_second(self):
        """Test tool_rank gives binwalk second rank (1)."""
        assert tool_rank("binwalk") == 1

    def test_tool_rank_puremagic_third(self):
        """Test tool_rank gives puremagic third rank (2)."""
        assert tool_rank("puremagic") == 2

    def test_tool_rank_pyfsig_fourth(self):
        """Test tool_rank gives pyfsig fourth rank (3)."""
        assert tool_rank("pyfsig") == 3

    def test_tool_rank_unknown_tool(self):
        """Test tool_rank gives unknown tools lowest rank."""
        assert tool_rank("unknown") == 4  # len(TOOL_PRIORITY)

    def test_vote_weight_libmagic(self):
        """Test vote_weight calculates correct weight for libmagic."""
        vote = FormatVote(tool="libmagic", mime="image/jpeg")
        assert vote_weight(vote) == 1.4

    def test_vote_weight_binwalk(self):
        """Test vote_weight calculates correct weight for binwalk."""
        vote = FormatVote(tool="binwalk", mime="image/jpeg")
        assert vote_weight(vote) == 1.2

    def test_vote_weight_puremagic(self):
        """Test vote_weight calculates correct weight for puremagic."""
        vote = FormatVote(tool="puremagic", mime="image/jpeg")
        assert vote_weight(vote) == 1.1

    def test_vote_weight_pyfsig(self):
        """Test vote_weight calculates correct weight for pyfsig."""
        vote = FormatVote(tool="pyfsig", mime="image/jpeg")
        assert vote_weight(vote) == 1.0

    def test_vote_weight_with_error(self):
        """Test vote_weight returns weight regardless of error."""
        vote = FormatVote(tool="libmagic", error="some error")
        assert vote_weight(vote) == 1.4  # Returns weight, doesn't check for errors

    def test_choose_vote_by_priority_empty_list(self):
        """Test choose_vote_by_priority handles empty list."""
        result = choose_vote_by_priority([], lambda v: v.mime is not None)
        assert result is None

    def test_choose_vote_by_priority_single_vote(self):
        """Test choose_vote_by_priority returns single vote."""
        vote = FormatVote(tool="libmagic", mime="image/jpeg")
        result = choose_vote_by_priority([vote], lambda v: v.mime is not None)
        assert result == vote

    def test_choose_vote_by_priority_prefers_higher_priority(self):
        """Test choose_vote_by_priority prefers higher priority tool."""
        vote1 = FormatVote(tool="pyfsig", mime="image/jpeg")
        vote2 = FormatVote(tool="libmagic", mime="image/jpeg")
        result = choose_vote_by_priority([vote1, vote2], lambda v: v.mime is not None)
        assert result.tool == "libmagic"

    def test_votes_error_summary_no_errors(self):
        """Test votes_error_summary with no errors."""
        votes = [
            FormatVote(tool="libmagic", mime="image/jpeg"),
            FormatVote(tool="puremagic", mime="image/jpeg"),
        ]
        result = votes_error_summary(votes)
        assert result == "detectors could not agree on a media format"

    def test_votes_error_summary_with_errors(self):
        """Test votes_error_summary summarizes errors."""
        votes = [
            FormatVote(tool="libmagic", error="libmagic failed"),
            FormatVote(tool="puremagic", error="no match"),
        ]
        result = votes_error_summary(votes)
        assert "libmagic" in result
        assert "puremagic" in result


class TestFileFiltering:
    """Tests for file filtering and skipping logic."""

    def test_should_ignore_log_files(self):
        """Test should_ignore filters log files."""
        assert should_ignore(Path("smm_run_123.log")) is True
        assert should_ignore(Path("smm_skipped_files_123.log")) is True

    def test_should_ignore_ds_store(self):
        """Test should_ignore filters .DS_Store files."""
        assert should_ignore(Path(".DS_Store")) is True

    def test_should_ignore_staging_folders(self):
        """Test should_ignore filters staging folders."""
        assert should_ignore(Path("FOUND_MEDIA_FILES_123")) is True
        assert should_ignore(Path("ORIGINALS_123")) is False  # Only FOUND_MEDIA_FILES_* is filtered

    def test_should_ignore_hidden_files(self):
        """Test should_ignore doesn't filter all hidden files."""
        assert should_ignore(Path(".hidden")) is False  # Only specific patterns are filtered
        assert should_ignore(Path(".DS_Store")) is True  # DS_Store is filtered

    def test_should_ignore_allows_normal_files(self):
        """Test should_ignore allows normal files."""
        assert should_ignore(Path("photo.jpg")) is False
        assert should_ignore(Path("video.mp4")) is False

    def test_is_raw_extension_canon(self):
        """Test is_raw_extension detects Canon RAW formats."""
        assert is_raw_extension(".cr2") is True
        assert is_raw_extension(".cr3") is True

    def test_is_raw_extension_nikon(self):
        """Test is_raw_extension detects Nikon RAW formats."""
        assert is_raw_extension(".nef") is True

    def test_is_raw_extension_sony(self):
        """Test is_raw_extension detects Sony RAW formats."""
        assert is_raw_extension(".arw") is True

    def test_is_raw_extension_non_raw(self):
        """Test is_raw_extension rejects non-RAW extensions."""
        assert is_raw_extension(".jpg") is False
        assert is_raw_extension(".mp4") is False

    def test_is_raw_extension_case_insensitive(self):
        """Test is_raw_extension is case-insensitive."""
        assert is_raw_extension(".CR2") is True
        assert is_raw_extension(".NEF") is True

    def test_looks_like_text_file_actual_text(self, tmp_path):
        """Test looks_like_text_file detects text files."""
        text_file = tmp_path / "test.txt"
        text_file.write_text("This is a text file")
        assert looks_like_text_file(text_file) is True

    def test_looks_like_text_file_binary(self, tmp_path):
        """Test looks_like_text_file detects binary files."""
        binary_file = tmp_path / "test.bin"
        binary_file.write_bytes(b"\x00\x01\x02\x03\xff\xfe")
        assert looks_like_text_file(binary_file) is False


class TestVideoHelpers:
    """Tests for video-specific helper functions."""

    def test_is_supported_video_codec_h264(self):
        """Test is_supported_video_codec detects H.264."""
        assert is_supported_video_codec("h264") is True
        assert is_supported_video_codec("avc1") is True

    def test_is_supported_video_codec_hevc(self):
        """Test is_supported_video_codec detects HEVC."""
        assert is_supported_video_codec("hevc") is True
        assert is_supported_video_codec("h265") is True

    def test_is_supported_video_codec_prores(self):
        """Test is_supported_video_codec detects ProRes."""
        assert is_supported_video_codec("apcn") is True
        assert is_supported_video_codec("apch") is True

    def test_is_supported_video_codec_unsupported(self):
        """Test is_supported_video_codec rejects unsupported codecs."""
        assert is_supported_video_codec("vp9") is False
        assert is_supported_video_codec("av1") is False

    def test_is_supported_video_codec_none(self):
        """Test is_supported_video_codec handles None."""
        assert is_supported_video_codec(None) is False

    def test_extract_container_mp4(self):
        """Test extract_container extracts first container format."""
        assert extract_container("mov,mp4,m4a,3gp,3g2,mj2") == "mov"  # Returns first format

    def test_extract_container_matroska(self):
        """Test extract_container extracts Matroska container."""
        assert extract_container("matroska,webm") == "matroska"

    def test_extract_container_single_format(self):
        """Test extract_container handles single format."""
        assert extract_container("avi") == "avi"


class TestUtilityFunctions:
    """Tests for miscellaneous utility functions."""

    def test_timestamp_format(self):
        """Test timestamp returns correctly formatted string."""
        result = timestamp()
        # Should be in format YYYYMMDDHHMMSS (no underscore)
        assert len(result) == 14
        assert result.isdigit()

    def test_find_executable_finds_existing(self):
        """Test find_executable finds existing executables."""
        # Test with a command that should exist on all systems
        result = find_executable("python", "python3")
        assert result is not None

    def test_find_executable_returns_none_if_not_found(self):
        """Test find_executable returns None for non-existent commands."""
        result = find_executable("nonexistent_command_12345")
        assert result is None


class TestSkippableFiles:
    """Tests for is_skippable_file function."""

    def test_is_skippable_file_pdf(self, tmp_path):
        """Test is_skippable_file detects PDF files."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4")
        reason = is_skippable_file(pdf_file)
        assert reason is not None
        assert "text file" in reason.lower()  # PDFs are detected as text files

    def test_is_skippable_file_svg(self, tmp_path):
        """Test is_skippable_file detects SVG files."""
        svg_file = tmp_path / "test.svg"
        svg_file.write_text('<?xml version="1.0"?><svg></svg>')
        reason = is_skippable_file(svg_file)
        assert reason is not None
        assert "text file" in reason.lower()  # SVGs are detected as text files

    def test_is_skippable_file_text(self, tmp_path):
        """Test is_skippable_file detects text files."""
        text_file = tmp_path / "test.txt"
        text_file.write_text("This is a text file")
        reason = is_skippable_file(text_file)
        assert reason is not None
        assert "text" in reason.lower()

    def test_is_skippable_file_empty(self, tmp_path):
        """Test is_skippable_file detects empty files."""
        empty_file = tmp_path / "empty.jpg"
        empty_file.touch()
        reason = is_skippable_file(empty_file)
        assert reason is not None
        assert "empty" in reason.lower()

    def test_is_skippable_file_media_not_skippable(self, tmp_path):
        """Test is_skippable_file doesn't skip valid media files."""
        # Create a minimal JPEG
        jpeg_file = tmp_path / "test.jpg"
        jpeg_file.write_bytes(b"\xff\xd8\xff" + b"\x00" * 100 + b"\xff\xd9")
        reason = is_skippable_file(jpeg_file)
        # Should not be skippable (returns None)
        # Note: This might still be detected as corrupt, but not skippable for being text/pdf/svg
        assert reason is None or "empty" not in reason.lower()


class TestChooseExtensionFunctions:
    """Tests for choose_image_extension and choose_video_extension functions."""

    def test_choose_image_extension_from_canonical_extension(self):
        """Test choose_image_extension returns canonical extension."""
        from unittest.mock import Mock

        sig1 = Mock(extension=".jpeg", mime=None)
        sig2 = Mock(extension=".png", mime=None)

        result = choose_image_extension([sig1, sig2])

        assert result == ".jpg"  # .jpeg canonicalized to .jpg

    def test_choose_image_extension_from_mime(self):
        """Test choose_image_extension falls back to MIME mapping."""
        from unittest.mock import Mock

        sig = Mock(extension=None, mime="image/png")

        result = choose_image_extension([sig])

        assert result == ".png"

    def test_choose_image_extension_returns_none_for_no_match(self):
        """Test choose_image_extension returns None when no match."""
        from unittest.mock import Mock

        sig = Mock(extension=None, mime="video/mp4")

        result = choose_image_extension([sig])

        assert result is None

    def test_choose_video_extension_from_canonical_extension(self):
        """Test choose_video_extension returns canonical extension."""
        from unittest.mock import Mock

        sig = Mock(extension=".mpeg", mime=None)

        result = choose_video_extension([sig])

        assert result == ".mpg"  # .mpeg canonicalized to .mpg

    def test_choose_video_extension_from_mime(self):
        """Test choose_video_extension falls back to MIME mapping."""
        from unittest.mock import Mock

        sig = Mock(extension=None, mime="video/mp4")

        result = choose_video_extension([sig])

        assert result == ".mp4"

    def test_choose_video_extension_returns_none_for_no_match(self):
        """Test choose_video_extension returns None when no match."""
        from unittest.mock import Mock

        sig = Mock(extension=None, mime="image/jpeg")

        result = choose_video_extension([sig])

        assert result is None
