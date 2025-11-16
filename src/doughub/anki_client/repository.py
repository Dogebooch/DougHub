"""High-level Anki repository for business operations.

This module provides application-facing operations that work with domain
models (Deck, NoteType, Note) and hide AnkiConnect implementation details.
"""

import logging
from typing import Any

from ..models import Deck, Note, NoteType
from .api import AnkiConnectAPI
from .transport import AnkiConnectTransport

logger = logging.getLogger(__name__)


class AnkiRepository:
    """High-level repository for Anki operations.

    Provides business-oriented operations that return domain models and
    combine multiple API calls when needed. This is the primary interface
    for application code interacting with Anki.
    """

    def __init__(
        self,
        url: str | None = None,
        version: int | None = None,
        timeout: float | None = None,
    ) -> None:
        """Initialize the repository.

        Args:
            url: Optional AnkiConnect URL (defaults to config).
            version: Optional API version (defaults to config).
            timeout: Optional timeout in seconds (defaults to config).
        """
        # Create transport with optional overrides
        transport_kwargs: dict[str, Any] = {}
        if url is not None:
            transport_kwargs["url"] = url
        if version is not None:
            transport_kwargs["version"] = version
        if timeout is not None:
            transport_kwargs["timeout"] = timeout

        self.transport = AnkiConnectTransport(**transport_kwargs)
        self.api = AnkiConnectAPI(self.transport)
        logger.debug("Initialized AnkiRepository")

    def __enter__(self) -> "AnkiRepository":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the underlying connections."""
        self.transport.close()

    def check_connection(self) -> bool:
        """Check if AnkiConnect is accessible.

        Returns:
            True if connection is successful, False otherwise.
        """
        return self.transport.check_connection()

    def get_version(self) -> int:
        """Get the AnkiConnect API version.

        Returns:
            The API version number.

        Raises:
            AnkiConnectConnectionError: If unable to connect.
            AnkiConnectAPIError: If the API returns an error.
        """
        return self.transport.get_version()

    def list_decks(self) -> list[Deck]:
        """Get a list of all decks.

        Returns:
            List of Deck objects with names and IDs.

        Raises:
            AnkiConnectConnectionError: If unable to connect.
            AnkiConnectAPIError: If the API returns an error.
        """
        decks_dict = self.api.get_decks_with_ids()
        return [Deck(name=name, id=deck_id) for name, deck_id in decks_dict.items()]

    def list_models(self) -> list[NoteType]:
        """Get a list of all note types.

        Returns:
            List of NoteType objects with names and IDs.

        Raises:
            AnkiConnectConnectionError: If unable to connect.
            AnkiConnectAPIError: If the API returns an error.
        """
        models_dict = self.api.get_model_names_and_ids()
        note_types = []
        for name, model_id in models_dict.items():
            # Fetch field names for each model
            try:
                fields = self.api.get_model_field_names(name)
                note_types.append(NoteType(name=name, id=model_id, fields=fields))
            except Exception as e:
                logger.warning(f"Could not fetch fields for model '{name}': {e}")
                note_types.append(NoteType(name=name, id=model_id, fields=[]))
        return note_types

    def get_model_fields(self, model_name: str) -> list[str]:
        """Get the field names for a specific note type.

        Args:
            model_name: The name of the note type.

        Returns:
            List of field names in order.

        Raises:
            AnkiConnectConnectionError: If unable to connect.
            AnkiConnectAPIError: If the API returns an error.
            ModelNotFoundError: If the note type does not exist.
        """
        return self.api.get_model_field_names(model_name)

    def list_notes_in_deck(self, deck: str, limit: int | None = None) -> list[Note]:
        """Get notes in a specific deck.

        Args:
            deck: The deck name to search.
            limit: Optional limit on number of notes to return.

        Returns:
            List of Note objects from the deck.

        Raises:
            AnkiConnectConnectionError: If unable to connect.
            AnkiConnectAPIError: If the API returns an error or query is invalid.
        """
        query = f'deck:"{deck}"'
        note_ids = self.api.find_note_ids(query)

        if limit is not None:
            note_ids = note_ids[:limit]

        if not note_ids:
            return []

        notes_data = self.api.get_notes_info(note_ids)
        return [Note.from_api_response(note_data) for note_data in notes_data]

    def get_note_detail(self, note_id: int) -> Note:
        """Get detailed information about a single note.

        Args:
            note_id: The ID of the note to retrieve.

        Returns:
            Note object with full details.

        Raises:
            AnkiConnectConnectionError: If unable to connect.
            AnkiConnectAPIError: If the API returns an error.
        """
        notes_data = self.api.get_notes_info([note_id])
        if not notes_data:
            from ..exceptions import NoteNotFoundError

            raise NoteNotFoundError(f"Note {note_id} not found")
        return Note.from_api_response(notes_data[0])

    def create_note(
        self,
        deck: str,
        model: str,
        field_values: dict[str, str],
        tags: list[str] | None = None,
    ) -> int:
        """Create a new note in Anki.

        Args:
            deck: The deck name to add the note to.
            model: The note type name to use.
            field_values: Dictionary mapping field names to their values.
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
        return self.api.add_note(deck, model, field_values, tags)

    def update_note(self, note_id: int, field_values: dict[str, str]) -> None:
        """Update the fields of an existing note.

        Args:
            note_id: The ID of the note to update.
            field_values: Dictionary mapping field names to their new values.

        Raises:
            AnkiConnectConnectionError: If unable to connect.
            AnkiConnectAPIError: If the API returns an error.
            NoteNotFoundError: If the note does not exist.
            InvalidNoteError: If the field data is invalid.
        """
        self.api.update_note_fields(note_id, field_values)

    # Backward compatibility aliases for old method names
    def get_deck_names(self) -> list[str]:
        """Get a list of all deck names (backward compatibility).

        Returns:
            List of deck names.
        """
        return self.api.get_deck_names()

    def get_deck_names_and_ids(self) -> dict[str, int]:
        """Get deck names and IDs (backward compatibility).

        Returns:
            Dictionary mapping deck names to IDs.
        """
        return self.api.get_decks_with_ids()

    def get_decks(self) -> list[Deck]:
        """Get all decks (backward compatibility).

        Returns:
            List of Deck objects.
        """
        return self.list_decks()

    def find_notes(self, query: str) -> list[int]:
        """Find notes matching a query (backward compatibility).

        Args:
            query: Anki search query.

        Returns:
            List of note IDs.
        """
        return self.api.find_note_ids(query)

    def get_notes_info(self, note_ids: list[int]) -> list[Note]:
        """Get note information (backward compatibility).

        Args:
            note_ids: List of note IDs.

        Returns:
            List of Note objects.
        """
        notes_data = self.api.get_notes_info(note_ids)
        return [Note.from_api_response(note_data) for note_data in notes_data]

    def get_model_names(self) -> list[str]:
        """Get all note type names (backward compatibility).

        Returns:
            List of note type names.
        """
        return self.api.get_model_names()

    def get_model_names_and_ids(self) -> dict[str, int]:
        """Get note type names and IDs (backward compatibility).

        Returns:
            Dictionary mapping note type names to IDs.
        """
        return self.api.get_model_names_and_ids()

    def get_note_types(self) -> list[NoteType]:
        """Get all note types (backward compatibility).

        Returns:
            List of NoteType objects.
        """
        return self.list_models()

    def get_model_field_names(self, model_name: str) -> list[str]:
        """Get field names for a note type (backward compatibility).

        Args:
            model_name: The note type name.

        Returns:
            List of field names.
        """
        return self.get_model_fields(model_name)

    def add_note(
        self,
        deck_name: str,
        model_name: str,
        fields: dict[str, str],
        tags: list[str] | None = None,
    ) -> int:
        """Add a note (backward compatibility).

        Args:
            deck_name: The deck name.
            model_name: The note type name.
            fields: Field values.
            tags: Optional tags.

        Returns:
            New note ID.
        """
        return self.create_note(deck_name, model_name, fields, tags)

    def update_note_fields(self, note_id: int, fields: dict[str, str]) -> None:
        """Update note fields (backward compatibility).

        Args:
            note_id: The note ID.
            fields: New field values.
        """
        self.update_note(note_id, fields)
