"""Preflight validation system for DougHub application startup.

This module implements a multi-stage preflight validation system that checks
the runtime environment, configuration, data integrity, and external service
health before the application launches. It follows a fail-fast approach,
aborting startup on critical errors and providing clear diagnostics.
"""

import logging
import platform
import sys
import tempfile
from dataclasses import dataclass
from enum import Enum
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class Severity(Enum):
    """Severity levels for preflight check results."""

    INFO = "INFO"
    WARN = "WARN"
    FATAL = "FATAL"


@dataclass
class CheckResult:
    """Result of a single preflight check.

    Attributes:
        name: Name of the check that was performed.
        severity: Severity level of the result.
        message: Human-readable message describing the result.
        details: Optional additional details about the check.
    """

    name: str
    severity: Severity
    message: str
    details: dict[str, Any] | None = None


@dataclass
class PreflightReport:
    """Aggregated results from all preflight checks.

    Attributes:
        checks: List of all check results.
        has_fatal: Whether any check resulted in FATAL severity.
        warnings: List of warning messages.
        infos: List of info messages.
    """

    checks: list[CheckResult]

    @property
    def has_fatal(self) -> bool:
        """Check if any result has FATAL severity."""
        return any(check.severity == Severity.FATAL for check in self.checks)

    @property
    def warnings(self) -> list[str]:
        """Get all warning messages."""
        return [
            check.message for check in self.checks if check.severity == Severity.WARN
        ]

    @property
    def infos(self) -> list[str]:
        """Get all info messages."""
        return [
            check.message for check in self.checks if check.severity == Severity.INFO
        ]

    @property
    def fatal_messages(self) -> list[str]:
        """Get all fatal error messages."""
        return [
            check.message for check in self.checks if check.severity == Severity.FATAL
        ]


def check_python_version() -> CheckResult:
    """Verify Python version meets minimum requirements.

    Returns:
        CheckResult indicating success or failure.
    """
    required_major = 3
    required_minor = 10
    current = sys.version_info

    if current.major < required_major or (
        current.major == required_major and current.minor < required_minor
    ):
        return CheckResult(
            name="python_version",
            severity=Severity.FATAL,
            message=f"Python {required_major}.{required_minor}+ required, but {current.major}.{current.minor}.{current.micro} found.",
            details={
                "required": f"{required_major}.{required_minor}",
                "current": f"{current.major}.{current.minor}.{current.micro}",
            },
        )

    return CheckResult(
        name="python_version",
        severity=Severity.INFO,
        message=f"Python version {current.major}.{current.minor}.{current.micro} OK.",
        details={
            "version": f"{current.major}.{current.minor}.{current.micro}",
            "architecture": platform.machine(),
        },
    )


def check_python_architecture() -> CheckResult:
    """Check Python architecture (mainly for logging/diagnostics).

    Returns:
        CheckResult with architecture information.
    """
    arch = platform.machine()
    bits = platform.architecture()[0]

    return CheckResult(
        name="python_architecture",
        severity=Severity.INFO,
        message=f"Python architecture: {arch} ({bits}).",
        details={"machine": arch, "bits": bits},
    )


def check_critical_dependencies() -> CheckResult:
    """Verify that critical dependencies are installed with correct versions.

    Returns:
        CheckResult indicating dependency health.
    """
    # Map package names to their distribution names (for importlib.metadata)
    critical_deps = {
        "PyQt6": "6.6.0",
        "PyQt6-Fluent-Widgets": "1.0.0",  # Distribution name, not import name
        "httpx": "0.27.0",
        "sqlalchemy": "2.0.0",
        "pyyaml": "6.0.0",
    }

    missing = []
    version_mismatches = []

    for package, min_version in critical_deps.items():
        try:
            installed_version = importlib_metadata.version(package)
            # Simple version comparison (assumes semantic versioning)
            if _version_less_than(installed_version, min_version):
                version_mismatches.append(
                    f"{package} {installed_version} (requires >={min_version})"
                )
        except importlib_metadata.PackageNotFoundError:
            missing.append(package)

    if missing:
        return CheckResult(
            name="critical_dependencies",
            severity=Severity.FATAL,
            message=f"Missing critical dependencies: {', '.join(missing)}.",
            details={"missing": missing, "mismatches": version_mismatches},
        )

    if version_mismatches:
        return CheckResult(
            name="critical_dependencies",
            severity=Severity.WARN,
            message=f"Dependency version mismatches: {', '.join(version_mismatches)}.",
            details={"mismatches": version_mismatches},
        )

    return CheckResult(
        name="critical_dependencies",
        severity=Severity.INFO,
        message="All critical dependencies installed and up-to-date.",
        details={"checked": list(critical_deps.keys())},
    )


