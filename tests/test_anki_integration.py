"""Integration tests for AnkiConnect client against real Anki instance.

These tests require Anki to be running with AnkiConnect installed.
They will attempt to auto-launch Anki if it's not running and auto-launch is enabled.

Run these tests with: pytest -m integration
Skip these tests with: pytest -m "not integration"
"""

from collections.abc import Generator
from unittest.mock import Mock, patch

import httpx
import pytest

from doughub.anki_client import AnkiConnectClient
from doughub.exceptions import (
    AnkiConnectAPIError,
    AnkiConnectConnectionError,
    DeckNotFoundError,
    InvalidNoteError,
    ModelNotFoundError,
    NoteNotFoundError,
)
from doughub.utils.anki_process import AnkiProcessManager


@pytest.fixture(scope="module")
def anki_manager() -> Generator[AnkiProcessManager, None, None]:
    """Fixture to manage Anki process for integration tests."""
    manager = AnkiProcessManager()
    if not manager.is_ankiconnect_running():
        success = manager.launch_anki(timeout=15.0)
        if not success:
            pytest.skip("Anki could not be started and is not running")
    yield manager
    # Note: We don't stop Anki after tests to avoid disrupting user's workflow
    # If you want to stop Anki after tests, uncomment the next line:
    # manager.stop_anki()


@pytest.fixture
def client(anki_manager: AnkiProcessManager) -> AnkiConnectClient:
    """Fixture to create an AnkiConnect client for integration tests."""
    client = AnkiConnectClient()
    if not client.check_connection():
        pytest.skip("AnkiConnect is not accessible")
    return client


@pytest.mark.integration
def test_connection_check(client: AnkiConnectClient) -> None:
    """Test that we can connect to AnkiConnect."""
    assert client.check_connection() is True


@pytest.mark.integration
def test_get_version(client: AnkiConnectClient) -> None:
    """Test getting AnkiConnect version."""
    version = client.get_version()
    assert isinstance(version, int)
    assert version >= 5  # AnkiConnect version should be at least 5


@pytest.mark.integration
def test_get_deck_names(client: AnkiConnectClient) -> None:
    """Test retrieving deck names."""
    deck_names = client.get_deck_names()
    assert isinstance(deck_names, list)
    assert "Default" in deck_names  # Default deck always exists


@pytest.mark.integration
def test_get_deck_names_and_ids(client: AnkiConnectClient) -> None:
    """Test retrieving deck names with IDs."""
    decks_dict = client.get_deck_names_and_ids()
    assert isinstance(decks_dict, dict)
    assert "Default" in decks_dict
    assert isinstance(decks_dict["Default"], int)


@pytest.mark.integration
def test_get_decks(client: AnkiConnectClient) -> None:
    """Test retrieving decks as objects."""
    decks = client.get_decks()
    assert isinstance(decks, list)
    assert len(decks) > 0
    assert any(deck.name == "Default" for deck in decks)


@pytest.mark.integration
def test_get_model_names(client: AnkiConnectClient) -> None:
    """Test retrieving note type names."""
    model_names = client.get_model_names()
    assert isinstance(model_names, list)
    assert len(model_names) > 0
    # Basic note type should exist in any Anki installation
    assert "Basic" in model_names


@pytest.mark.integration
def test_get_model_names_and_ids(client: AnkiConnectClient) -> None:
    """Test retrieving note type names with IDs."""
    models_dict = client.get_model_names_and_ids()
    assert isinstance(models_dict, dict)
    assert "Basic" in models_dict
    assert isinstance(models_dict["Basic"], int)


@pytest.mark.integration
def test_get_note_types(client: AnkiConnectClient) -> None:
    """Test retrieving note types as objects."""
    note_types = client.get_note_types()
    assert isinstance(note_types, list)
    assert len(note_types) > 0
    assert any(nt.name == "Basic" for nt in note_types)


@pytest.mark.integration
def test_get_model_field_names(client: AnkiConnectClient) -> None:
    """Test retrieving field names for a note type."""
    fields = client.get_model_field_names("Basic")
    assert isinstance(fields, list)
    assert "Front" in fields
    assert "Back" in fields


