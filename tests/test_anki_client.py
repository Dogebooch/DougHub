"""Unit tests for AnkiConnect client with mocked HTTP responses."""

from collections.abc import Generator

import pytest
import respx
from httpx import Response
from respx import MockRouter

from doughub.anki_client import AnkiConnectClient
from doughub.exceptions import (
    AnkiConnectAPIError,
    AnkiConnectConnectionError,
    DeckNotFoundError,
    InvalidNoteError,
    ModelNotFoundError,
    NoteNotFoundError,
)


@pytest.fixture
def mock_ankiconnect() -> Generator[MockRouter, None, None]:
    """Fixture to set up respx for mocking httpx requests."""
    with respx.mock(base_url="http://127.0.0.1:8765") as respx_mock:
        yield respx_mock


@pytest.fixture
def client() -> AnkiConnectClient:
    """Fixture to create an AnkiConnect client."""
    return AnkiConnectClient()


def test_get_version_success(mock_ankiconnect: MockRouter, client: AnkiConnectClient) -> None:
    """Test successful version retrieval."""
    mock_ankiconnect.post("/").mock(
        return_value=Response(200, json={"result": 6, "error": None})
    )

    version = client.get_version()
    assert version == 6


def test_get_version_connection_error(mock_ankiconnect: MockRouter, client: AnkiConnectClient) -> None:
    """Test connection error when AnkiConnect is not running."""
    import httpx

    mock_ankiconnect.post("/").mock(
        side_effect=httpx.ConnectError("Connection refused")
    )

    with pytest.raises(AnkiConnectConnectionError):
        client.get_version()


def test_get_version_api_error(mock_ankiconnect: MockRouter, client: AnkiConnectClient) -> None:
    """Test API error response."""
    mock_ankiconnect.post("/").mock(
        return_value=Response(
            200, json={"result": None, "error": "Something went wrong"}
        )
    )

    with pytest.raises(AnkiConnectAPIError) as exc_info:
        client.get_version()
    assert "Something went wrong" in str(exc_info.value)


def test_check_connection_success(mock_ankiconnect: MockRouter, client: AnkiConnectClient) -> None:
    """Test successful connection check."""
    mock_ankiconnect.post("/").mock(
        return_value=Response(200, json={"result": 6, "error": None})
    )

    assert client.check_connection() is True


def test_check_connection_failure(mock_ankiconnect: MockRouter, client: AnkiConnectClient) -> None:
    """Test connection check when AnkiConnect is unavailable."""
    import httpx

    mock_ankiconnect.post("/").mock(
        side_effect=httpx.ConnectError("Connection refused")
    )

    assert client.check_connection() is False


def test_get_deck_names(mock_ankiconnect: MockRouter, client: AnkiConnectClient) -> None:
    """Test retrieving deck names."""
    mock_ankiconnect.post("/").mock(
        return_value=Response(
            200, json={"result": ["Default", "Programming", "Japanese"], "error": None}
        )
    )

    deck_names = client.get_deck_names()
    assert deck_names == ["Default", "Programming", "Japanese"]


def test_get_deck_names_and_ids(mock_ankiconnect: MockRouter, client: AnkiConnectClient) -> None:
    """Test retrieving deck names with IDs."""
    mock_ankiconnect.post("/").mock(
        return_value=Response(
            200,
            json={
                "result": {
                    "Default": 1,
                    "Programming": 123456789,
                    "Japanese": 987654321,
                },
                "error": None,
            },
        )
    )

    decks_dict = client.get_deck_names_and_ids()
    assert decks_dict == {"Default": 1, "Programming": 123456789, "Japanese": 987654321}


def test_get_decks(mock_ankiconnect: MockRouter, client: AnkiConnectClient) -> None:
    """Test retrieving decks as Deck objects."""
    mock_ankiconnect.post("/").mock(
        return_value=Response(
            200,
            json={
                "result": {"Default": 1, "Programming": 123456789},
                "error": None,
            },
        )
    )

    decks = client.get_decks()
    assert len(decks) == 2
    assert any(d.name == "Default" and d.id == 1 for d in decks)
    assert any(d.name == "Programming" and d.id == 123456789 for d in decks)


def test_find_notes(mock_ankiconnect: MockRouter, client: AnkiConnectClient) -> None:
    """Test finding notes with a query."""
    mock_ankiconnect.post("/").mock(
        return_value=Response(
            200, json={"result": [1483959289817, 1483959291695], "error": None}
        )
    )

    note_ids = client.find_notes('deck:"Programming"')
    assert note_ids == [1483959289817, 1483959291695]


def test_get_notes_info(mock_ankiconnect: MockRouter, client: AnkiConnectClient) -> None:
    """Test retrieving detailed note information."""
    mock_ankiconnect.post("/").mock(
        return_value=Response(
            200,
            json={
                "result": [
                    {
                        "noteId": 1483959289817,
                        "modelName": "Basic",
                        "fields": {"Front": "Python", "Back": "A programming language"},
                        "tags": ["programming", "python"],
                        "cards": [1498938915662],
                    }
                ],
                "error": None,
            },
        )
    )

    notes = client.get_notes_info([1483959289817])
    assert len(notes) == 1
    note = notes[0]
    assert note.note_id == 1483959289817
    assert note.model_name == "Basic"
    assert note.fields["Front"] == "Python"
    assert "programming" in note.tags


def test_get_notes_info_empty_list(mock_ankiconnect: MockRouter, client: AnkiConnectClient) -> None:
    """Test getting notes info with empty list."""
    notes = client.get_notes_info([])
    assert notes == []