def _version_less_than(version: str, min_version: str) -> bool:
    """Simple version comparison helper.

    Args:
        version: Installed version string.
        min_version: Minimum required version string.

    Returns:
        True if version is less than min_version.
    """
    try:
        v_parts = [int(p) for p in version.split(".")[:3]]
        min_parts = [int(p) for p in min_version.split(".")[:3]]

        # Pad with zeros if needed
        while len(v_parts) < 3:
            v_parts.append(0)
        while len(min_parts) < 3:
            min_parts.append(0)

        return tuple(v_parts) < tuple(min_parts)
    except (ValueError, AttributeError):
        # If parsing fails, assume version is OK (conservative)
        return False


def check_logging_directory() -> CheckResult:
    """Verify that the logging directory exists and is writable.

    Returns:
        CheckResult indicating directory health.
    """
    # Default logs directory
    logs_dir = Path("logs")

    # Try to create the directory if it doesn't exist
    try:
        logs_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        return CheckResult(
            name="logging_directory",
            severity=Severity.FATAL,
            message=f"Cannot create logs directory: {e}.",
            details={"path": str(logs_dir.absolute()), "error": str(e)},
        )

    # Test writability by creating and deleting a temp file
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", dir=logs_dir, delete=False
        ) as test_file:
            test_path = Path(test_file.name)
            test_file.write("preflight write test")

        test_path.unlink()
    except OSError as e:
        return CheckResult(
            name="logging_directory",
            severity=Severity.FATAL,
            message=f"Logs directory is not writable: {e}.",
            details={"path": str(logs_dir.absolute()), "error": str(e)},
        )

    return CheckResult(
        name="logging_directory",
        severity=Severity.INFO,
        message=f"Logs directory is writable: {logs_dir.absolute()}.",
        details={"path": str(logs_dir.absolute())},
    )


def check_config_validity() -> CheckResult:
    """Verify that configuration is valid and complete.

    Returns:
        CheckResult indicating configuration health.
    """
    # Import config to check if it loads successfully
    try:
        from doughub import config

        # Check for required configuration attributes
        required_attrs = [
            "ANKICONNECT_URL",
            "DATABASE_URL",
            "MEDIA_ROOT",
            "NOTES_DIR",
            "NOTESIUM_PORT",
        ]

        missing_attrs = []
        for attr in required_attrs:
            if not hasattr(config, attr):
                missing_attrs.append(attr)

        if missing_attrs:
            return CheckResult(
                name="config_validity",
                severity=Severity.FATAL,
                message=f"Configuration missing required attributes: {', '.join(missing_attrs)}.",
                details={"missing": missing_attrs},
            )

        # Validate config values are not empty
        empty_attrs = []
        for attr in required_attrs:
            value = getattr(config, attr)
            if value is None or (isinstance(value, str) and not value.strip()):
                empty_attrs.append(attr)

        if empty_attrs:
            return CheckResult(
                name="config_validity",
                severity=Severity.FATAL,
                message=f"Configuration has empty values: {', '.join(empty_attrs)}.",
                details={"empty": empty_attrs},
            )

        return CheckResult(
            name="config_validity",
            severity=Severity.INFO,
            message="Configuration is valid and complete.",
            details={"checked_attrs": required_attrs},
        )

    except ImportError as e:
        return CheckResult(
            name="config_validity",
            severity=Severity.FATAL,
            message=f"Cannot import configuration: {e}.",
            details={"error": str(e)},
        )
    except Exception as e:
        return CheckResult(
            name="config_validity",
            severity=Severity.FATAL,
            message=f"Configuration loading failed: {e}.",
            details={"error": str(e)},
        )


