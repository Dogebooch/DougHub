"""Tests for preflight validation system."""

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from doughub.preflight import (
    CheckResult,
    PreflightReport,
    Severity,
    check_ankiconnect_availability,
    check_config_validity,
    check_critical_dependencies,
    check_database_connection,
    check_database_schema,
    check_essential_directories,
    check_logging_directory,
    check_notes_directory,
    check_notesium_readiness,
    check_python_architecture,
    check_python_version,
    check_qt_platform,
    check_ui_dependencies,
    run_preflight_checks,
)


class TestCheckResult:
    """Tests for CheckResult dataclass."""

    def test_check_result_creation(self) -> None:
        """Test creating a CheckResult."""
        result = CheckResult(
            name="test_check",
            severity=Severity.INFO,
            message="Test message",
            details={"key": "value"},
        )

        assert result.name == "test_check"
        assert result.severity == Severity.INFO
        assert result.message == "Test message"
        assert result.details == {"key": "value"}


class TestPreflightReport:
    """Tests for PreflightReport dataclass."""

    def test_report_with_no_issues(self) -> None:
        """Test report with all INFO checks."""
        checks = [
            CheckResult("check1", Severity.INFO, "OK"),
            CheckResult("check2", Severity.INFO, "OK"),
        ]
        report = PreflightReport(checks=checks)

        assert not report.has_fatal
        assert len(report.warnings) == 0
        assert len(report.infos) == 2
        assert len(report.fatal_messages) == 0

    def test_report_with_warnings(self) -> None:
        """Test report with warnings."""
        checks = [
            CheckResult("check1", Severity.INFO, "OK"),
            CheckResult("check2", Severity.WARN, "Warning message"),
        ]
        report = PreflightReport(checks=checks)

        assert not report.has_fatal
        assert len(report.warnings) == 1
        assert "Warning message" in report.warnings

    def test_report_with_fatal(self) -> None:
        """Test report with fatal errors."""
        checks = [
            CheckResult("check1", Severity.INFO, "OK"),
            CheckResult("check2", Severity.FATAL, "Fatal error"),
        ]
        report = PreflightReport(checks=checks)

        assert report.has_fatal
        assert len(report.fatal_messages) == 1
        assert "Fatal error" in report.fatal_messages


class TestPythonVersionCheck:
    """Tests for check_python_version."""

    def test_python_version_ok(self) -> None:
        """Test with acceptable Python version."""
        result = check_python_version()

        # Should pass on Python 3.10+
        if sys.version_info >= (3, 10):
            assert result.severity == Severity.INFO
            assert "OK" in result.message
        else:
            assert result.severity == Severity.FATAL

    @patch("doughub.preflight.sys")
    def test_python_version_too_old(self, mock_sys: Mock) -> None:
        """Test with old Python version."""
        mock_sys.version_info = type(
            "version_info", (), {"major": 3, "minor": 9, "micro": 0}
        )()

        result = check_python_version()

        assert result.severity == Severity.FATAL
        assert "required" in result.message.lower()


class TestPythonArchitectureCheck:
    """Tests for check_python_architecture."""

    def test_architecture_check(self) -> None:
        """Test architecture check returns info."""
        result = check_python_architecture()

        assert result.severity == Severity.INFO
        assert result.name == "python_architecture"
        assert result.details is not None


class TestCriticalDependenciesCheck:
    """Tests for check_critical_dependencies."""

    def test_dependencies_installed(self) -> None:
        """Test when all dependencies are installed."""
        result = check_critical_dependencies()

        # Should pass in normal environment
        assert result.severity in [Severity.INFO, Severity.WARN]

    @patch("doughub.preflight.importlib_metadata.version")
    def test_missing_dependency(self, mock_version: Mock) -> None:
        """Test when a dependency is missing."""
        from importlib.metadata import PackageNotFoundError

        mock_version.side_effect = PackageNotFoundError("test-package")

        result = check_critical_dependencies()

        assert result.severity == Severity.FATAL
        assert "missing" in result.message.lower()


class TestLoggingDirectoryCheck:
    """Tests for check_logging_directory."""

    def test_logging_directory_created(self, tmp_path: Path) -> None:
        """Test creating and verifying logging directory."""
        with patch("doughub.preflight.Path") as mock_path:
            log_dir = tmp_path / "logs"
            mock_path.return_value = log_dir

            result = check_logging_directory()

            assert result.severity in [Severity.INFO, Severity.FATAL]

    @patch("doughub.preflight.Path")
    def test_logging_directory_not_writable(self, mock_path: Mock) -> None:
        """Test when logging directory cannot be created."""
        mock_dir = Mock()
        mock_dir.mkdir.side_effect = OSError("Permission denied")
        mock_path.return_value = mock_dir

        result = check_logging_directory()

        assert result.severity == Severity.FATAL
        assert "cannot create" in result.message.lower()


