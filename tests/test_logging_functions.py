"""
Unit tests for logging and configuration functions.

Tests cover:
- File logger attachment
- Log directory creation
- Handler management
"""

from unittest.mock import patch
import logging


class TestAttachFileLogger:
    """Tests for attach_file_logger function."""

    @patch("smart_media_manager.cli._FILE_LOG_HANDLER", None)
    def test_attach_file_logger_creates_log_file(self, tmp_path, monkeypatch):
        """Test attach_file_logger creates log file and directory."""
        from smart_media_manager.cli import attach_file_logger

        # Change to temp directory
        monkeypatch.chdir(tmp_path)

        root = tmp_path / "media"
        run_ts = "20250101120000"

        # Execute
        log_path = attach_file_logger(root, run_ts)

        # Verify log file created
        assert log_path.exists()
        assert log_path.is_file()
        assert log_path.name == f"smm_run_{run_ts}.log"

        # Verify log directory created with correct pattern
        log_dir = log_path.parent
        assert log_dir.exists()
        assert log_dir.is_dir()
        assert log_dir.name.startswith(".smm__runtime_logs_20250101120000_")

    @patch("smart_media_manager.cli._FILE_LOG_HANDLER", None)
    def test_attach_file_logger_returns_same_path_when_called_twice(self, tmp_path, monkeypatch):
        """Test attach_file_logger returns same path on subsequent calls."""
        from smart_media_manager.cli import attach_file_logger

        monkeypatch.chdir(tmp_path)

        root = tmp_path / "media"
        run_ts = "20250101120000"

        # First call
        log_path1 = attach_file_logger(root, run_ts)

        # Second call
        log_path2 = attach_file_logger(root, run_ts)

        # Should return same path
        assert log_path1 == log_path2

    @patch("smart_media_manager.cli._FILE_LOG_HANDLER", None)
    def test_attach_file_logger_attaches_handler_to_log(self, tmp_path, monkeypatch):
        """Test attach_file_logger attaches handler to LOG."""
        from smart_media_manager.cli import attach_file_logger, LOG

        monkeypatch.chdir(tmp_path)

        root = tmp_path / "media"
        run_ts = "20250101120000"

        # Count handlers before
        handlers_before = len(LOG.handlers)

        # Execute
        attach_file_logger(root, run_ts)

        # Count handlers after
        handlers_after = len(LOG.handlers)

        # Should have one more handler
        assert handlers_after == handlers_before + 1

        # Verify handler is FileHandler
        file_handlers = [h for h in LOG.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) >= 1


class TestConfigureLogging:
    """Tests for configure_logging function."""

    def test_configure_logging_sets_log_level_to_debug(self):
        """Test configure_logging sets LOG level to DEBUG (allows all messages to file handlers)."""
        from smart_media_manager.cli import configure_logging, LOG

        configure_logging()

        # LOG level is DEBUG to allow all messages through to file handlers
        # Console handler controls what the user sees (default: WARNING)
        assert LOG.level == logging.DEBUG

    def test_configure_logging_clears_existing_handlers(self):
        """Test configure_logging clears existing handlers."""
        from smart_media_manager.cli import configure_logging, LOG

        # Add a dummy handler
        dummy_handler = logging.StreamHandler()
        LOG.addHandler(dummy_handler)

        configure_logging()

        # Should have cleared and added only the console handler
        assert len(LOG.handlers) == 1
        assert dummy_handler not in LOG.handlers

    def test_configure_logging_adds_console_handler(self):
        """Test configure_logging adds StreamHandler to LOG."""
        from smart_media_manager.cli import configure_logging, LOG

        # Clear handlers first
        LOG.handlers.clear()

        configure_logging()

        # Should have one handler
        assert len(LOG.handlers) == 1

        # Should be a StreamHandler
        handler = LOG.handlers[0]
        assert isinstance(handler, logging.StreamHandler)

    def test_configure_logging_sets_console_level_to_warning(self):
        """Test configure_logging sets console handler level to WARNING."""
        from smart_media_manager.cli import configure_logging, LOG

        LOG.handlers.clear()

        configure_logging()

        # Get the console handler
        handler = LOG.handlers[0]

        # Should be WARNING level
        assert handler.level == logging.WARNING

    def test_configure_logging_sets_proper_formatter(self):
        """Test configure_logging sets proper formatter on console handler."""
        from smart_media_manager.cli import configure_logging, LOG

        LOG.handlers.clear()

        configure_logging()

        # Get the console handler
        handler = LOG.handlers[0]

        # Should have a formatter
        assert handler.formatter is not None

        # Test formatter format string
        formatter = handler.formatter
        test_record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )
        formatted = formatter.format(test_record)

        # Should match pattern "LEVELNAME: message"
        assert formatted == "WARNING: test message"

    def test_configure_logging_verbose_sets_info_level(self):
        """Test configure_logging with verbosity=1 sets console to INFO."""
        from smart_media_manager.cli import configure_logging, LOG

        LOG.handlers.clear()

        configure_logging(verbosity=1)

        handler = LOG.handlers[0]
        assert handler.level == logging.INFO

    def test_configure_logging_very_verbose_sets_debug_level(self):
        """Test configure_logging with verbosity=2 sets console to DEBUG."""
        from smart_media_manager.cli import configure_logging, LOG

        LOG.handlers.clear()

        configure_logging(verbosity=2)

        handler = LOG.handlers[0]
        assert handler.level == logging.DEBUG

    def test_configure_logging_quiet_sets_error_level(self):
        """Test configure_logging with quiet=True sets console to ERROR."""
        from smart_media_manager.cli import configure_logging, LOG

        LOG.handlers.clear()

        configure_logging(quiet=True)

        handler = LOG.handlers[0]
        assert handler.level == logging.ERROR

    def test_configure_logging_quiet_overrides_verbose(self):
        """Test configure_logging quiet mode overrides verbosity."""
        from smart_media_manager.cli import configure_logging, LOG

        LOG.handlers.clear()

        # Even with verbosity=2, quiet should set ERROR level
        configure_logging(verbosity=2, quiet=True)

        handler = LOG.handlers[0]
        assert handler.level == logging.ERROR
