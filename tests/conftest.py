"""Shared pytest fixtures and configuration for DougHub tests."""

import logging
from collections.abc import Generator
from typing import Any

import pytest

from doughub.anki_client import AnkiRepository
from doughub.utils.anki_process import AnkiProcessManager

# Backward compatibility alias
AnkiConnectClient = AnkiRepository

logger = logging.getLogger(__name__)

# Track note IDs created during tests for cleanup
_created_note_ids: list[int] = []


@pytest.fixture(scope="session")
def anki_manager() -> Generator[AnkiProcessManager, None, None]:
    """Fixture to manage Anki process for integration tests.

    This fixture will attempt to launch Anki if it's not already running.
    It does not stop Anki after tests to avoid disrupting user workflow.
    """
    manager = AnkiProcessManager()
    if not manager.is_ankiconnect_running():
        success = manager.launch_anki(timeout=15.0)
        if not success:
            pytest.skip("Anki could not be started and is not running")
    yield manager
    # Note: We don't stop Anki after tests to avoid disrupting user's workflow


@pytest.fixture(scope="session")
def test_deck_manager(anki_manager: AnkiProcessManager) -> Generator[str, None, None]:
    """Fixture to ensure test deck exists and is available.

    Creates a dedicated test deck if it doesn't exist. The deck persists
    after tests to enable manual inspection of test data.

    Returns:
        The name of the test deck.
    """
    deck_name = "DougHub_Testing"
    client = AnkiConnectClient()

    try:
        deck_names = client.get_deck_names()
        if deck_name not in deck_names:
            logger.info(f"Creating test deck: {deck_name}")
            # AnkiConnect doesn't have createDeck, so we'll create a note in the deck
            # which will auto-create it. Then we can delete the note.
            try:
                temp_note_id = client.add_note(
                    deck_name=deck_name,
                    model_name="Basic",
                    fields={"Front": "__temp__", "Back": "__temp__"},
                    tags=["__temp__"],
                )
                # Note: We keep the note for now as a deck anchor
                # In future, implement deck creation via AnkiConnect if available
                logger.debug(f"Created temporary note {temp_note_id} to establish deck")
            except Exception as e:
                logger.warning(f"Could not create test deck: {e}")
    except Exception as e:
        logger.warning(f"Could not verify test deck: {e}")

    yield deck_name

    # Cleanup: optionally remove test deck
    # For now, we keep it to allow manual inspection
    client.close()


@pytest.fixture
def integration_client(
    anki_manager: AnkiProcessManager,
) -> Generator[AnkiRepository, None, None]:
    """Fixture to create an AnkiConnect client for integration tests.

    Skips tests if AnkiConnect is not accessible.
    """
    client = AnkiRepository()
    if not client.check_connection():
        pytest.skip("AnkiConnect is not accessible")
    yield client
    client.close()


@pytest.fixture(autouse=True, scope="function")
def track_test_notes() -> Generator[None, None, None]:
    """Autouse fixture to track and cleanup notes created during tests.

    Tests can call register_note_for_cleanup(note_id) to mark notes
    for deletion after the test completes.
    """
    global _created_note_ids
    _created_note_ids = []
    yield
    # Cleanup created notes
    if _created_note_ids:
        try:
            client = AnkiRepository()
            # Access transport directly for deleteNotes (not in public API)
            client.transport.invoke("deleteNotes", {"notes": _created_note_ids})
            logger.info(f"Cleaned up {len(_created_note_ids)} test notes")
            client.close()
        except Exception as e:
            logger.warning(f"Could not cleanup test notes: {e}")


def register_note_for_cleanup(note_id: int) -> None:
    """Register a note ID to be deleted after the current test.

    Args:
        note_id: The note ID to clean up.
    """
    global _created_note_ids
    _created_note_ids.append(note_id)


def assert_valid_note_structure(note_dict: dict[str, Any]) -> None:
    """Assert that a note dictionary has the expected structure.

    Args:
        note_dict: The note dictionary from AnkiConnect API.

    Raises:
        AssertionError: If the note structure is invalid.
    """
    assert "noteId" in note_dict, "Note missing 'noteId' field"
    assert isinstance(note_dict["noteId"], int), "'noteId' must be an integer"

    assert "modelName" in note_dict, "Note missing 'modelName' field"
    assert isinstance(note_dict["modelName"], str), "'modelName' must be a string"

    assert "fields" in note_dict, "Note missing 'fields' field"
    assert isinstance(note_dict["fields"], dict), "'fields' must be a dictionary"

    # Validate fields structure: each field should be a dict with 'value' key
    for field_name, field_data in note_dict["fields"].items():
        assert isinstance(field_data, dict), f"Field '{field_name}' must be a dict"
        assert "value" in field_data, f"Field '{field_name}' missing 'value' key"
        assert isinstance(field_data["value"], str), (
            f"Field '{field_name}' value must be a string"
        )

    assert "tags" in note_dict, "Note missing 'tags' field"
    assert isinstance(note_dict["tags"], list), "'tags' must be a list"