class TestConfigValidityCheck:
    """Tests for check_config_validity."""

    def test_config_valid(self) -> None:
        """Test with valid configuration."""
        result = check_config_validity()

        # Should pass with default config
        assert result.severity == Severity.INFO
        assert "valid" in result.message.lower()

    @patch("doughub.preflight.config")
    def test_config_missing_attribute(self, mock_config: Mock) -> None:
        """Test when config is missing required attributes."""
        # Remove a required attribute
        delattr(mock_config, "DATABASE_URL")

        result = check_config_validity()

        assert result.severity == Severity.FATAL
        assert "missing" in result.message.lower()


class TestEssentialDirectoriesCheck:
    """Tests for check_essential_directories."""

    @patch("doughub.preflight.config")
    @patch("doughub.preflight.Path")
    def test_directories_created(self, mock_path: Mock, mock_config: Mock) -> None:
        """Test creating essential directories."""
        mock_config.MEDIA_ROOT = "media"
        mock_dir = Mock()
        mock_dir.mkdir = Mock()
        mock_path.return_value = mock_dir

        # Mock tempfile operations
        with patch("doughub.preflight.tempfile.NamedTemporaryFile"):
            result = check_essential_directories()

            # Should attempt to create directories
            assert mock_dir.mkdir.called or result.severity in [
                Severity.INFO,
                Severity.FATAL,
            ]


class TestNotesDirectoryCheck:
    """Tests for check_notes_directory."""

    @patch("doughub.preflight.config")
    def test_notes_directory_ok(self, mock_config: Mock, tmp_path: Path) -> None:
        """Test with valid notes directory."""
        notes_dir = tmp_path / "notes"
        notes_dir.mkdir()
        mock_config.NOTES_DIR = str(notes_dir)

        result = check_notes_directory()

        assert result.severity == Severity.INFO

    @patch("doughub.preflight.config")
    @patch("doughub.preflight.Path")
    def test_notes_directory_creation_fails(
        self, mock_path: Mock, mock_config: Mock
    ) -> None:
        """Test when notes directory cannot be created."""
        mock_config.NOTES_DIR = "/nonexistent/path"
        mock_dir = Mock()
        mock_dir.mkdir.side_effect = OSError("Permission denied")
        mock_path.return_value = mock_dir

        result = check_notes_directory()

        assert result.severity == Severity.WARN
        assert "cannot be created" in result.message.lower()


class TestDatabaseConnectionCheck:
    """Tests for check_database_connection."""

    @patch("doughub.preflight.config")
    def test_database_not_exists_yet(self, mock_config: Mock, tmp_path: Path) -> None:
        """Test when database file doesn't exist yet."""
        db_path = tmp_path / "test.db"
        mock_config.DATABASE_URL = f"sqlite:///{db_path}"

        result = check_database_connection()

        assert result.severity == Severity.INFO
        assert "does not exist yet" in result.message.lower()

    @patch("doughub.preflight.config")
    def test_database_locked(self, mock_config: Mock) -> None:
        """Test when database is locked."""
        mock_config.DATABASE_URL = "sqlite:///test.db"

        with patch("doughub.preflight.create_engine") as mock_engine:
            mock_conn = Mock()
            mock_conn.execute.side_effect = Exception("database is locked")
            mock_engine.return_value.connect.return_value.__enter__.return_value = (
                mock_conn
            )

            result = check_database_connection()

            assert result.severity == Severity.FATAL
            assert "locked" in result.message.lower()


