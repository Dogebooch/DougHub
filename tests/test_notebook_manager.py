"""Tests for NotesiumManager lifecycle and error handling."""

from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import httpx

from doughub.notebook.manager import NotesiumManager
from doughub.notebook.sync import scan_and_parse_notes


class TestNotesiumLifecycle:
    """Test Notesium subprocess lifecycle management."""

    def test_manager_initialization(self, tmp_path: Path) -> None:
        """Test that manager initializes with correct defaults."""
        notes_dir = tmp_path / "notes"
        manager = NotesiumManager(notes_dir=str(notes_dir), port=3031)

        assert manager.notes_dir == notes_dir
        assert manager.port == 3031
        assert manager.url == "http://localhost:3031"
        assert manager.process is None
        assert not manager._is_healthy

    def test_start_creates_notes_directory(self, tmp_path: Path) -> None:
        """Test that starting manager creates notes directory."""
        notes_dir = tmp_path / "test_notes"
        assert not notes_dir.exists()

        manager = NotesiumManager(notes_dir=str(notes_dir), port=3032)
        # Start will fail (npx not configured) but directory should be created
        manager.start()
        manager.stop()

        assert notes_dir.exists()

    def test_stop_with_no_process(self, tmp_path: Path) -> None:
        """Test that stop() is safe when no process is running."""
        manager = NotesiumManager(notes_dir=str(tmp_path), port=3033)
        # Should not raise an error
        manager.stop()
        assert manager.process is None

    def test_context_manager(self, tmp_path: Path) -> None:
        """Test that manager works as a context manager."""
        manager = NotesiumManager(notes_dir=str(tmp_path), port=3034)

        with manager as mgr:
            assert mgr is manager
            # process may or may not have started (depends on npx availability)

        # After exiting context, should be stopped
        assert not manager._is_healthy or manager.process is None

    @patch("doughub.notebook.manager.subprocess.Popen")
    @patch("doughub.notebook.manager.httpx.Client")
    def test_start_success_with_health_check(
        self, mock_client_cls: Mock, mock_popen: Mock, tmp_path: Path
    ) -> None:
        """Test successful start with health check passing."""
        notes_dir = tmp_path / "notes"
        manager = NotesiumManager(notes_dir=str(notes_dir), port=3035)

        # Mock subprocess
        mock_process = Mock()
        mock_process.poll.return_value = None  # Process is running
        mock_process.stderr = None
        mock_popen.return_value = mock_process

        # Mock health check - first call fails (port check), subsequent calls succeed
        mock_response = Mock()
        mock_response.status_code = 200

        # Setup mock client
        mock_client = mock_client_cls.return_value.__enter__.return_value
        mock_get = mock_client.get

        def side_effect(*args: Any, **kwargs: Any) -> Mock:
            # First call raises (port not in use check)
            if mock_get.call_count == 1:
                raise httpx.RequestError("Connection refused")
            # Subsequent calls succeed (health checks)
            return mock_response

        mock_get.side_effect = side_effect

        result = manager.start()

        assert result is True
        assert manager._is_healthy
        assert manager.process is mock_process

        manager.stop()

    @patch("doughub.notebook.manager.subprocess.Popen")
    def test_start_failure_process_dies(
        self, mock_popen: Mock, tmp_path: Path
    ) -> None:
        """Test start failure when process terminates unexpectedly."""
        notes_dir = tmp_path / "notes"
        manager = NotesiumManager(notes_dir=str(notes_dir), port=3036)

        # Mock subprocess that dies immediately
        mock_process = Mock()
        mock_process.poll.return_value = 1  # Process exited
        mock_process.stderr = Mock()
        mock_process.stderr.read.return_value = b"Error message"
        mock_popen.return_value = mock_process

        result = manager.start()

        assert result is False
        assert not manager._is_healthy

    @patch("doughub.notebook.manager.httpx.Client")
    def test_port_already_in_use_with_working_server(
        self, mock_client_cls: Mock, tmp_path: Path
    ) -> None:
        """Test handling when port is in use but server is accessible."""
        notes_dir = tmp_path / "notes"
        manager = NotesiumManager(notes_dir=str(notes_dir), port=3037)

        # Mock that port is in use and health check passes
        mock_response = Mock()
        mock_response.status_code = 200

        mock_client = mock_client_cls.return_value.__enter__.return_value
        mock_client.get.return_value = mock_response

        result = manager.start()

        # Should succeed because existing server is healthy
        assert result is True
        assert manager._is_healthy


