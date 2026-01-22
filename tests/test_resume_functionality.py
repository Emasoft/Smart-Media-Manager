"""
Unit tests for --resume functionality.

Tests cover:
- StagingState dataclass serialization/deserialization
- State file creation and loading
- Resume mode argument parsing
- Resume flow with different phases
"""

import json
from pathlib import Path

import pytest


class TestStagingState:
    """Tests for StagingState dataclass."""

    def test_staging_state_save_creates_file(self, tmp_path):
        """Test StagingState.save() creates .smm_state.json file."""
        from smart_media_manager.cli import StagingState

        staging_dir = tmp_path / "FOUND_MEDIA_FILES_20250101120000"
        staging_dir.mkdir()

        state = StagingState(
            phase="staged",
            staging_root=str(staging_dir),
            originals_root=str(tmp_path / "ORIGINALS_20250101120000"),
            output_dir=str(tmp_path),
            run_ts="20250101120000",
            album_name="Test Album",
            files=[],
        )
        state.save(staging_dir)

        state_file = staging_dir / ".smm_state.json"
        assert state_file.exists()

    def test_staging_state_save_writes_correct_content(self, tmp_path):
        """Test StagingState.save() writes all fields correctly."""
        from smart_media_manager.cli import StagingState

        staging_dir = tmp_path / "FOUND_MEDIA_FILES_20250101120000"
        staging_dir.mkdir()

        state = StagingState(
            phase="converted",
            staging_root=str(staging_dir),
            originals_root=str(tmp_path / "ORIGINALS_20250101120000"),
            output_dir=str(tmp_path),
            run_ts="20250101120000",
            album_name="My Album",
            files=[{"source": "/test/file.jpg", "kind": "image"}],
        )
        state.completed.append("/test/done.jpg")
        state.failed.append(("/test/fail.jpg", "conversion error"))
        state.save(staging_dir)

        state_file = staging_dir / ".smm_state.json"
        data = json.loads(state_file.read_text())

        assert data["phase"] == "converted"
        assert data["staging_root"] == str(staging_dir)
        assert data["run_ts"] == "20250101120000"
        assert data["album_name"] == "My Album"
        assert len(data["files"]) == 1
        assert data["completed"] == ["/test/done.jpg"]
        assert data["failed"] == [["/test/fail.jpg", "conversion error"]]

    def test_staging_state_load_restores_state(self, tmp_path):
        """Test StagingState.load() restores state from file."""
        from smart_media_manager.cli import StagingState

        staging_dir = tmp_path / "FOUND_MEDIA_FILES_20250101120000"
        staging_dir.mkdir()

        # Write state manually
        state_file = staging_dir / ".smm_state.json"
        state_file.write_text(
            json.dumps(
                {
                    "phase": "importing",
                    "staging_root": str(staging_dir),
                    "originals_root": str(tmp_path / "ORIGINALS"),
                    "output_dir": str(tmp_path),
                    "run_ts": "20250101120000",
                    "album_name": "Loaded Album",
                    "files": [{"source": "/test/file.jpg"}],
                    "completed": ["/test/done.jpg"],
                    "failed": [["/test/fail.jpg", "error"]],
                }
            )
        )

        loaded_state = StagingState.load(staging_dir)

        assert loaded_state.phase == "importing"
        assert loaded_state.staging_root == str(staging_dir)
        assert loaded_state.run_ts == "20250101120000"
        assert loaded_state.album_name == "Loaded Album"
        assert len(loaded_state.files) == 1
        assert loaded_state.completed == ["/test/done.jpg"]
        assert loaded_state.failed == [("/test/fail.jpg", "error")]

    def test_staging_state_load_raises_on_missing_file(self, tmp_path):
        """Test StagingState.load() raises FileNotFoundError if state file missing."""
        from smart_media_manager.cli import StagingState

        staging_dir = tmp_path / "FOUND_MEDIA_FILES_20250101120000"
        staging_dir.mkdir()

        with pytest.raises(FileNotFoundError):
            StagingState.load(staging_dir)

    def test_staging_state_mark_completed(self, tmp_path):
        """Test StagingState.mark_completed() adds file to completed list."""
        from smart_media_manager.cli import StagingState, MediaFile

        staging_dir = tmp_path / "FOUND_MEDIA_FILES_20250101120000"
        staging_dir.mkdir()

        state = StagingState(
            phase="importing",
            staging_root=str(staging_dir),
            originals_root=str(tmp_path / "ORIGINALS"),
            output_dir=str(tmp_path),
            run_ts="20250101120000",
            album_name="",
            files=[],
        )

        media = MediaFile(
            source=Path("/test/file.jpg"),
            kind="image",
            extension=".jpg",
            format_name="jpeg",
        )
        state.mark_completed(media)

        assert str(media.source) in state.completed

    def test_staging_state_mark_failed(self, tmp_path):
        """Test StagingState.mark_failed() adds file and reason to failed list."""
        from smart_media_manager.cli import StagingState, MediaFile

        staging_dir = tmp_path / "FOUND_MEDIA_FILES_20250101120000"
        staging_dir.mkdir()

        state = StagingState(
            phase="importing",
            staging_root=str(staging_dir),
            originals_root=str(tmp_path / "ORIGINALS"),
            output_dir=str(tmp_path),
            run_ts="20250101120000",
            album_name="",
            files=[],
        )

        media = MediaFile(
            source=Path("/test/file.jpg"),
            kind="image",
            extension=".jpg",
            format_name="jpeg",
        )
        state.mark_failed(media, "conversion failed")

        assert (str(media.source), "conversion failed") in state.failed

    def test_staging_state_is_completed(self, tmp_path):
        """Test StagingState.is_completed() correctly checks completion status."""
        from smart_media_manager.cli import StagingState, MediaFile

        staging_dir = tmp_path / "FOUND_MEDIA_FILES_20250101120000"
        staging_dir.mkdir()

        state = StagingState(
            phase="importing",
            staging_root=str(staging_dir),
            originals_root=str(tmp_path / "ORIGINALS"),
            output_dir=str(tmp_path),
            run_ts="20250101120000",
            album_name="",
            files=[],
        )

        media1 = MediaFile(
            source=Path("/test/file1.jpg"),
            kind="image",
            extension=".jpg",
            format_name="jpeg",
        )
        media2 = MediaFile(
            source=Path("/test/file2.jpg"),
            kind="image",
            extension=".jpg",
            format_name="jpeg",
        )

        state.mark_completed(media1)

        assert state.is_completed(media1) is True
        assert state.is_completed(media2) is False