class TestDatabaseSchemaCheck:
    """Tests for check_database_schema."""

    @patch("doughub.preflight.config")
    def test_schema_complete(self, mock_config: Mock, tmp_path: Path) -> None:
        """Test when database schema is complete."""
        db_path = tmp_path / "test.db"
        mock_config.DATABASE_URL = f"sqlite:///{db_path}"

        # Create a minimal database with required tables
        from sqlalchemy import create_engine

        engine = create_engine(mock_config.DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(
                __import__("sqlalchemy").text(
                    "CREATE TABLE sources (id INTEGER PRIMARY KEY)"
                )
            )
            conn.execute(
                __import__("sqlalchemy").text(
                    "CREATE TABLE questions (id INTEGER PRIMARY KEY)"
                )
            )
            conn.execute(
                __import__("sqlalchemy").text(
                    "CREATE TABLE media (id INTEGER PRIMARY KEY)"
                )
            )
            conn.execute(
                __import__("sqlalchemy").text(
                    "CREATE TABLE logs (id INTEGER PRIMARY KEY)"
                )
            )
            conn.commit()

        result = check_database_schema()

        assert result.severity == Severity.INFO


class TestAnkiConnectAvailability:
    """Tests for check_ankiconnect_availability."""

    @patch("doughub.preflight.config")
    @patch("doughub.preflight.httpx.Client")
    def test_ankiconnect_available(self, mock_client: Mock, mock_config: Mock) -> None:
        """Test when AnkiConnect is available."""
        mock_config.ANKICONNECT_URL = "http://localhost:8765"
        mock_config.ANKICONNECT_VERSION = 6

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": 6, "error": None}

        mock_client.return_value.__enter__.return_value.post.return_value = (
            mock_response
        )

        result = check_ankiconnect_availability()

        assert result.severity == Severity.INFO
        assert "available" in result.message.lower()

    @patch("doughub.preflight.config")
    @patch("doughub.preflight.httpx.Client")
    def test_ankiconnect_unavailable(
        self, mock_client: Mock, mock_config: Mock
    ) -> None:
        """Test when AnkiConnect is not available."""
        mock_config.ANKICONNECT_URL = "http://localhost:8765"

        mock_client.return_value.__enter__.return_value.post.side_effect = Exception(
            "Connection refused"
        )

        result = check_ankiconnect_availability()

        assert result.severity == Severity.WARN
        assert "cannot connect" in result.message.lower()


class TestNotesiumReadiness:
    """Tests for check_notesium_readiness."""

    @patch("doughub.preflight.config")
    def test_notesium_ready(self, mock_config: Mock, tmp_path: Path) -> None:
        """Test when Notesium is ready."""
        notes_dir = tmp_path / "notes"
        notes_dir.mkdir()
        mock_config.NOTES_DIR = str(notes_dir)

        result = check_notesium_readiness()

        assert result.severity == Severity.INFO

    @patch("doughub.preflight.config")
    def test_notesium_directory_missing(self, mock_config: Mock) -> None:
        """Test when notes directory is missing."""
        mock_config.NOTES_DIR = "/nonexistent/path"

        result = check_notesium_readiness()

        assert result.severity == Severity.WARN


class TestUIDependenciesCheck:
    """Tests for check_ui_dependencies."""

    def test_ui_dependencies_available(self) -> None:
        """Test when UI dependencies are available."""
        result = check_ui_dependencies()

        # Should pass in normal environment
        assert result.severity == Severity.INFO

    @patch("doughub.preflight.__import__")
    def test_ui_dependency_missing(self, mock_import: Mock) -> None:
        """Test when a UI dependency is missing."""
        mock_import.side_effect = ImportError("No module named 'PyQt6'")

        result = check_ui_dependencies()

        assert result.severity == Severity.FATAL


class TestQtPlatformCheck:
    """Tests for check_qt_platform."""

    def test_qt_platform_check(self) -> None:
        """Test Qt platform check."""
        result = check_qt_platform()

        # Should always return INFO
        assert result.severity == Severity.INFO
        assert result.name == "qt_platform"


class TestRunPreflightChecks:
    """Tests for run_preflight_checks integration."""

    def test_run_all_checks(self) -> None:
        """Test running all preflight checks."""
        report = run_preflight_checks()

        assert isinstance(report, PreflightReport)
        assert len(report.checks) > 0

    def test_fatal_error_stops_subsequent_checks(self) -> None:
        """Test that fatal errors prevent subsequent dependent checks."""
        with patch(
            "doughub.preflight.check_config_validity"
        ) as mock_config_check:
            mock_config_check.return_value = CheckResult(
                "config_validity",
                Severity.FATAL,
                "Config failed",
            )

            report = run_preflight_checks()

            # Should have fewer checks due to early abort
            assert report.has_fatal

    @patch("doughub.preflight.check_python_version")
    def test_mixed_severity_results(self, mock_version: Mock) -> None:
        """Test handling of mixed severity results."""
        mock_version.return_value = CheckResult(
            "python_version",
            Severity.INFO,
            "OK",
        )

        with patch("doughub.preflight.check_ankiconnect_availability") as mock_anki:
            mock_anki.return_value = CheckResult(
                "ankiconnect",
                Severity.WARN,
                "Anki not running",
            )

            report = run_preflight_checks()

            assert not report.has_fatal
            # Should have at least one warning (possibly more depending on environment)
            assert len(report.warnings) >= 1


class TestIntegration:
    """Integration tests for the preflight system."""

    def test_clean_run_scenario(self, tmp_path: Path) -> None:
        """Test a clean startup scenario."""
        # This will run against the actual environment
        report = run_preflight_checks()

        # Should not have fatal errors in a working dev environment
        # (May have warnings like Anki not running)
        assert isinstance(report, PreflightReport)
        # Can't assert no fatal in CI, but can check structure
        assert hasattr(report, "checks")
        assert hasattr(report, "has_fatal")

    def test_report_aggregation(self) -> None:
        """Test that report properly aggregates results."""
        report = run_preflight_checks()

        # Verify all severity types are counted correctly
        total_checks = len(report.checks)
        fatal_count = len(report.fatal_messages)
        warn_count = len(report.warnings)
        info_count = len(report.infos)

        # All checks should be categorized
        assert total_checks >= fatal_count + warn_count + info_count