def check_essential_directories() -> CheckResult:
    """Verify that essential directories exist and are accessible.

    Returns:
        CheckResult indicating directory health.
    """
    from doughub import config

    # Define essential directories
    essential_dirs = {
        "extractions": Path("extractions"),
        "media_root": Path(config.MEDIA_ROOT),
        "logs": Path("logs"),
    }

    missing_dirs = []
    permission_errors = []

    for name, dir_path in essential_dirs.items():
        # Try to create directory if it doesn't exist
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            missing_dirs.append(f"{name} ({dir_path})")
            permission_errors.append(str(e))
            continue

        # Test writability
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", dir=dir_path, delete=False
            ) as test_file:
                test_path = Path(test_file.name)
                test_file.write("preflight write test")
            test_path.unlink()
        except OSError as e:
            permission_errors.append(f"{name} ({dir_path}): {e}")

    if missing_dirs:
        return CheckResult(
            name="essential_directories",
            severity=Severity.FATAL,
            message=f"Cannot create essential directories: {', '.join(missing_dirs)}.",
            details={"missing": missing_dirs, "errors": permission_errors},
        )

    if permission_errors:
        return CheckResult(
            name="essential_directories",
            severity=Severity.FATAL,
            message=f"Directory permission errors: {'; '.join(permission_errors)}.",
            details={"errors": permission_errors},
        )

    return CheckResult(
        name="essential_directories",
        severity=Severity.INFO,
        message=f"All essential directories are accessible: {', '.join(essential_dirs.keys())}.",
        details={"directories": {k: str(v.absolute()) for k, v in essential_dirs.items()}},
    )


def check_notes_directory() -> CheckResult:
    """Verify that the notes directory is valid and accessible.

    Returns:
        CheckResult indicating notes directory health.
    """
    from doughub import config

    notes_dir = Path(config.NOTES_DIR)

    # Notes directory is not critical for startup - it's a degraded mode scenario
    try:
        notes_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        return CheckResult(
            name="notes_directory",
            severity=Severity.WARN,
            message=f"Notes directory cannot be created: {e}. Notebook features will be unavailable.",
            details={"path": str(notes_dir), "error": str(e)},
        )

    # Test writability
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", dir=notes_dir, delete=False
        ) as test_file:
            test_path = Path(test_file.name)
            test_file.write("preflight write test")
        test_path.unlink()
    except OSError as e:
        return CheckResult(
            name="notes_directory",
            severity=Severity.WARN,
            message=f"Notes directory is not writable: {e}. Notebook features may be limited.",
            details={"path": str(notes_dir), "error": str(e)},
        )

    return CheckResult(
        name="notes_directory",
        severity=Severity.INFO,
        message=f"Notes directory is ready: {notes_dir.absolute()}.",
        details={"path": str(notes_dir.absolute())},
    )


def check_database_connection() -> CheckResult:
    """Verify that the database is accessible and healthy.

    Returns:
        CheckResult indicating database health.
    """
    from doughub import config

    try:
        from sqlalchemy import create_engine, text

        # Extract the database file path from DATABASE_URL
        db_url = config.DATABASE_URL
        if not db_url.startswith("sqlite:///"):
            return CheckResult(
                name="database_connection",
                severity=Severity.WARN,
                message=f"Non-SQLite database detected: {db_url}. Integrity checks skipped.",
                details={"db_url": db_url},
            )

        db_path = db_url.replace("sqlite:///", "")

        # Check if database file exists (it's OK if it doesn't - will be created)
        db_file = Path(db_path)
        if not db_file.exists():
            return CheckResult(
                name="database_connection",
                severity=Severity.INFO,
                message=f"Database file does not exist yet: {db_path}. It will be created on first run.",
                details={"db_path": db_path, "exists": False},
            )

        # Try to connect and run a simple query
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # Test basic connectivity
            conn.execute(text("SELECT 1"))

            # Run SQLite integrity check
            result = conn.execute(text("PRAGMA integrity_check"))
            integrity_result = result.scalar()

            if integrity_result != "ok":
                return CheckResult(
                    name="database_connection",
                    severity=Severity.FATAL,
                    message=f"Database integrity check failed: {integrity_result}.",
                    details={"db_path": db_path, "integrity": integrity_result},
                )

        engine.dispose()

        return CheckResult(
            name="database_connection",
            severity=Severity.INFO,
            message=f"Database is healthy: {db_path}.",
            details={"db_path": db_path, "integrity": "ok"},
        )

    except Exception as e:
        error_msg = str(e).lower()
        # Check for common error patterns
        if "locked" in error_msg or "busy" in error_msg:
            return CheckResult(
                name="database_connection",
                severity=Severity.FATAL,
                message="Database is locked by another process. Close other instances and try again.",
                details={"error": str(e)},
            )
        elif "malformed" in error_msg or "corrupt" in error_msg:
            return CheckResult(
                name="database_connection",
                severity=Severity.FATAL,
                message=f"Database file is corrupted: {e}. Restore from backup or delete to recreate.",
                details={"error": str(e)},
            )
        else:
            return CheckResult(
                name="database_connection",
                severity=Severity.FATAL,
                message=f"Cannot connect to database: {e}.",
                details={"error": str(e)},
            )