class TestStagingStateMediaFileSerialization:
    """Tests for MediaFile serialization in StagingState."""

    def test_media_file_to_dict_basic(self, tmp_path):
        """Test media_file_to_dict() converts basic MediaFile to dict."""
        from smart_media_manager.cli import StagingState, MediaFile

        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()

        state = StagingState(
            phase="staged",
            staging_root=str(staging_dir),
            originals_root=str(tmp_path / "originals"),
            output_dir=str(tmp_path),
            run_ts="20250101120000",
            album_name="",
            files=[],
        )

        media = MediaFile(
            source=Path("/test/photo.jpg"),
            kind="image",
            extension=".jpg",
            format_name="jpeg",
            compatible=True,
        )

        result = state.media_file_to_dict(media)

        assert result["source"] == "/test/photo.jpg"
        assert result["kind"] == "image"
        assert result["extension"] == ".jpg"
        assert result["format_name"] == "jpeg"
        assert result["compatible"] is True

    def test_media_file_to_dict_with_stage_path(self, tmp_path):
        """Test media_file_to_dict() includes stage_path when set."""
        from smart_media_manager.cli import StagingState, MediaFile

        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()

        state = StagingState(
            phase="staged",
            staging_root=str(staging_dir),
            originals_root=str(tmp_path / "originals"),
            output_dir=str(tmp_path),
            run_ts="20250101120000",
            album_name="",
            files=[],
        )

        media = MediaFile(
            source=Path("/test/photo.jpg"),
            kind="image",
            extension=".jpg",
            format_name="jpeg",
        )
        media.stage_path = staging_dir / "photo_0001.jpg"

        result = state.media_file_to_dict(media)

        assert result["stage_path"] == str(staging_dir / "photo_0001.jpg")

    def test_dict_to_media_file_basic(self, tmp_path):
        """Test dict_to_media_file() restores MediaFile from dict."""
        from smart_media_manager.cli import StagingState

        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()

        state = StagingState(
            phase="staged",
            staging_root=str(staging_dir),
            originals_root=str(tmp_path / "originals"),
            output_dir=str(tmp_path),
            run_ts="20250101120000",
            album_name="",
            files=[],
        )

        data = {
            "source": "/test/photo.jpg",
            "kind": "image",
            "extension": ".jpg",
            "format_name": "jpeg",
            "compatible": True,
            "stage_path": str(staging_dir / "photo_0001.jpg"),
            "video_codec": None,
            "audio_codec": None,
            "original_suffix": None,
            "rule_id": "R-IMG-001",
            "action": "import",
            "requires_processing": False,
            "notes": "",
            "metadata": {},
            "was_converted": False,
        }

        media = state.dict_to_media_file(data)

        assert media.source == Path("/test/photo.jpg")
        assert media.kind == "image"
        assert media.extension == ".jpg"
        assert media.format_name == "jpeg"
        assert media.compatible is True
        assert media.stage_path == staging_dir / "photo_0001.jpg"
        assert media.rule_id == "R-IMG-001"

    def test_roundtrip_serialization(self, tmp_path):
        """Test MediaFile survives roundtrip through dict serialization."""
        from smart_media_manager.cli import StagingState, MediaFile

        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()

        state = StagingState(
            phase="staged",
            staging_root=str(staging_dir),
            originals_root=str(tmp_path / "originals"),
            output_dir=str(tmp_path),
            run_ts="20250101120000",
            album_name="",
            files=[],
        )

        original = MediaFile(
            source=Path("/test/video.mp4"),
            kind="video",
            extension=".mp4",
            format_name="mp4",
            compatible=True,
            video_codec="h264",
            audio_codec="aac",
        )
        original.stage_path = staging_dir / "video_0001.mp4"
        original.rule_id = "R-VID-001"
        original.action = "import"
        original.requires_processing = False

        # Roundtrip
        data = state.media_file_to_dict(original)
        restored = state.dict_to_media_file(data)

        assert restored.source == original.source
        assert restored.kind == original.kind
        assert restored.extension == original.extension
        assert restored.format_name == original.format_name
        assert restored.compatible == original.compatible
        assert restored.stage_path == original.stage_path
        assert restored.video_codec == original.video_codec
        assert restored.audio_codec == original.audio_codec
        assert restored.rule_id == original.rule_id
        assert restored.action == original.action


