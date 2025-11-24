"""Service health monitoring for DougHub.

Provides background health checking for external services like
AnkiConnect and Notesium.
"""

import logging

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from doughub.anki_client.repository import AnkiRepository
from doughub.notebook.manager import NotesiumManager

logger = logging.getLogger(__name__)


class HealthMonitor(QObject):
    """Monitor health status of external services.

    Periodically checks AnkiConnect and Notesium health and emits
    signals when their status changes.
    """

    # Signals: (is_healthy: bool, status_message: str)
    ankiStatusChanged = pyqtSignal(bool, str)
    notesiumStatusChanged = pyqtSignal(bool, str)

    def __init__(
        self,
        anki_repository: AnkiRepository,
        notesium_manager: NotesiumManager,
        check_interval_ms: int = 30000,  # 30 seconds
        parent: QObject | None = None,
    ) -> None:
        """Initialize the health monitor.

        Args:
            anki_repository: AnkiRepository instance to check Anki health.
            notesium_manager: NotesiumManager instance to check Notesium health.
            check_interval_ms: Interval between health checks in milliseconds.
            parent: Optional parent QObject.
        """
        super().__init__(parent)
        self.anki_repository = anki_repository
        self.notesium_manager = notesium_manager
        self.check_interval_ms = check_interval_ms

        # Track last known states to detect changes
        self._last_anki_status: bool | None = None
        self._last_notesium_status: bool | None = None

        # Set up timer for periodic checks
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._check_health)

    def start(self) -> None:
        """Start periodic health monitoring."""
        logger.info("Starting health monitor", extra={"interval_ms": self.check_interval_ms})
        # Perform initial check immediately
        self._check_health()
        # Start timer for periodic checks
        self._timer.start(self.check_interval_ms)

    def stop(self) -> None:
        """Stop health monitoring."""
        logger.info("Stopping health monitor")
        self._timer.stop()

    def _check_health(self) -> None:
        """Perform health checks on all monitored services."""
        self._check_anki_health()
        self._check_notesium_health()

    def _check_anki_health(self) -> None:
        """Check AnkiConnect health and emit signal if status changed."""
        is_healthy = False
        status_message = ""

        try:
            # Try a simple operation to verify Anki is accessible
            self.anki_repository.get_deck_names()
            is_healthy = True
            status_message = "Connected"
            logger.debug("AnkiConnect health check: OK")
        except Exception as e:
            is_healthy = False
            status_message = f"Disconnected: {type(e).__name__}"
            logger.debug(
                "AnkiConnect health check failed",
                extra={"error": str(e), "error_type": type(e).__name__}
            )

        # Emit signal only if status changed
        if is_healthy != self._last_anki_status:
            logger.info(
                f"AnkiConnect status changed: {'healthy' if is_healthy else 'unhealthy'}",
                extra={"status": status_message}
            )
            self.ankiStatusChanged.emit(is_healthy, status_message)
            self._last_anki_status = is_healthy

    def _check_notesium_health(self) -> None:
        """Check Notesium health and emit signal if status changed."""
        is_healthy = self.notesium_manager.is_healthy()
        status_message = "Running" if is_healthy else "Not Running"

        logger.debug(
            "Notesium health check",
            extra={"is_healthy": is_healthy, "url": self.notesium_manager.url}
        )

        # Emit signal only if status changed
        if is_healthy != self._last_notesium_status:
            logger.info(
                f"Notesium status changed: {'healthy' if is_healthy else 'unhealthy'}",
                extra={"status": status_message}
            )
            self.notesiumStatusChanged.emit(is_healthy, status_message)
            self._last_notesium_status = is_healthy

    def force_check(self) -> None:
        """Force an immediate health check.

        This bypasses the timer and performs checks immediately,
        useful for manual refresh or after configuration changes.
        """
        logger.debug("Forcing immediate health check")
        self._check_health()