@pytest.mark.integration
def test_get_model_field_names_not_found(client: AnkiConnectClient) -> None:
    """Test error when requesting fields for non-existent note type."""
    with pytest.raises(ModelNotFoundError):
        client.get_model_field_names("NonExistentModel12345")


@pytest.mark.integration
def test_find_notes(client: AnkiConnectClient) -> None:
    """Test finding notes with a query."""
    # Search for any notes (empty query returns all notes)
    note_ids = client.find_notes("")
    assert isinstance(note_ids, list)
    # Can be empty if no notes exist, which is fine


@pytest.mark.integration
def test_add_and_update_note_lifecycle(client: AnkiConnectClient) -> None:
    """Test full lifecycle: add a note, update it, retrieve it, verify changes."""
    import time
    timestamp = int(time.time())
    
    # Add a test note
    note_id = client.add_note(
        deck_name="Default",
        model_name="Basic",
        fields={"Front": f"Integration Test Front {timestamp}", "Back": f"Integration Test Back {timestamp}"},
        tags=["integration-test", "doughub"],
    )
    assert isinstance(note_id, int)
    assert note_id > 0

    try:
        # Retrieve the note
        notes = client.get_notes_info([note_id])
        assert len(notes) == 1
        note = notes[0]
        assert note.note_id == note_id
        assert note.model_name == "Basic"
        assert note.fields["Front"] == f"Integration Test Front {timestamp}"
        assert note.fields["Back"] == f"Integration Test Back {timestamp}"
        assert "integration-test" in note.tags
        assert "doughub" in note.tags

        # Update the note
        client.update_note_fields(
            note_id=note_id,
            fields={"Front": f"Updated Front {timestamp}", "Back": f"Updated Back {timestamp}"},
        )

        # Verify the update
        updated_notes = client.get_notes_info([note_id])
        assert len(updated_notes) == 1
        updated_note = updated_notes[0]
        assert updated_note.fields["Front"] == f"Updated Front {timestamp}"
        assert updated_note.fields["Back"] == f"Updated Back {timestamp}"

    finally:
        # Clean up: delete the test note
        # Note: AnkiConnect doesn't have a direct deleteNotes action in the plan,
        # but we can search for the note to verify it exists
        found_notes = client.find_notes(f"nid:{note_id}")
        assert note_id in found_notes


@pytest.mark.integration
def test_add_note_deck_not_found(client: AnkiConnectClient) -> None:
    """Test error when adding note to non-existent deck."""
    with pytest.raises(DeckNotFoundError):
        client.add_note(
            deck_name="NonExistentDeck12345",
            model_name="Basic",
            fields={"Front": "Test", "Back": "Test"},
        )


@pytest.mark.integration
def test_add_note_model_not_found(client: AnkiConnectClient) -> None:
    """Test error when adding note with non-existent note type."""
    with pytest.raises(ModelNotFoundError):
        client.add_note(
            deck_name="Default",
            model_name="NonExistentModel12345",
            fields={"Front": "Test", "Back": "Test"},
        )


@pytest.mark.integration
def test_add_note_invalid_fields(client: AnkiConnectClient) -> None:
    """Test error when adding note with invalid field names."""
    with pytest.raises(InvalidNoteError):
        client.add_note(
            deck_name="Default",
            model_name="Basic",
            fields={"InvalidField": "Value"},
        )


@pytest.mark.integration
def test_update_note_not_found(client: AnkiConnectClient) -> None:
    """Test error when updating non-existent note."""
    with pytest.raises(NoteNotFoundError):
        client.update_note_fields(
            note_id=999999999999, fields={"Front": "Test", "Back": "Test"}
        )


@pytest.mark.integration
def test_update_note_invalid_fields(client: AnkiConnectClient) -> None:
    """Test that updating note with invalid field names is ignored or handled gracefully."""
    import time
    timestamp = int(time.time())
    
    # First create a note to get a valid ID
    note_id = client.add_note(
        deck_name="Default",
        model_name="Basic",
        fields={"Front": f"Invalid Update Test {timestamp}", "Back": f"Invalid Update Test Back {timestamp}"},
        tags=["integration-test"],
    )

    try:
        # Try to update with non-existent field - AnkiConnect ignores this silently
        client.update_note_fields(
            note_id=note_id,
            fields={"NonExistentField": "New Value", "Front": f"Valid Update {timestamp}"},
        )
        
        # Verify that the valid field WAS updated
        notes = client.get_notes_info([note_id])
        assert len(notes) == 1
        assert notes[0].fields["Front"] == f"Valid Update {timestamp}"
        
        # Verify that the invalid field is NOT present (implied by model definition, but good to check logic holds)
        assert "NonExistentField" not in notes[0].fields
        
    finally:
        # The note will remain in Anki; cleanup would require additional actions
        pass