def check_database_schema() -> CheckResult:
    """Verify that the database schema is up-to-date.

    Returns:
        CheckResult indicating schema health.
    """
    from doughub import config

    try:
        from sqlalchemy import create_engine, inspect

        db_url = config.DATABASE_URL
        if not db_url.startswith("sqlite:///"):
            return CheckResult(
                name="database_schema",
                severity=Severity.INFO,
                message="Schema check skipped for non-SQLite database.",
            )

        db_path = db_url.replace("sqlite:///", "")
        db_file = Path(db_path)

        # If database doesn't exist, it will be created - that's OK
        if not db_file.exists():
            return CheckResult(
                name="database_schema",
                severity=Severity.INFO,
                message="Database will be initialized on first run.",
            )

        # Check if required tables exist
        engine = create_engine(db_url)
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        required_tables = {"sources", "questions", "media", "logs"}

        missing_tables = required_tables - existing_tables

        if missing_tables:
            # Check if alembic_version table exists (indicates migrations are used)
            has_alembic = "alembic_version" in existing_tables

            if has_alembic:
                return CheckResult(
                    name="database_schema",
                    severity=Severity.WARN,
                    message=f"Database schema incomplete. Missing tables: {', '.join(missing_tables)}. "
                    f"Run 'alembic upgrade head' to apply migrations.",
                    details={
                        "missing_tables": list(missing_tables),
                        "has_alembic": True,
                    },
                )
            else:
                return CheckResult(
                    name="database_schema",
                    severity=Severity.WARN,
                    message=f"Database schema incomplete. Missing tables: {', '.join(missing_tables)}. "
                    f"Schema will be created on first run.",
                    details={
                        "missing_tables": list(missing_tables),
                        "has_alembic": False,
                    },
                )

        engine.dispose()

        return CheckResult(
            name="database_schema",
            severity=Severity.INFO,
            message="Database schema is complete.",
            details={"tables": list(existing_tables)},
        )

    except Exception as e:
        return CheckResult(
            name="database_schema",
            severity=Severity.WARN,
            message=f"Cannot verify database schema: {e}. Proceeding with caution.",
            details={"error": str(e)},
        )