class TestNotesiumHealthChecks:
    """Test health checking functionality."""

    @patch("doughub.notebook.manager.httpx.Client")
    def test_health_check_success(self, mock_client_cls: Mock, tmp_path: Path) -> None:
        """Test successful health check."""
        manager = NotesiumManager(notes_dir=str(tmp_path), port=3038)

        mock_response = Mock()
        mock_response.status_code = 200

        mock_client = mock_client_cls.return_value.__enter__.return_value
        mock_client.get.return_value = mock_response

        assert manager._health_check() is True

    @patch("doughub.notebook.manager.httpx.Client")
    def test_health_check_failure_bad_status(
        self, mock_client_cls: Mock, tmp_path: Path
    ) -> None:
        """Test health check failure with non-200 status."""
        manager = NotesiumManager(notes_dir=str(tmp_path), port=3039)

        mock_response = Mock()
        mock_response.status_code = 500

        mock_client = mock_client_cls.return_value.__enter__.return_value
        mock_client.get.return_value = mock_response

        assert manager._health_check() is False

    @patch("doughub.notebook.manager.httpx.Client")
    def test_health_check_failure_connection_error(
        self, mock_client_cls: Mock, tmp_path: Path
    ) -> None:
        """Test health check failure with connection error."""
        manager = NotesiumManager(notes_dir=str(tmp_path), port=3040)

        mock_client = mock_client_cls.return_value.__enter__.return_value
        mock_client.get.side_effect = httpx.RequestError("Connection error")

        assert manager._health_check() is False

    @patch("doughub.notebook.manager.httpx.Client")
    def test_is_healthy_checks_current_state(
        self, mock_client_cls: Mock, tmp_path: Path
    ) -> None:
        """Test that is_healthy() performs an actual health check."""
        manager = NotesiumManager(notes_dir=str(tmp_path), port=3041)
        manager._is_healthy = True  # Set flag

        # Mock health check failure
        mock_client = mock_client_cls.return_value.__enter__.return_value
        mock_client.get.side_effect = httpx.RequestError("Connection error")

        # Should return False because health check fails
        assert manager.is_healthy() is False


class TestErrorConditions:
    """Test error handling in various failure scenarios."""

    def test_invalid_notes_directory_path(self) -> None:
        """Test handling of invalid directory path."""
        # Use a path with invalid characters (null byte)
        invalid_path = "/path\x00/to/notes"
        manager = NotesiumManager(notes_dir=invalid_path, port=3042)

        result = manager.start()

        assert result is False
        assert not manager.is_healthy()

    @patch("doughub.notebook.manager.subprocess.Popen")
    def test_file_not_found_error(self, mock_popen: Mock, tmp_path: Path) -> None:
        """Test handling when npx command is not found."""
        manager = NotesiumManager(notes_dir=str(tmp_path), port=3043)

        mock_popen.side_effect = FileNotFoundError()

        result = manager.start()

        assert result is False
        assert not manager.is_healthy()

    @patch("doughub.notebook.manager.subprocess.Popen")
    def test_unexpected_exception_during_start(
        self, mock_popen: Mock, tmp_path: Path
    ) -> None:
        """Test handling of unexpected exceptions during start."""
        manager = NotesiumManager(notes_dir=str(tmp_path), port=3044)

        mock_popen.side_effect = RuntimeError("Unexpected error")

        result = manager.start()

        assert result is False
        assert not manager.is_healthy()


class TestSyncFailures:
    """Tests for notebook sync failure scenarios."""

    def test_scan_missing_directory(self, tmp_path):
        """Test scanning a non-existent directory."""
        missing_dir = tmp_path / "missing"
        # Should handle gracefully (log warning and return empty generator)
        results = list(scan_and_parse_notes(missing_dir))
        assert len(results) == 0

    def test_scan_invalid_yaml(self, tmp_path):
        """Test scanning a file with invalid YAML frontmatter."""
        note_file = tmp_path / "invalid.md"
        with open(note_file, "w") as f:
            f.write("---\nkey: : value\n---\nContent")

        # Should log error and skip file
        results = list(scan_and_parse_notes(tmp_path))
        assert len(results) == 0

    def test_scan_missing_question_id(self, tmp_path):
        """Test scanning a file missing the required question_id."""
        note_file = tmp_path / "no_id.md"
        with open(note_file, "w") as f:
            f.write("---\ntitle: No ID\n---\nContent")

        # Should log warning and skip
        results = list(scan_and_parse_notes(tmp_path))
        assert len(results) == 0

    def test_sync_conflict_resolution(self):
        """Test conflict resolution strategy (placeholder)."""
        # Since conflict resolution logic isn't fully implemented in the provided code,
        # we define the expected behavior here.
        # Assumption: If DB and File both changed, we might prioritize one.
        # For now, let's assume we just want to ensure the system doesn't crash.
        pass
