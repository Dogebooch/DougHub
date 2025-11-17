"""Manager for Notesium subprocess lifecycle."""

import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Any

import httpx

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
            # Notesium is a standalone Go binary that needs to be installed separately
            # See: https://github.com/alonswartz/notesium
            import shutil
            
            # Try to find notesium in PATH
            notesium_path = shutil.which("notesium")
            if not notesium_path:
                # Try common Windows locations
                import platform
                if platform.system() == "Windows":
                    possible_locations = [
                        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "notesium" / "notesium.exe",
                        Path.home() / "AppData" / "Local" / "Programs" / "notesium" / "notesium.exe",
                        Path("C:/Program Files/notesium/notesium.exe"),
                    ]
                    for loc in possible_locations:
                        if loc.exists():
                            notesium_path = str(loc)
                            logger.info(f"Found notesium at: {notesium_path}")
                            break
            
            if not notesium_path:
                raise FileNotFoundError("notesium binary not found in PATH or common locations")
            
            cmd = [
                notesium_path,
                "web",
                f"--port={self.port}",
                "--writable",
            ]
            
            logger.info(f"Starting Notesium with command: {' '.join(cmd)}")
            logger.debug(f"Working directory: {Path.cwd()}")
            logger.debug(f"Notes directory (absolute): {self.notes_dir.absolute()}")
            
            # Set NOTESIUM_DIR environment variable for the subprocess
            env = os.environ.copy()
            env["NOTESIUM_DIR"] = str(self.notes_dir.absolute())
            logger.debug(f"Setting NOTESIUM_DIR={env['NOTESIUM_DIR']}")

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
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
                    stdout = self.process.stdout.read().decode() if self.process.stdout else ""
                    stderr = self.process.stderr.read().decode() if self.process.stderr else ""
                    logger.error(f"Notesium process terminated unexpectedly")
                    logger.error(f"Exit code: {self.process.returncode}")
                    if stdout:
                        logger.error(f"STDOUT: {stdout}")
                    if stderr:
                        logger.error(f"STDERR: {stderr}")
                    return False

            logger.error(f"Notesium failed health check after {max_attempts} attempts")
            # Try to capture any output before stopping
            if self.process and self.process.poll() is None:
                logger.warning("Process still running but health check failed")
            elif self.process:
                stdout = self.process.stdout.read().decode() if self.process.stdout else ""
                stderr = self.process.stderr.read().decode() if self.process.stderr else ""
                if stdout:
                    logger.error(f"Process STDOUT: {stdout}")
                if stderr:
                    logger.error(f"Process STDERR: {stderr}")
            self.stop()
            return False

        except FileNotFoundError as e:
            logger.error(
                f"'notesium' binary not found in PATH. "
                f"Please install Notesium from https://github.com/alonswartz/notesium/releases/latest. "
                f"Error: {e}"
            )
            return False
        except Exception as e:
            logger.exception(f"Failed to start Notesium: {e}")
            if self.process:
                try:
                    stdout = self.process.stdout.read().decode() if self.process.stdout else ""
                    stderr = self.process.stderr.read().decode() if self.process.stderr else ""
                    if stdout:
                        logger.error(f"Process STDOUT: {stdout}")
                    if stderr:
                        logger.error(f"Process STDERR: {stderr}")
                except Exception as read_err:
                    logger.error(f"Could not read process output: {read_err}")
            self.stop()
            return False

    def stop(self) -> None:
        """Stop the Notesium server if it's running."""
        if self.process:
            logger.info("Stopping Notesium process...")
            try:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning("Notesium didn't terminate gracefully, forcing kill")
                    self.process.kill()
                    self.process.wait()
                logger.info("Notesium process stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping Notesium: {e}")
            finally:
                self.process = None
                self._is_healthy = False
        else:
            logger.debug("No Notesium process to stop")

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
            logger.debug(f"Health check: requesting {self.url}")
            with httpx.Client() as client:
                response = client.get(self.url, timeout=2.0)
            logger.debug(f"Health check response: {response.status_code}")
            return bool(response.status_code == 200)
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.debug(f"Health check failed: {e}")
            return False

    def _check_port_in_use(self) -> bool:
        """Check if the configured port is already in use.

        Returns:
            True if the port is in use, False otherwise.
        """
        try:
            with httpx.Client() as client:
                client.get(self.url, timeout=1.0)
            return True
        except (httpx.RequestError, httpx.HTTPStatusError):
            return False

    def __enter__(self) -> "NotesiumManager":
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.stop()
