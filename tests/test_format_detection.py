"""
Unit tests for format detection and voting functions.

Tests cover:
- Format vote collection
- Consensus vote selection
- Media kind determination
"""

from unittest.mock import Mock, patch


class TestCollectFormatVotes:
    """Tests for collect_format_votes function."""

    @patch("smart_media_manager.cli.classify_with_binwalk")
    @patch("smart_media_manager.cli.classify_with_pyfsig")
    @patch("smart_media_manager.cli.classify_with_puremagic")
    @patch("smart_media_manager.cli.classify_with_libmagic")
    def test_collect_format_votes_calls_all_classifiers(self, mock_libmagic, mock_puremagic, mock_pyfsig, mock_binwalk, tmp_path):
        """Test collect_format_votes calls all 4 classifiers."""
        from smart_media_manager.cli import collect_format_votes, FormatVote

        test_file = tmp_path / "test.jpg"
        test_file.touch()

        # Create mock votes
        mock_libmagic.return_value = FormatVote(tool="libmagic", mime="image/jpeg", extension=".jpg")
        mock_puremagic.return_value = FormatVote(tool="puremagic", mime="image/jpeg", extension=".jpg")
        mock_pyfsig.return_value = FormatVote(tool="pyfsig", extension=".jpg")
        mock_binwalk.return_value = FormatVote(tool="binwalk", description="JPEG image data")

        result = collect_format_votes(test_file)

        # Should return 4 votes (one from each classifier)
        assert len(result) == 4
        assert result[0].tool == "libmagic"
        assert result[1].tool == "puremagic"
        assert result[2].tool == "pyfsig"
        assert result[3].tool == "binwalk"

        # Verify each classifier was called
        mock_libmagic.assert_called_once_with(test_file)
        mock_puremagic.assert_called_once_with(test_file, None)
        mock_pyfsig.assert_called_once_with(test_file)
        mock_binwalk.assert_called_once_with(test_file)

    @patch("smart_media_manager.cli.classify_with_binwalk")
    @patch("smart_media_manager.cli.classify_with_pyfsig")
    @patch("smart_media_manager.cli.classify_with_puremagic")
    @patch("smart_media_manager.cli.classify_with_libmagic")
    def test_collect_format_votes_passes_puremagic_signature(self, mock_libmagic, mock_puremagic, mock_pyfsig, mock_binwalk, tmp_path):
        """Test collect_format_votes passes puremagic signature."""
        from smart_media_manager.cli import collect_format_votes, FormatVote

        test_file = tmp_path / "test.jpg"
        test_file.touch()

        mock_sig = Mock()
        mock_sig.extension = ".jpg"

        mock_libmagic.return_value = FormatVote(tool="libmagic")
        mock_puremagic.return_value = FormatVote(tool="puremagic")
        mock_pyfsig.return_value = FormatVote(tool="pyfsig")
        mock_binwalk.return_value = FormatVote(tool="binwalk")

        collect_format_votes(test_file, puremagic_signature=mock_sig)

        # Should pass signature to puremagic
        mock_puremagic.assert_called_once_with(test_file, mock_sig)


class TestSelectConsensusVote:
    """Tests for select_consensus_vote function."""

    def test_select_consensus_vote_returns_none_for_empty_votes(self):
        """Test select_consensus_vote returns None for empty vote list."""
        from smart_media_manager.cli import select_consensus_vote

        result = select_consensus_vote([])

        assert result is None

    def test_select_consensus_vote_returns_none_for_all_error_votes(self):
        """Test select_consensus_vote returns None when all votes have errors."""
        from smart_media_manager.cli import select_consensus_vote, FormatVote

        votes = [
            FormatVote(tool="libmagic", error="libmagic not installed"),
            FormatVote(tool="puremagic", error="no match"),
        ]

        result = select_consensus_vote(votes)

        assert result is None

    def test_select_consensus_vote_selects_by_mime_consensus(self):
        """Test select_consensus_vote selects vote by MIME type consensus."""
        from smart_media_manager.cli import select_consensus_vote, FormatVote

        votes = [
            FormatVote(tool="libmagic", mime="image/jpeg", extension=".jpg", kind="image"),
            FormatVote(tool="puremagic", mime="image/jpeg", extension=".jpg", kind="image"),
            FormatVote(tool="binwalk", mime="image/png", extension=".png", kind="image"),
        ]

        result = select_consensus_vote(votes)

        # Should select JPEG (2 votes vs 1 vote)
        assert result is not None
        assert result.mime == "image/jpeg"

    def test_select_consensus_vote_selects_by_extension_when_no_mime_consensus(self):
        """Test select_consensus_vote selects by extension when no MIME consensus."""
        from smart_media_manager.cli import select_consensus_vote, FormatVote

        votes = [
            FormatVote(tool="libmagic", extension=".jpg", description="JPEG image"),
            FormatVote(tool="puremagic", extension=".jpg", description="JPEG image"),
            FormatVote(tool="binwalk", extension=".png", description="PNG image"),
        ]

        result = select_consensus_vote(votes)

        # Should select JPG (2 votes vs 1 vote)
        assert result is not None
        assert result.extension == ".jpg"

    def test_select_consensus_vote_uses_tool_priority_for_ties(self):
        """Test select_consensus_vote uses tool priority to break ties."""
        from smart_media_manager.cli import select_consensus_vote, FormatVote

        # libmagic has highest priority (1.4 weight)
        votes = [
            FormatVote(tool="libmagic", mime="image/jpeg", extension=".jpg"),
            FormatVote(tool="puremagic", mime="image/jpeg", extension=".jpg"),
        ]

        result = select_consensus_vote(votes)

        # Should select libmagic due to higher priority
        assert result is not None
        assert result.tool == "libmagic"

    def test_select_consensus_vote_handles_normalized_mime_types(self):
        """Test select_consensus_vote normalizes MIME types for comparison."""
        from smart_media_manager.cli import select_consensus_vote, FormatVote

        votes = [
            FormatVote(tool="libmagic", mime="image/jpeg", extension=".jpg"),
            FormatVote(tool="puremagic", mime="image/jpg", extension=".jpg"),  # Different MIME but same meaning
        ]

        result = select_consensus_vote(votes)

        # Should treat both as same MIME type
        assert result is not None
        assert result.extension == ".jpg"

    def test_select_consensus_vote_returns_highest_weighted_vote_as_fallback(self):
        """Test select_consensus_vote returns highest weighted vote when no consensus."""
        from smart_media_manager.cli import select_consensus_vote, FormatVote

        votes = [
            FormatVote(tool="binwalk", mime="image/jpeg", extension=".jpg"),  # weight 1.2
            FormatVote(tool="puremagic", mime="image/png", extension=".png"),  # weight 1.1
            FormatVote(tool="pyfsig", mime="video/mp4", extension=".mp4"),  # weight 1.0
        ]

        result = select_consensus_vote(votes)

        # Should return binwalk (highest weight 1.2)
        assert result is not None
        assert result.tool == "binwalk"