@pytest.mark.integration
def test_get_notes_info_multiple(client: AnkiConnectClient) -> None:
    """Test retrieving information for multiple notes at once."""
    import time
    timestamp = int(time.time())
    
    # Create two test notes
    note_id1 = client.add_note(
        deck_name="Default",
        model_name="Basic",
        fields={"Front": f"Multi Test 1 {timestamp}", "Back": f"Back 1 {timestamp}"},
        tags=["integration-test"],
    )
    note_id2 = client.add_note(
        deck_name="Default",
        model_name="Basic",
        fields={"Front": f"Multi Test 2 {timestamp}", "Back": f"Back 2 {timestamp}"},
        tags=["integration-test"],
    )

    try:
        # Retrieve both notes
        notes = client.get_notes_info([note_id1, note_id2])
        assert len(notes) == 2
        note_ids = {note.note_id for note in notes}
        assert note_id1 in note_ids
        assert note_id2 in note_ids
    finally:
        # Notes will remain in Anki
        pass


@pytest.mark.integration
def test_context_manager(anki_manager: AnkiProcessManager) -> None:
    """Test using client as a context manager."""
    with AnkiConnectClient() as client:
        version = client.get_version()
        assert isinstance(version, int)
    # Client should be closed after exiting context


class TestAnkiFailures:
    """Tests for AnkiConnect failure scenarios using mocks."""

    @patch("doughub.anki_client.transport.httpx.Client")
    def test_connection_refused(self, mock_client_cls):
        """Test handling of connection refused error."""
        mock_client = mock_client_cls.return_value
        mock_client.post.side_effect = httpx.ConnectError("Connection refused")

        client = AnkiConnectClient()

        with pytest.raises(AnkiConnectConnectionError, match="Unable to connect"):
            client.get_version()

    @patch("doughub.anki_client.transport.httpx.Client")
    def test_http_error(self, mock_client_cls):
        """Test handling of HTTP errors."""
        mock_client = mock_client_cls.return_value
        mock_client.post.side_effect = httpx.HTTPStatusError(
            "500 Internal Server Error", request=Mock(), response=Mock()
        )

        client = AnkiConnectClient()

        with pytest.raises(AnkiConnectConnectionError, match="HTTP error"):
            client.get_version()

    @patch("doughub.anki_client.transport.httpx.Client")
    def test_malformed_json_response(self, mock_client_cls):
        """Test handling of invalid JSON response."""
        mock_client = mock_client_cls.return_value
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_client.post.return_value = mock_response

        client = AnkiConnectClient()

        with pytest.raises(AnkiConnectAPIError, match="Invalid JSON"):
            client.get_version()

    @patch("doughub.anki_client.transport.httpx.Client")
    def test_missing_error_field(self, mock_client_cls):
        """Test handling of response missing 'error' field."""
        mock_client = mock_client_cls.return_value
        mock_response = Mock()
        mock_response.json.return_value = {"result": 6}  # Missing 'error'
        mock_client.post.return_value = mock_response

        client = AnkiConnectClient()

        with pytest.raises(AnkiConnectAPIError, match="missing 'error' field"):
            client.get_version()

    @patch("doughub.anki_client.transport.httpx.Client")
    def test_api_error_response(self, mock_client_cls):
        """Test handling of API error response."""
        mock_client = mock_client_cls.return_value
        mock_response = Mock()
        mock_response.json.return_value = {"result": None, "error": "Some API Error"}
        mock_client.post.return_value = mock_response

        client = AnkiConnectClient()

        with pytest.raises(AnkiConnectAPIError, match="Some API Error"):
            client.get_version()
