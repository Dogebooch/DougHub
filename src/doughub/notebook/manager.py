"""Manager for Notesium subprocess lifecycle."""

import logging
import subprocess
import time
from pathlib import Path
from typing import Any

import requests

from doughub import config

logger = logging.getLogger(__name__)


class NotesiumManager:
    """Manages the Notesium server subprocess.

    Handles starting, stopping, and health-checking the Notesium server.
    Ensures the notes directory exists and the server is accessible.
    """

    def __init__(self, notes_dir: str | None = None, port: int | None = None) -> None:
        """Initialize the Notesium manager.

        Args:
            notes_dir: Path to the notes directory. Defaults to config.NOTES_DIR.
            port: Port to run Notesium on. Defaults to config.NOTESIUM_PORT.
        """
        self.notes_dir = Path(notes_dir or config.NOTES_DIR)
        self.port = port or config.NOTESIUM_PORT
        self.process: subprocess.Popen[bytes] | None = None
        self.url = f"http://localhost:{self.port}"
        self._is_healthy = False

    def start(self) -> bool:
        """Start the Notesium server.

        Creates the notes directory if it doesn't exist, launches the
        Notesium process, and verifies it's healthy.

        Returns:
            True if the server started successfully, False otherwise.
        """
        # Ensure notes directory exists
        try:
            self.notes_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Notes directory ready: {self.notes_dir}")
        except Exception as e:
            logger.error(f"Failed to create notes directory {self.notes_dir}: {e}")
            return False

        # Check if port is already in use
        if self._check_port_in_use():
            logger.warning(f"Port {self.port} already in use")
            # Try to connect anyway - maybe Notesium is already running
            if self._health_check():
                logger.info("Notesium appears to be already running")
                self._is_healthy = True
                return True
            logger.error("Port in use but health check failed")
            return False

        # Start Notesium process
        try:
            # Using npx to run notesium without global installation
            cmd = [
                "npx",
                "-y",
                "notesium",
                "--port",
                str(self.port),
                "--root",
                str(self.notes_dir),
            ]
            logger.info(f"Starting Notesium: {' '.join(cmd)}")

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
            )

            # Wait for server to start and check health
            max_attempts = 10
            for _attempt in range(max_attempts):
                time.sleep(0.5)
                if self._health_check():
                    logger.info(f"Notesium started successfully on port {self.port}")
                    self._is_healthy = True
                    return True

                # Check if process died
                if self.process.poll() is not None:
                    stderr = self.process.stderr.read().decode() if self.process.stderr else ""
                    logger.error(f"Notesium process terminated unexpectedly: {stderr}")
                    return False

            logger.error(f"Notesium failed health check after {max_attempts} attempts")
            self.stop()
            return False

        except FileNotFoundError:
            logger.error("npx not found. Please ensure Node.js and npm are installed.")
            return False
        except Exception as e:
            logger.exception(f"Failed to start Notesium: {e}")
            self.stop()
            return False

    def stop(self) -> None:
        """Stop the Notesium server if it's running."""
        if self.process:
            try:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning("Notesium didn't terminate, forcing kill")
                    self.process.kill()
                    self.process.wait()
                logger.info("Notesium stopped")
            except Exception as e:
                logger.error(f"Error stopping Notesium: {e}")
            finally:
                self.process = None
                self._is_healthy = False

    def is_healthy(self) -> bool:
        """Check if the Notesium server is currently healthy.

        Returns:
            True if the server is accessible, False otherwise.
        """
        return self._is_healthy and self._health_check()

    def _health_check(self) -> bool:
        """Perform a health check by attempting to connect to the server.

        Returns:
            True if the server responds, False otherwise.
        """
        try:
            response = requests.get(self.url, timeout=2)
            return bool(response.status_code == 200)
        except requests.RequestException:
            return False

    def _check_port_in_use(self) -> bool:
        """Check if the configured port is already in use.

        Returns:
            True if the port is in use, False otherwise.
        """
        try:
            requests.get(self.url, timeout=1)
            return True
        except requests.RequestException:
            return False

    def __enter__(self) -> "NotesiumManager":
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.stop()
