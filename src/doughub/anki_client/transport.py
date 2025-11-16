"""Low-level HTTP transport for AnkiConnect API.

This module provides the HTTP client layer that handles communication with
AnkiConnect, request/response formatting, and basic error handling.
"""

import logging
from typing import Any

import httpx

from ..config import (
    ANKICONNECT_TIMEOUT,
    ANKICONNECT_URL,
    ANKICONNECT_VERSION,
)
from ..exceptions import (
    AnkiConnectAPIError,
    AnkiConnectConnectionError,
)

logger = logging.getLogger(__name__)


class AnkiConnectTransport:
    """Low-level HTTP client for AnkiConnect API.

    Handles HTTP communication with AnkiConnect, including:
    - Building and sending JSON-RPC style requests
    - Parsing responses
    - Basic error detection (connection failures, API errors)

    Does not interpret error messages or convert data structures - that's
    the responsibility of higher layers.
    """

    def __init__(
        self,
        url: str = ANKICONNECT_URL,
        version: int = ANKICONNECT_VERSION,
        timeout: float = ANKICONNECT_TIMEOUT,
    ) -> None:
        """Initialize the transport layer.

        Args:
            url: The URL of the AnkiConnect server.
            version: The AnkiConnect API version to use.
            timeout: Timeout in seconds for HTTP requests.
        """
        self.url = url
        self.version = version
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)
        logger.debug(f"Initialized AnkiConnect transport: {url} (version {version})")

    def __enter__(self) -> "AnkiConnectTransport":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the HTTP client connection."""
        self._client.close()

    def invoke(self, action: str, params: dict[str, Any] | None = None) -> Any:
        """Invoke an AnkiConnect API action.

        This is the core transport method that handles all communication with
        AnkiConnect. It builds the JSON payload, makes the HTTP request,
        and performs basic validation.

        Args:
            action: The API action to invoke.
            params: Optional parameters for the action.

        Returns:
            The result from the API response (raw, not interpreted).

        Raises:
            AnkiConnectConnectionError: If unable to connect to AnkiConnect.
            AnkiConnectAPIError: If the API returns an error.
        """
        payload = {"action": action, "version": self.version}
        if params is not None:
            payload["params"] = params

        logger.debug(f"Invoking AnkiConnect action: {action} with params: {params}")

        try:
            response = self._client.post(self.url, json=payload)
            response.raise_for_status()
        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to AnkiConnect at {self.url}: {e}")
            raise AnkiConnectConnectionError(
                f"Unable to connect to AnkiConnect at {self.url}. "
                "Ensure Anki is running with AnkiConnect installed."
            ) from e
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during AnkiConnect request: {e}")
            raise AnkiConnectConnectionError(
                f"HTTP error connecting to AnkiConnect: {e}"
            ) from e

        try:
            data = response.json()
        except Exception as e:
            logger.error(f"Failed to parse AnkiConnect response: {e}")
            raise AnkiConnectAPIError(
                f"Invalid JSON response from AnkiConnect: {e}", action=action
            ) from e

        if "error" not in data:
            logger.error(f"AnkiConnect response missing 'error' field: {data}")
            raise AnkiConnectAPIError(
                "Malformed response from AnkiConnect (missing 'error' field)",
                action=action,
            )

        if data["error"] is not None:
            error_msg = data["error"]
            logger.error(f"AnkiConnect API error for action '{action}': {error_msg}")
            raise AnkiConnectAPIError(error_msg, action=action)

        logger.debug(f"AnkiConnect action '{action}' succeeded")
        return data.get("result")

    def get_version(self) -> int:
        """Get the AnkiConnect API version.

        Returns:
            The API version number.

        Raises:
            AnkiConnectConnectionError: If unable to connect.
            AnkiConnectAPIError: If the API returns an error.
        """
        result: int = self.invoke("version")
        return result

    def check_connection(self) -> bool:
        """Check if AnkiConnect is accessible.

        Returns:
            True if connection is successful, False otherwise.
        """
        try:
            self.get_version()
            return True
        except (AnkiConnectConnectionError, AnkiConnectAPIError):
            return False