class TestResumeArgumentParsing:
    """Tests for --resume argument parsing."""

    def test_parse_args_resume_without_path(self, tmp_path, monkeypatch):
        """Test --resume can be used without PATH argument."""
        from smart_media_manager.cli import parse_args
        import json

        # Create a valid staging directory with state file
        staging_dir = tmp_path / "FOUND_MEDIA_FILES_20250101120000"
        staging_dir.mkdir()
        state_file = staging_dir / ".smm_state.json"
        state_file.write_text(
            json.dumps(
                {
                    "phase": "converted",
                    "staging_root": str(staging_dir),
                    "originals_root": str(tmp_path / "ORIGINALS"),
                    "output_dir": str(tmp_path),
                    "run_ts": "20250101120000",
                    "album_name": "",
                    "files": [],
                    "completed": [],
                    "failed": [],
                }
            )
        )

        monkeypatch.setattr("sys.argv", ["smm", "--resume", str(staging_dir), "--skip-bootstrap"])

        args = parse_args()

        assert args.resume_staging == staging_dir
        assert args.path is None

    def test_parse_args_resume_with_path_fails(self, tmp_path, monkeypatch, capsys):
        """Test --resume with PATH argument raises error."""
        import json

        # Create a valid staging directory with state file
        staging_dir = tmp_path / "FOUND_MEDIA_FILES_20250101120000"
        staging_dir.mkdir()
        state_file = staging_dir / ".smm_state.json"
        state_file.write_text(
            json.dumps(
                {
                    "phase": "converted",
                    "staging_root": str(staging_dir),
                    "originals_root": str(tmp_path / "ORIGINALS"),
                    "output_dir": str(tmp_path),
                    "run_ts": "20250101120000",
                    "album_name": "",
                    "files": [],
                    "completed": [],
                    "failed": [],
                }
            )
        )

        monkeypatch.setattr(
            "sys.argv",
            ["smm", str(tmp_path), "--resume", str(staging_dir), "--skip-bootstrap"],
        )

        from smart_media_manager.cli import parse_args

        with pytest.raises(SystemExit):
            parse_args()

    def test_parse_args_resume_missing_dir_fails(self, tmp_path, monkeypatch):
        """Test --resume with non-existent directory raises error."""
        monkeypatch.setattr(
            "sys.argv",
            [
                "smm",
                "--resume",
                str(tmp_path / "nonexistent"),
                "--skip-bootstrap",
            ],
        )

        from smart_media_manager.cli import parse_args

        with pytest.raises(SystemExit):
            parse_args()

    def test_parse_args_resume_missing_state_file_fails(self, tmp_path, monkeypatch):
        """Test --resume with directory lacking state file raises error."""
        staging_dir = tmp_path / "FOUND_MEDIA_FILES_20250101120000"
        staging_dir.mkdir()  # No state file

        monkeypatch.setattr("sys.argv", ["smm", "--resume", str(staging_dir), "--skip-bootstrap"])

        from smart_media_manager.cli import parse_args

        with pytest.raises(SystemExit):
            parse_args()
