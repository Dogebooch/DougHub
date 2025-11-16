"""Typed API wrapper for AnkiConnect actions.

This module provides a typed interface to AnkiConnect actions, handling
error message parsing and raising specific exceptions. It delegates to
the transport layer for HTTP communication and returns structured data.
"""

import logging
from typing import Any

from ..exceptions import (
    AnkiConnectAPIError,
    DeckNotFoundError,
    InvalidNoteError,
    ModelNotFoundError,
    NoteNotFoundError,
)
from .transport import AnkiConnectTransport

logger = logging.getLogger(__name__)


class AnkiConnectAPI:
    """Typed wrapper around AnkiConnect API actions.

    Provides one method per AnkiConnect action with proper type signatures.
    Centralizes error message parsing and raises domain-specific exceptions.
    Returns raw or lightly-coerced data structures - model conversion is
    the responsibility of the repository layer.
    """

    def __init__(self, transport: AnkiConnectTransport | None = None) -> None:
        """Initialize the API wrapper.

        Args:
            transport: Optional transport instance. If not provided, creates a new one.
        """
        self.transport = transport or AnkiConnectTransport()
        self._owns_transport = transport is None

    def __enter__(self) -> "AnkiConnectAPI":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the underlying transport if we own it."""
        if self._owns_transport:
            self.transport.close()

    def get_deck_names(self) -> list[str]:
        """Get a list of all deck names.

        Returns:
            List of deck names.

        Raises:
            AnkiConnectConnectionError: If unable to connect.
            AnkiConnectAPIError: If the API returns an error.
        """
        result: list[str] = self.transport.invoke("deckNames")
        return result

    def get_decks_with_ids(self) -> dict[str, int]:
        """Get a mapping of deck names to their IDs.

        Returns:
            Dictionary mapping deck names to deck IDs.

        Raises:
            AnkiConnectConnectionError: If unable to connect.
            AnkiConnectAPIError: If the API returns an error.
        """
        result: dict[str, int] = self.transport.invoke("deckNamesAndIds")
        return result

    def get_model_names(self) -> list[str]:
        """Get a list of all note type (model) names.

        Returns:
            List of note type names.

        Raises:
            AnkiConnectConnectionError: If unable to connect.
            AnkiConnectAPIError: If the API returns an error.
        """
        result: list[str] = self.transport.invoke("modelNames")
        return result

    def get_model_names_and_ids(self) -> dict[str, int]:
        """Get a mapping of note type names to their IDs.

        Returns:
            Dictionary mapping note type names to IDs.

        Raises:
            AnkiConnectConnectionError: If unable to connect.
            AnkiConnectAPIError: If the API returns an error.
        """
        result: dict[str, int] = self.transport.invoke("modelNamesAndIds")
        return result

    def get_model_field_names(self, model_name: str) -> list[str]:
        """Get the field names for a specific note type.

        Args:
            model_name: The name of the note type.

        Returns:
            List of field names for the note type.

        Raises:
            AnkiConnectConnectionError: If unable to connect.
            AnkiConnectAPIError: If the API returns an error.
            ModelNotFoundError: If the note type does not exist.
        """
        try:
            result: list[str] = self.transport.invoke(
                "modelFieldNames", {"modelName": model_name}
            )
            return result
        except AnkiConnectAPIError as e:
            if "model was not found" in str(e).lower():
                raise ModelNotFoundError(f"Note type '{model_name}' not found") from e
            raise

    def get_model_fields_on_templates(self, model_name: str) -> dict[str, Any]:
        """Get field information including templates for a note type.

        Args:
            model_name: The name of the note type.

        Returns:
            Dictionary with field information.

        Raises:
            AnkiConnectConnectionError: If unable to connect.
            AnkiConnectAPIError: If the API returns an error.
            ModelNotFoundError: If the note type does not exist.
        """
        try:
            result: dict[str, Any] = self.transport.invoke(
                "modelFieldsOnTemplates", {"modelName": model_name}
            )
            return result
        except AnkiConnectAPIError as e:
            if "model was not found" in str(e).lower():
                raise ModelNotFoundError(f"Note type '{model_name}' not found") from e
            raise

    def find_note_ids(self, query: str) -> list[int]:
        """Find notes matching a search query.

        Args:
            query: Anki search query (e.g., 'deck:"My Deck"', 'tag:important').

        Returns:
            List of note IDs matching the query.

        Raises:
            AnkiConnectConnectionError: If unable to connect.
            AnkiConnectAPIError: If the API returns an error or query is invalid.
        """
        result: list[int] = self.transport.invoke("findNotes", {"query": query})
        return result

    def get_notes_info(self, note_ids: list[int]) -> list[dict[str, Any]]:
        """Get detailed information about notes.

        Args:
            note_ids: List of note IDs to retrieve information for.

        Returns:
            List of dictionaries with note information (raw API format).

        Raises:
            AnkiConnectConnectionError: If unable to connect.
            AnkiConnectAPIError: If the API returns an error.
        """
        if not note_ids:
            return []

        result: list[dict[str, Any]] = self.transport.invoke(
            "notesInfo", {"notes": note_ids}
        )
        return result

    def add_note(
        self,
        deck_name: str,
        model_name: str,
        fields: dict[str, str],
        tags: list[str] | None = None,
    ) -> int:
        """Add a new note to Anki.

        Args:
            deck_name: The name of the deck to add the note to.
            model_name: The name of the note type to use.
            fields: Dictionary mapping field names to their values.
            tags: Optional list of tags to add to the note.

        Returns:
            The ID of the newly created note.

        Raises:
            AnkiConnectConnectionError: If unable to connect.
            AnkiConnectAPIError: If the API returns an error.
            DeckNotFoundError: If the deck does not exist.
            ModelNotFoundError: If the note type does not exist.
            InvalidNoteError: If the note data is invalid.
        """
        note_data = {
            "deckName": deck_name,
            "modelName": model_name,
            "fields": fields,
            "tags": tags or [],
        }

        try:
            result: int = self.transport.invoke("addNote", {"note": note_data})
            logger.info(
                f"Added note {result} to deck '{deck_name}' with model '{model_name}'"
            )
            return result
        except AnkiConnectAPIError as e:
            error_msg = str(e).lower()
            if "deck was not found" in error_msg:
                raise DeckNotFoundError(f"Deck '{deck_name}' not found") from e
            if "model was not found" in error_msg:
                raise ModelNotFoundError(f"Note type '{model_name}' not found") from e
            if "cannot create note" in error_msg or "invalid" in error_msg:
                raise InvalidNoteError(
                    f"Invalid note data for model '{model_name}': {e}"
                ) from e
            raise

    def update_note_fields(self, note_id: int, fields: dict[str, str]) -> None:
        """Update the fields of an existing note.

        Args:
            note_id: The ID of the note to update.
            fields: Dictionary mapping field names to their new values.

        Raises:
            AnkiConnectConnectionError: If unable to connect.
            AnkiConnectAPIError: If the API returns an error.
            NoteNotFoundError: If the note does not exist.
            InvalidNoteError: If the field data is invalid.
        """
        note_data = {"id": note_id, "fields": fields}

        try:
            self.transport.invoke("updateNoteFields", {"note": note_data})
            logger.info(f"Updated fields for note {note_id}")
        except AnkiConnectAPIError as e:
            error_msg = str(e).lower()
            if "note was not found" in error_msg or "note does not exist" in error_msg:
                raise NoteNotFoundError(f"Note {note_id} not found") from e
            if "cannot update" in error_msg or "invalid" in error_msg:
                raise InvalidNoteError(
                    f"Invalid field data for note {note_id}: {e}"
                ) from e
            raise
