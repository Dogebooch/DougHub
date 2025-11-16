"""Utilities for managing Anki process during testing."""

import logging
import subprocess
import time
from typing import Any

import httpx

from doughub.config import (
    ANKI_EXECUTABLE,
    ANKI_TEST_PROFILE,
    ANKICONNECT_URL,
    ENABLE_ANKI_AUTO_LAUNCH,
)

logger = logging.getLogger(__name__)


class AnkiProcessManager:
    """Manager for launching and monitoring Anki process during tests."""

    def __init__(
        self,
        executable: str = ANKI_EXECUTABLE,
        profile: str = ANKI_TEST_PROFILE,
        url: str = ANKICONNECT_URL,
    ) -> None:
        """Initialize the Anki process manager.

        Args:
            executable: Path or name of the Anki executable.
            profile: Name of the Anki profile to use for testing.
            url: URL where AnkiConnect should be accessible.
        """
        self.executable = executable
        self.profile = profile
        self.url = url
        self.process: subprocess.Popen | None = None

    def is_ankiconnect_running(self) -> bool:
        """Check if AnkiConnect is accessible.

        Returns:
            True if AnkiConnect responds to requests, False otherwise.
        """
        try:
            with httpx.Client(timeout=2.0) as client:
                response = client.post(
                    self.url, json={"action": "version", "version": 6}
                )
                data = response.json()
                return data.get("error") is None
        except Exception:
            return False

    def launch_anki(self, timeout: float = 10.0) -> bool:
        """Launch Anki with the test profile.

        Args:
            timeout: Maximum seconds to wait for AnkiConnect to become available.

        Returns:
            True if Anki was launched and AnkiConnect is accessible, False otherwise.
        """
        if self.is_ankiconnect_running():
            logger.info("AnkiConnect is already running")
            return True

        if not ENABLE_ANKI_AUTO_LAUNCH:
            logger.warning("Anki auto-launch is disabled")
            return False

        try:
            logger.info(
                f"Launching Anki with profile '{self.profile}' using executable '{self.executable}'"
            )
            # Launch Anki with the specified profile
            # -p selects the profile, -b specifies base directory (optional)
            self.process = subprocess.Popen(
                [self.executable, "-p", self.profile],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # Wait for AnkiConnect to become available
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.is_ankiconnect_running():
                    logger.info("Anki launched successfully and AnkiConnect is running")
                    return True
                time.sleep(0.5)

            logger.error(
                f"AnkiConnect did not become available within {timeout} seconds"
            )
            return False

        except FileNotFoundError:
            logger.error(
                f"Anki executable '{self.executable}' not found. "
                "Please ensure Anki is installed and the path is correct."
            )
            return False
        except Exception as e:
            logger.error(f"Failed to launch Anki: {e}")
            return False

    def stop_anki(self) -> None:
        """Stop the Anki process if it was launched by this manager."""
        if self.process is not None:
            try:
                logger.info("Stopping Anki process")
                self.process.terminate()
                self.process.wait(timeout=5.0)
                logger.info("Anki process stopped")
            except subprocess.TimeoutExpired:
                logger.warning("Anki did not terminate gracefully, forcing kill")
                self.process.kill()
            except Exception as e:
                logger.error(f"Error stopping Anki process: {e}")
            finally:
                self.process = None

    def __enter__(self) -> "AnkiProcessManager":
        """Context manager entry."""
        self.launch_anki()
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.stop_anki()
