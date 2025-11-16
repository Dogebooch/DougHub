"""Custom exceptions for AnkiConnect operations."""


class AnkiConnectError(Exception):
    """Base exception for all AnkiConnect-related errors."""

    pass


class AnkiConnectConnectionError(AnkiConnectError):
    """Raised when unable to connect to AnkiConnect."""

    pass


class AnkiConnectAPIError(AnkiConnectError):
    """Raised when AnkiConnect returns an error response."""

    def __init__(self, message: str, action: str | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Error message from AnkiConnect.
            action: The API action that failed.
        """
        self.action = action
        super().__init__(message)


class DeckNotFoundError(AnkiConnectError):
    """Raised when a requested deck does not exist."""

    pass


class NoteNotFoundError(AnkiConnectError):
    """Raised when a requested note does not exist."""

    pass


class ModelNotFoundError(AnkiConnectError):
    """Raised when a requested note type (model) does not exist."""

    pass


class InvalidNoteError(AnkiConnectError):
    """Raised when attempting to create or update a note with invalid data."""

    pass
