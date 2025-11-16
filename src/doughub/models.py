"""Data models for Anki deck management."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Deck:
    """Represents an Anki deck.

    Attributes:
        name: The name of the deck.
        id: The unique identifier of the deck (optional).
    """

    name: str
    id: int | None = None


@dataclass
class NoteType:
    """Represents an Anki note type (model).

    Attributes:
        name: The name of the note type.
        id: The unique identifier of the note type (optional).
        fields: List of field names for this note type (optional).
    """

    name: str
    id: int | None = None
    fields: list[str] = field(default_factory=list)


@dataclass
class Note:
    """Represents an Anki note.

    Attributes:
        note_id: The unique identifier of the note.
        model_name: The name of the note type (model).
        fields: Dictionary mapping field names to their values.
        tags: List of tags associated with the note.
        cards: List of card IDs associated with this note.
    """

    note_id: int
    model_name: str
    fields: dict[str, str]
    tags: list[str] = field(default_factory=list)
    cards: list[int] = field(default_factory=list)

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "Note":
        """Create a Note instance from AnkiConnect API response.

        Args:
            data: Dictionary containing note data from notesInfo action.

        Returns:
            A Note instance populated with the response data.
        """
        return cls(
            note_id=data["noteId"],
            model_name=data["modelName"],
            fields=data["fields"],
            tags=data.get("tags", []),
            cards=data.get("cards", []),
        )


@dataclass
class Card:
    """Represents an Anki card.

    Attributes:
        card_id: The unique identifier of the card.
        note_id: The ID of the note this card belongs to.
        deck_name: The name of the deck containing this card.
        deck_id: The ID of the deck containing this card.
        front: The front side of the card (optional).
        back: The back side of the card (optional).
    """

    card_id: int
    note_id: int
    deck_name: str
    deck_id: int
    front: str | None = None
    back: str | None = None