class TestDetermineMediaKind:
    """Tests for determine_media_kind function."""

    def test_determine_media_kind_returns_none_for_empty_votes(self):
        """Test determine_media_kind returns None for empty vote list."""
        from smart_media_manager.cli import determine_media_kind

        result = determine_media_kind([], None)

        assert result is None

    def test_determine_media_kind_returns_none_for_all_error_votes(self):
        """Test determine_media_kind returns None when all votes have errors."""
        from smart_media_manager.cli import determine_media_kind, FormatVote

        votes = [
            FormatVote(tool="libmagic", error="not installed"),
            FormatVote(tool="puremagic", error="no match"),
        ]

        result = determine_media_kind(votes, None)

        assert result is None

    def test_determine_media_kind_selects_by_kind_consensus(self):
        """Test determine_media_kind selects kind by consensus."""
        from smart_media_manager.cli import determine_media_kind, FormatVote

        votes = [
            FormatVote(tool="libmagic", mime="image/jpeg", kind="image"),
            FormatVote(tool="puremagic", mime="image/jpeg", kind="image"),
            FormatVote(tool="binwalk", mime="video/mp4", kind="video"),
        ]

        result = determine_media_kind(votes, None)

        # Should select "image" (2 votes vs 1 vote)
        assert result == "image"

    def test_determine_media_kind_prefers_consensus_vote_kind(self):
        """Test determine_media_kind prefers consensus vote when available."""
        from smart_media_manager.cli import determine_media_kind, FormatVote

        votes = [
            FormatVote(tool="libmagic", mime="image/jpeg", kind="image"),
            FormatVote(tool="puremagic", mime="video/mp4", kind="video"),
        ]

        consensus = FormatVote(tool="libmagic", mime="image/jpeg", kind="image")

        result = determine_media_kind(votes, consensus)

        # Should use consensus vote's kind
        assert result == "image"

    def test_determine_media_kind_infers_from_mime(self):
        """Test determine_media_kind infers kind from MIME type."""
        from smart_media_manager.cli import determine_media_kind, FormatVote

        votes = [
            FormatVote(tool="libmagic", mime="image/jpeg"),
            FormatVote(tool="puremagic", mime="image/png"),
        ]

        result = determine_media_kind(votes, None)

        # Should infer "image" from MIME types
        assert result == "image"

    def test_determine_media_kind_infers_from_extension(self):
        """Test determine_media_kind infers kind from extension."""
        from smart_media_manager.cli import determine_media_kind, FormatVote

        votes = [
            FormatVote(tool="libmagic", extension=".jpg"),
            FormatVote(tool="puremagic", extension=".png"),
        ]

        result = determine_media_kind(votes, None)

        # Should infer "image" from extensions
        assert result == "image"

    def test_determine_media_kind_uses_highest_priority_for_ties(self):
        """Test determine_media_kind uses tool priority to break ties."""
        from smart_media_manager.cli import determine_media_kind, FormatVote

        votes = [
            FormatVote(tool="libmagic", kind="image"),  # priority 0 (highest weight 1.4)
            FormatVote(tool="binwalk", kind="video"),  # priority 1 (weight 1.2)
        ]

        result = determine_media_kind(votes, None)

        # Should select "image" due to libmagic's higher weight
        assert result == "image"

    def test_determine_media_kind_returns_consensus_kind_when_no_votes_have_kind(self):
        """Test determine_media_kind falls back to consensus kind."""
        from smart_media_manager.cli import determine_media_kind, FormatVote

        votes = [
            FormatVote(tool="pyfsig", description="Unknown file"),
        ]

        consensus = FormatVote(tool="libmagic", mime="image/jpeg", kind="image")

        result = determine_media_kind(votes, consensus)

        # Should fall back to consensus
        assert result == "image"