def test_get_model_names(mock_ankiconnect: MockRouter, client: AnkiConnectClient) -> None:
    """Test retrieving note type names."""
    mock_ankiconnect.post("/").mock(
        return_value=Response(
            200, json={"result": ["Basic", "Basic (and reversed card)"], "error": None}
        )
    )

    model_names = client.get_model_names()
    assert model_names == ["Basic", "Basic (and reversed card)"]


def test_get_model_names_and_ids(mock_ankiconnect: MockRouter, client: AnkiConnectClient) -> None:
    """Test retrieving note type names with IDs."""
    mock_ankiconnect.post("/").mock(
        return_value=Response(
            200,
            json={
                "result": {"Basic": 1483883011648, "Cloze": 1498938915523},
                "error": None,
            },
        )
    )

    models_dict = client.get_model_names_and_ids()
    assert models_dict == {"Basic": 1483883011648, "Cloze": 1498938915523}


def test_get_note_types(mock_ankiconnect: MockRouter, client: AnkiConnectClient) -> None:
    """Test retrieving note types as NoteType objects."""
    mock_ankiconnect.post("/").mock(
        return_value=Response(
            200,
            json={
                "result": {"Basic": 1483883011648, "Cloze": 1498938915523},
                "error": None,
            },
        )
    )

    note_types = client.get_note_types()
    assert len(note_types) == 2
    assert any(nt.name == "Basic" and nt.id == 1483883011648 for nt in note_types)


def test_get_model_field_names(mock_ankiconnect: MockRouter, client: AnkiConnectClient) -> None:
    """Test retrieving field names for a note type."""
    mock_ankiconnect.post("/").mock(
        return_value=Response(200, json={"result": ["Front", "Back"], "error": None})
    )

    fields = client.get_model_field_names("Basic")
    assert fields == ["Front", "Back"]


def test_get_model_field_names_not_found(mock_ankiconnect: MockRouter, client: AnkiConnectClient) -> None:
    """Test error when note type does not exist."""
    mock_ankiconnect.post("/").mock(
        return_value=Response(
            200, json={"result": None, "error": "model was not found"}
        )
    )

    with pytest.raises(ModelNotFoundError):
        client.get_model_field_names("NonExistent")


def test_add_note_success(mock_ankiconnect: MockRouter, client: AnkiConnectClient) -> None:
    """Test successfully adding a note."""
    mock_ankiconnect.post("/").mock(
        return_value=Response(200, json={"result": 1496198395707, "error": None})
    )

    note_id = client.add_note(
        deck_name="Programming",
        model_name="Basic",
        fields={"Front": "Python", "Back": "A programming language"},
        tags=["python"],
    )
    assert note_id == 1496198395707


def test_add_note_deck_not_found(mock_ankiconnect: MockRouter, client: AnkiConnectClient) -> None:
    """Test error when deck does not exist."""
    mock_ankiconnect.post("/").mock(
        return_value=Response(200, json={"result": None, "error": "deck was not found"})
    )

    with pytest.raises(DeckNotFoundError):
        client.add_note(
            deck_name="NonExistent",
            model_name="Basic",
            fields={"Front": "Test", "Back": "Test"},
        )


def test_add_note_model_not_found(mock_ankiconnect: MockRouter, client: AnkiConnectClient) -> None:
    """Test error when note type does not exist."""
    mock_ankiconnect.post("/").mock(
        return_value=Response(
            200, json={"result": None, "error": "model was not found"}
        )
    )

    with pytest.raises(ModelNotFoundError):
        client.add_note(
            deck_name="Default",
            model_name="NonExistent",
            fields={"Front": "Test", "Back": "Test"},
        )


def test_add_note_invalid_fields(mock_ankiconnect: MockRouter, client: AnkiConnectClient) -> None:
    """Test error when note fields are invalid."""
    mock_ankiconnect.post("/").mock(
        return_value=Response(
            200,
            json={"result": None, "error": "cannot create note because it is invalid"},
        )
    )

    with pytest.raises(InvalidNoteError):
        client.add_note(
            deck_name="Default", model_name="Basic", fields={"InvalidField": "Value"}
        )


def test_update_note_fields_success(mock_ankiconnect: MockRouter, client: AnkiConnectClient) -> None:
    """Test successfully updating note fields."""
    mock_ankiconnect.post("/").mock(
        return_value=Response(200, json={"result": None, "error": None})
    )

    client.update_note_fields(
        note_id=1496198395707, fields={"Front": "Updated Front", "Back": "Updated Back"}
    )
    # No exception means success


def test_update_note_fields_not_found(mock_ankiconnect: MockRouter, client: AnkiConnectClient) -> None:
    """Test error when note does not exist."""
    mock_ankiconnect.post("/").mock(
        return_value=Response(200, json={"result": None, "error": "note was not found"})
    )

    with pytest.raises(NoteNotFoundError):
        client.update_note_fields(note_id=999999, fields={"Front": "Test"})


def test_update_note_fields_invalid(mock_ankiconnect: MockRouter, client: AnkiConnectClient) -> None:
    """Test error when field data is invalid."""
    mock_ankiconnect.post("/").mock(
        return_value=Response(
            200,
            json={"result": None, "error": "cannot update note with invalid fields"},
        )
    )

    with pytest.raises(InvalidNoteError):
        client.update_note_fields(
            note_id=1496198395707, fields={"InvalidField": "Value"}
        )


def test_context_manager(mock_ankiconnect: MockRouter) -> None:
    """Test using client as a context manager."""
    mock_ankiconnect.post("/").mock(
        return_value=Response(200, json={"result": 6, "error": None})
    )

    with AnkiConnectClient() as client:
        version = client.get_version()
        assert version == 6
    # Client should be closed after exiting context