def check_ankiconnect_availability() -> CheckResult:
    """Check if AnkiConnect is available and responding.

    This is a non-fatal check - the app can run in degraded mode without Anki.

    Returns:
        CheckResult indicating AnkiConnect availability.
    """
    from doughub import config

    try:
        import httpx

        # Short timeout to avoid long startup delays
        timeout = 2.0
        url = config.ANKICONNECT_URL

        # Try to ping AnkiConnect with version action
        with httpx.Client(timeout=timeout) as client:
            response = client.post(
                url,
                json={"action": "version", "version": config.ANKICONNECT_VERSION},
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("error") is None:
                    version = data.get("result")
                    return CheckResult(
                        name="ankiconnect_availability",
                        severity=Severity.INFO,
                        message=f"AnkiConnect is available (version {version}).",
                        details={"url": url, "version": version},
                    )
                else:
                    return CheckResult(
                        name="ankiconnect_availability",
                        severity=Severity.WARN,
                        message=f"AnkiConnect responded with error: {data.get('error')}. Card features will be unavailable.",
                        details={"url": url, "error": data.get("error")},
                    )
            else:
                return CheckResult(
                    name="ankiconnect_availability",
                    severity=Severity.WARN,
                    message=f"AnkiConnect returned HTTP {response.status_code}. Card features will be unavailable.",
                    details={"url": url, "status_code": response.status_code},
                )

    except Exception as e:
        # Network errors are expected if Anki isn't running
        return CheckResult(
            name="ankiconnect_availability",
            severity=Severity.WARN,
            message=f"Cannot connect to AnkiConnect at {config.ANKICONNECT_URL}. Anki card features will be unavailable. Start Anki to enable these features.",
            details={"url": config.ANKICONNECT_URL, "error": str(e)},
        )


def check_notesium_readiness() -> CheckResult:
    """Check if Notesium can be started (notes directory is ready).

    This is informational - Notesium failures are handled gracefully at runtime.

    Returns:
        CheckResult indicating Notesium readiness.
    """
    from doughub import config

    notes_dir = Path(config.NOTES_DIR)

    # Check if notes directory exists and is accessible
    if not notes_dir.exists():
        return CheckResult(
            name="notesium_readiness",
            severity=Severity.WARN,
            message=f"Notes directory does not exist: {notes_dir}. Notesium features may be limited.",
            details={"notes_dir": str(notes_dir), "exists": False},
        )

    # Check if it's a directory
    if not notes_dir.is_dir():
        return CheckResult(
            name="notesium_readiness",
            severity=Severity.WARN,
            message=f"Notes path is not a directory: {notes_dir}. Notesium features will be unavailable.",
            details={"notes_dir": str(notes_dir), "is_dir": False},
        )

    # Check readability
    try:
        list(notes_dir.iterdir())
    except OSError as e:
        return CheckResult(
            name="notesium_readiness",
            severity=Severity.WARN,
            message=f"Notes directory is not readable: {e}. Notesium features will be limited.",
            details={"notes_dir": str(notes_dir), "error": str(e)},
        )

    return CheckResult(
        name="notesium_readiness",
        severity=Severity.INFO,
        message=f"Notes directory is ready for Notesium: {notes_dir.absolute()}.",
        details={"notes_dir": str(notes_dir.absolute())},
    )


def check_ui_dependencies() -> CheckResult:
    """Verify that UI dependencies can be imported.

    This catches packaging or installation issues before attempting to create the UI.

    Returns:
        CheckResult indicating UI readiness.
    """
    ui_imports = [
        ("PyQt6.QtWidgets", "QApplication"),
        ("PyQt6.QtCore", "Qt"),
        ("qfluentwidgets", "Theme"),
    ]

    failed_imports = []

    for module_name, attr_name in ui_imports:
        try:
            module = __import__(module_name, fromlist=[attr_name])
            if not hasattr(module, attr_name):
                failed_imports.append(f"{module_name}.{attr_name} (missing attribute)")
        except ImportError as e:
            failed_imports.append(f"{module_name} ({e})")

    if failed_imports:
        return CheckResult(
            name="ui_dependencies",
            severity=Severity.FATAL,
            message=f"Cannot import UI dependencies: {'; '.join(failed_imports)}.",
            details={"failed": failed_imports},
        )

    return CheckResult(
        name="ui_dependencies",
        severity=Severity.INFO,
        message="All UI dependencies can be imported successfully.",
        details={"checked": [f"{m}.{a}" for m, a in ui_imports]},
    )


def check_qt_platform() -> CheckResult:
    """Check Qt platform plugin availability.

    Returns:
        CheckResult indicating Qt platform health.
    """
    try:
        # Try to get QT_QPA_PLATFORM_PLUGIN_PATH
        import os

        qpa_path = os.environ.get("QT_QPA_PLATFORM_PLUGIN_PATH")

        # This is informational - Qt will handle platform selection
        return CheckResult(
            name="qt_platform",
            severity=Severity.INFO,
            message=f"Qt platform: {sys.platform}, plugin path: {qpa_path or 'default'}.",
            details={"platform": sys.platform, "plugin_path": qpa_path},
        )

    except Exception as e:
        return CheckResult(
            name="qt_platform",
            severity=Severity.INFO,
            message=f"Qt platform check informational only: {e}.",
            details={"error": str(e)},
        )


def run_preflight_checks() -> PreflightReport:
    """Run all preflight checks and aggregate results.

    Returns:
        PreflightReport containing all check results.
    """
    logger.info("Starting preflight checks...")

    checks: list[CheckResult] = []

    # Stage 1: Core environment checks (cheap, fundamental)
    checks.append(check_python_version())
    checks.append(check_python_architecture())
    checks.append(check_critical_dependencies())
    checks.append(check_logging_directory())

    # Stage 2: Configuration and filesystem checks
    checks.append(check_config_validity())
    # Only proceed with directory checks if config is valid
    if checks[-1].severity != Severity.FATAL:
        checks.append(check_essential_directories())
        checks.append(check_notes_directory())

        # Stage 3: Database checks
        checks.append(check_database_connection())
        if checks[-1].severity != Severity.FATAL:
            checks.append(check_database_schema())

        # Stage 4: External integration checks (non-fatal, allow degraded mode)
        checks.append(check_ankiconnect_availability())
        checks.append(check_notesium_readiness())

        # Stage 5: UI readiness checks
        checks.append(check_ui_dependencies())
        checks.append(check_qt_platform())

    report = PreflightReport(checks=checks)

    logger.info(f"Preflight checks complete: {len(checks)} checks performed.")
    if report.has_fatal:
        logger.error(
            f"Preflight failed with {len(report.fatal_messages)} fatal error(s)."
        )
    elif report.warnings:
        logger.warning(f"Preflight passed with {len(report.warnings)} warning(s).")
    else:
        logger.info("All preflight checks passed.")

    return report
